import unittest

from scripts.option_rotation import (cross_fitted_offsets, estimate_offsets,
                                     original_choice, predict, rotate_document,
                                     source_fold)


class RotationTest(unittest.TestCase):
    def test_all_gold_positions_preserve_answer_content(self):
        for gold in range(4):
            doc = dict(correct_answer_num=str(gold + 1), question='q', flores_passage='p',
                       **{f'mc_answer{i+1}': f'content-{i}' for i in range(4)})
            for shift in range(4):
                rotated = rotate_document(doc, shift)
                position = int(rotated['correct_answer_num']) - 1
                self.assertEqual(original_choice(position, shift), gold)
                self.assertEqual(rotated[f'mc_answer{position+1}'], f'content-{gold}')
                self.assertEqual(rotated['question'], 'q')
                self.assertEqual(rotated['flores_passage'], 'p')
            self.assertEqual(rotate_document(doc, 0), doc)

    def test_balanced_rotation_recovers_additive_offset(self):
        bias = [3, -1, -1, -1]
        content = [-4, -2, -3, -5]
        rotations = [[content[(j+s) % 4] + bias[j] + s * 10 for j in range(4)] for s in range(4)]
        offsets = estimate_offsets([rotations])
        self.assertEqual(offsets, bias)
        for shift, scores in enumerate(rotations):
            self.assertEqual(original_choice(predict(scores, offsets), shift), 1)
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            estimate_offsets([rotations[:3]])

    def test_same_source_never_fits_its_own_correction(self):
        sources = [f'source-{i}' for i in range(50)]
        first = sources[0]
        second = next(s for s in sources if source_fold(s) != source_fold(first))
        records = [dict(source=first, question=str(i), rotations=[[100, 0, 0, 0]] * 4) for i in range(2)]
        records.append(dict(source=second, question='0', rotations=[[0, 0, 0, 0]] * 4))
        offsets = cross_fitted_offsets(records)
        self.assertEqual(offsets[first, '0'], [0, 0, 0, 0])
        self.assertEqual(offsets[first, '0'], offsets[first, '1'])
        self.assertEqual(offsets[second, '0'], [75, -25, -25, -25])


if __name__ == '__main__':
    unittest.main()
