import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('shards', Path(__file__).parents[1] / 'scripts/run_shards.py')
shards = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shards)


class ResumeTest(unittest.TestCase):
    def test_nonzero_range_is_resumed_and_range_changes_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock, runtime = root / 'lock', root / 'runtime'
            lock.write_text('lock'); runtime.write_text('runtime')
            argv = ['run_shards', '--lock', str(lock), '--runtime-manifest', str(runtime),
                    '--directory', str(root / 'results'), '--arm', 'test',
                    '--base-url', 'http://localhost', '--start', '50', '--count', '10']
            starts = []
            def evaluate(command, check):
                starts.append(int(command[command.index('--start') + 1]))
                language = command[command.index('--language') + 1]
                Path(command[command.index('--output') + 1]).write_text(json.dumps(
                    {'samples': {'belebele_' + language: [{'acc': 1}] * 5}}))
            with patch('sys.argv', argv), patch.object(shards.subprocess, 'run', side_effect=evaluate):
                shards.main(); shards.main()
                self.assertEqual(starts, [50, 55] * 3)
                argv[-1] = '15'
                with self.assertRaises(AssertionError):
                    shards.main()

    def test_reuses_complete_groups_and_rejects_changed_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock, runtime = root / 'lock', root / 'runtime'
            lock.write_text('locked sample'); runtime.write_text('runtime A')
            argv = ['run_shards', '--lock', str(lock), '--runtime-manifest', str(runtime),
                    '--directory', str(root / 'results'), '--arm', 'test', '--base-url', 'http://localhost']
            def evaluate(command, check):
                language = command[command.index('--language') + 1]
                out = Path(command[command.index('--output') + 1])
                out.write_text(json.dumps({'samples': {'belebele_' + language: [{'acc': 1}] * 5}}))
            with patch('sys.argv', argv), patch.object(shards.subprocess, 'run', side_effect=evaluate) as run:
                shards.main()
                self.assertEqual(run.call_count, 30)
                shards.main()
                self.assertEqual(run.call_count, 30)
                runtime.write_text('runtime B')
                with self.assertRaises(AssertionError):
                    shards.main()


if __name__ == '__main__':
    unittest.main()
