"""Package or verify complete T3 scoring evidence without weights or logit caches."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def package(config,directory,output):
    config,directory,output=map(Path,(config,directory,output))
    if output.exists():
        raise FileExistsError(output)
    cfg=json.loads(config.read_text())
    identity=json.loads((directory/'identity.json').read_text())
    if identity['config_sha256']!=digest(config.read_bytes()) or identity['arm']!=cfg['arm']:
        raise ValueError('Wrong archive arm/configuration')
    names={f'{lang}-{start:03}.json' for lang in ('eng_Latn','ben_Beng','hin_Deva') for start in range(0,300,5)}
    if {p.name for p in directory.iterdir()}!=names|{'identity.json'}:
        raise ValueError('Archive requires complete180shards and identity only')
    files={f'shards/{name}':directory/name for name in sorted(names|{'identity.json'})}
    files['readiness/config.json']=config
    for key in ('runtime','build','token_check','t1_runtime','t1_identity','t1_client','t1_oracle'):
        files['readiness/'+key+'.json']=Path(cfg[key])
    for key,value in cfg['gate'].items():
        suffix=Path(value).suffix
        files['readiness/gate-'+key+suffix]=Path(value)
    files['source/run_t3_baselines.py']=Path(__file__).with_name('run_t3_baselines.py')
    files['source/t1_baselines.py']=Path(__file__).with_name('t1_baselines.py')
    files['source/run_scoring_variants.py']=Path(__file__).with_name('run_scoring_variants.py')
    # The request lock is referenced by hash; source models and vocabulary logits
    # are never traversed from the runtime manifest's model paths.
    output.mkdir(parents=True)
    records=[]
    archive=output/'evidence.tar.gz'
    with archive.open('xb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as compressed,tarfile.open(fileobj=compressed,mode='w') as tar:
        for member,path in sorted(files.items()):
            if path.suffix not in ('.json','.py','.md'):
                raise ValueError('Unexpected evidence type')
            payload=path.read_bytes()
            item=tarfile.TarInfo(member)
            item.size=len(payload)
            item.mtime=0
            item.mode=0o644
            tar.addfile(item,io.BytesIO(payload))
            records.append(dict(member=member,source_path=str(path),bytes=len(payload),sha256=digest(payload)))
    manifest=dict(schema='t3-arm-archive-v1',arm=cfg['arm'],members=records,
        archive_bytes=archive.stat().st_size,archive_sha256=digest(archive.read_bytes()),
        lock_sha256=identity['inputs']['lock'],scope='Complete scoring and readiness evidence; no model weights, raw vocabulary logits or final holdout')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    verify(output)


def verify(directory):
    directory=Path(directory)
    manifest=json.loads((directory/'manifest.json').read_text())
    archive=directory/'evidence.tar.gz'
    if archive.stat().st_size!=manifest['archive_bytes'] or digest(archive.read_bytes())!=manifest['archive_sha256']:
        raise ValueError('Archive identity failed')
    expected={row['member']:row for row in manifest['members']}
    found=set()
    with tarfile.open(archive,'r:gz') as tar:
        for member in tar:
            if not member.isfile() or member.name not in expected or member.name in found:
                raise ValueError('Unexpected archive member')
            payload=tar.extractfile(member).read()
            row=expected[member.name]
            if member.size!=row['bytes'] or len(payload)!=row['bytes'] or digest(payload)!=row['sha256']:
                raise ValueError('Member hash failed')
            found.add(member.name)
    if found!=expected.keys():
        raise ValueError('Missing archive member')
    print(json.dumps(dict(verified_members=len(found),archive_sha256=manifest['archive_sha256'])),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='mode',required=True)
    pack=sub.add_parser('package')
    for key in ('config','directory','output'):
        pack.add_argument('--'+key,type=Path,required=True)
    check=sub.add_parser('verify')
    check.add_argument('directory',type=Path)
    a=p.parse_args()
    if a.mode=='package':
        package(a.config,a.directory,a.output)
    else:
        verify(a.directory)


if __name__=='__main__':
    main()
