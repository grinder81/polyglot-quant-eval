"""Lossless T1 packaging from a trusted complete frozen report, without inference.

Only explicit report-bound shards, identities, gates and provenance are read.
No scientific source is modified; model and request-lock payloads are references.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

ARMS = ('bf16-gguf','local-q4')
LANGS = ('eng_Latn','ben_Beng','hin_Deva')
GATES = {'oracle':'oracle.json','validation':'client.json','order_validation':'reverse.json',
         'validator_script':'validator.py','protocol':'protocol.md'}


def require(condition,message):
    if not condition:raise ValueError(message)


def digest(data):return hashlib.sha256(data).hexdigest()


def sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def exact(a,b):
    return json.dumps(a,sort_keys=True,allow_nan=False,separators=(',',':')) == json.dumps(
        b,sort_keys=True,allow_nan=False,separators=(',',':'))


def integer(value,expected):return type(value) is int and value == expected


def shard_names():
    return {f'{lang}-{start:03}.json' for lang in LANGS for start in range(0,300,5)}


def flag(record,name):
    command = record['report_command']
    require(isinstance(command,list) and all(isinstance(x,str) for x in command)
            and command.count('--'+name) == 1,'Ambiguous/missing recorded report argument: '+name)
    i = command.index('--'+name)
    require(i+1 < len(command) and not command[i+1].startswith('--'),'Missing report argument value')
    return command[i+1]


def validate_report(report):
    """Structural completeness only; root's frozen scientific report is the trust anchor."""
    require(report['schema'] == 't1-complete-report-v1','Wrong final report schema')
    require(set(report['provenance']['fresh']) == set(ARMS) and set(report['fresh_rows']) == set(ARMS)
            and set(report['historical_to_fresh_by_arm']) == set(ARMS),'Both complete arms required')
    summaries = [report['fresh_paired_GGUF']] + [
        report['historical_to_fresh_by_arm'][a]['outcomes_historical_to_fresh'] for a in ARMS]
    for summary in summaries:
        require(integer(summary['bootstrap_replicates'],10000) and integer(summary['bootstrap_seed'],42)
                and set(summary['languages']) == set(LANGS),'Frozen bootstrap/language scope required')
        require(all(integer(v['n'],300) for v in summary['languages'].values()),'Complete 300/language required')
    for arm in ARMS:
        evidence = report['provenance']['fresh'][arm]
        identity = evidence['identity']
        require(evidence['complete'] is True and set(evidence['shard_sha256']) == shard_names(),
                'Complete 180-shard hashes required per arm')
        require(identity['schema'] == 't1-cold-original-order-v1' and identity['arm'] == arm
                and set(identity['expanded_gate_paths']) == set(GATES)
                and set(identity['expanded_gate_sha256']) == set(GATES),'Complete pinned identity/gates required')
        rows = report['fresh_rows'][arm]
        require(len(rows) == 900 and len({(r['language'],r['source'],r['question']) for r in rows}) == 900
                and all(sum(r['language'] == lang for r in rows) == 300 for lang in LANGS),
                'Complete unique fresh rows required')
        require(all(sha(h) for h in evidence['shard_sha256'].values())
                and all(sha(h) for h in identity['expanded_gate_sha256'].values()),'Invalid source hash')
    require(report['fresh_margin']['input_schema'] == 'validated-t1-original-order',
            'Fresh margin identity missing')


def completed_receipt(record,report_bytes):
    """Root's reviewed completion proof, never infer success from a launch proposal."""
    proof=record.get('archive_completion',{})
    require(proof.get('schema') == 't1-completed-execution-receipt-v1'
            and proof.get('collection_complete') is True
            and integer(proof.get('report_exit_code'),0)
            and proof.get('report_sha256') == digest(report_bytes)
            and integer(proof.get('report_bytes'),len(report_bytes)),
            'Completed execution/report receipt required')
    require(set(proof.get('arms',{})) == set(ARMS),'Both completion proofs required')
    for arm in ARMS:
        evidence=proof['arms'][arm]
        require(integer(evidence.get('validated_shards'),180)
                and integer(evidence.get('validated_questions'),900)
                and integer(evidence.get('runner_exit_code'),0)
                and evidence.get('server_stopped') is True,'Incomplete arm execution proof: '+arm)


