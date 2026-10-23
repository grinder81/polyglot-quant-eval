"""Offline T1 request, shard and provenance validation; no model execution."""
import json
import math
from pathlib import Path

from scripts.run_scoring_variants import LANGUAGES, LOCK, sha, task_for, validate as a3_validate
from scripts.summarize_scoring_variants import require, read, load_evidence, verify_files

ARMS = ('bf16-gguf', 'local-q4')
TOKEN_ATOL = 0.0002
SUM_ATOL = 0.001


def validate(data,expected,arm):
    """Use the frozen A3 sample join plus strict numeric type/margin checks."""
    import sys
    require(not sys.flags.optimize,'Upstream assertion validators require Python without -O')
    for sample in data['samples']['a3_locked']:
        scores=[r[0] for r in sample['filtered_resps']]
        require(len(scores)==4 and all(type(s) in (int,float) and math.isfinite(s) for s in scores),
                'Four finite nonboolean numeric scores required')
        ordered=sorted(scores,reverse=True)
        require(math.isfinite(ordered[0]-ordered[1]),'Nonfinite margin')
    return a3_validate(data,expected,arm)


def validate_lock(lock):
    rows = lock['rows']
    require(lock['schema'] == 't1-original-order-v1' and lock['context'] == 8192,
            'Wrong T1 lock schema/context')
    require(len(rows) == 900 and [(r['language'], r['index']) for r in rows] ==
            [(l, i) for l in LANGUAGES for i in range(300)], 'Exact ordered 300/language required')
    for language in LANGUAGES:
        subset = [r for r in rows if r['language'] == language]
        require(len({(r['source'], r['question']) for r in subset}) == 300,
                'Duplicate original source/question')
    import hashlib
    for r in rows:
        require(r['variant'] == 'plain-letter' and r['shift'] == 0 and
                type(r['target']) is int and r['target'] in range(4) and
                r['original_target'] == r['target'], 'Original-order target contract')
        require(r['choices'] == list('ABCD') and r['candidates'] == [' A',' B',' C',' D'] and
                r['choice_character_lengths'] == [1]*4, 'Letter contract mismatch')
        require(hashlib.sha256(r['prompt'].encode()).hexdigest() == r['prompt_sha256'],
                'Prompt byte hash mismatch')
        context = r['model_context_ids']
        require(context and context[1:] == r['wire_context_ids'], 'BOS/context mismatch')
        require(len(r['model_token_ids']) == len(r['wire_token_ids']) == 4,
                'Four candidate token arrays required')
        for full, wire in zip(r['model_token_ids'], r['wire_token_ids'], strict=True):
            require(full == context[:1] + wire and full[:-1] == context and
                    len(full) < 8192, 'Exactly one continuation token and one BOS required')
    return rows


def compare_a3_requests(rows, a3):
    old = {(r['language'], r['index']): r for r in a3['rows']
           if r['variant'] == 'plain-letter' and r['shift'] == 0}
    require(len(old) == 300, 'Exact A3 original-order overlap required')
    fields = ('language','index','dataset_index','source','question','target','prompt',
              'prompt_sha256','candidates','choices','choice_character_lengths',
              'model_context_ids','model_token_ids','wire_context_ids','wire_token_ids')
    for row in rows:
        if row['index'] < 100:
            require(all(row[f] == old[row['language'], row['index']][f] for f in fields),
                    'A3 overlap request bytes/tokens/identity changed')


def compare_original_requests(rows,original):
    require(len(original['items'])==300 and original['context']==8192,
            'Exact original 300-question authority required')
    for row in rows:
        before=original['items'][row['index']][row['language']]
        require(row['dataset_index']==before['index'] and all(row[f]==before[f] for f in
                ('source','question','target','prompt','prompt_sha256','candidates')) and
                row['model_context_ids']==before['context_ids'] and
                row['model_token_ids']==before['token_ids'], 'Original 900 request membership/bytes/tokens changed')


