import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('expanded', ROOT / 'scripts/summarize_expanded_local.py')
expanded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(expanded)


class ExpandedEvidenceTest(unittest.TestCase):
    def test_all_frozen_records_and_saved_summary(self):
        root = ROOT / 'results/stage1/local-q4-three-hundred'
        summary, rows = expanded.summarize(root)
        self.assertEqual(summary, json.loads((root / 'summary.json').read_text()))
        self.assertEqual(len(rows), 900)
        self.assertEqual(len({(r['language'], r['source'], r['question']) for r in rows}), 900)

    def test_corrupted_runtime_is_rejected(self):
        root = ROOT / 'results/stage1/local-q4-three-hundred'
        original = Path.read_bytes
        def read(path):
            return b'changed' if path.name == 'local-q4-runtime.json' else original(path)
        with patch.object(Path, 'read_bytes', read), self.assertRaises(AssertionError):
            expanded.summarize(root)


if __name__ == '__main__':
    unittest.main()
