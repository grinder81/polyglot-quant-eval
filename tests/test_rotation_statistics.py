import pytest

from scripts.option_rotation import source_fold
from scripts.rotation_statistics import joint_statistics, measure


def records():
    # Each source has an exact additive content/position model, with A bias 10.
    # Content zero is correct; rotating it gives raw accuracy 1/4 but correction 1.
    return [dict(source=f'source-{i}', question='1', target=0,
                 rotations=[[int((position + shift) % 4 == 0) + (10 if position == 0 else 0)
                             for position in range(4)] for shift in range(4)]) for i in range(20)]


def test_known_bias_and_content_consistency():
    result, predictions = measure(records())
    m = result['metrics']
    assert m['raw_accuracy_average'] == .25
    assert m['raw_consistency'] == 0
    assert m['raw_pairwise_agreement'] == 0
    assert m['cross_fitted_accuracy_average'] == 1
    assert m['cross_fitted_consistency'] == 1
    assert m['cross_fitted_pairwise_agreement'] == 1
    assert all(v == [0, 0, 0, 0] for v in predictions['cross_fitted'].values())


def test_fitting_excludes_held_source_and_weights_fit():
    rows = records()
    held = source_fold(rows[0]['source'])
    weights = {r['source']: i + 1 for i, r in enumerate(rows)}
    # Different source-specific A offsets require multiplicity-weighted fitting.
    for i, r in enumerate(rows):
        for scores in r['rotations']:
            scores[0] += i
    result, _ = measure(rows, weights)
    fit = [(i, i + 1) for i, r in enumerate(rows) if source_fold(r['source']) != held]
    expected_bias = sum((10 + i) * weight for i, weight in fit) / sum(weight for _, weight in fit)
    assert result['offsets'][held] == pytest.approx([.75 * expected_bias] + [-.25 * expected_bias] * 3)
    before = result['offsets'][held]
    for r in rows:
        if source_fold(r['source']) == held:
            for scores in r['rotations']:
                scores[1] += 1000
    assert measure(rows, weights)[0]['offsets'][held] == before


def test_joint_bootstrap_preserves_model_pairing():
    cells = {(arm, lang): records() for arm in ('bf16-gguf', 'local-q4') for lang in ('en', 'bn', 'hi')}
    result = joint_statistics(cells, replicates=40, english='en')
    assert result['invalid_empty_training_fold_replicates'] == 0
    for metrics in result['q4_minus_bf16'].values():
        assert all(m['estimate'] == 0 and m['cluster_95_interval'] == [0, 0] for m in metrics.values())


def test_reject_incomplete_and_flag_empty_fold_bootstraps():
    rows = records()
    with pytest.raises(ValueError, match='duplicate'):
        measure(rows + rows[:1])
    rows[0]['rotations'].pop()
    with pytest.raises(ValueError, match='rotation'):
        measure(rows)
    rows = records()
    a = rows[0]
    b = next(r for r in rows if source_fold(r['source']) != source_fold(a['source']))
    cells = {(arm, 'eng_Latn'): [a, b] for arm in ('bf16-gguf', 'local-q4')}
    result = joint_statistics(cells, replicates=40)
    assert 0 < result['invalid_empty_training_fold_replicates'] < 40
