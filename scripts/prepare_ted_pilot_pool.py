"""Freeze matched TED2020 text by talk, disjoint from protected wiki sources."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
import zipfile

LANGUAGES=('eng_Latn','ben_Beng','hin_Deva')
ARCHIVES={'bn-en':'e5461d5f1a1dc89960359e6c75c54ba43be39217625678273258c2a80f20cd19',
          'en-hi':'4aaea1c9fb2fda3c96926c1c9494a3da502b0f80bf2ee958531691c0e55917ce'}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def aligned_rows(path,pair):
    """Moses inserts one blank separator after each XML document group."""
    left,right=pair.split('-')
    with zipfile.ZipFile(path) as archive:
        prefix='TED2020.'+pair
        a=archive.read(prefix+'.'+left).decode().splitlines()
        b=archive.read(prefix+'.'+right).decode().splitlines()
        root=ET.fromstring(archive.read(prefix+'.xml'))
    if len(a)!=len(b):
        raise ValueError('Unequal bilingual lines')
    index=0
    result={}
    for group in root.findall('linkGrp'):
        talk_left=re.fullmatch(left+r'/ted2020-(\d+)\.xml\.gz',group.attrib['fromDoc'])
        talk_right=re.fullmatch(right+r'/ted2020-(\d+)\.xml\.gz',group.attrib['toDoc'])
        if not talk_left or not talk_right or talk_left[1]!=talk_right[1]:
            raise ValueError('Document identity mismatch')
        talk=talk_left[1]
        for link in group.findall('link'):
            l,r=link.attrib['xtargets'].split(';')
            english_id=l if left=='en' else r
            if not a[index] or not b[index]:
                raise ValueError('Empty aligned sentence')
            key=talk,english_id
            if key in result:
                raise ValueError('Duplicate source sentence')
            result[key]={'en':a[index] if left=='en' else b[index],
                         'other':b[index] if left=='en' else a[index]}
            index+=1
        if a[index] or b[index]:
            raise ValueError('Missing Moses document separator')
        index+=1
    if index!=len(a):
        raise ValueError('Unconsumed Moses lines')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('bn-en','en-hi','lock','holdout-membership','tokenizer','output'):
        p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    paths={'bn-en':a.bn_en,'en-hi':a.en_hi}
    if any(sha(paths[k])!=v for k,v in ARCHIVES.items()):
        raise ValueError('Archive hash mismatch')
    lock=json.loads(a.lock.read_text())
    holdout=json.loads(a.holdout_membership.read_text())
    if sha(a.lock)!='6dfdd304dcba7bd772c37a7634e74c0c16d1e4b70728be6dcb0e218f3847aa19' or holdout['membership_sha256']!='6081033157b4b05d3c82dca198ff19ff318bc38f051549f305a0a8f6a75e5fdc':
        raise ValueError('Protected membership mismatch')
    hosts=sorted({urlsplit(r['source']).netloc.lower() for r in lock['rows']+holdout['members']})
    if any(h=='ted.com' or h.endswith('.ted.com') for h in hosts):
        raise ValueError('Protected sources include TED; source audit needs expansion')
    bn,hi=aligned_rows(a.bn_en,'bn-en'),aligned_rows(a.en_hi,'en-hi')
    docs={}
    for key in bn.keys() & hi.keys():
        if bn[key]['en']==hi[key]['en']:
            docs.setdefault(key[0],[]).append((key[1],{'eng_Latn':bn[key]['en'],'ben_Beng':bn[key]['other'],'hin_Deva':hi[key]['other']}))
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(str(a.tokenizer),local_files_only=True)
    dev_prompts=[r['prompt'].casefold() for r in lock['rows'] if r['language']=='eng_Latn']
    eligible=[]
    for doc,segments in sorted(docs.items(),key=lambda x:int(x[0])):
        segments.sort(key=lambda x:tuple(float(v) for v in x[0].split()))
        text={lang:'' for lang in LANGUAGES}
        used=[]
        for segment,translations in segments:
            for lang in LANGUAGES:
                text[lang]+=(' ' if text[lang] else '')+translations[lang]
            used.append(segment)
            ids={lang:tokenizer(text[lang],add_special_tokens=True)['input_ids'] for lang in LANGUAGES}
            if all(len(v)>=65 for v in ids.values()):
                break
        if not all(len(v)>=65 and v[0]==2 for v in ids.values()):
            continue
        english=text['eng_Latn'].casefold()
        if any(english in prompt or (len(prompt)>50 and prompt in english) for prompt in dev_prompts):
            continue
        eligible.append(dict(source='TED2020:talk:'+doc,english_segment_ids=used,text=text,
            model_ids={lang:v[:65] for lang,v in ids.items()},original_tokens={lang:len(v)-1 for lang,v in ids.items()}))
    random.Random(20261101).shuffle(eligible)
    if len(eligible)<19:
        raise ValueError('Too few common source-disjoint talks')
    selected=eligible[:19]
    pools={'g1_fisher_profile':[selected[0]]}
    for rep in (1,2,3):
        start=1+(rep-1)*6
        pools[f'rep{rep}_construction']=selected[start:start+3]
        pools[f'rep{rep}_probe']=selected[start+3:start+6]
    report=dict(schema='compression-pilot-pools-v1',corpus='OPUS TED2020 v1',
        archives={pair:dict(sha256=ARCHIVES[pair],url='https://object.pouta.csc.fi/OPUS-TED2020/v1/moses/'+pair+'.txt.zip') for pair in paths},
        license='Original-source TED Talks usage policy; cache text locally, publish identifiers/hashes rather than transcript extracts.',
        lock_sha256=sha(a.lock),holdout_membership_file_sha256=sha(a.holdout_membership),
        implementation_sha256=sha(__file__),protected_source_hosts=hosts,
        tokenizer_files={n:sha(a.tokenizer/n) for n in ('tokenizer.json','tokenizer_config.json','special_tokens_map.json')},
        eligible_parallel_talks=len(eligible),selected_source_groups=19,seed=20261101,pools=pools,
        tokens_per_example=64,examples_per_language_per_repeat=3,total_tokens_per_language_per_repeat=192,
        pooled_rule='For both construction and probe, source0 English, source1 Bangla, source2 Hindi,64 tokens each. Individual-language arms use all3 matched sources. All arms total192 tokens.',
        limitations='Exact English sentence alignment and talk grouping; protected wiki source domains differ. No guarantee against quoted content or pretraining contamination. Prefix truncation equalizes tokens, not semantic coverage. TED-to-Belebele domain transfer remains empirical. No holdout text, labels or outcomes read.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(eligible_parallel_talks=len(eligible),selected_sources=[r['source'] for r in selected],pool_sha256=sha(a.output))))


if __name__=='__main__':
    main()
