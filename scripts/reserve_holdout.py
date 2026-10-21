"""Reserve source-disjoint Belebele membership without inspecting answers."""
import argparse
import hashlib
import json
from pathlib import Path

LANGUAGES = ('eng_Latn', 'ben_Beng', 'hin_Deva')
REVISION = '7899cdfa4e1e0d733fd77c848e2c273cb1d32be2'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def reserve(metadata, lock, lock_sha):
    if lock['revision'] != REVISION or len(lock['items']) != 300:
        raise ValueError('Expected pinned 300-group development lock')
    maps = {}
    development = {}
    for lang in LANGUAGES:
        rows = metadata[lang]
        keys = [(r['link'], r['question_number']) for r in rows]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate dataset identity')
        maps[lang] = set(keys)
        development[lang] = {(g[lang]['source'], g[lang]['question']) for g in lock['items']}
        if len(development[lang]) != 300 or not development[lang] <= maps[lang]:
            raise ValueError('Development identities missing or duplicated')
    first = LANGUAGES[0]
    if any(maps[l] != maps[first] or development[l] != development[first] for l in LANGUAGES):
        raise ValueError('Languages do not have aligned membership')
    sources = {source for source, _ in development[first]}
    held = sorted(k for k in maps[first] if k[0] not in sources)
    excluded = sorted(maps[first] - development[first] - set(held))
    members = [dict(source=s, question=q) for s, q in held]
    return dict(version=1, dataset='facebook/belebele', revision=REVISION, split='test',
                languages=list(LANGUAGES), development_lock_sha256=lock_sha,
                membership_sha256=digest(members), members=members,
                counts_per_language=dict(dataset=len(maps[first]), development=300,
                    development_sources=len(sources), held_out=len(held),
                    held_out_sources=len({k[0] for k in held}),
                    excluded_shared_development_source=len(excluded)),
                metadata_sha256={l: digest(sorted(maps[l])) for l in LANGUAGES},
                access='Frozen finalists only; no tuning, calibration, probing or scoring before selection.',
                provenance_limit='Source-disjoint from recorded development only. Future calibration/train sources and near-duplicates must be audited before use.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    from datasets import load_dataset
    metadata = {}
    for lang in LANGUAGES:
        data = load_dataset('facebook/belebele', lang, revision=REVISION, split='test')
        metadata[lang] = list(data.select_columns(['link', 'question_number']))
    raw = args.lock.read_bytes()
    result = reserve(metadata, json.loads(raw), hashlib.sha256(raw).hexdigest())
    if result['counts_per_language']['held_out'] != 424:
        raise ValueError('Unexpected membership; review before reserving')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as out:
        json.dump(result, out, ensure_ascii=False, indent=2)
        out.write('\n')
    print(json.dumps(result['counts_per_language']))


if __name__ == '__main__':
    main()
