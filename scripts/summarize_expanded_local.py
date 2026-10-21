"""Validate frozen local-Q4 shards and summarize passage-clustered accuracy."""
import argparse
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

LANGS = ('eng_Latn', 'ben_Beng', 'hin_Deva')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def summarize(root):
    identity = json.loads((root / 'local-q4/identity.json').read_text())
    assert identity['count_per_language'] == 300 and identity.get('start', 0) == 0
    assert sha((root / 'local-q4-runtime.json').read_bytes()) == identity['runtime']
    lock = json.loads((root / 'sample-identities.json').read_text(encoding='utf-8'))
    assert lock['original_lock_sha256'] == identity['lock']
    assert len(lock['items']) == 300
    expected_files = {f'{l}-{i:03}.json' for l in LANGS for i in range(0, 300, 5)}
    assert {p.name for p in (root / 'local-q4').glob('*-*.json')} == expected_files
    rows = []
    for lang in LANGS:
        seen = set()
        for start in range(0, 300, 5):
            expected = {(g[lang]['source'], g[lang]['question']): g[lang]
                        for g in lock['items'][start:start + 5]}
            data = json.loads((root / 'local-q4' / f'{lang}-{start:03}.json').read_text(encoding='utf-8'))
            samples = data['samples']['belebele_' + lang]
            assert len(samples) == 5
            shard_correct = 0
            for s in samples:
                key = (s['doc']['link'], s['doc']['question_number'])
                assert key not in seen and key in expected
                seen.add(key)
                item = expected[key]
                assert s['doc']['link'] == item['source']
                assert s['doc']['question_number'] == item['question']
                assert s['target'] == item['target']
                args = s['arguments']
                assert len(args) == 4 and [a[1] for a in args] == [' A', ' B', ' C', ' D']
                assert all(sha(a[0].encode()) == item['prompt_sha256'] for a in args)
                assert [sha(a[1].encode()) for a in args] == item['candidate_sha256']
                scores = [r[0] for r in s['filtered_resps']]
                assert len(scores) == 4 and all(math.isfinite(v) for v in scores)
                prediction = max(range(4), key=scores.__getitem__)
                correct = int(prediction == s['target'])
                assert correct == s['acc']
                shard_correct += correct
                rows.append(dict(language=lang, doc_id=item['index'], raw_doc_id=s['doc_id'], source=item['source'],
                                 question=item['question'], correct=correct,
                                 target=s['target'], prediction=prediction, scores=scores))
            assert math.isclose(data['results']['belebele_' + lang]['acc,none'], shard_correct / 5)
        assert len(seen) == 300
    # Resample whole source passages, retaining their questions, to avoid treating
    # questions sharing a passage as independent Bernoulli trials.
    result = {}
    for lang in LANGS:
        selected = [r for r in rows if r['language'] == lang]
        groups = defaultdict(list)
        for r in selected:
            groups[r['source']].append(r['correct'])
        clusters = [(sum(g), len(g)) for g in groups.values()]
        rng = random.Random(42)
        draws = []
        for _ in range(10000):
            sampled = rng.choices(clusters, k=len(clusters))
            draws.append(sum(c for c, n in sampled) / sum(n for c, n in sampled))
        draws.sort()
        correct = sum(r['correct'] for r in selected)
        result[lang] = dict(n=300, correct=correct, accuracy=correct / 300,
                            source_passages=len(groups),
                            cluster_bootstrap_95_interval=[draws[249], draws[9749]])
    paired = defaultdict(int)
    mapped = {l: {(r['source'], r['question']): r for r in rows if r['language'] == l} for l in LANGS}
    assert all(mapped[l].keys() == mapped[LANGS[0]].keys() for l in LANGS)
    for key in mapped['eng_Latn']:
        paired[f"en{mapped['eng_Latn'][key]['correct']}_bn{mapped['ben_Beng'][key]['correct']}"] += 1
    return dict(n=900, correct=sum(r['correct'] for r in rows), languages=result,
                english_bangla_paired=dict(paired), bootstrap_seed=42,
                bootstrap_replicates=10000), rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    summary, _ = summarize(args.root)
    (args.root / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
