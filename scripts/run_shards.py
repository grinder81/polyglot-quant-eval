"""Checkpoint upstream evaluations in five-question groups; no scoring adapter."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', required=True)
    p.add_argument('--runtime-manifest', required=True,
                   help='Exact model/runtime identity; changes invalidate saved shards')
    p.add_argument('--directory', type=Path, required=True)
    p.add_argument('--arm', required=True)
    p.add_argument('--base-url', required=True)
    p.add_argument('--backend', default='gguf', choices=['gguf', 'local-completions'])
    p.add_argument('--tokenizer')
    args = p.parse_args()
    runner = Path(__file__).with_name('run_pilot.py')
    identity = dict(lock=sha(args.lock), runtime=sha(args.runtime_manifest),
                    runner=sha(runner), arm=args.arm, backend=args.backend,
                    tokenizer=args.tokenizer, count_per_language=50, shard_size=5)
    args.directory.mkdir(parents=True, exist_ok=True)
    marker = args.directory / 'identity.json'
    if marker.exists():
        assert json.loads(marker.read_text()) == identity, 'Checkpoint identity differs'
    else:
        assert not list(args.directory.glob('*.json')), 'Unidentified existing results'
        marker.write_text(json.dumps(identity, indent=2))
    for language in ['eng_Latn', 'ben_Beng', 'hin_Deva']:
        for start in range(0, 50, 5):
            output = args.directory / f'{language}-{start:03d}.json'
            if output.exists():
                saved = json.loads(output.read_text(encoding='utf-8'))
                rows = saved['samples']['belebele_' + language]
                assert len(rows) == 5 and all('acc' in row for row in rows)
                print(f'Reusing {output.name}', flush=True)
                continue
            command = [sys.executable, str(runner), '--lock', args.lock,
                       '--base-url', args.base_url, '--arm', args.arm,
                       '--backend', args.backend, '--language', language,
                       '--start', str(start), '--count', '5', '--output', str(output)]
            if args.tokenizer:
                command += ['--tokenizer', args.tokenizer]
            subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
