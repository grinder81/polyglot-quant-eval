import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from compare_local_q4 import compare


class LocalQ4ComparisonTest(unittest.TestCase):
    def test_saved_fourth_arm(self):
        result = compare(ROOT / "results/stage1/local-q4-fifty",
                         ROOT / "results/stage1/fifty-per-language")
        self.assertEqual(sum(result["correct"].values()), 86)
        for stats in result["comparisons"]["q4"].values():
            self.assertEqual(stats["changed_choices"], 0)
            self.assertEqual(stats["max_absolute_likelihood_difference"], 0)
        for comparison in result["comparisons"].values():
            for stats in comparison.values():
                self.assertEqual(stats["delta_pp"], 2 * (stats["wrong_to_right"] - stats["right_to_wrong"]))
