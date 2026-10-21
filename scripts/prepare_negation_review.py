"""Prepare a score-blind bilingual review packet from completed development runs."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


MARKERS = {
    'eng_Latn': {'not', 'except', 'false', 'incorrect', 'least', 'unlikely',
                 'atypical', 'cannot', 'never', 'no', 'without'},
    'ben_Beng': {'না', 'নয়', 'নয়', 'নেই', 'নন', 'ব্যতীত', 'ছাড়া', 'ছাড়া',
                 'বাদে', 'ভুল', 'অসত্য', 'অসম্ভব', 'অস্বাভাবিক', 'ব্যতিক্রম', 'সর্বনিম্ন'},
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hints(question, language):
    # Screening hints only: every item is reviewed, including zero-hit items.
    tokens = {t.strip('।?!,;:"\'“”‘’()[]').lower() for t in question.split()}
    return sorted(tokens & MARKERS[language])


def public_document(doc, language):
    # Whitelist fields so model scores, predictions and answer keys cannot leak.
    return dict(passage=doc['flores_passage'], question=doc['question'],
        choices=[doc[f'mc_answer{i}'] for i in range(1, 5)],
        screening_hints=hints(doc['question'], language),
        review=dict(selection_polarity=None, subtype=None, scope_quote=None, notes=None))


def load_documents(directory, language):
    docs, files = {}, {}
    for path in sorted(directory.glob(f'{language}-*.json')):
        raw = json.loads(path.read_text(encoding='utf-8'))
        files[path.name] = digest(path)
        for sample in raw['samples'][f'belebele_{language}']:
            doc = sample['doc']
            key = (doc['link'], doc['question_number'])
            if key in docs:
                raise ValueError('Duplicate source/question')
            docs[key] = doc
    if len(docs) != 300:
        raise ValueError('Expected exactly 300 development documents per language')
    return docs, files


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, required=True)
    p.add_argument('--raw-directory', type=Path, required=True)
    p.add_argument('--output-directory', type=Path, required=True)
    args = p.parse_args()
    if args.output_directory.exists():
        raise FileExistsError(args.output_directory)
    groups = json.loads(args.lock.read_text(encoding='utf-8'))['items']
    if len(groups) != 300:
        raise ValueError('Expected 300 frozen development groups')
    documents, inputs = {}, {}
    for lang in MARKERS:
        documents[lang], files = load_documents(args.raw_directory, lang)
        inputs.update(files)
        expected = {(g[lang]['source'], g[lang]['question']) for g in groups}
        if len(expected) != 300 or expected != set(documents[lang]):
            raise ValueError('Raw documents do not match frozen membership')
    rows = []
    for index, group in enumerate(groups):
        key = (group['eng_Latn']['source'], group['eng_Latn']['question'])
        if key != (group['ben_Beng']['source'], group['ben_Beng']['question']):
            raise ValueError('Cross-language item mismatch')
        rows.append(dict(index=index, source=key[0], question_number=key[1],
            languages={lang:public_document(documents[lang][key], lang) for lang in MARKERS},
            pair_review=dict(polarity_equivalent=None, translation_issue=None,
                             adjudication_notes=None, reviewer=None, reviewed_at=None)))
    packet = dict(scope='All 300 matched development pairs; no model outputs or gold labels',
        sample_lock_sha256=digest(args.lock), generator_sha256=digest(__file__),
        input_hashes=inputs, rows=rows)
    counts = Counter()
    for row in rows:
        en = bool(row['languages']['eng_Latn']['screening_hints'])
        bn = bool(row['languages']['ben_Beng']['screening_hints'])
        counts[f'en_hint_{int(en)}_bn_hint_{int(bn)}'] += 1
    summary = dict(scope='Keyword screening only, not negation labels or model-error counts',
        matched_pairs=300, pending_human_reviews=300, screening_pair_counts=dict(counts),
        sample_lock_sha256=digest(args.lock), no_accuracy_analysis=True)
    args.output_directory.mkdir(parents=True)
    path = args.output_directory / 'packet.json'
    path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding='utf-8')
    summary['packet_sha256'] = digest(path)
    (args.output_directory / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    lines = ['# Bilingual question review — labels pending', '',
             'All 300 development pairs; no model predictions, scores or answer keys.',
             'Record labels in a separate copy of packet.json. Screening hints are not labels.', '']
    for row in rows:
        lines += [f"## Item {row['index']} · question {row['question_number']}", '',
                  f"Source: {row['source']}", '']
        for lang, doc in row['languages'].items():
            lines += [f'### {lang}', '', doc['passage'], '', '**Question:** ' + doc['question'], '']
            lines += [f'{letter}. {text}' for letter, text in zip('ABCD', doc['choices'], strict=True)]
            lines += ['', 'Screening hints: ' + ', '.join(doc['screening_hints']), '']
    # Presentation-only whitespace cleanup; packet.json preserves source text exactly.
    display = '\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()).rstrip() + '\n'
    (args.output_directory / 'review.md').write_text(display, encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
