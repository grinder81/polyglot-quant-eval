"""Source-clustered statistics for the preregistered rotation diagnostic.

Input records contain one arm/language's complete four-rotation score vectors.
Bootstrap multiplicities weight both offset fitting and evaluation; all translations
and arms share the same sampled sources. No canonical scoring change is made.
"""
from collections import Counter
import random

from .option_rotation import estimate_offsets, original_choice, predict, source_fold


def measure(records, weights=None):
    keys = [(r['source'], r['question']) for r in records]
    if len(set(keys)) != len(keys) or not keys:
        raise ValueError('Empty or duplicate records')
    weights = {s: 1 for s, _ in keys} if weights is None else weights
    active = [r for r in records if weights.get(r['source'], 0)]
    if not active:
        raise ValueError('Empty sample')
    offsets = {}
    for fold in {source_fold(r['source']) for r in active}:
        fit = [r['rotations'] for r in active if source_fold(r['source']) != fold
               for _ in range(weights[r['source']])]
        if not fit:
            raise ValueError('Empty training fold')
        offsets[fold] = estimate_offsets(fit)
    counts = {mode: Counter() for mode in ('raw', 'cross_fitted')}
    predictions = {mode: {} for mode in counts}
    n = sum(weights[r['source']] for r in active)
    for r in active:
        if r['target'] not in range(4) or len(r['rotations']) != 4:
            raise ValueError('Invalid target or rotation count')
        weight = weights[r['source']]
        for mode in counts:
            offset = None if mode == 'raw' else offsets[source_fold(r['source'])]
            positions = [predict(scores, offset) for scores in r['rotations']]
            content = [original_choice(p, shift) for shift, p in enumerate(positions)]
            predictions[mode][r['source'], r['question']] = content
            c = counts[mode]
            for shift, (position, choice) in enumerate(zip(positions, content)):
                c[f'correct_r{shift}'] += weight * (choice == r['target'])
                c[f'predicted_r{shift}_{"ABCD"[position]}'] += weight
                c[f'gold_r{shift}_{"ABCD"[(r["target"] - shift) % 4]}'] += weight
            c['consistent'] += weight * (len(set(content)) == 1)
            c['pairwise'] += weight * sum(content[i] == content[j] for i in range(4) for j in range(i))
    metrics = {}
    for mode, c in counts.items():
        metrics[mode + '_accuracy_original'] = c['correct_r0'] / n
        metrics[mode + '_accuracy_average'] = sum(c[f'correct_r{s}'] for s in range(4)) / (4 * n)
        metrics[mode + '_consistency'] = c['consistent'] / n
        metrics[mode + '_pairwise_agreement'] = c['pairwise'] / (6 * n)
        for shift in range(4):
            metrics[f'{mode}_accuracy_r{shift}'] = c[f'correct_r{shift}'] / n
    for metric in ('accuracy_original', 'accuracy_average', 'consistency', 'pairwise_agreement'):
        metrics['correction_delta_' + metric] = metrics['cross_fitted_' + metric] - metrics['raw_' + metric]
    return dict(n=n, metrics=metrics, counts=counts, offsets=offsets,
                fold_sizes=dict(Counter(source_fold(r['source']) for r in active))), predictions


def joint_statistics(cells, replicates=10000, seed=42, english='eng_Latn'):
    """cells maps (arm, language) to matched records; tuple keys stay in memory."""
    if replicates < 1 or not cells:
        raise ValueError('Positive bootstrap count and cells required')
    keysets = [{(r['source'], r['question']) for r in records} for records in cells.values()]
    if any(k != keysets[0] for k in keysets):
        raise ValueError('Unmatched cells')
    targets = [{(r['source'], r['question']): r['target'] for r in records} for records in cells.values()]
    if any(t != targets[0] for t in targets):
        raise ValueError('Target mismatch')
    sources = sorted({s for s, _ in keysets[0]})
    estimates = {key: measure(records)[0] for key, records in cells.items()}
    draws = {key: {m: [] for m in result['metrics']} for key, result in estimates.items()}
    paired = {}
    languages = sorted({language for _, language in cells})
    if english not in languages:
        raise ValueError('English comparison required')
    for language in languages:
        if ('bf16-gguf', language) not in cells or ('local-q4', language) not in cells:
            raise ValueError('Both model arms required')
        paired[language] = {m: [] for m in estimates['bf16-gguf', language]['metrics']}
    rng = random.Random(seed)
    invalid = 0
    for _ in range(replicates):
        weights = Counter(rng.choices(sources, k=len(sources)))
        try:
            sample = {key: measure(records, weights)[0]['metrics'] for key, records in cells.items()}
        except ValueError as error:
            if str(error) != 'Empty training fold':
                raise
            invalid += 1
            continue
        for key, metrics in sample.items():
            for metric, value in metrics.items():
                draws[key][metric].append(value)
        for language in languages:
            for metric in paired[language]:
                paired[language][metric].append(sample['local-q4', language][metric] - sample['bf16-gguf', language][metric])
    def interval(values):
        if not values:
            return None
        values = sorted(values)
        return [values[max(0, int(.025 * len(values)) - 1)], values[max(0, int(.975 * len(values)) - 1)]]
    def delta(language, metric):
        return estimates['local-q4', language]['metrics'][metric] - estimates['bf16-gguf', language]['metrics'][metric]
    return dict(cells={key: {**result, 'cluster_95_intervals': {m: interval(v) for m, v in draws[key].items()}}
                       for key, result in estimates.items()},
                q4_minus_bf16={language: {m: {
                    'estimate': delta(language, m),
                    'cluster_95_interval': interval(v),
                    'delta_minus_english': delta(language, m) - delta(english, m),
                    'delta_minus_english_cluster_95_interval': interval([x - y for x, y in zip(v, paired[english][m])])}
                    for m, v in metrics.items()}
                    for language, metrics in paired.items()},
                bootstrap_replicates=replicates, invalid_empty_training_fold_replicates=invalid,
                bootstrap_seed=seed, source_clusters=len(sources))
