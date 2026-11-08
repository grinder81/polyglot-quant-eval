"""Publish reproducible corpus identifiers and hashes without transcript extracts."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pool',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    raw=a.pool.read_bytes()
    pool=json.loads(raw)
    result={key:value for key,value in pool.items() if key!='pools'}
    result['private_pool_sha256']=hashlib.sha256(raw).hexdigest()
    result['pools']={name:[dict(source=row['source'],english_segment_ids=row['english_segment_ids'],
        original_tokens=row['original_tokens'],
        text_sha256={lang:hashlib.sha256(text.encode()).hexdigest() for lang,text in row['text'].items()},
        model_ids_sha256={lang:hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()
            for lang,ids in row['model_ids'].items()}) for row in rows] for name,rows in pool['pools'].items()}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
        stream.write('\n')


if __name__=='__main__':
    main()