def expected_shards(rows):
    return {f'{language}-{start:03}.json': [r for r in rows if
                r['language'] == language and start <= r['index'] < start+5]
            for language in LANGUAGES for start in range(0,300,5)}


def validation_selection(rows):
    indices = {i for i,r in enumerate(rows) if r['index'] in (0,100,299)}
    for language in LANGUAGES:
        subset = [i for i,r in enumerate(rows) if r['language']==language]
        indices.add(max(subset,key=lambda i:max(map(len,rows[i]['model_token_ids']))))
    return sorted(indices)


def verify_expanded_gate(lock_path, runtime_path, paths, previous_gate, previous_oracle):
    rows=validate_lock(read(lock_path))
    selection=validation_selection(rows)
    oracle,client,order=[read(paths[n]) for n in ('oracle','validation','order_validation')]
    pairs=[(i,c) for i in selection for c in range(4)]
    for artifact,expected in ((oracle,pairs),(client,pairs),(order,list(reversed(pairs)))):
        require(artifact['lock_sha256']==sha(lock_path) and
                artifact['runtime_sha256']==sha(runtime_path) and
                artifact['script_sha256']==sha(paths['validator_script']) and
                artifact['protocol_sha256']==sha(paths['protocol']), 'Expanded gate identity mismatch')
        require(artifact['selection']==selection and not artifact['failures'] and
                [(r['row'],r['candidate']) for r in artifact['records']]==expected and
                all(not r.get('errors') for r in artifact['records']), 'Incomplete/failed expanded gate')
    require(client['order_check'] is False and order['order_check'] is True and
            client['oracle_sha256']==order['oracle_sha256']==sha(paths['oracle']) and
            [r['row'] for r in client['predictions']]==selection, 'Expanded gate order/oracle mismatch')
    runtime=read(runtime_path)
    require(oracle['server_model_settings']==previous_oracle['server_model_settings'],
            'Expanded direct model settings differ from validated cold runtime')
    require(oracle['bos_id']==previous_oracle['bos_id'] and oracle['eos_id']==previous_oracle['eos_id'],
            'Expanded runtime BOS/EOS identity changed')
    required_runtime={str(Path(p).resolve()):h for p,h in runtime['files'].items()
                      if p!=oracle['server_model_settings']['model']}
    require(oracle['imported_runtime_files']==required_runtime,
            'Expanded direct imported runtime mismatch')
    verify_files(oracle['imported_runtime_files'])
    refs={(r['row'],r['candidate']):r for r in oracle['records']}
    for ref in refs.values():
        row=rows[ref['row']]
        ids=row['model_token_ids'][ref['candidate']]
        require(ref['model_ids']==ids and oracle['bos_id']==ids[0] and
                len(ref['supplied_logprobs'])==len(ids)-1 and
                len(ref['echo_strings'])==len(ids), 'Expanded direct token alignment mismatch')
        require(type(ref['generated_id']) is int and all(type(x) in (int,float) and math.isfinite(x)
                for x in ref['supplied_logprobs']+[ref['generated_logprob']]),'Nonfinite direct gate')
        if ref['row']==selection[0]:
            require('repeat_max_logprob_error' in ref,'Missing repeated-forward gate')
        if 'repeat_max_logprob_error' in ref:
            require(math.isfinite(ref['repeat_max_logprob_error']) and
                    ref['repeat_max_logprob_error']<=TOKEN_ATOL,'Direct repeat drift')
    for artifact in (client,order):
        require(all(artifact[k]==previous_gate[k] for k in
                    ('versions','tokenizer_files','source_files')), 'Expanded client/source identity mismatch')
        verify_files(artifact['source_files'])
        for rec in artifact['records']:
            ref=refs[rec['row'],rec['candidate']]
            row=rows[rec['row']]
            n=len(ref['model_ids'])-1
            context=len(row['wire_context_ids'])
            payload=rec['payload']
            require(payload==dict(model='t1-validation',prompt=row['prompt']+row['candidates'][rec['candidate']],
                    temperature=0,max_tokens=1,echo=True,logprobs=1,seed=1234),'Wrong expanded HTTP payload')
            response=rec['response']
            logs=response['choices'][0]['logprobs']
            require(logs['tokens']==ref['echo_strings'] and all(len(logs[k])==n+1 for k in
                    ('tokens','token_logprobs','top_logprobs','text_offset')) and
                    response['usage']['prompt_tokens']==n+1 and response['usage']['completion_tokens']==1,
                    'Expanded echo counts/strings/BOS/suffix mismatch')
            supplied=logs['token_logprobs']
            require(supplied[0] is None and all(type(x) in (int,float) and math.isfinite(x) for x in supplied[1:]),
                    'Nonfinite/missing expanded echo probabilities')
            observed=supplied[context:-1]
            direct=ref['supplied_logprobs'][context:]
            require(len(observed)==len(direct)==1,'Expanded continuation boundary mismatch')
            parsed=rec['parsed'][0]
            require(type(parsed) in (int,float) and math.isfinite(parsed) and
                    abs(parsed-math.fsum(observed))<=1e-8 and
                    abs(parsed-math.fsum(direct))<=SUM_ATOL and
                    abs(observed[0]-direct[0])<=TOKEN_ATOL and
                    all(abs(supplied[i]-ref['supplied_logprobs'][i])<=TOKEN_ATOL for i in range(1,n)) and
                    abs(supplied[-1]-ref['generated_logprob'])<=TOKEN_ATOL,
                    'Expanded raw numerical probability/parser gate failed')
            require(rec['direct_sum']==math.fsum(direct),'Expanded stored direct sum mismatch')
        require([p['row'] for p in artifact['predictions']]==selection,'Expanded predictions incomplete')
        for ri in selection:
            scores=[next(r for r in artifact['records'] if (r['row'],r['candidate'])==(ri,c))['parsed'][0] for c in range(4)]
            direct=[math.fsum(refs[ri,c]['supplied_logprobs'][len(rows[ri]['wire_context_ids']):]) for c in range(4)]
            require(max(range(4),key=scores.__getitem__)==max(range(4),key=direct.__getitem__),
                    'Expanded direct/client argmax inversion')
            def prediction(values):
                order=sorted(range(4),key=lambda i:-values[i])
                return dict(prediction=order[0],margin=values[order[0]]-values[order[1]])
            d,c=prediction(direct),prediction(scores)
            expected=dict(row=ri,direct=d,client=c,inversion=False,tie_sensitive=d['margin']<=2*SUM_ATOL)
            require(next(p for p in artifact['predictions'] if p['row']==ri)==expected,
                    'Expanded stored prediction/margin differs from raw evidence')
    return {n:sha(p) for n,p in paths.items()}


