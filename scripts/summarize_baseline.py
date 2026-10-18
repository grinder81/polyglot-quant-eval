"""Validate and summarize the frozen three-arm, 50-per-language run."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ARMS = ('bf16-vllm', 'bf16-gguf', 'q4')
LANGS = ('eng_Latn', 'ben_Beng', 'hin_Deva')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(root, arm):
    identity = json.loads((root / arm / 'identity.json').read_text(encoding="utf-8"))
    assert digest(root / f'{arm}-runtime.json') == identity['runtime']
    records = {}
    for lang in LANGS:
        for start in range(0, 50, 5):
            path = root / arm / f'{lang}-{start:03}.json'
            data = json.loads(path.read_text(encoding="utf-8"))
            samples = [s for rows in data['samples'].values() for s in rows]
            assert len(samples) == 5, path
            for sample in samples:
                key = (lang, sample['doc_hash'])
                assert key not in records, key
                scores = [r[0] for r in sample['filtered_resps']]
                assert len(scores) == 4 and all(math.isfinite(x) for x in scores)
                pred = max(range(4), key=scores.__getitem__)
                target = int(sample['target'])
                assert int(pred == target) == sample['acc']
                assert [a[1] for a in sample['arguments']] == [' A', ' B', ' C', ' D']
                ordered = sorted(scores, reverse=True)
                records[key] = dict(sample, prediction=pred,
                                    margin=ordered[0] - ordered[1])
        assert sum(k[0] == lang for k in records) == 50
    return identity, records


def summarize(root):
    loaded = {arm: load(root, arm) for arm in ARMS}
    reference = loaded[ARMS[0]][1]
    for identity, records in loaded.values():
        assert identity['lock'] == loaded[ARMS[0]][0]['lock']
        assert identity['runner'] == loaded[ARMS[0]][0]['runner']
        assert records.keys() == reference.keys()
        for key, row in records.items():
            assert row['arguments'] == reference[key]['arguments'], key
            assert row['target'] == reference[key]['target'], key
    accuracy = {arm: {lang: sum(s['acc'] for k, s in rec.items() if k[0] == lang)
                      for lang in LANGS} for arm, (_, rec) in loaded.items()}
    pairs = {}
    for base, other in [('bf16-gguf', 'q4'), ('bf16-vllm', 'bf16-gguf'), ('bf16-vllm', 'q4')]:
        by_lang = {}
        for lang in LANGS:
            rows = [(loaded[base][1][k], loaded[other][1][k]) for k in reference if k[0] == lang]
            by_lang[lang] = {
                'changed_answers': sum(a['prediction'] != b['prediction'] for a, b in rows),
                'right_to_wrong': sum(a['acc'] == 1 and b['acc'] == 0 for a, b in rows),
                'wrong_to_right': sum(a['acc'] == 0 and b['acc'] == 1 for a, b in rows),
                'delta_pp': 2 * (accuracy[other][lang] - accuracy[base][lang]),
                'mean_margin_delta': sum(b['margin'] - a['margin'] for a, b in rows) / 50,
            }
        for lang in LANGS:
            by_lang[lang]['delta_gap_vs_english_pp'] = by_lang[lang]['delta_pp'] - by_lang['eng_Latn']['delta_pp']
        pairs[f'{base}_to_{other}'] = by_lang
    return {'n_per_language': 50, 'correct': accuracy, 'pairs': pairs}, loaded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    summary, loaded = summarize(args.root)
    (args.root / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    rows = []
    for arm in ARMS:
        for lang, code in zip(LANGS, ('en', 'bn', 'hi')):
            rows.append(dict(run_id=f'fifty-{arm}', timestamp='2026-10-18T23:53:48Z',
                             model_id='CohereLabs/tiny-aya-global', format='gguf-q4_k_m' if arm == 'q4' else 'bf16',
                             runtime='vllm' if arm == 'bf16-vllm' else 'llama-cpp-python',
                             device='rtx5090', task='belebele', language=code, metric='acc',
                             value=summary['correct'][arm][lang] / 50, n=50,
                             mode='loglikelihood_mcq', fewshot=0, seed=42,
                             source_file=f'{arm}/', notes='Development baseline; patched runtimes in accompanying manifest.'))
    (args.root / 'rows.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
