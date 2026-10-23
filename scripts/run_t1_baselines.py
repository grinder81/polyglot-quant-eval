"""Resume fresh T1 cold baselines with the unchanged reviewed upstream scorer.

--validate-only is offline. --collect requires an approved expanded live gate;
readiness authorization alone does not authorize calling it.
"""
import argparse
import json
import os
from pathlib import Path
from scripts.t1_baselines import (ARMS,expected_shards,overlap_check,read,require,
    run_identity,load_shards,task_for,validate,verify_run_identity)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('lock','readiness','token-check','a3-lock','a3-execution-record','tokenizer','directory'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--arm',choices=ARMS,required=True)
    p.add_argument('--base-url',default='http://127.0.0.1:8098/v1/completions')
    p.add_argument('--expanded-gate',type=Path,help='JSON paths: oracle,validation,order_validation,validator_script,protocol')
    p.add_argument('--max-new-shards',type=int)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--validate-only',action='store_true')
    mode.add_argument('--collect',action='store_true')
    a=p.parse_args()
    require(a.max_new_shards is None or a.max_new_shards>=0,'Negative shard limit')
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    expanded=read(a.expanded_gate) if a.expanded_gate else None
    args=(a.lock,a.readiness,a.token_check,a.a3_lock,a.a3_execution_record,
          a.tokenizer,a.directory,a.arm,a.base_url)
    records,proof=verify_run_identity(*args,expanded_gate=expanded)
    print(json.dumps(dict(mode='offline-validation',completed_shards=len(proof['shard_sha256']),
        total_shards=180,complete=proof['complete'],identity=proof['identity']),allow_nan=False),flush=True)
    if a.validate_only:
        return
    identity,rows,cells,_=run_identity(a.lock,a.readiness,a.token_check,a.a3_lock,
        a.a3_execution_record,a.tokenizer,a.arm,a.base_url,expanded or proof['identity']['expanded_gate_paths'])
    require(identity['expanded_gate_sha256'] is not None,'Expanded live cold/order gate required before collection')
    from lm_eval import evaluator
    from lm_eval.models.openai_completions import LocalCompletionsAPI
    import requests
    response=requests.get(a.base_url.rsplit('/',1)[0]+'/models',timeout=30)
    response.raise_for_status()
    require(sorted(r['id'] for r in response.json()['data'])==identity['endpoint_models'],
            'Endpoint model mismatch')
    a.directory.mkdir(parents=True,exist_ok=True)
    marker=a.directory/'identity.json'
    if not marker.exists():
        with marker.open('x',encoding='utf-8') as f:
            json.dump(identity,f,indent=2,allow_nan=False)
    model=None
    count=0
    for name,expected in expected_shards(rows).items():
        output=a.directory/name
        if output.exists():
            continue  # All saved shards validated above, including later ones.
        if a.max_new_shards is not None and count>=a.max_new_shards:
            continue
        if model is None:
            model=LocalCompletionsAPI(**identity['model_args'])
        result=evaluator.simple_evaluate(model=model,tasks=[task_for(expected)],num_fewshot=0,
            apply_chat_template=False,log_samples=True,bootstrap_iters=0,random_seed=42,
            numpy_random_seed=42,torch_random_seed=None,fewshot_random_seed=42)
        temporary=output.with_suffix('.tmp')
        with temporary.open('x',encoding='utf-8') as f:
            json.dump(result,f,ensure_ascii=False,default=str,allow_nan=False)
        scored=validate(read(temporary),expected,a.arm)
        overlap=overlap_check(scored,cells,a.arm)
        if overlap['failures'] or overlap['inversions']:
            # Keep the exact raw .tmp and explicit diagnostics; never promote
            # failed overlap as completed or silently rerun it on resume.
            with temporary.with_suffix('.overlap.json').open('x',encoding='utf-8') as f:
                json.dump(overlap,f,indent=2,allow_nan=False)
            raise ValueError('Overlap gate failed; raw temporary evidence preserved')
        temporary.replace(output)
        count+=1
        print(f'Validated {name}',flush=True)
    completed,_=load_shards(a.directory,rows,a.arm)
    print(f'Completed {len(completed)//5}/180 shards; added {count}',flush=True)


if __name__=='__main__':
    main()