def load_shards(directory, rows, arm, complete=False):
    require(__debug__,'Scientific validators require Python without -O')
    directory = Path(directory)
    expected = expected_shards(rows)
    require(not list(directory.glob('*.tmp')), 'Interrupted shard: preserve and inspect')
    present = {p.name for p in directory.glob('*.json')}
    require(present <= set(expected) | {'identity.json'}, 'Unexpected shard files')
    if complete:
        require(present == set(expected) | {'identity.json'}, 'Incomplete T1 shards')
    records, hashes = [], {}
    for name, wanted in expected.items():
        path = directory/name
        if path.exists():
            records.extend(validate(read(path), wanted, arm))
            hashes[name] = sha(path)
    return records, hashes


def a3_paths(record):
    root = Path(record['runtime_repository'])
    return {arm: dict(directory=info['output_directory'], runtime=info['runtime_manifest'],
            validation=info['validation'], oracle=info['oracle'],
            order_validation=info['order_validation'],
            validator_script=str(root/'setup/validate_a3_cold.py'),
            protocol=str(root/'docs/a3-fast-validation.md'))
            for arm, info in record['arms'].items()}


def verified_a3(lock_path, record_path):
    require(sha(lock_path) == LOCK, 'A3 lock changed')
    record = read(record_path)
    # Completed evidence is authoritative; historical process/decision fields
    # are deliberately not interpreted as current operational state.
    verify_files(record['frozen_source_files'])
    cells, evidence = load_evidence(lock_path, a3_paths(record))
    return cells, evidence


