from pathlib import Path
import unittest

from scripts.audit_harness_ids import audit, label_map


class HarnessLabelsTest(unittest.TestCase):
    def test_unsorted_request_relabels_only_metadata(self):
        # Actual documents iterate as 1,3,4, but labels are requested[0:3].
        self.assertEqual(label_map([4, 1, 3]), {1: 4, 3: 1, 4: 3})
        self.assertEqual(label_map([1, 3, 4]), {1: 1, 3: 3, 4: 4})
        with self.assertRaises(ValueError):
            label_map([1, 1])

    def test_entire_saved_local_q4_run_is_explained(self):
        result = audit(Path(__file__).parents[1] / 'results/stage1/local-q4-three-hundred')
        self.assertEqual(result['total'], 900)
        self.assertEqual(result['explained_by_order_mapping'], 900)
        self.assertEqual(result['mislabeled'], 707)


if __name__ == '__main__':
    unittest.main()