def bindings(report,record):
    """Map fixed member names to source paths and report-bound proof, never recurse."""
    validate_report(report)
    result = {}
    for arm,prefix in zip(ARMS,('bf16','q4')):
        evidence = report['provenance']['fresh'][arm]
        identity,runtime = evidence['identity'],evidence['runtime']
        directory = Path(flag(record,prefix+'-directory'))
        require({p.name for p in directory.glob('*.json')} == shard_names() | {'identity.json'}
                and not list(directory.glob('*.tmp')),'Incomplete/unexpected source shard inventory')
        for name,h in evidence['shard_sha256'].items():
            result[f'raw/{arm}/{name}'] = dict(path=directory/name,sha256=h)
        # T1 report stores a full identity, not the identity FILE's byte hash.
        # Prove exact typed JSON equality, then capture/archive its original bytes.
        result[f'raw/{arm}/identity.json'] = dict(path=directory/'identity.json',json=identity)
        for name,member in GATES.items():
            result[f'validation/{arm}/{member}'] = dict(path=Path(identity['expanded_gate_paths'][name]),
                sha256=identity['expanded_gate_sha256'][name])
        runtime_path = Path(record['arms'][arm]['runtime_manifest'])
        require(record['arms'][arm]['runtime_manifest_sha256'] == identity['runtime_sha256'],
                'Execution/runtime reference mismatch')
        result[f'validation/{arm}/runtime.json'] = dict(path=runtime_path,
            sha256=identity['runtime_sha256'],json=runtime)
        result[f'validation/{arm}/tokens.json'] = dict(path=Path(flag(record,prefix+'-token-check')),
            sha256=identity['token_check_sha256'])
        require(flag(record,'base-url') == identity['model_args']['base_url'],
                'Execution/client reference mismatch')
    identities = [report['provenance']['fresh'][a]['identity'] for a in ARMS]
    require(identities[0]['lock_sha256'] == identities[1]['lock_sha256']
            and identities[0]['readiness_sha256'] == identities[1]['readiness_sha256'],
            'Paired lock/readiness references differ')
    result['validation/preparation.json'] = dict(path=Path(flag(record,'readiness')),
        sha256=identities[0]['readiness_sha256'])
    return result


def groups():
    return {**{arm+'.tar.gz':{f'raw/{arm}/{name}' for name in shard_names() | {'identity.json'}} for arm in ARMS},
        'validation.tar.gz':{f'validation/{arm}/{name}' for arm in ARMS
            for name in (*GATES.values(),'runtime.json','tokens.json')}
            | {'validation/preparation.json','validation/execution-record.json'},
        'validated-report.json.gz':{'validated-report.json'}}


def check_original(name,data,proof):
    if 'sha256' in proof:require(digest(data) == proof['sha256'],'Original hash mismatch: '+name)
    if 'json' in proof:require(exact(json.loads(data),proof['json']),'Typed JSON identity mismatch: '+name)


def create(report_path,report_sha256,execution_record,execution_sha256,destination):
    require(sha(report_sha256) and sha(execution_sha256),'Explicit trusted report/execution SHA-256 required')
    raw_report,raw_record = Path(report_path).read_bytes(),Path(execution_record).read_bytes()
    require(digest(raw_report) == report_sha256 and digest(raw_record) == execution_sha256,
            'Trusted report/execution byte identity mismatch')
    report,record = json.loads(raw_report),json.loads(raw_record)
    completed_receipt(record,raw_report)
    sources = bindings(report,record)
    sources['validated-report.json'] = dict(path=Path(report_path),sha256=report_sha256)
    sources['validation/execution-record.json'] = dict(path=Path(execution_record),sha256=execution_sha256)
    require(set(sources) == set().union(*groups().values()),'Unexpected packaging inventory')
    destination = Path(destination)
    require(not destination.exists(),'Destination must be new')
    # Reject partial/corrupt runs before creating any output.
    for name,proof in sources.items():check_original(name,proof['path'].read_bytes(),proof)
    destination.mkdir(parents=True,exist_ok=False)
    index = dict(format='t1-lossless-tar-gzip-v1',report_sha256=report_sha256,
        execution_record_sha256=execution_sha256,
        lock_reference=dict(path=flag(record,'lock'),
            sha256=report['provenance']['fresh'][ARMS[0]]['identity']['lock_sha256'],included=False),
        files={},archives={},identity_proof='Typed JSON equality to report identity; original identity byte hashes captured here')
    for archive,names in groups().items():
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer,mode='wb',filename='',mtime=0,compresslevel=9) as stream:
            if archive.endswith('.tar.gz'):
                with tarfile.open(fileobj=stream,mode='w',format=tarfile.USTAR_FORMAT) as tar:
                    for name in sorted(names):
                        data = sources[name]['path'].read_bytes()
                        check_original(name,data,sources[name])
                        info = tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0
                        tar.addfile(info,io.BytesIO(data))
                        index['files'][name] = dict(bytes=len(data),sha256=digest(data),
                            storage=dict(archive=archive,member=name))
            else:
                data = sources['validated-report.json']['path'].read_bytes()
                check_original('validated-report.json',data,sources['validated-report.json'])
                stream.write(data)
                index['files']['validated-report.json'] = dict(bytes=len(data),sha256=digest(data),
                    storage=dict(archive=archive,member=None))
        packed=buffer.getvalue()
        with (destination/archive).open('xb') as output:output.write(packed)
        index['archives'][archive] = dict(bytes=len(packed),sha256=digest(packed))
    with (destination/'archive-manifest.json').open('x',encoding='utf-8',newline='\n') as output:
        json.dump(index,output,sort_keys=True,indent=2,allow_nan=False);output.write('\n')
    verify(destination,report_sha256,execution_sha256)
    return index