def overlap_check(records, cells, arm):
    old = {(language, r['source'], r['question']): r['rotations'][0]
           for language in LANGUAGES for r in cells[arm,'plain-letter',language]}
    comparisons, inversions = [], []
    for row in records:
        if row['index'] >= 100:
            continue
        before = old[row['language'], row['source'], row['question']]
        after = row['scores']
        require(all(math.isfinite(x) for x in before+after), 'Nonfinite overlap scores')
        deltas = [b-a for a,b in zip(before,after,strict=True)]
        token_ok = all(abs(x) <= TOKEN_ATOL for x in deltas)
        sum_ok = all(abs(x) <= SUM_ATOL for x in deltas)
        entry = dict(language=row['language'], index=row['index'], source=row['source'],
            question=row['question'], a3_scores=before, t1_scores=after, deltas=deltas,
            token_pass=token_ok, sum_pass=sum_ok)
        p0,p1 = [max(range(4), key=s.__getitem__) for s in (before,after)]
        entry.update(a3_prediction=p0,t1_prediction=p1)
        if p0 != p1:
            inversions.append(entry)
        comparisons.append(entry)
    return dict(comparisons=comparisons, inversions=inversions,
        failures=[r for r in comparisons if not r['token_pass'] or not r['sum_pass']],
        interpretation='Intersection of one-token 0.0002 and summed 0.001 absolute limits; inversions retained for review')


