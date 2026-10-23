"""Freeze original 300/language T1 requests with offline HF token validation."""
import argparse
import inspect
import json
from pathlib import Path
from scripts.prepare_scoring_variants import requests_for
from scripts.run_scoring_variants import LANGUAGES, LOCK, sha
from scripts.t1_baselines import validate_lock, compare_a3_requests, compare_original_requests, require, read


def prepare(original, a3, tokenizer):
    # pilot_count=50 describes the original pilot CLI default; items retains
    # the full frozen 300-question development selection used by A1.
    require(original['context'] == 8192 and
            len(original['items']) == 300, 'Original frozen 300 development questions required')
    rows = []
    for language in LANGUAGES:
        for index, group in enumerate(original['items']):
            old = group[language]
            rows.append(dict(language=language,index=index,dataset_index=old['index'],
                source=old['source'],question=old['question'],shift=0,
                target=old['target'],original_target=old['target']) |
                requests_for(old,tokenizer,'plain-letter'))
    lock = dict(schema='t1-original-order-v1',context=8192,rows=rows)
    validate_lock(lock)
    compare_original_requests(rows,original)
    compare_a3_requests(rows,a3)
    return lock


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('sample-lock','a3-lock','tokenizer','output','summary'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    require(a.output != a.summary and not a.output.exists() and not a.summary.exists(),
            'Outputs must be distinct new files')
    require(sha(a.a3_lock)==LOCK,'A3 frozen lock mismatch')
    old,a3=read(a.sample_lock),read(a.a3_lock)
    require(sha(a.sample_lock)==a3['provenance']['original_lock_sha256'],
            'Original development membership authority mismatch')
    from transformers import AutoTokenizer
    import transformers, tokenizers
    tokenizer=AutoTokenizer.from_pretrained(a.tokenizer,local_files_only=True)
    lock=prepare(old,a3,tokenizer)
    tokenfiles={n:sha(a.tokenizer/n) for n in
        ('tokenizer.json','tokenizer_config.json','special_tokens_map.json')}
    require(tokenfiles==a3['provenance']['tokenizer_files'],'Tokenizer artifact identity changed')
    lock['provenance']=dict(original_lock_path=str(a.sample_lock.resolve()),
        original_lock_sha256=sha(a.sample_lock),a3_lock_sha256=LOCK,
        tokenizer_files=tokenfiles,transformers_version=transformers.__version__,
        tokenizers_version=tokenizers.__version__,files={str(Path(f).resolve()):sha(f) for f in
        (__file__,inspect.getfile(prepare),inspect.getfile(requests_for),inspect.getfile(validate_lock),
         inspect.getfile(type(tokenizer)))})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:
        json.dump(lock,f,ensure_ascii=False,allow_nan=False)
    rows=lock['rows']
    coverage={l:dict(contexts=300,candidates=1200,
        max_model_tokens=max(max(map(len,r['model_token_ids'])) for r in rows if r['language']==l),
        longest_indices=[r['index'] for r in rows if r['language']==l and max(map(len,r['model_token_ids']))==
            max(max(map(len,x['model_token_ids'])) for x in rows if x['language']==l)]) for l in LANGUAGES}
    report=dict(status='offline-ready; live expanded coverage NOT run',lock_sha256=sha(a.output),
        provenance=lock['provenance'],coverage=coverage,continuation_tokens=1,
        a3_overlap_contexts=300,a3_overlap_candidates_per_arm=1200,
        a3_live_max_model_tokens=717,
        future_gate='Review expanded longest contexts and novel token boundaries; bounded direct-logit and cold/order gate after explicit collection approval')
    with a.summary.open('x',encoding='utf-8') as f:
        json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps(coverage))


if __name__=='__main__':
    main()
