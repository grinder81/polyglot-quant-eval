"""Exploratory margin/flip association on validated original-order GGUF evidence.

Input paths are expanded evidence ROOTS, not arbitrary shard folders. See
docs/margin-flip-analysis.md. No silent intersection joins or causal conclusions.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

try:
    from .compare_expanded import validate_runtime_pair
    from .summarize_expanded_local import LANGS, summarize
except ImportError:
    from compare_expanded import validate_runtime_pair
    from summarize_expanded_local import LANGS, summarize

BINS = [(0., .25), (.25, .5), (.5, 1.), (1., 2.), (2., math.inf)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def valid_identity(source, question):
    return (isinstance(source, str) and bool(source.strip())
            and type(question) in (str, int) and bool(str(question).strip()))


def validate_scores(scores, target):
    require(type(target) is int and target in range(4), 'Invalid target index')
    require(len(scores) == 4 and all(type(s) in (int, float) and math.isfinite(s) for s in scores),
            'Expected four finite numeric candidate scores')
    require(math.isfinite(margin(scores)), 'Nonfinite top-two margin')


def _strict_inputs(root, arm):
    directory = root / arm
    names = {f'{lang}-{start:03}.json' for lang in LANGS for start in range(0, 300, 5)}
    require({p.name for p in directory.glob('*.json')} == names | {'identity.json'}
            and not list(directory.glob('*.tmp')), 'Incomplete or unexpected shard inventory')
    identity = read(directory / 'identity.json')
    require(identity['arm'] == arm and identity['backend'] == 'gguf'
            and identity['count_per_language'] == 300 and identity['shard_size'] == 5
            and identity.get('start', 0) == 0, 'Unsupported original-order run identity')
    for name in ('lock', 'runner', 'runtime'):
        require(isinstance(identity[name], str) and re.fullmatch('[0-9a-f]{64}', identity[name]),
                'Missing hashed source provenance')
    runtime = read(root / f'{arm}-runtime.json')
    require(runtime['arm'] == arm and sha(root / f'{arm}-runtime.json') == identity['runtime'],
            'Runtime identity mismatch')
    command = runtime['server_command']
    require(command.count('--model') == 1 and bool(runtime['packages']), 'Invalid runtime manifest')
    model = command[command.index('--model') + 1]
    require(model in runtime['files'] and len(runtime['files']) >= 2, 'Missing model/runtime provenance')
    require(all(isinstance(h, str) and re.fullmatch('[0-9a-f]{64}', h) for h in runtime['files'].values()),
            'Invalid runtime source hash')
    membership = read(root / 'sample-identities.json')
    require(membership['original_lock_sha256'] == identity['lock'] and len(membership['items']) == 300,
            'Frozen membership identity mismatch')
    seen = set()
    for group in membership['items']:
        require(set(group) == set(LANGS), 'All three language memberships required')
        for lang, row in group.items():
            require(valid_identity(row['source'], row['question']), 'Missing source/question identity')
            key = lang, row['source'], str(row['question'])
            require(key not in seen, 'Duplicate frozen question identity')
            seen.add(key)
            validate_scores([0] * 4, row['target'])
    for name in sorted(names):
        language = next(lang for lang in LANGS if name.startswith(lang + '-'))
        data = read(directory / name)
        require(set(data['samples']) == {'belebele_' + language}, 'Unexpected task in shard')
        samples = data['samples']['belebele_' + language]
        require(len(samples) == 5, 'Expected five questions per shard')
        for sample in samples:
            doc = sample['doc']
            require(valid_identity(doc.get('link'), doc.get('question_number')),
                    'Missing source/question identity')
            validate_scores([response[0] for response in sample['filtered_resps']], sample['target'])
    return identity, membership, {name: sha(directory / name) for name in sorted(names)}


def load_pair(reference, candidate):
    """Reuse complete membership/request/score validation and paired runtime checks.

    Each root contains sample-identities.json, ARM-runtime.json and ARM/ with
    identity.json plus 180 original-order shards. No future runner schema inferred.
    """
    require(__debug__, 'Run without -O: reused evidence validation requires assertions')
    roots, arms = [Path(reference), Path(candidate)], ('bf16-gguf', 'local-q4')
    evidence = [_strict_inputs(root, arm) for root, arm in zip(roots, arms)]
    require(evidence[0][1] == evidence[1][1], 'Frozen memberships differ between arms')
    try:
        validate_runtime_pair(*roots)
        validated = [summarize(root, arm)[1] for root, arm in zip(roots, arms)]
    except (AssertionError, KeyError, TypeError, IndexError) as error:
        raise ValueError('Existing expanded-evidence validation failed') from error
    records = []
    for rows in validated:
        mapped = {}
        for row in rows:
            key = ('belebele_' + row['language'], row['source'], str(row['question']))
            require(key not in mapped, 'Duplicate question identity')
            mapped[key] = (row['scores'], row['target'])
        records.append(mapped)
    provenance = {}
    for root, arm, (identity, _, shards) in zip(roots, arms, evidence):
        require(read(root / arm / 'identity.json') == identity
                and read(root / 'sample-identities.json') == evidence[0][1]
                and sha(root / f'{arm}-runtime.json') == identity['runtime']
                and all(sha(root / arm / name) == h for name, h in shards.items()),
                'Input evidence changed during validation')
        provenance[arm] = dict(root=str(root.resolve()), identity=identity,
            identity_sha256=sha(root / arm / 'identity.json'),
            membership_sha256=sha(root / 'sample-identities.json'),
            runtime_sha256=sha(root / f'{arm}-runtime.json'), shard_sha256=shards)
    return *records, provenance


def margin(scores):
    ordered = sorted(scores, reverse=True)
    return ordered[0] - ordered[1]


def argmax(scores):
    return max(range(len(scores)), key=scores.__getitem__)


def analyze(reference, candidate):
    """Descriptive counts only; scientific inputs must first pass load_pair."""
    require(bool(reference) and reference.keys() == candidate.keys(), 'Unmatched or empty identities')
    for key in reference:
        require(len(key) == 3 and isinstance(key[0], str) and bool(key[0])
                and valid_identity(key[1], key[2]), 'Missing task/source/question identity')
        for records in (reference, candidate):
            validate_scores(*records[key])
        require(reference[key][1] == candidate[key][1], 'Target mismatch')
    keys = sorted(reference, key=lambda k: (k[0], k[1], str(k[2])))
    out = {}
    for task in sorted({k[0] for k in keys}):
        rows = [(reference[k], candidate[k]) for k in keys if k[0] == task]
        bins = []
        for lo, hi in BINS:
            selected = [(r, c) for r, c in rows if lo <= margin(r[0]) < hi]
            flips = sum(argmax(r[0]) != argmax(c[0]) for r, c in selected)
            bins.append(dict(margin_nats=[lo, None if math.isinf(hi) else hi],
                n=len(selected), flips=flips, flip_rate=flips / len(selected) if selected else None))
        ref_correct = sum(argmax(r[0]) == r[1] for r, _ in rows)
        cand_correct = sum(argmax(c[0]) == c[1] for _, c in rows)
        out[task] = dict(n=len(rows), bins=bins,
            share_margin_below_1_nat=sum(margin(r[0]) < 1 for r, _ in rows) / len(rows),
            total_flips=sum(b['flips'] for b in bins), reference_correct=ref_correct,
            candidate_correct=cand_correct, accuracy_delta=(cand_correct-ref_correct) / len(rows),
            source_clusters=len({k[1] for k in keys if k[0] == task}))
    english = out.get('belebele_eng_Latn')
    for row in out.values():
        row['accuracy_delta_minus_english'] = row['accuracy_delta']-english['accuracy_delta'] if english else None
    return out


def render(result):
    lines = []
    for task, stats in result.items():
        lines.append(f"{task}: n={stats['n']}, flips={stats['total_flips']}, "
            f"correct reference/candidate={stats['reference_correct']}/{stats['candidate_correct']}; "
            f"accuracy delta={stats['accuracy_delta']:+.4f}, delta minus English={stats['accuracy_delta_minus_english']}")
        for b in stats['bins']:
            lines.append(f"  margin {b['margin_nats']}: n={b['n']}, flips={b['flips']}, rate={b['flip_rate']}")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True, type=Path, help='validated BF16 expanded evidence root')
    parser.add_argument('--candidate', required=True, type=Path, help='validated local-Q4 expanded evidence root')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), 'Output must be new')
    reference, candidate, provenance = load_pair(args.reference, args.candidate)
    result = analyze(reference, candidate)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(dict(input_schema='validated-expanded-original-order-v1', provenance=provenance,
            results=result, interpretation='Exploratory historical association; descriptive counts without '
            'source-cluster confidence intervals. Not a causal explanation, calibrated confidence measure, '
            'language-adjusted effect or evidence of no residual language effect. Older runtime identities '
            'retain their A3 request-history caveat; these are not fresh cold-runtime baselines.'),
            stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(render(result))


if __name__ == '__main__':
    main()
