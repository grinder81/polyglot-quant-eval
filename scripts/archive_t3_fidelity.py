"""Archive verified KL summaries, excluding all raw vocabulary-logit arrays."""
import argparse
import gzip
import io
import json
from pathlib import Path
import tarfile

from scripts.archive_t3_arm import digest,verify
from scripts.run_t3_baselines import LOCK_SHA
from scripts.validate_t3_fidelity import validate,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('directory','lock','runtime','output'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--model-sha256',required=True)
    a=p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    if sha(a.lock)!=LOCK_SHA:
        raise ValueError('Wrong frozen development lock')
    rows=json.loads(a.lock.read_text())['rows']
    validated=validate(a.directory,rows,a.model_sha256,LOCK_SHA,sha(a.runtime))
    names=set(validated['manifest']['per_question_files'])|{'identity.json','manifest.json'}
    if {file.name for file in a.directory.iterdir()}!=names:
        raise ValueError('Unexpected fidelity artifacts')
    files={name:a.directory/name for name in names}
    files['verified-execution.json']=a.directory.parent/(a.directory.name+'-verified.json')
    a.output.mkdir(parents=True)
    archive=a.output/'evidence.tar.gz'
    records=[]
    with archive.open('xb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as compressed,tarfile.open(fileobj=compressed,mode='w') as tar:
        for member,path in sorted(files.items()):
            payload=path.read_bytes()
            item=tarfile.TarInfo(member)
            item.size=len(payload)
            item.mtime=0
            item.mode=0o644
            tar.addfile(item,io.BytesIO(payload))
            records.append(dict(member=member,bytes=len(payload),sha256=digest(payload)))
    manifest=dict(schema='t3-fidelity-archive-v1',model_sha256=a.model_sha256,
        fidelity_manifest_sha256=validated['manifest_sha256'],archive_sha256=sha(archive),
        archive_bytes=archive.stat().st_size,members=records,
        scope='900question KL summaries and execution lineage; no prompts, weights or vocabulary-logit arrays')
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    verify(a.output)


if __name__=='__main__':
    main()
