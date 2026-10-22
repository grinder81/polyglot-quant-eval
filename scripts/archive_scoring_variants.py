"""Losslessly package complete, already validated A3 evidence; never run inference.

The final frozen report is the trust anchor. Every original shard and identity
must match its report hash before an output directory can be created. Model and
environment files are references only, never archive inputs.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

from scripts.run_scoring_variants import LANGUAGES, LOCK, VARIANTS
from scripts.scoring_variant_statistics import ARMS


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def shard_names():
    return {f'{language}-{variant}-r{shift}-{start:03}.json'
            for language in LANGUAGES for variant in VARIANTS
            for shift in range(4) for start in range(0, 100, 5)}


def report_inventory(report):
    """Reject partial reports and return the exact whitelisted original inventory."""
    require(report['evidence']['lock_sha256'] == LOCK, 'Unexpected lock identity')
    require(set(report['evidence']['arms']) == set(ARMS), 'Both evidence arms required')
    statistics = report['statistics']
    require(statistics['bootstrap_replicates'] == 10000 and statistics['bootstrap_seed'] == 42,
            'Frozen bootstrap identity required')
    expected_cells = {(arm, variant, language) for arm in ARMS
                      for variant in VARIANTS for language in LANGUAGES}
    cells = statistics['cells']
    require(len(cells) == 18 and {tuple(c['key']) for c in cells} == expected_cells,
            'All 18 final statistical cells required')
    for cell in cells:
        value = cell['value']
        require(value['unique_questions'] == 100 and value['rotation_contexts'] == 400,
                'Complete 100-question statistical cell required')
    inventory = {}
    for arm in ARMS:
        evidence = report['evidence']['arms'][arm]
        require(set(evidence['shard_sha256']) == shard_names(), 'All 720 shard hashes required per arm')
        inventory[f'raw/{arm}/identity.json'] = evidence['identity_sha256']
        inventory.update({f'raw/{arm}/{name}': sha for name, sha in evidence['shard_sha256'].items()})
    require(all(re.fullmatch('[0-9a-f]{64}', sha) for sha in inventory.values()),
            'Invalid evidence hash')
    return inventory


def archive(report_path, arm_directories, destination, *, lock_location,
            evaluation_commit, runtime_commit):
    """Create a new archive from a complete frozen report and unchanged originals.

    Caller must first generate the report with summarize_scoring_variants in the
    pinned environment. This function checks every raw byte identity against it;
    it does not re-score or reinterpret samples. Original files remain untouched.
    """
    require(set(arm_directories) == set(ARMS), 'Both source arm directories required')
    for commit in (evaluation_commit, runtime_commit):
        require(re.fullmatch('[0-9a-f]{40}', commit) is not None, 'Full reproduction commit SHA required')
    require(isinstance(lock_location, str) and bool(lock_location), 'Lock location reference required')
    destination = Path(destination)
    require(not destination.exists(), 'Archive destination must be new')
    report_bytes = Path(report_path).read_bytes()
    report = json.loads(report_bytes)
    inventory = report_inventory(report)
    sources = {'validated-report.json': Path(report_path)}
    for arm in ARMS:
        directory = Path(arm_directories[arm])
        require({p.name for p in directory.glob('*.json')} == shard_names() | {'identity.json'}
                and not list(directory.glob('*.tmp')), 'Incomplete or unexpected source shard inventory')
        sources.update({f'raw/{arm}/{name}': directory / name
                        for name in shard_names() | {'identity.json'}})
    inventory['validated-report.json'] = digest(report_bytes)
    # Validate the entire run before creating any output, including missing files.
    for name, source in sources.items():
        require(digest(source.read_bytes()) == inventory[name], f'Original hash mismatch: {name}')
    destination.mkdir(parents=True, exist_ok=False)
    index = dict(format='a3-lossless-tar-gzip-v1', lock=dict(sha256=LOCK, location=lock_location,
        included=False), reproduction=dict(evaluation_commit=evaluation_commit,
        runtime_commit=runtime_commit), files={}, archives={})
    groups = [('validated-report.json.gz', ['validated-report.json'])] + [
        (f'{arm}.tar.gz', sorted(n for n in sources if n.startswith(f'raw/{arm}/')))
        for arm in ARMS]
    for relative, names in groups:
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb', filename='', mtime=0, compresslevel=9) as stream:
            if relative.endswith('.tar.gz'):
                with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as tar:
                    for name in names:
                        original = sources[name].read_bytes()
                        require(digest(original) == inventory[name], f'Original changed during packaging: {name}')
                        member = name.removeprefix('raw/')
                        info = tarfile.TarInfo(member)
                        info.size, info.mode, info.mtime = len(original), 0o644, 0
                        tar.addfile(info, io.BytesIO(original))
                        index['files'][name] = dict(bytes=len(original), sha256=inventory[name],
                            storage=dict(archive=relative, member=member))
            else:
                name = names[0]
                original = sources[name].read_bytes()
                require(digest(original) == inventory[name], f'Original changed during packaging: {name}')
                stream.write(original)
                index['files'][name] = dict(bytes=len(original), sha256=inventory[name],
                    storage=dict(archive=relative, member=None))
        packed = buffer.getvalue()
        output = destination / relative
        with output.open('xb') as stream:
            stream.write(packed)
        index['archives'][relative] = dict(bytes=len(packed), sha256=digest(packed))
    with (destination / 'archive-manifest.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(index, stream, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    verify_archive(destination)
    return index


def verify_archive(directory):
    """Verify every stored and decompressed byte plus the embedded report inventory."""
    root = Path(directory).resolve()
    index = json.loads((root / 'archive-manifest.json').read_text(encoding='utf-8'))
    require(index['format'] == 'a3-lossless-tar-gzip-v1', 'Unknown archive format')
    originals = {}
    expected_storage = {'validated-report.json.gz', *(f'{arm}.tar.gz' for arm in ARMS)}
    require(set(index['archives']) == expected_storage, 'Unexpected archive inventory')
    for relative in sorted(expected_storage):
        storage = index['archives'][relative]
        path = root / relative
        require(path.resolve().is_relative_to(root), 'Unsafe archive path')
        packed = path.read_bytes()
        require(len(packed) == storage['bytes'] and digest(packed) == storage['sha256'],
                f'Compressed hash/length mismatch: {relative}')
        try:
            if relative.endswith('.tar.gz'):
                arm = relative.removesuffix('.tar.gz')
                expected_members = {f'{arm}/{name}' for name in shard_names() | {'identity.json'}}
                seen = set()
                with tarfile.open(fileobj=io.BytesIO(packed), mode='r|gz') as tar:
                    for member in tar:
                        require(member.isfile() and member.name in expected_members and member.name not in seen,
                                'Unexpected, unsafe, nonregular or duplicate tar member')
                        seen.add(member.name)
                        stream = tar.extractfile(member)
                        originals['raw/' + member.name] = stream.read()
                require(seen == expected_members, 'Incomplete tar member inventory')
            else:
                originals['validated-report.json'] = gzip.decompress(packed)
        except (OSError, EOFError, tarfile.TarError) as error:
            raise ValueError(f'Invalid compressed stream: {relative}') from error
    require({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
            == expected_storage | {'archive-manifest.json'}, 'Unexpected or missing archive files')
    require('validated-report.json' in originals, 'Archived final report required')
    report = json.loads(originals['validated-report.json'])
    inventory = report_inventory(report)
    inventory['validated-report.json'] = digest(originals['validated-report.json'])
    require(set(index['files']) == set(inventory), 'Archive differs from complete report inventory')
    require(index['lock']['sha256'] == LOCK and index['lock']['included'] is False
            and bool(index['lock']['location']), 'Lock reproduction reference missing')
    require(all(re.fullmatch('[0-9a-f]{40}', index['reproduction'][name])
                for name in ('evaluation_commit', 'runtime_commit')), 'Reproduction commits missing')
    for name, sha in inventory.items():
        record = index['files'][name]
        expected_archive = ('validated-report.json.gz' if name == 'validated-report.json'
                            else name.split('/')[1] + '.tar.gz')
        expected_member = None if name == 'validated-report.json' else name.removeprefix('raw/')
        require(record['storage'] == dict(archive=expected_archive, member=expected_member),
                'Unexpected member storage reference')
        require(record['sha256'] == sha and digest(originals[name]) == sha
                and record['bytes'] == len(originals[name]), f'Report evidence hash/length mismatch: {name}')
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('create')
    for name in ('report', 'bf16-directory', 'q4-directory', 'destination'):
        create.add_argument('--' + name, type=Path, required=True)
    for name in ('lock-location', 'evaluation-commit', 'runtime-commit'):
        create.add_argument('--' + name, required=True)
    verify = sub.add_parser('verify')
    verify.add_argument('directory', type=Path)
    args = parser.parse_args()
    if args.command == 'verify':
        index = verify_archive(args.directory)
    else:
        index = archive(args.report, dict(zip(ARMS, (args.bf16_directory, args.q4_directory))),
            args.destination, lock_location=args.lock_location, evaluation_commit=args.evaluation_commit,
            runtime_commit=args.runtime_commit)
    print(f"Verified {len(index['files'])} losslessly archived original files")


if __name__ == '__main__':
    main()
