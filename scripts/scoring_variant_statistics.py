"""Pure A3 statistics; no inference, correction fitting, or contract selection.

Cells map (arm, variant, language) to records containing source, question,
target (original index), original_choices, rotations (four score vectors), and
choices (four displayed choice lists, without the added delimiter).
"""
from collections import Counter
from itertools import combinations
import math
import random

ARMS = ('bf16-gguf', 'local-q4')
VARIANTS = ('plain-letter', 'chat-letter', 'plain-option-text')
MODES = ('raw', 'acc_norm')


def cells_from_rows(rows):
    """Group runner compact rows after their provenance/lock join validation.

    Uses exact preparer lock field names plus arm and scores. This function does
    not replace the runner's byte-hash and runtime-identity validation.
    """
    grouped = {}
    for row in rows:
        cell = (row['arm'], row['variant'], row['language'])
        identity = (row['source'], row['question'])
        shift = row['shift']
        if type(shift) is not int or shift not in range(4):
            raise ValueError('Invalid rotation shift')
        if row['target'] != (row['original_target'] - shift) % 4:
            raise ValueError('Rotation target mismatch')
        choices = row['choices']
        expected = ([row['original_choices'][(i + shift) % 4] for i in range(4)]
                    if row['variant'] == 'plain-option-text' else list('ABCD'))
        if choices != expected or row['choice_character_lengths'] != list(map(len, choices)):
            raise ValueError('Choice text or Unicode character lengths mismatch')
        bucket = grouped.setdefault(cell, {})
        if identity not in bucket:
            bucket[identity] = dict(source=identity[0], question=identity[1],
                target=row['original_target'], original_choices=row['original_choices'],
                rotations=[None] * 4, choices=[None] * 4)
        record = bucket[identity]
        if record['target'] != row['original_target'] or record['original_choices'] != row['original_choices']:
            raise ValueError('Original item changed across rotations')
        if record['rotations'][shift] is not None:
            raise ValueError('Duplicate rotation row')
        record['rotations'][shift] = row['scores']
        record['choices'][shift] = choices
    cells = {key: list(bucket.values()) for key, bucket in grouped.items()}
    if any(any(value is None for value in r['rotations']) for records in cells.values() for r in records):
        raise ValueError('Incomplete rotations')
    return cells


def _prepare(records):
    output = {}
    for r in records:
        key = (r['source'], r['question'])
        if key in output:
            raise ValueError('Duplicate source/question')
        if (type(r['target']) is not int or r['target'] not in range(4)
                or len(r['original_choices']) != 4
                or len(r['rotations']) != 4 or len(r['choices']) != 4):
            raise ValueError('Invalid target, choices, or rotation count')
        predictions = {}
        features = {}
        histograms = {}
        for mode in MODES:
            positions = []
            for scores, choices in zip(r['rotations'], r['choices']):
                if (len(scores) != 4 or len(choices) != 4
                        or any(not isinstance(c, str) or not c for c in choices)
                        or any(isinstance(s, bool) or not isinstance(s, (int, float))
                               or not math.isfinite(s) for s in scores)):
                    raise ValueError('Invalid score vector or choice text')
                values = [s / len(c) if mode == 'acc_norm' else s
                          for s, c in zip(scores, choices)]
                positions.append(max(range(4), key=values.__getitem__))
            content = [(p + shift) % 4 for shift, p in enumerate(positions)]
            predictions[mode] = content
            correct = [int(p == r['target']) for p in content]
            features.update({f'{mode}_accuracy_r{i}': v for i, v in enumerate(correct)})
            features.update({f'{mode}_accuracy_original': correct[0],
                f'{mode}_accuracy_average': sum(correct) / 4,
                f'{mode}_consistency': int(len(set(content)) == 1),
                f'{mode}_pairwise_agreement': sum(content[i] == content[j]
                    for i, j in combinations(range(4), 2)) / 6})
            histograms[mode] = positions
        output[key] = dict(record=r, features=features, predictions=predictions,
                           positions=histograms)
    if not output:
        raise ValueError('Empty cell')
    return output


def _mean(prepared, weights):
    denominator = sum(weights.get(source, 0) for source, _ in prepared)
    return {metric: sum(weights.get(source, 0) * row['features'][metric]
                        for (source, _), row in prepared.items()) / denominator
            for metric in next(iter(prepared.values()))['features']}


def _interval(values):
    values = sorted(values)
    # Match the existing A2 empirical percentile convention.
    return [values[max(0, int(.025 * len(values)) - 1)],
            values[max(0, int(.975 * len(values)) - 1)]]


def _flips(left, right):
    result = {}
    for mode in MODES:
        counts = Counter()
        for key, a in left.items():
            b = right[key]
            target = a['record']['target']
            for shift, (x, y) in enumerate(zip(a['predictions'][mode], b['predictions'][mode])):
                if x != y:
                    kind = ('regression' if x == target else
                            'improvement' if y == target else 'wrong_to_wrong')
                    counts[kind] += 1
                    counts['changed'] += 1
                    counts[f'changed_r{shift}'] += 1
        result[mode] = dict(contexts=4 * len(left), unique_questions=len(left),
                            **{k: counts[k] for k in ('changed', 'regression',
                                'improvement', 'wrong_to_wrong',
                                *(f'changed_r{i}' for i in range(4)))})
    return result