def run_identity(lock_path,readiness_path,token_check_path,a3_lock_path,a3_record_path,
                 tokenizer_path,arm,base_url,expanded_gate=None):
    """Compute current identity offline; no endpoint request or output mutation."""
    require(__debug__,'Scientific validators require Python without -O')
    import importlib.metadata
    import inspect
    from lm_eval import evaluator
    from lm_eval.models.openai_completions import LocalCompletionsAPI
    from lm_eval.api.task import ConfigurableTask
    from lm_eval.api.model import TemplateLM
    import lm_eval.models.api_models as api_base
    from transformers import AutoTokenizer
    require(arm in ARMS,'Unknown arm')
    lock,ready,tokens=map(read,(lock_path,readiness_path,token_check_path))
    rows=validate_lock(lock)
    compare_a3_requests(rows,read(a3_lock_path))
    original_path=lock['provenance']['original_lock_path']
    require(sha(original_path)==lock['provenance']['original_lock_sha256']==
            read(a3_lock_path)['provenance']['original_lock_sha256'],'Original authority identity mismatch')
    compare_original_requests(rows,read(original_path))
    require(ready['lock_sha256']==tokens['lock_sha256']==sha(lock_path) and
            ready['provenance']==lock['provenance'] and ready['continuation_tokens']==1,
            'Readiness/token lock mismatch')
    verify_files(lock['provenance']['files'])
    verify_files(tokens['files'])
    require(tokens['contexts']==900 and tokens['candidates']==3600 and not tokens['failures'],
            'Incomplete/failed vocabulary check')
    cells,a3_evidence=verified_a3(a3_lock_path,a3_record_path)
    paths=a3_paths(read(a3_record_path))[arm]
    runtime=read(paths['runtime'])
    previous=read(Path(paths['directory'])/'identity.json')
    require(tokens['model']==previous['endpoint_models'][0] and
            all(tokens['files'].get(f)==h for f,h in runtime['files'].items()
                if f in tokens['files']), 'Vocab/runtime artifact mismatch')
    require(tokens['runtime_sha256']==sha(paths['runtime']), 'Vocab/runtime manifest mismatch')
    require(tokens['files'][tokens['model']]==runtime['files'][tokens['model']],
            'Wrong vocabulary model artifact')
    tokenizer_path=Path(tokenizer_path)
    tokenfiles={n:sha(tokenizer_path/n) for n in previous['tokenizer']}
    require(tokenfiles==previous['tokenizer']==lock['provenance']['tokenizer_files'],
            'Tokenizer identity mismatch')
    versions={n:importlib.metadata.version(n) for n in previous['versions']}
    require(versions==previous['versions'],'Client package version mismatch')
    # Frozen A3 scoring modules must still be exact; new orchestrator is added
    # separately, never substituted for a model/scorer implementation.
    verify_files(previous['files'])
    tokenizer=AutoTokenizer.from_pretrained(tokenizer_path,local_files_only=True)
    code=[__file__,Path(__file__).with_name('run_t1_baselines.py'),
          inspect.getfile(LocalCompletionsAPI),inspect.getfile(ConfigurableTask),
          inspect.getfile(TemplateLM),api_base.__file__,evaluator.__file__,inspect.getfile(task_for),
          inspect.getfile(type(tokenizer))]
    known_sources=previous['files']|read(paths['validation'])['source_files']
    for actual in code[2:]:
        require(any(Path(p).resolve()==Path(actual).resolve() and h==sha(actual)
                    for p,h in known_sources.items()),
                f'Imported scorer module differs from frozen A3: {actual}')
    model_args=dict(previous['model_args'])
    model_args.update(base_url=base_url,tokenizer=str(tokenizer_path))
    gate_hashes=None
    if expanded_gate is not None:
        gate_hashes=verify_expanded_gate(lock_path,paths['runtime'],expanded_gate,
            read(paths['validation']),read(paths['oracle']))
        client=read(expanded_gate['validation'])
        require(client['versions']==versions and client['tokenizer_files']==tokenfiles,
                'Expanded gate client identity mismatch')
        verify_files(client['source_files'])
    identity=dict(schema='t1-cold-original-order-v1',arm=arm,lock_sha256=sha(lock_path),
        readiness_sha256=sha(readiness_path),token_check_sha256=sha(token_check_path),
        a3_record_sha256=sha(a3_record_path),a3_evidence=a3_evidence,
        runtime_sha256=sha(paths['runtime']),model_args=model_args,
        endpoint_models=previous['endpoint_models'],versions=versions,tokenizer=tokenfiles,
        files={str(Path(f).resolve()):sha(f) for f in code},
        scorer=previous['scorer'],expanded_gate_paths=expanded_gate,expanded_gate_sha256=gate_hashes)
    return identity,rows,cells,runtime


def verify_run_identity(lock_path,readiness_path,token_check_path,a3_lock_path,a3_record_path,
                        tokenizer_path,directory,arm,base_url,complete=False,expanded_gate=None):
    """Validate saved or proposed identity and every present shard offline."""
    marker=Path(directory)/'identity.json'
    saved=read(marker) if marker.exists() else None
    if saved is not None and expanded_gate is None:
        expanded_gate=saved['expanded_gate_paths']
    identity,rows,cells,runtime=run_identity(lock_path,readiness_path,token_check_path,
        a3_lock_path,a3_record_path,tokenizer_path,arm,base_url,expanded_gate)
    if saved is not None:
        require(saved==identity,'T1 checkpoint identity differs')
        require(identity['expanded_gate_sha256'] is not None,'Saved scores require expanded live gate')
    else:
        require(not list(Path(directory).glob('*.json')),'Unidentified existing shards')
    records,hashes=load_shards(directory,rows,arm,complete)
    overlap=overlap_check(records,cells,arm)
    require(not overlap['failures'],'T1/A3 stricter-intersection overlap failed; preserve evidence')
    # A prediction inversion inside tolerance is not silently accepted as parity.
    require(not overlap['inversions'],'T1/A3 overlap prediction inversion: review before continuing')
    return records,dict(identity=identity,runtime=runtime,shard_sha256=hashes,
        overlap=overlap,complete=len(hashes)==180)
