"""T3 checkpoints reject changed identities and retain incomplete failure evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import run_t3_baselines as runner


class T3CheckpointTests(unittest.TestCase):
    def test_saved_identity_change_stops_before_any_endpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'identity.json').write_text(json.dumps({'schema':'old'}))
            args=['run_t3','--config','config.json','--directory',str(root),'--collect']
            with patch('sys.argv',args),patch.object(runner,'identity',return_value=({'schema':'new'},[])):
                with self.assertRaisesRegex(ValueError,'checkpoint identity changed'):
                    runner.main()

    def test_partial_or_unidentified_shard_cannot_be_adopted(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'eng_Latn-000.json').write_text('{}')
            with patch('sys.argv',['run_t3','--config','config.json','--directory',str(root)]),patch.object(runner,'identity',return_value=({'arm':'diag-q3km'},[])):
                with self.assertRaisesRegex(ValueError,'Unidentified shards'):
                    runner.main()


if __name__=='__main__':
    unittest.main()
