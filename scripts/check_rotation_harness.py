"""Exercise the diagnostic runner with upstream DummyLM, never a real endpoint."""
import argparse
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from lm_eval.models.dummy import DummyLM
import run_rotation_shard
from run_rotation_shards import validate_shard


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / 'dummy-only.json'
        argv = ['run_rotation_shard', '--lock', str(args.lock), '--language', 'ben_Beng',
                '--shift', '1', '--start', '0', '--arm', 'bf16-gguf',
                '--base-url', 'http://unused.invalid', '--output', str(output)]
        with patch('sys.argv', argv), patch('lm_eval.models.gguf.GGUFLM', side_effect=lambda **kw: DummyLM()):
            run_rotation_shard.main()
        expected = [r for r in json.loads(args.lock.read_text(encoding='utf-8'))['rows']
                    if r['language'] == 'ben_Beng' and r['shift'] == 1 and r['index'] < 5]
        validate_shard(json.loads(output.read_text(encoding='utf-8')), expected, 'ben_Beng')
    print('Five rotated Bangla records passed upstream DummyLM plumbing; no real scores retained.')


if __name__ == '__main__':
    main()
