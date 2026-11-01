"""Collect new precision arms through the unchanged T1 task and API scorer."""
import argparse
import copy
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import time

from scripts.t1_baselines import (exact_json,expected_shards,load_shards,read,require,
    task_for,validate,validate_lock,verify_expanded_gate)
from scripts.run_scoring_variants import sha
from scripts.summarize_scoring_variants import verify_files

LOCK_SHA='6dfdd304dcba7bd772c37a7634e74c0c16d1e4b70728be6dcb0e218f3847aa19'


def identity(config):
    paths=read(config)
    required=('lock','runtime','build','token_check','t1_runtime','t1_identity','t1_client','t1_oracle','tokenizer')
    require(all(k in paths for k in required),'Missing T3 readiness path')
    require(sha(paths['lock'])==LOCK_SHA,'Wrong frozen T1 request lock')
    rows=validate_lock(read(paths['lock']))
    runtime,build,tokens,old_runtime,previous=[read(paths[k]) for k in ('runtime','build','token_check','t1_runtime','t1_identity')]
    model=runtime['server_command'][runtime['server_command'].index('--model')+1]
    original_model=old_runtime['server_command'][old_runtime['server_command'].index('--model')+1]
    require(build['status']=='complete' and model==build['output_path'] and
        build['specification_git_blob']=='700a0f601e6503d95b485ad5d048c20b4ef96910' and
        runtime['files'][model]==build['output_sha256'],'T3 build/runtime binding failed')
    expected=copy.deepcopy(old_runtime['server_command'])
    expected[expected.index('--model')+1]=model
    require(runtime['server_command']==expected,'Non-model T3 runtime setting changed')
    require({p:h for p,h in runtime['files'].items() if p!=model}==
            {p:h for p,h in old_runtime['files'].items() if p!=original_model},'Non-model runtime files changed')
    verify_files(runtime['files'])
    verify_files(tokens['files'])
    require(tokens['contexts']==900 and tokens['candidates']==3600 and not tokens['failures'] and
        tokens['model']==model and tokens['lock_sha256']==LOCK_SHA and
        tokens['runtime_sha256']==sha(paths['runtime']),'Incomplete or mismatched token gate')
    oracle=copy.deepcopy(read(paths['t1_oracle']))
    oracle['server_model_settings']['model']=model
    gate_hashes=verify_expanded_gate(paths['lock'],paths['runtime'],paths['gate'],read(paths['t1_client']),oracle)
    gate=read(paths['gate']['validation'])
    versions={k:importlib.metadata.version(k) for k in previous['versions']}
    require(versions==previous['versions']==gate['versions'],'Client versions changed')
    tokenfiles={n:sha(Path(paths['tokenizer'])/n) for n in previous['tokenizer']}
    require(tokenfiles==previous['tokenizer']==gate['tokenizer_files'],'Tokenizer files changed')
    from lm_eval import evaluator
    from lm_eval.models.openai_completions import LocalCompletionsAPI
    from lm_eval.api.task import ConfigurableTask
    from lm_eval.api.model import TemplateLM
    import lm_eval.models.api_models as api_base
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(paths['tokenizer'],local_files_only=True)
    imported=[inspect.getfile(LocalCompletionsAPI),inspect.getfile(ConfigurableTask),inspect.getfile(TemplateLM),
        api_base.__file__,evaluator.__file__,inspect.getfile(type(tokenizer))]
    known=previous['files']|gate['source_files']
    for file in imported:
        require(any(Path(p).resolve()==Path(file).resolve() and h==sha(file) for p,h in known.items()),
            'Imported scorer changed: '+file)
    # Relocating our repository must preserve the frozen task implementation.
    task_file=inspect.getfile(task_for)
    require(any(p.replace('\\','/').endswith('/scripts/run_scoring_variants.py') and h==sha(task_file)
        for p,h in known.items()),'Frozen upstream task wrapper changed')
    model_args=dict(previous['model_args'])
    model_args.update(base_url=paths.get('base_url','http://127.0.0.1:8098/v1/completions'),tokenizer=paths['tokenizer'])
    return dict(schema='t3-cold-original-order-v1',arm=paths['arm'],config_sha256=sha(config),
        inputs={k:sha(paths[k]) for k in required if k!='tokenizer'},
        gate_sha256=gate_hashes,model_args=model_args,endpoint_models=[model],versions=versions,tokenizer=tokenfiles,
        files={str(Path(f).resolve()):sha(f) for f in imported+[__file__,task_file,inspect.getfile(validate)]}),rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--collect',action='store_true')
    p.add_argument('--max-new-shards',type=int)
    a=p.parse_args()
    require(__debug__,'No optimized Python validators')
    require(a.max_new_shards is None or a.max_new_shards>=0,'Negative shard limit')
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    frozen,rows=identity(a.config)
    marker=a.directory/'identity.json'
    if marker.exists():
        require(exact_json(read(marker),frozen),'T3 checkpoint identity changed')
    else:
        require(not list(a.directory.glob('*.json')),'Unidentified shards')
    records,hashes=load_shards(a.directory,rows,frozen['arm'])
    print(json.dumps(dict(completed_shards=len(hashes),total_shards=180,mode='validated',identity=frozen)),flush=True)
    if not a.collect:
        return
    import requests
    from lm_eval import evaluator
    from lm_eval.models.openai_completions import LocalCompletionsAPI
    response=requests.get(frozen['model_args']['base_url'].rsplit('/',1)[0]+'/models',timeout=30)
    response.raise_for_status()
    require(sorted(m['id'] for m in response.json()['data'])==frozen['endpoint_models'],'Wrong served model')
    a.directory.mkdir(parents=True,exist_ok=True)
    if not marker.exists():
        with marker.open('x') as stream:
            json.dump(frozen,stream,indent=2,allow_nan=False)
    model=None
    count=0
    started=time.monotonic()
    for name,expected in expected_shards(rows).items():
        output=a.directory/name
        if output.exists() or (a.max_new_shards is not None and count>=a.max_new_shards):
            continue
        if model is None:
            model=LocalCompletionsAPI(**frozen['model_args'])
        result=evaluator.simple_evaluate(model=model,tasks=[task_for(expected)],num_fewshot=0,
            apply_chat_template=False,log_samples=True,bootstrap_iters=0,random_seed=42,
            numpy_random_seed=42,torch_random_seed=None,fewshot_random_seed=42)
        temporary=output.with_suffix('.tmp')
        with temporary.open('x',encoding='utf-8') as stream:
            json.dump(result,stream,ensure_ascii=False,default=str,allow_nan=False)
        validate(read(temporary),expected,frozen['arm'])
        temporary.rename(output)
        count+=1
        print(json.dumps(dict(validated_shard=name,new_shards=count,seconds=time.monotonic()-started)),flush=True)
    records,hashes=load_shards(a.directory,rows,frozen['arm'])
    print(json.dumps(dict(completed_shards=len(hashes),total_shards=180,new_shards=count,seconds=time.monotonic()-started)),flush=True)


if __name__=='__main__':
    main()