def joint_statistics(cells, replicates=10000, seed=42, english='eng_Latn'):
    """Joint paired source bootstrap, retaining every language/arm/variant endpoint.

    Return tuple-keyed in-memory dictionaries, like rotation_statistics. Accuracy
    and intervals are fractions; histogram and flip counts are unweighted points.
    """
    if type(replicates) is not int or replicates < 1 or not cells:
        raise ValueError('Positive bootstrap count and cells required')
    languages = sorted({key[2] for key in cells})
    expected = {(a, v, lang) for a in ARMS for v in VARIANTS for lang in languages}
    if english not in languages or set(cells) != expected:
        raise ValueError('All arms/variants and English required')
    prepared = {key: _prepare(rows) for key, rows in cells.items()}
    reference = next(iter(prepared.values()))
    for rows in prepared.values():
        if rows.keys() != reference.keys():
            raise ValueError('Unmatched source/question cells')
        if any(rows[k]['record']['target'] != reference[k]['record']['target'] for k in rows):
            raise ValueError('Target mismatch')
    # Translations may have different strings, but each language's content must
    # remain exactly fixed across models and variants.
    for lang in languages:
        base = prepared[ARMS[0], VARIANTS[0], lang]
        for a in ARMS:
            for v in VARIANTS:
                if any(prepared[a, v, lang][k]['record']['original_choices'] !=
                       base[k]['record']['original_choices'] for k in base):
                    raise ValueError('Original choices changed across cells')
    sources = sorted({source for source, _ in reference})
    estimates = {key: _mean(rows, dict.fromkeys(sources, 1)) for key, rows in prepared.items()}
    contrasts = {}
    for v in VARIANTS:
        for lang in languages:
            contrasts['q4_minus_bf16', v, lang] = [
                (1, ('local-q4', v, lang)), (-1, ('bf16-gguf', v, lang))]
            contrasts['compression_delta_minus_english', v, lang] = [
                (1, ('local-q4', v, lang)), (-1, ('bf16-gguf', v, lang)),
                (-1, ('local-q4', v, english)), (1, ('bf16-gguf', v, english))]
    for a in ARMS:
        for lang in languages:
            for left, right in combinations(VARIANTS, 2):
                contrasts['variant_difference', a, lang, right, left] = [
                    (1, (a, right, lang)), (-1, (a, left, lang))]
    def differences(sample):
        return {key: {m: sum(sign * sample[cell][m] for sign, cell in terms)
                      for m in next(iter(sample.values()))} for key, terms in contrasts.items()}
    points = differences(estimates)
    draws = {key: {m: [] for m in metrics} for key, metrics in estimates.items()}
    contrast_draws = {key: {m: [] for m in metrics} for key, metrics in points.items()}
    rng = random.Random(seed)
    for _ in range(replicates):
        weights = Counter(rng.choices(sources, k=len(sources)))
        sample = {key: _mean(rows, weights) for key, rows in prepared.items()}
        for destination, values in ((draws, sample), (contrast_draws, differences(sample))):
            for key, metrics in values.items():
                for metric, value in metrics.items():
                    destination[key][metric].append(value)
    results = {}
    for key, rows in prepared.items():
        def histogram(values):
            counts = Counter(values)
            return {letter: counts[letter] for letter in 'ABCD'}
        hist = {mode: {f'r{i}': histogram('ABCD'[row['positions'][mode][i]]
                for row in rows.values()) for i in range(4)} for mode in MODES}
        for mode in MODES:
            hist[mode]['all_rotations'] = histogram('ABCD'[p] for row in rows.values()
                                                    for p in row['positions'][mode])
        gold = {f'r{i}': histogram('ABCD'[(row['record']['target'] - i) % 4]
                for row in rows.values()) for i in range(4)}
        gold['all_rotations'] = histogram('ABCD'[(row['record']['target'] - i) % 4]
                                          for row in rows.values() for i in range(4))
        duplicates = [dict(source=s, question=q, duplicate_groups=[indices
            for indices in ([i for i, value in enumerate(row['record']['original_choices']) if value == text]
                for text in dict.fromkeys(row['record']['original_choices'])) if len(indices) > 1])
            for (s, q), row in rows.items() if len(set(row['record']['original_choices'])) < 4]
        results[key] = dict(unique_questions=len(rows), rotation_contexts=4 * len(rows),
            metrics=estimates[key], cluster_95_intervals={m: _interval(v) for m, v in draws[key].items()},
            predicted_letter_histograms=hist, gold_letter_histograms=gold,
            exact_duplicate_choice_flags=duplicates,
            predictions=[dict(source=s, question=q,
                displayed_positions=row['positions'], original_content=row['predictions'])
                for (s, q), row in rows.items()])
    arm_flips = {(v, lang): _flips(prepared[ARMS[0], v, lang], prepared[ARMS[1], v, lang])
                 for v in VARIANTS for lang in languages}
    variant_flips = {(a, lang, left, right): _flips(prepared[a, left, lang], prepared[a, right, lang])
                     for a in ARMS for lang in languages for left, right in combinations(VARIANTS, 2)}
    return dict(cells=results, contrasts={key: {m: dict(estimate=value,
        cluster_95_interval=_interval(contrast_draws[key][m])) for m, value in metrics.items()}
        for key, metrics in points.items()}, arm_flips=arm_flips, variant_flips=variant_flips,
        bootstrap_replicates=replicates, bootstrap_seed=seed, source_clusters=len(sources),
        tie_policy='first displayed candidate', uncertainty_unit='joint source cluster',
        scope='Development diagnostic; no canonical scoring decision')
