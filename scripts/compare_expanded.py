"""Compare matched BF16 and Q4 evidence with joint passage-cluster uncertainty."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random

try:
    from .summarize_expanded_local import LANGS, summarize
except ImportError:
    from summarize_expanded_local import LANGS, summarize


def compare_rows(reference, candidate, replicates=10000):
    def index(rows):
        result = {(r['language'], r['source'], r['question']): r for r in rows}
        if len(result) != len(rows):
            raise ValueError('Duplicate identity')
        return result
    ref, cand = index(reference), index(candidate)
    if ref.keys() != cand.keys():
        raise ValueError('Unmatched items')
    keys = sorted((s, q) for l, s, q in ref if l == LANGS[0])
    if not keys or any({(s, q) for l, s, q in ref if l == lang} != set(keys) for lang in LANGS):
        raise ValueError('Unmatched translated items')
    clusters = defaultdict(list)
    result = {}
    for source, question in keys:
        delta = []
        for lang in LANGS:
            a, b = ref[lang, source, question], cand[lang, source, question]
            if a['target'] != b['target']:
                raise ValueError('Target mismatch')
            delta.append(b['correct'] - a['correct'])
        clusters[source].append(delta)
    for lang in LANGS:
        pairs = [(ref[lang, s, q], cand[lang, s, q]) for s, q in keys]
        result[lang] = dict(n=len(pairs), bf16_correct=sum(a['correct'] for a, b in pairs),
            q4_correct=sum(b['correct'] for a, b in pairs),
            changed_choices=sum(a['prediction'] != b['prediction'] for a, b in pairs),
            right_to_wrong=sum(a['correct'] == 1 and b['correct'] == 0 for a, b in pairs),
            wrong_to_right=sum(a['correct'] == 0 and b['correct'] == 1 for a, b in pairs),
            wrong_to_wrong=sum(a['correct'] == b['correct'] == 0 and a['prediction'] != b['prediction'] for a, b in pairs),
            bf16_predicted_letters=dict(Counter('ABCD'[a['prediction']] for a, b in pairs)),
            q4_predicted_letters=dict(Counter('ABCD'[b['prediction']] for a, b in pairs)),
            gold_letters=dict(Counter('ABCD'[a['target']] for a, b in pairs)))
        result[lang]['accuracy_delta_q4_minus_bf16'] = (result[lang]['q4_correct'] - result[lang]['bf16_correct']) / len(pairs)
    # Draw the SAME source clusters for languages and model arms. This preserves
    # pairing when estimating whether compression changes one language more.
    values = [(len(v), [sum(row[i] for row in v) for i in range(3)]) for v in clusters.values()]
    rng = random.Random(42)
    draws = [[] for _ in LANGS]
    relative = [[] for _ in LANGS]
    for _ in range(replicates):
        sampled = rng.choices(values, k=len(values))
        n = sum(v[0] for v in sampled)
        d = [sum(v[1][i] for v in sampled) / n for i in range(3)]
        for i in range(3):
            draws[i].append(d[i])
            relative[i].append(d[i] - d[0])
    def interval(v):
        v = sorted(v)
        return [v[max(0, int(.025 * len(v)) - 1)], v[max(0, int(.975 * len(v)) - 1)]]
    for i, lang in enumerate(LANGS):
        row = result[lang]
        row['paired_cluster_95_delta_interval'] = interval(draws[i])
        row['delta_minus_english_delta'] = row['accuracy_delta_q4_minus_bf16'] - result[LANGS[0]]['accuracy_delta_q4_minus_bf16']
        row['paired_cluster_95_delta_minus_english_interval'] = interval(relative[i])
        for arm in ('bf16', 'q4'):
            row[arm + '_accuracy_gap_to_english'] = (row[arm + '_correct'] - result[LANGS[0]][arm + '_correct']) / len(keys)
    return dict(languages=result, source_clusters=len(values), bootstrap_seed=42,
                bootstrap_replicates=replicates,
                interpretation='Development-sample uncertainty, conditional on these sources and scoring. Not evidence of equivalence or a causal language mechanism.')


def validate_runtime_pair(reference, candidate):
    manifests = [json.loads((root / (arm + '-runtime.json')).read_text())
                 for root, arm in ((reference, 'bf16-gguf'), (candidate, 'local-q4'))]
    a, b = manifests
    def settings(m):
        command = list(m['server_command'])
        model = command[command.index('--model') + 1]
        command[command.index('--model') + 1] = '<model>'
        return dict(command=command, packages=m['packages'],
                    runtime_files={p: h for p, h in m['files'].items() if p != model})
    if settings(a) != settings(b):
        raise ValueError('Runtime/settings differ between arms')
    identities = [json.loads((root / arm / 'identity.json').read_text())
                  for root, arm in ((reference, 'bf16-gguf'), (candidate, 'local-q4'))]
    comparable = [{k: v for k, v in identity.items() if k not in ('arm', 'runtime')} for identity in identities]
    if comparable[0] != comparable[1]:
        raise ValueError('Lock, runner or scoring identity differs')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    validate_runtime_pair(args.reference, args.candidate)
    _, reference = summarize(args.reference, 'bf16-gguf')
    _, candidate = summarize(args.candidate, 'local-q4')
    report = compare_rows(reference, candidate)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
