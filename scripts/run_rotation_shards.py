"""Resume validated diagnostic shards without changing upstream scoring."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def validate_shard(data, expected, language):
    rows = data['samples']['belebele_' + language]
    wanted = {(r['source'], r['question']): r for r in expected}
    assert len(rows) == len(wanted) == 5
    seen = set()
    correct = 0
    for row in rows:
        key = row['doc']['link'], row['doc']['question_number']
        assert key in wanted and key not in seen
        seen.add(key)
        item = wanted[key]
        assert row['target'] == item['target']
        args = row['arguments']
        assert len(args) == 4 and [a[1] for a in args] == item['candidates']
        assert all(hashlib.sha256(a[0].encode()).hexdigest() == item['prompt_sha256'] for a in args)
        scores = [v[0] for v in row['filtered_resps']]
        assert len(scores) == 4 and all(math.isfinite(v) for v in scores)
        accuracy = int(max(range(4), key=scores.__getitem__) == item['target'])
        assert accuracy == row['acc']
        correct += accuracy
    assert math.isclose(data['results']['belebele_' + language]['acc,none'], correct / 5)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, required=True)
    p.add_argument('--preflight', type=Path, required=True)
    p.add_argument('--runtime-manifest', type=Path, required=True)
    p.add_argument('--arm', choices=['bf16-gguf', 'local-q4'], required=True)
    p.add_argument('--base-url', required=True)
    p.add_argument('--directory', type=Path, required=True)
    args = p.parse_args()
    lock = json.loads(args.lock.read_text(encoding='utf-8'))
    preflight = json.loads(args.preflight.read_text())
    runtime = json.loads(args.runtime_manifest.read_text())
    assert preflight['lock_sha256'] == sha(args.lock)
    assert not preflight['failures'] and preflight['passed_contexts'] == 1200
    assert preflight['passed_candidates'] == 4800
    assert preflight['runtime_files'] == runtime['files']
    assert runtime['arm'] == args.arm
    assert all(sha(path) == value for path, value in runtime['files'].items())
    runner = Path(__file__).with_name('run_rotation_shard.py')
    identity = dict(arm=args.arm, lock=sha(args.lock), preflight=sha(args.preflight),
                    runtime=sha(args.runtime_manifest), code={p.name: sha(p) for p in
                    [Path(__file__), runner, runner.with_name('option_rotation.py'), runner.with_name('prepare_pilot.py')]})
    args.directory.mkdir(parents=True, exist_ok=True)
    marker = args.directory / 'identity.json'
    if marker.exists():
        assert json.loads(marker.read_text()) == identity, 'Changed diagnostic identity'
    else:
        assert not list(args.directory.glob('*.json')), 'Unidentified results present'
        marker.write_text(json.dumps(identity, indent=2))
    for language in ('eng_Latn', 'ben_Beng', 'hin_Deva'):
        for shift in range(4):
            for start in range(0, 100, 5):
                expected = [r for r in lock['rows'] if r['language'] == language and r['shift'] == shift
                            and start <= r['index'] < start + 5]
                output = args.directory / f'{language}-r{shift}-{start:03}.json'
                if not output.exists():
                    subprocess.run([sys.executable, str(runner), '--lock', str(args.lock),
                        '--language', language, '--shift', str(shift), '--start', str(start),
                        '--arm', args.arm, '--base-url', args.base_url, '--output', str(output)], check=True)
                validate_shard(json.loads(output.read_text(encoding='utf-8')), expected, language)
                print(f'Validated {output.name}', flush=True)


if __name__ == '__main__':
    main()
