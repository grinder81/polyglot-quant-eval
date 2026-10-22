"""Resume locked A3 shards through unchanged upstream task, model and evaluator."""
import argparse
import hashlib
import importlib.metadata
import inspect
import json
import math
import os
from pathlib import Path

LOCK = '75486c22c0c25f7c6c9d3da6abfaaa0165babf4a5de24970147ab9d1488d9844'
LANGUAGES = ('eng_Latn', 'ben_Beng', 'hin_Deva')
VARIANTS = ('plain-letter', 'chat-letter', 'plain-option-text')
DOC_FIELDS = ('language','variant','index','dataset_index','source','question','shift',
              'target','original_target','original_choices','choices',
              'choice_character_lengths','prompt','prompt_sha256','candidates')


def task_document(row):
    # Token arrays remain in the hash-pinned lock, rather than copied into every
    # upstream sample. Projection changes neither text nor task choices.
    return {key:row[key] for key in DOC_FIELDS if key in row}


def validate_directory_files(directory):
    allowed={f'{l}-{v}-r{s}-{i:03}.json' for l in LANGUAGES for v in VARIANTS for s in range(4) for i in range(0,100,5)} | {'identity.json'}
    unexpected={p.name for p in directory.glob('*.json')}-allowed
    if unexpected or list(directory.glob('*.tmp')):
        raise ValueError(f'Unexpected or interrupted shard files in {directory}; preserve and inspect before resuming')


def validation_selection(rows):
    indices={i for i,r in enumerate(rows) if r['index']==0}
    for language in LANGUAGES:
        for variant in VARIANTS:
            subset=[i for i,r in enumerate(rows) if (r['language'],r['variant'])==(language,variant)]
            indices.add(max(subset,key=lambda i:max(map(len,rows[i]['model_token_ids']))))
            indices.add(max(subset,key=lambda i:max(len(t)-len(rows[i]['model_context_ids']) for t in rows[i]['model_token_ids'])))
    return sorted(indices)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def validate(data, expected, arm):
    samples = data['samples']['a3_locked']
    wanted = {(r['source'], r['question']):r for r in expected}
    assert len(samples) == len(wanted) == 5
    compact = []
    for sample in samples:
        doc = sample['doc']
        key = doc['source'], doc['question']
        row = wanted.pop(key)
        assert doc == task_document(row) and sample['target'] == row['target']
        assert sample['arguments'] == [[row['prompt'], c] for c in row['candidates']]
        scores = [response[0] for response in sample['filtered_resps']]
        assert len(scores)==4 and all(math.isfinite(v) for v in scores)
        pred = max(range(4), key=lambda i:scores[i])
        norm = max(range(4), key=lambda i:scores[i]/row['choice_character_lengths'][i])
        assert sample['acc']==int(pred==row['target']) and sample['acc_norm']==int(norm==row['target'])
        compact.append(row | dict(arm=arm, scores=scores))
    assert not wanted
    return compact