def verify(directory,expected_report_sha256=None,expected_execution_sha256=None):
    """Verify trusted package bytes and fixed regular members without filesystem extraction."""
    root=Path(directory).resolve()
    index=json.loads((root/'archive-manifest.json').read_bytes())
    require(index['format'] == 't1-lossless-tar-gzip-v1','Unknown archive format')
    require(set(index['archives']) == set(groups()),'Unexpected archive inventory')
    require({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
            == set(groups()) | {'archive-manifest.json'},'Unexpected/missing archive files')
    originals={}
    for archive,names in groups().items():
        path=root/archive
        require(path.resolve().is_relative_to(root),'Unsafe archive path')
        packed=path.read_bytes();proof=index['archives'][archive]
        require(digest(packed) == proof['sha256'] and len(packed) == proof['bytes'],
                'Compressed hash/length mismatch: '+archive)
        try:
            if archive.endswith('.tar.gz'):
                seen=set()
                with tarfile.open(fileobj=io.BytesIO(packed),mode='r|gz') as tar:
                    for member in tar:
                        require(member.isfile() and member.name in names and member.name not in seen,
                                'Unsafe/nonregular/duplicate tar member')
                        seen.add(member.name);originals[member.name]=tar.extractfile(member).read()
                require(seen == names,'Incomplete tar members')
            else:originals['validated-report.json']=gzip.decompress(packed)
        except (OSError,EOFError,tarfile.TarError) as error:
            raise ValueError('Invalid compressed stream: '+archive) from error
    require(set(index['files']) == set(originals),'Original member inventory mismatch')
    for archive,names in groups().items():
        for name in names:
            proof=index['files'][name];data=originals[name]
            require(proof['storage'] == dict(archive=archive,member=name if archive.endswith('.tar.gz') else None)
                    and digest(data) == proof['sha256'] and len(data) == proof['bytes'],
                    'Original hash/length/storage mismatch: '+name)
    report_hash=digest(originals['validated-report.json'])
    record_hash=digest(originals['validation/execution-record.json'])
    require(report_hash == index['report_sha256'] and record_hash == index['execution_record_sha256']
            and (expected_report_sha256 is None or report_hash == expected_report_sha256)
            and (expected_execution_sha256 is None or record_hash == expected_execution_sha256),
            'Trusted report/execution identity mismatch')
    report=json.loads(originals['validated-report.json']);record=json.loads(originals['validation/execution-record.json'])
    completed_receipt(record,originals['validated-report.json'])
    # Derive proofs from archived metadata without touching original source paths.
    validate_report(report)
    for arm,prefix in zip(ARMS,('bf16','q4')):
        evidence=report['provenance']['fresh'][arm];identity=evidence['identity']
        for name,h in evidence['shard_sha256'].items():
            check_original(f'raw/{arm}/{name}',originals[f'raw/{arm}/{name}'],dict(sha256=h))
        check_original(f'raw/{arm}/identity.json',originals[f'raw/{arm}/identity.json'],dict(json=identity))
        for name,member in GATES.items():
            check_original(member,originals[f'validation/{arm}/{member}'],dict(sha256=identity['expanded_gate_sha256'][name]))
        check_original('runtime',originals[f'validation/{arm}/runtime.json'],
                       dict(sha256=identity['runtime_sha256'],json=evidence['runtime']))
        check_original('tokens',originals[f'validation/{arm}/tokens.json'],dict(sha256=identity['token_check_sha256']))
        require(record['arms'][arm]['runtime_manifest_sha256'] == identity['runtime_sha256']
                and flag(record,'base-url') == identity['model_args']['base_url'],
                'Execution/runtime/client reference mismatch')
        check_original('preparation',originals['validation/preparation.json'],dict(sha256=identity['readiness_sha256']))
    require(index['lock_reference'] == dict(path=flag(record,'lock'),
        sha256=report['provenance']['fresh'][ARMS[0]]['identity']['lock_sha256'],included=False),
        'Lock reference mismatch')
    return index


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    create_parser=sub.add_parser('create')
    for name in ('report','execution-record','destination'):create_parser.add_argument('--'+name,type=Path,required=True)
    for name in ('report-sha256','execution-record-sha256'):create_parser.add_argument('--'+name,required=True)
    verify_parser=sub.add_parser('verify');verify_parser.add_argument('directory',type=Path)
    verify_parser.add_argument('--report-sha256');verify_parser.add_argument('--execution-record-sha256')
    args=parser.parse_args()
    if args.command == 'create':
        index=create(args.report,args.report_sha256,args.execution_record,args.execution_record_sha256,args.destination)
    else:index=verify(args.directory,args.report_sha256,args.execution_record_sha256)
    print(f"Verified {len(index['files'])} original T1 evidence files without extraction")


if __name__ == '__main__':main()
