import copy
import unittest

from scripts.compare_expanded import LANGS, compare_rows


class PairedComparisonTest(unittest.TestCase):
    def rows(self):
        return [dict(language=lang, source=f'source-{i // 2}', question=str(i),
                     target=0, prediction=0, correct=1) for lang in LANGS for i in range(4)]

    def test_identical_language_damage_has_zero_interaction_uncertainty(self):
        reference = self.rows()
        candidate = copy.deepcopy(reference)
        for row in candidate:
            if row['question'] == '0':
                row.update(prediction=1, correct=0)
        result = compare_rows(reference, candidate, replicates=1000)
        for row in result['languages'].values():
            self.assertEqual(row['accuracy_delta_q4_minus_bf16'], -.25)
            self.assertEqual(row['right_to_wrong'], 1)
            self.assertEqual(row['changed_choices'], 1)
            self.assertEqual(row['paired_cluster_95_delta_minus_english_interval'], [0, 0])

    def test_semantic_outcome_counts_and_alignment(self):
        reference = self.rows()
        candidate = copy.deepcopy(reference)
        reference[0].update(prediction=1, correct=0)
        reference[1].update(prediction=1, correct=0)
        candidate[1].update(prediction=2, correct=0)
        candidate[2].update(prediction=1, correct=0)
        row = compare_rows(reference, candidate, replicates=100)['languages']['eng_Latn']
        self.assertEqual((row['right_to_wrong'], row['wrong_to_right'], row['wrong_to_wrong']), (1, 1, 1))
        self.assertEqual(row['accuracy_delta_q4_minus_bf16'], 0)
        with self.assertRaisesRegex(ValueError, 'Unmatched'):
            compare_rows(reference, candidate[:-1])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            compare_rows(reference, candidate + [candidate[0]])
        candidate[0]['target'] = 1
        with self.assertRaisesRegex(ValueError, 'Target'):
            compare_rows(reference, candidate)


if __name__ == '__main__':
    unittest.main()
