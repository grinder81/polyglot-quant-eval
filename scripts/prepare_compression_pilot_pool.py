"""Audit FLORES dev source metadata and freeze source-disjoint pilot text pools."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import random
import tarfile
import unicodedata
from urllib.parse import unquote,urlsplit

ARCHIVE_SHA='b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6'
LOCK_SHA='6dfdd304dcba7bd772c37a7634e74c0c16d1e4b70728be6dcb0e218f3847aa19'
LANGUAGES=('eng_Latn','ben_Beng','hin_Deva')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def normalized_source(value):
    url=urlsplit(unquote(value))
    return (url.netloc.lower().removeprefix('www.'),unicodedata.normalize('NFC',url.path).replace('_',' ').rstrip('/').casefold())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('archive','lock','holdout-membership','tokenizer','output'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--tokens',type=int,default=32)
    a=p.parse_args()
    if a.tokens<8:
        raise ValueError('At least eight content tokens required')
    if a.output.exists():
        raise FileExistsError(a.output)
    if sha(a.archive)!=ARCHIVE_SHA or sha(a.lock)!=LOCK_SHA:
        raise ValueError('Input identity mismatch')
    lock=json.loads(a.lock.read_text())
    holdout=json.loads(a.holdout_membership.read_text())
    if holdout['membership_sha256']!='6081033157b4b05d3c82dca198ff19ff318bc38f051549f305a0a8f6a75e5fdc':
        raise ValueError('Holdout membership identity mismatch')
    forbidden={normalized_source(r['source']) for r in lock['rows']+holdout['members']}
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(str(a.tokenizer),local_files_only=True)
    prefix='./flores200_dataset/'
    with tarfile.open(a.archive,'r:gz') as archive:
        def read(name):
            return archive.extractfile(prefix+name).read().decode('utf-8')
        meta=list(csv.DictReader(io.StringIO(read('metadata_dev.tsv')),delimiter='\t'))
        texts={lang:read('dev/'+lang+'.dev').splitlines() for lang in LANGUAGES}
    if any(len(t)!=len(meta) for t in texts.values()):
        raise ValueError('Parallel metadata membership mismatch')
    dev_prompts=[r['prompt'].casefold() for r in lock['rows'] if r['language']=='eng_Latn']
    candidates=[]
    excluded={'source_overlap':0,'development_text_overlap':0,'too_short':0}
    for i,record in enumerate(meta):
        source=normalized_source(record['URL'])
        if source in forbidden:
            excluded['source_overlap']+=1
            continue
        english=texts['eng_Latn'][i].casefold()
        if any(english in prompt for prompt in dev_prompts):
            excluded['development_text_overlap']+=1
            continue
        token_ids={lang:tokenizer(texts[lang][i],add_special_tokens=True)['input_ids'] for lang in LANGUAGES}
        if any(ids[0]!=2 or len(ids)<a.tokens+1 for ids in token_ids.values()):
            excluded['too_short']+=1
            continue
        candidates.append(dict(index=i,source=record['URL'],normalized_source=list(source),
            text={lang:texts[lang][i] for lang in LANGUAGES},
            original_tokens={lang:len(ids)-1 for lang,ids in token_ids.items()},
            model_ids={lang:ids[:a.tokens+1] for lang,ids in token_ids.items()}))
    random.Random(20261101).shuffle(candidates)
    chosen=[]
    seen=set()
    for row in candidates:
        key=tuple(row['normalized_source'])
        if key not in seen:
            chosen.append(row)
            seen.add(key)
        if len(chosen)==19:
            break
    if len(chosen)!=19:
        raise ValueError('Insufficient parallel source-disjoint examples: '+str(len(chosen))+'; excluded='+repr(excluded)+'; eligible='+str(len(candidates)))
    pools={'g1_fisher_profile':[chosen[0]]}
    for rep in (1,2,3):
        start=1+(rep-1)*6
        pools['rep'+str(rep)+'_construction']=chosen[start:start+3]
        pools['rep'+str(rep)+'_probe']=chosen[start+3:start+6]
    report=dict(schema='compression-pilot-pools-v1',archive_sha256=ARCHIVE_SHA,lock_sha256=LOCK_SHA,
        holdout_membership_file_sha256=sha(a.holdout_membership),implementation_sha256=sha(__file__),
        tokenizer_files={n:sha(a.tokenizer/n) for n in ('tokenizer.json','tokenizer_config.json','special_tokens_map.json')},
        source='https://github.com/facebookresearch/flores/blob/main/flores200/README.md',
        download='https://tinyurl.com/flores200dataset',split='dev',seed=20261101,
        total_sentences=len(meta),excluded=excluded,eligible_parallel_sentences=len(candidates),
        forbidden_sources=len(forbidden),selected_source_groups=19,pools=pools,
        tokens_per_example=a.tokens,examples_per_language_per_repeat=3,total_tokens_per_language_per_repeat=3*a.tokens,
        pooled_rule='One equal-length example per language: source 0 English, source 1 Bangla, source 2 Hindi. Individual-language arms use all three matched source examples. Total model-token budgets match.',
        limitations='URL normalization and exact development-English substring exclusion; not proof against redirects, cross-source paraphrases or pretraining contamination. Truncation equalizes model tokens, not semantic coverage. No holdout text, labels or outcomes read.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write('\n')
    print(json.dumps({k:report[k] for k in ('total_sentences','excluded','eligible_parallel_sentences','selected_source_groups')}))


if __name__=='__main__':
    main()
