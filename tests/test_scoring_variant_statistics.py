import copy
import pytest

from scripts.scoring_variant_statistics import (
    ARMS, VARIANTS, _prepare, cells_from_rows, joint_statistics,
)


def cells():
    return {(arm, variant, lang): [dict(source=f's{i // 2}', question=str(i),
        target=0, original_choices=['অ', 'long text', 'x', 'z'],
        rotations=[[0 if (p + shift) % 4 == 0 else -10 for p in range(4)]
                   for shift in range(4)], choices=[list('ABCD') for _ in range(4)])
        for i in range(4)] for arm in ARMS for variant in VARIANTS
        for lang in ('eng_Latn', 'ben_Beng')}


def test_rotation_remapping_and_joint_pairing():
    report = joint_statistics(cells(), replicates=12)
    assert report['source_clusters'] == 2
    assert report['bootstrap_seed'] == 42
    for cell in report['cells'].values():
        assert cell['unique_questions'] == 4
        assert cell['rotation_contexts'] == 16
        assert cell['metrics']['raw_accuracy_average'] == 1
        assert cell['metrics']['raw_consistency'] == 1
        assert cell['metrics']['raw_pairwise_agreement'] == 1
        assert cell['gold_letter_histograms']['r1'] == {'A': 0, 'B': 0, 'C': 0, 'D': 4}
    for contrast in report['contrasts'].values():
        assert all(v['estimate'] == 0 and v['cluster_95_interval'] == [0, 0]
                   for v in contrast.values())


def test_default_ten_thousand_replicates_single_cluster_is_valid():
    data = {key: rows[:1] for key, rows in cells().items()}
    report = joint_statistics(data)
    assert report['bootstrap_replicates'] == 10000
    assert report['source_clusters'] == 1
    assert report['cells'][ARMS[0], VARIANTS[0], 'eng_Latn'][
        'cluster_95_intervals']['raw_accuracy_average'] == [1, 1]


def test_unicode_character_normalization_is_separate_and_duplicates_flagged():
    data = cells()
    key = ('local-q4', 'plain-option-text', 'ben_Beng')
    for row in data[key]:
        row['choices'] = [['অ', 'long text', 'x', 'z'] for _ in range(4)]
        row['rotations'] = [[-1, -2, -8, -8] for _ in range(4)]
    report = joint_statistics(data, replicates=5)
    result = report['cells'][key]
    assert result['predicted_letter_histograms']['raw']['r0']['A'] == 4
    assert result['predicted_letter_histograms']['acc_norm']['r0']['B'] == 4
    assert result['metrics']['raw_accuracy_original'] == 1
    assert result['metrics']['acc_norm_accuracy_original'] == 0
    assert report['arm_flips']['plain-option-text', 'ben_Beng']['raw']['changed'] == 12
    # Maintain identical original content across every cell of this language.
    for (_, _, lang), rows in data.items():
        if lang == 'ben_Beng':
            for row in rows:
                row['original_choices'] = ['same', 'same', 'x', 'z']
    duplicate = joint_statistics(data, replicates=2)['cells'][key]['exact_duplicate_choice_flags']
    assert duplicate[0]['duplicate_groups'] == [[0, 1]]


def test_bootstrap_source_weighting_and_interaction():
    data = cells()
    for row in data['local-q4', 'plain-letter', 'ben_Beng'][:2]:
        row['rotations'] = [[0 if (p + shift) % 4 == 1 else -10 for p in range(4)]
                           for shift in range(4)]
    report = joint_statistics(data, replicates=60)
    delta = report['contrasts']['q4_minus_bf16', 'plain-letter', 'ben_Beng']['raw_accuracy_average']
    interaction = report['contrasts']['compression_delta_minus_english', 'plain-letter', 'ben_Beng']['raw_accuracy_average']
    assert delta == interaction
    assert delta['estimate'] == -.5
    assert delta['cluster_95_interval'] == [-1, 0]
    assert report == joint_statistics(data, replicates=60)


def test_reject_bad_inputs_and_tie_policy():
    data = cells()
    row = data[ARMS[0], VARIANTS[0], 'eng_Latn'][0]
    row['rotations'] = [[0] * 4 for _ in range(4)]
    prepared = _prepare([row])
    assert prepared['s0', '0']['positions']['raw'] == [0, 0, 0, 0]
    with pytest.raises(ValueError, match='Duplicate'):
        _prepare([row, row])
    row['rotations'][0][0] = float('nan')
    with pytest.raises(ValueError, match='Invalid score'):
        _prepare([row])
    data = cells()
    data[ARMS[0], VARIANTS[0], 'eng_Latn'].pop()
    with pytest.raises(ValueError, match='Unmatched'):
        joint_statistics(data, replicates=1)


def test_compact_schema_requires_complete_exact_rows():
    rows = [dict(arm=ARMS[0], variant='plain-option-text', language='eng_Latn',
        source='s', question='q', shift=shift, target=(-shift) % 4,
        original_target=0, original_choices=['a', 'bb', 'ccc', 'dddd'],
        choices=[['a', 'bb', 'ccc', 'dddd'][(i + shift) % 4] for i in range(4)],
        choice_character_lengths=[(i + shift) % 4 + 1 for i in range(4)],
        scores=[-1, -2, -3, -4]) for shift in range(4)]
    assert len(next(iter(cells_from_rows(rows).values()))) == 1
    with pytest.raises(ValueError, match='Incomplete'):
        cells_from_rows(rows[:3])
    with pytest.raises(ValueError, match='Duplicate'):
        cells_from_rows(rows + rows[:1])
    altered = copy.deepcopy(rows)
    altered[0]['choice_character_lengths'][0] = 2
    with pytest.raises(ValueError, match='Unicode'):
        cells_from_rows(altered)