def task_for(rows):
    from datasets import Dataset, DatasetDict
    from lm_eval.api.task import ConfigurableTask
    task = ConfigurableTask(config=dict(task='a3_locked', output_type='multiple_choice',
        custom_dataset=lambda **kwargs: DatasetDict(test=Dataset.from_list([task_document(r) for r in rows])),
        test_split='test', doc_to_text='prompt', doc_to_target='target',
        doc_to_choice='choices', target_delimiter=' ', num_fewshot=0,
        metric_list=[dict(metric='acc', aggregation='mean', higher_is_better=True),
                     dict(metric='acc_norm', aggregation='mean', higher_is_better=True)]))
    for row in rows:
        context = task.fewshot_context(row, num_fewshot=0)
        requests = task.construct_requests(row, context)
        assert context == row['prompt'] and [list(r.args) for r in requests] == [[context,c] for c in row['candidates']]
    return task


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('lock','runtime','validation','order-validation','tokenizer','directory'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--base-url', default='http://127.0.0.1:8098/v1/completions')
    p.add_argument('--max-new-shards', type=int)
    a=p.parse_args()
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    from lm_eval import evaluator
    from lm_eval.models.openai_completions import LocalCompletionsAPI
    from lm_eval.api.task import ConfigurableTask
    from lm_eval.api.model import TemplateLM
    import lm_eval.models.api_models as api_base
    import requests
    assert sha(a.lock)==LOCK
    rows=json.loads(a.lock.read_text())['rows']
    assert len(rows)==3600
    membership={(r['language'],r['variant'],r['index'],r['shift']) for r in rows}
    assert membership=={(l,v,i,s) for l in LANGUAGES for v in VARIANTS for i in range(100) for s in range(4)}
    runtime=json.loads(a.runtime.read_text())
    gate=json.loads(a.validation.read_text())
    order=json.loads(a.order_validation.read_text())
    assert gate['lock_sha256']==LOCK and not gate['failures']
    assert gate['runtime_sha256']==sha(a.runtime)
    assert gate['selection']==validation_selection(rows) and len(gate['selection'])==48
    assert [(r['row'],r['candidate']) for r in gate['records']]==[(i,c) for i in gate['selection'] for c in range(4)]
    assert [r['row'] for r in gate['predictions']]==gate['selection']
    assert not gate['order_check'] and order['order_check'] and not order['failures']
    assert order['runtime_sha256']==gate['runtime_sha256'] and order['lock_sha256']==LOCK
    assert order['script_sha256']==gate['script_sha256'] and order['oracle_sha256']==gate['oracle_sha256']
    order_expected=list(reversed([(i,c) for i in gate['selection'] if rows[i]['index']==0 and rows[i]['shift']==0 for c in range(4)]))
    assert [(r['row'],r['candidate']) for r in order['records']]==order_expected and len(order_expected)==36
    assert all(sha(f)==h for f,h in runtime['files'].items())
    assert all(sha(f)==h for f,h in gate['source_files'].items())
    assert all(sha(a.tokenizer/n)==h for n,h in gate['tokenizer_files'].items())
    expected_model=runtime['server_command'][runtime['server_command'].index('--model')+1]
    response=requests.get(a.base_url.rsplit('/',1)[0]+'/models',timeout=30)
    response.raise_for_status()
    endpoint_models=sorted(row['id'] for row in response.json()['data'])
    assert endpoint_models==[expected_model], 'Endpoint serves a different model artifact'
    code=[__file__,inspect.getfile(LocalCompletionsAPI),inspect.getfile(ConfigurableTask),inspect.getfile(TemplateLM),api_base.__file__,evaluator.__file__]
    model_args=dict(model='a3-locked',base_url=a.base_url,tokenizer=str(a.tokenizer),tokenizer_backend='huggingface',tokenized_requests=False,add_bos_token=False,max_length=8192,batch_size=1)
    identity=dict(arm=runtime['arm'],lock_sha256=LOCK,runtime_sha256=sha(a.runtime),model_args=model_args,endpoint_models=endpoint_models,
        validation_sha256=sha(a.validation),order_validation_sha256=sha(a.order_validation),files={str(f):sha(f) for f in code},
        tokenizer=gate['tokenizer_files'],versions={n:importlib.metadata.version(n) for n in ('lm-eval','transformers','tokenizers','datasets')},
        scorer='unchanged upstream ConfigurableTask + LocalCompletionsAPI; summed primary; Unicode-choice-character acc_norm')
    a.directory.mkdir(parents=True, exist_ok=True)
    validate_directory_files(a.directory)
    marker=a.directory/'identity.json'
    if marker.exists():
        assert json.loads(marker.read_text())==identity
    else:
        assert not list(a.directory.glob('*.json'))
        marker.write_text(json.dumps(identity,indent=2))
    model=LocalCompletionsAPI(**model_args)
    count=0
    for language in LANGUAGES:
        for variant in VARIANTS:
            for shift in range(4):
                for start in range(0,100,5):
                    expected=[r for r in rows if (r['language'],r['variant'],r['shift'])==(language,variant,shift) and start<=r['index']<start+5]
                    output=a.directory/f'{language}-{variant}-r{shift}-{start:03}.json'
                    if not output.exists():
                        if a.max_new_shards is not None and count>=a.max_new_shards:
                            return
                        result=evaluator.simple_evaluate(model=model,tasks=[task_for(expected)],num_fewshot=0,apply_chat_template=False,log_samples=True,bootstrap_iters=0,random_seed=42,numpy_random_seed=42,torch_random_seed=None,fewshot_random_seed=42)
                        temporary=output.with_suffix('.tmp')
                        temporary.write_text(json.dumps(result,ensure_ascii=False,default=str))
                        validate(json.loads(temporary.read_text()),expected,runtime['arm'])
                        temporary.replace(output)
                        count+=1
                    validate(json.loads(output.read_text()),expected,runtime['arm'])
                    print(f'Validated {output.name}',flush=True)


if __name__=='__main__':
    main()
