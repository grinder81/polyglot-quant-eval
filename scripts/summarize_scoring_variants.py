"""Validate complete frozen A3 evidence before computing development statistics."""
import argparse
import json
from pathlib import Path

from scripts.run_scoring_variants import LOCK, LANGUAGES, VARIANTS, sha, validate, validation_selection
from scripts.scoring_variant_statistics import ARMS, cells_from_rows, joint_statistics


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify_files(files):
    require(bool(files), 'Missing hashed files')
    for path, digest in files.items():
        require(sha(path) == digest, f'File hash mismatch: {path}')


def command_without_model(command):
    command = list(command)
    require(command.count('--model') == 1, 'Expected one runtime model argument')
    i = command.index('--model')
    model = command[i + 1]
    command[i + 1] = '<model>'
    return command, model


def load_evidence(lock_path, arms):
    """arms maps exact arm names to directory/runtime/validation/oracle/order_validation paths.

    Run where recorded absolute paths are accessible. Source/model/tokenizer hashes
    are checked against their actual files, never inferred from filenames.
    """
    require(set(arms) == set(ARMS), 'Exact BF16 and local-Q4 arms required')
    require(sha(lock_path) == LOCK, 'Request lock hash mismatch')
    lock = read(lock_path)
    rows = lock['rows']
    expected_membership = {(l, v, i, s) for l in LANGUAGES for v in VARIANTS
                           for i in range(100) for s in range(4)}
    membership = [(r['language'], r['variant'], r['index'], r['shift']) for r in rows]
    require(len(rows) == 3600 and set(membership) == expected_membership,
            'Exact 3 languages x 3 variants x 100 questions x 4 rotations required')
    selection = validation_selection(rows)
    require(len(selection) == 48, 'Frozen 48-context validation coverage required')
    compact = []
    provenance = {}
    matched = []
    for arm in ARMS:
        paths = {name: Path(path) for name, path in arms[arm].items()}
        directory = paths['directory']
        identity = read(directory / 'identity.json')
        runtime = read(paths['runtime'])
        gate = read(paths['validation'])
        oracle = read(paths['oracle'])
        order = read(paths['order_validation'])
        require(identity['arm'] == runtime['arm'] == arm, 'Arm identity mismatch')
        require(identity['lock_sha256'] == LOCK, 'Input identity lock mismatch')
        require(identity['runtime_sha256'] == sha(paths['runtime']), 'Runtime identity hash mismatch')
        require(identity['validation_sha256'] == sha(paths['validation']), 'Validation identity hash mismatch')
        require(identity['order_validation_sha256'] == sha(paths['order_validation']),
                'Order validation identity hash mismatch')
        verify_files(runtime['files'])
        verify_files(identity['files'])
        runner = Path(__file__).with_name('run_scoring_variants.py').resolve()
        require(any(Path(path).resolve() == runner and digest == sha(runner)
                    for path, digest in identity['files'].items()),
                'Runner source identity mismatch')
        require(identity['tokenizer'] == gate['tokenizer_files'] == lock['provenance']['tokenizer_files'],
                'Tokenizer identity mismatch')
        require(identity['versions'] == gate['versions'], 'Client version identity mismatch')
        verify_files({str(Path(identity['model_args']['tokenizer']) / name): digest
                      for name, digest in identity['tokenizer'].items()})
        verify_files(gate['source_files'])
        for artifact in (gate, order, oracle):
            require(artifact['lock_sha256'] == LOCK and artifact['runtime_sha256'] == sha(paths['runtime']),
                    'Validation lock/runtime mismatch')
            require(artifact['selection'] == selection and not artifact['failures'],
                    'Incomplete or failed cold validation')
            require(artifact['script_sha256'] == sha(paths['validator_script']),
                    'Cold validator script hash mismatch')
        require(runtime['provenance']['protocol_sha256'] == sha(paths['protocol']),
                'Cold protocol document hash mismatch')
        require(gate['order_check'] is False and order['order_check'] is True,
                'Both normal and reverse-order cold validation required')
        require(gate['oracle_sha256'] == order['oracle_sha256'] == sha(paths['oracle']),
                'Direct oracle hash mismatch')
        expected_pairs = [(i, c) for i in selection for c in range(4)]
        reverse_pairs = list(reversed([(i, c) for i in selection
            if rows[i]['index'] == 0 and rows[i]['shift'] == 0 for c in range(4)]))
        require(len(reverse_pairs) == 36, 'Reverse-order coverage mismatch')
        for artifact, pairs in ((gate, expected_pairs), (oracle, expected_pairs), (order, reverse_pairs)):
            require([(r['row'], r['candidate']) for r in artifact['records']] == pairs,
                    'Incomplete or duplicated validation candidates')
            require(all(not r.get('errors') for r in artifact['records']), 'Validation record errors')
        require([p['row'] for p in gate['predictions']] == selection,
                'Incomplete validation predictions')
        command, model = command_without_model(runtime['server_command'])
        require(model in runtime['files'], 'Runtime model artifact not hashed')
        require(identity['endpoint_models'] == [model], 'Served endpoint model identity mismatch')
        settings = dict(oracle['server_model_settings'])
        require(settings.pop('model') == model, 'Direct oracle model mismatch')
        client = dict(identity['model_args'])
        require(client == dict(model='a3-locked', base_url=client['base_url'],
            tokenizer=client['tokenizer'], tokenizer_backend='huggingface',
            tokenized_requests=False, add_bos_token=False, max_length=8192, batch_size=1),
            'Unexpected scoring client configuration')
        matched.append(dict(command=command, files={p: h for p, h in runtime['files'].items() if p != model},
            packages=runtime['packages'], patch=runtime['provenance']['patch_sha256'],
            additional_patch=runtime['provenance']['additional_patch_sha256'],
            protocol=runtime['provenance']['protocol_sha256'], settings=settings,
            client=client, scorer=identity['scorer'], versions=identity['versions'],
            files_client=identity['files'], tokenizer=identity['tokenizer']))
        expected_files = {}
        for language in LANGUAGES:
            for variant in VARIANTS:
                for shift in range(4):
                    for start in range(0, 100, 5):
                        name = f'{language}-{variant}-r{shift}-{start:03}.json'
                        expected_files[name] = [r for r in rows if
                            (r['language'], r['variant'], r['shift']) == (language, variant, shift)
                            and start <= r['index'] < start + 5]
        require({p.name for p in directory.glob('*.json')} == set(expected_files) | {'identity.json'},
                'Incomplete, duplicate, or unexpected shard files')
        require(not list(directory.glob('*.tmp')), 'Incomplete temporary shards present')
        hashes = {}
        for name, expected in expected_files.items():
            try:
                compact.extend(validate(read(directory / name), expected, arm))
            except (AssertionError, KeyError, TypeError, ValueError) as error:
                raise ValueError(f'Invalid shard {arm}/{name}: {error}') from error
            hashes[name] = sha(directory / name)
        provenance[arm] = dict(identity_sha256=sha(directory / 'identity.json'),
            artifacts={name: sha(path) for name, path in paths.items() if name != 'directory'},
            runtime_provenance=runtime['provenance'],
            shard_sha256=hashes, a2_bridge_failures=gate['a2_bridge_failures'],
            validation_predictions=gate['predictions'])
    require(matched[0] == matched[1], 'Runtime/client settings differ beyond model artifact')
    cells = cells_from_rows(compact)
    require(set(cells) == {(a, v, l) for a in ARMS for v in VARIANTS for l in LANGUAGES}
            and all(len(records) == 100 for records in cells.values()), 'Incomplete statistical cells')
    return cells, dict(lock_sha256=LOCK, arms=provenance)


def json_ready(value):
    """Tuple keyed maps become explicit key/value records, without lossy delimiters."""
    if isinstance(value, dict):
        if any(isinstance(key, tuple) for key in value):
            return [dict(key=list(key), value=json_ready(item)) for key, item in value.items()]
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--validator-script', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    for arm in ('bf16', 'q4'):
        for name in ('directory', 'runtime', 'validation', 'oracle', 'order-validation'):
            parser.add_argument(f'--{arm}-{name}', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Output must be new')
    arms = {arm: {name: getattr(args, prefix + '_' + name) for name in
            ('directory', 'runtime', 'validation', 'oracle', 'order_validation')}
            for prefix, arm in zip(('bf16', 'q4'), ARMS)}
    for paths in arms.values():
        paths.update(validator_script=args.validator_script, protocol=args.protocol)
    cells, evidence = load_evidence(args.lock, arms)
    report = dict(evidence=evidence, statistics=json_ready(joint_statistics(cells)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)


if __name__ == '__main__':
    main()
