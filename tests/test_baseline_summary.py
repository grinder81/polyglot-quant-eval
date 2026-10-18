import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('baseline', ROOT / 'scripts/summarize_baseline.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BaselineSummaryTest(unittest.TestCase):
    def test_saved_evidence_and_paired_accounting(self):
        summary, _ = module.summarize(ROOT / 'results/stage1/fifty-per-language')
        self.assertEqual(sum(summary['correct']['q4'].values()), 86)
        self.assertEqual(sum(summary['correct']['bf16-vllm'].values()), 93)
        for pair in summary['pairs'].values():
            for row in pair.values():
                self.assertEqual(row['delta_pp'], 2 * (row['wrong_to_right'] - row['right_to_wrong']))
                self.assertGreaterEqual(row['changed_answers'], row['right_to_wrong'] + row['wrong_to_right'])


if __name__ == '__main__':
    unittest.main()
