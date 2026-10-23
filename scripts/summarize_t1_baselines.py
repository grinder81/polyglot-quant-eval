"""Complete original-order T1 reporting; no inference or partial-run estimates."""
from collections import defaultdict
import argparse
import hashlib
import inspect
import json
import math
from pathlib import Path
import random

from scripts.compare_expanded import compare_rows
from scripts.margin_flip_analysis import analyze as margin_analysis, load_pair as load_historical_pair, validate_scores
from scripts.margin_flip_analysis import read
from scripts.summarize_expanded_local import LANGS
from scripts.t1_baselines import ARMS, validate_lock, verify_run_identity


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalize(records):
    """Only call after runner validation; retain original-order candidate scores."""
    rows = []
    for record in records:
        require(record['variant'] == 'plain-letter' and record['shift'] == 0
                and record['target'] == record['original_target'], 'Not original-order plain-letter')
        require(record['choices'] == list('ABCD') and record['candidates'] == [' A',' B',' C',' D']
                and record['choice_character_lengths'] == [1]*4, 'Candidate contract changed')
        validate_scores(record['scores'], record['target'])
        require(isinstance(record['source'], str) and bool(record['source'].strip())
                and type(record['question']) in (str, int) and bool(str(record['question']).strip()),
                'Missing source/question identity')
        prediction = max(range(4), key=record['scores'].__getitem__)
        rows.append(dict(language=record['language'], source=record['source'],
            question=str(record['question']), target=record['target'], scores=record['scores'],
            prediction=prediction, correct=int(prediction == record['target'])))
    validate_rows(rows)
    return rows


def validate_rows(rows):
    index = {}
    for row in rows:
        require(isinstance(row['source'],str) and bool(row['source'].strip())
                and isinstance(row['question'],str) and bool(row['question'].strip()),
                'Missing normalized source/question identity')
        key = row['language'], row['source'], row['question']
        require(row['language'] in LANGS and key not in index, 'Invalid language or duplicate identity')
        validate_scores(row['scores'], row['target'])
        prediction = max(range(4), key=row['scores'].__getitem__)
        require(row['prediction'] == prediction and row['correct'] == int(prediction == row['target']),
                'Prediction/correctness mismatch')
        index[key] = row
    require(len(index) == 900 and all(sum(k[0] == lang for k in index) == 300 for lang in LANGS),
            'Exact three-language 300-question membership required')
    identities = [{(s,q) for l,s,q in index if l == lang} for lang in LANGS]
    require(all(group == identities[0] for group in identities), 'Unmatched translated identities')
    return index


def interval(values):
    values = sorted(values)
    return [values[max(0,int(.025*len(values))-1)], values[max(0,int(.975*len(values))-1)]]


ENDPOINTS = ('reference_accuracy','candidate_accuracy','changed_choices_rate',
             'regression_rate','improvement_rate','wrong_to_wrong_rate')


def paired_report(reference, candidate, replicates=10000):
    """Reuse verified paired deltas; add joint-source absolute/churn uncertainty.

    Names are generic so historical→fresh within-arm outcomes are not mislabeled
    as a compression comparison. Fractions, not percentage points, are serialized.
    """
    require(type(replicates) is int and replicates > 0, 'Positive bootstrap count required')
    ref, cand = validate_rows(reference), validate_rows(candidate)
    require(ref.keys() == cand.keys(), 'Unmatched paired identities')
    require(all(ref[k]['target'] == cand[k]['target'] for k in ref), 'Target mismatch')
    base = compare_rows(reference, candidate, replicates=replicates)
    keys = sorted((s,q) for l,s,q in ref if l == LANGS[0])
    clusters = defaultdict(list)
    for source, question in keys:
        features = []
        for lang in LANGS:
            a, b = ref[lang,source,question], cand[lang,source,question]
            changed = a['prediction'] != b['prediction']
            features.extend((a['correct'], b['correct'], int(changed),
                int(a['correct'] == 1 and b['correct'] == 0),
                int(a['correct'] == 0 and b['correct'] == 1),
                int(changed and a['correct'] == b['correct'] == 0)))
        clusters[source].append(features)
    aggregate = [(len(group), [sum(row[i] for row in group) for i in range(18)])
                 for group in clusters.values()]
    draws = [[] for _ in range(18)]
    rng = random.Random(42)
    for _ in range(replicates):
        sampled = rng.choices(aggregate, k=len(aggregate))
        count = sum(n for n,_ in sampled)
        totals = [sum(values[i] for _,values in sampled)/count for i in range(18)]
        for i,value in enumerate(totals):
            draws[i].append(value)
    results = {}
    for i,lang in enumerate(LANGS):
        old = base['languages'][lang]
        row = {key.replace('bf16_', 'reference_').replace('q4_', 'candidate_'):value
               for key,value in old.items() if key != 'accuracy_delta_q4_minus_bf16'}
        row['accuracy_delta_candidate_minus_reference'] = old['accuracy_delta_q4_minus_bf16']
        row['reference_accuracy'] = old['bf16_correct']/old['n']
        row['candidate_accuracy'] = old['q4_correct']/old['n']
        row['joint_source_95_intervals'] = {name:interval(draws[6*i+j]) for j,name in enumerate(ENDPOINTS)}
        # Preserve zero-count displayed positions explicitly.
        for name in ('reference_predicted_letters','candidate_predicted_letters','gold_letters'):
            row[name] = {letter:row[name].get(letter,0) for letter in 'ABCD'}
        results[lang] = row
    return dict(languages=results, source_clusters=len(clusters), bootstrap_seed=42,
        bootstrap_replicates=replicates, interpretation=base['interpretation'],
        uncertainty='Same source clusters jointly sampled across languages and paired arms; original order only')


def distribution(values):
    require(bool(values) and all(math.isfinite(x) for x in values), 'Nonfinite or empty delta distribution')
    ordered = sorted(values)
    return dict(n=len(ordered), min=ordered[0], max=ordered[-1], mean=math.fsum(ordered)/len(ordered),
        quantile_definition='nearest lower empirical order statistic at floor(p*(n-1))',
        **{f'p{int(p*100):02}':ordered[int(p*(len(ordered)-1))] for p in (.5,.9,.95,.99)})


def historical_comparison(historical, fresh, replicates=10000):
    """Observed per-arm runtime difference, not attribution to an individual patch."""
    old, new = validate_rows(historical), validate_rows(fresh)
    require(old.keys() == new.keys(), 'Historical/fresh membership mismatch')
    outcome = paired_report(historical, fresh, replicates)
    by_language = {}
    records = []
    for lang in LANGS:
        deltas, margins = [], []
        for key in sorted(k for k in old if k[0] == lang):
            a,b = old[key],new[key]
            require(a['target'] == b['target'], 'Historical/fresh target mismatch')
            candidate_delta = [y-x for x,y in zip(a['scores'],b['scores'])]
            margin = lambda scores: sorted(scores,reverse=True)[0]-sorted(scores,reverse=True)[1]
            old_margin, new_margin = margin(a['scores']),margin(b['scores'])
            deltas.extend(candidate_delta)
            margins.append(new_margin-old_margin)
            records.append(dict(language=lang,source=key[1],question=key[2],target=a['target'],
                historical_prediction=a['prediction'],fresh_prediction=b['prediction'],
                candidate_deltas_nats=candidate_delta,historical_margin_nats=old_margin,
                fresh_margin_nats=new_margin,margin_delta_nats=new_margin-old_margin))
        by_language[lang] = dict(signed_candidate_delta_nats=distribution(deltas),
            absolute_candidate_delta_nats=distribution([abs(x) for x in deltas]),
            margin_delta_nats=distribution(margins))
    for lang in LANGS:
        by_language[lang]['mean_candidate_delta_minus_english_nats_point_only'] = (
            by_language[lang]['signed_candidate_delta_nats']['mean']
            - by_language[LANGS[0]]['signed_candidate_delta_nats']['mean'])
        by_language[lang]['mean_margin_delta_minus_english_nats_point_only'] = (
            by_language[lang]['margin_delta_nats']['mean']
            - by_language[LANGS[0]]['margin_delta_nats']['mean'])
    return dict(outcomes_historical_to_fresh=outcome, descriptive_distributions=by_language,
        records=records, interpretation='Combined recorded runtime difference on identical requests/models; '
        'observed distributions are not universal error bounds, new-run tolerances, or causal patch attribution')


def fresh_margin_report(reference, candidate):
    """PR40 core on actual validated T1 records, not its historical-only loader."""
    def keyed(rows):
        return {('belebele_'+r['language'],r['source'],r['question']):(r['scores'],r['target']) for r in rows}
    validate_rows(reference)
    validate_rows(candidate)
    return dict(input_schema='validated-t1-original-order', results=margin_analysis(keyed(reference),keyed(candidate)),
        interpretation='Fresh T1 reference top-two summed-letter margin versus paired Q4 flip; '
        'exploratory counts without source-cluster intervals or causal/language-adjusted inference')


def verify_historical_requests(fresh_lock_rows, historical_membership):
    """No intersection: require every original-order request/target to be identical."""
    require(len(historical_membership['items']) == 300
            and all(set(group) == set(LANGS) for group in historical_membership['items']),
            'Incomplete historical request membership')
    fresh = {(r['language'],r['source'],str(r['question'])):r for r in fresh_lock_rows}
    old = {(lang,r['source'],str(r['question'])):r
           for group in historical_membership['items'] for lang,r in group.items()}
    require(len(fresh_lock_rows) == len(fresh) == len(old) == 900 and fresh.keys() == old.keys(),
            'Historical/fresh request membership mismatch')
    for key,row in fresh.items():
        previous = old[key]
        candidate_hashes = [hashlib.sha256(c.encode('utf-8')).hexdigest() for c in row['candidates']]
        require(row['target'] == previous['target']
                and row['prompt_sha256'] == previous['prompt_sha256']
                and candidate_hashes == previous['candidate_sha256'],
                'Historical/fresh request or target changed')


def model_hash(runtime):
    command = runtime['server_command']
    require(command.count('--model') == 1, 'Expected one runtime model argument')
    return runtime['files'][command[command.index('--model')+1]]


def load_historical(reference_root, candidate_root, fresh_lock_rows, fresh_runtimes):
    """Reuse PR40 historical loader, then establish unchanged requests/model bytes."""
    reference, candidate, provenance = load_historical_pair(reference_root,candidate_root)
    rows = {}
    for arm,root,mapped in zip(('bf16-gguf','local-q4'),
                               (Path(reference_root),Path(candidate_root)),(reference,candidate)):
        verify_historical_requests(fresh_lock_rows,read(root/'sample-identities.json'))
        previous_runtime = read(root/f'{arm}-runtime.json')
        require(model_hash(previous_runtime) == model_hash(fresh_runtimes[arm]),
                'Historical/fresh model artifact changed')
        normalized = []
        for (task,source,question),(scores,target) in mapped.items():
            prediction = max(range(4),key=scores.__getitem__)
            normalized.append(dict(language=task.removeprefix('belebele_'),source=source,
                question=question,scores=scores,target=target,prediction=prediction,
                correct=int(prediction == target)))
        validate_rows(normalized)
        rows[arm] = normalized
    return rows, provenance


def validate_fresh_pair(provenance):
    """Same task/client/runtime settings; arm-specific model/gates remain pinned."""
    comparable = []
    for arm in ARMS:
        identity,runtime = provenance[arm]['identity'],provenance[arm]['runtime']
        require(identity['schema'] == 't1-cold-original-order-v1' and identity['arm'] == arm
                and identity['expanded_gate_sha256'] is not None, 'Incomplete fresh run identity')
        command = list(runtime['server_command'])
        require(command.count('--model') == 1, 'Expected one runtime model argument')
        i = command.index('--model')+1
        model = command[i]
        require(identity['endpoint_models'] == [model], 'Endpoint model identity mismatch')
        command[i] = '<model>'
        common = {k:v for k,v in runtime.items() if k not in ('arm','server_command','files','provenance')}
        common.update(command=command, files={p:h for p,h in runtime['files'].items() if p != model},
            provenance={k:v for k,v in runtime['provenance'].items() if k != 'original_runtime_sha256'})
        comparable.append(dict(runtime=common, client={key:identity[key] for key in (
            'schema','lock_sha256','readiness_sha256','a3_record_sha256','a3_evidence',
            'model_args','versions','tokenizer','files','scorer')}))
    require(comparable[0] == comparable[1], 'Fresh paired runtime/client/scoring settings differ')


def load_complete(lock_path,readiness_path,a3_lock_path,a3_record_path,tokenizer_path,
                  arm_inputs,base_url):
    """Only the actual T1 runner helper can validate the complete scientific input."""
    require(set(arm_inputs) == set(ARMS), 'Both fresh arms required')
    validate_lock(read(lock_path))
    fresh,provenance = {},{}
    for arm in ARMS:
        config = arm_inputs[arm]
        records,evidence = verify_run_identity(lock_path,readiness_path,config['token_check'],
            a3_lock_path,a3_record_path,tokenizer_path,config['directory'],arm,base_url,complete=True)
        require(evidence['complete'] and len(evidence['shard_sha256']) == 180 and len(records) == 900,
                'Complete 180-shard/900-question arm required')
        fresh[arm],provenance[arm] = normalize(records),evidence
    validate_fresh_pair(provenance)
    require(validate_rows(fresh[ARMS[0]]).keys() == validate_rows(fresh[ARMS[1]]).keys(),
            'Fresh membership mismatch')
    return fresh,provenance


def build_report(lock_path,readiness_path,a3_lock_path,a3_record_path,tokenizer_path,
                 arm_inputs,base_url,historical_reference,historical_candidate,replicates=10000):
    fresh,provenance = load_complete(lock_path,readiness_path,a3_lock_path,a3_record_path,
                                    tokenizer_path,arm_inputs,base_url)
    historical,historical_provenance = load_historical(historical_reference,historical_candidate,
        read(lock_path)['rows'],{arm:provenance[arm]['runtime'] for arm in ARMS})
    return dict(schema='t1-complete-report-v1',
        analysis_source_sha256={str(Path(path).resolve()):hashlib.sha256(Path(path).read_bytes()).hexdigest()
            for path in (str(Path(__file__).resolve()),inspect.getfile(compare_rows),
                         inspect.getfile(margin_analysis),inspect.getfile(verify_run_identity))},
        scope='Fresh original-order BF16 GGUF versus local Q4_K_M development comparison; '
              'canonical original BF16 vLLM reference remains separate; no generation/device/holdout claim',
        scoring='Plain-letter summed likelihood, first displayed maximum on exact tie; '
                'acc_norm identical for one-character choices; original order, not rotation mean',
        provenance=dict(fresh=provenance,historical_A1=historical_provenance),
        fresh_paired_GGUF=paired_report(fresh[ARMS[0]],fresh[ARMS[1]],replicates),
        historical_to_fresh_by_arm={arm:historical_comparison(historical[arm],fresh[arm],replicates)
                                    for arm in ARMS},
        fresh_margin=fresh_margin_report(fresh[ARMS[0]],fresh[ARMS[1]]),
        fresh_rows=fresh)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('lock','readiness','a3-lock','a3-record','tokenizer','historical-reference',
                 'historical-candidate','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    for prefix in ('bf16','q4'):
        for name in ('directory','token-check'):
            parser.add_argument('--'+prefix+'-'+name,type=Path,required=True)
    parser.add_argument('--base-url',required=True,help='exact model_args base URL recorded in both run identities')
    args = parser.parse_args()
    require(not args.output.exists(), 'Report output must be new')
    report = build_report(args.lock,args.readiness,args.a3_lock,args.a3_record,args.tokenizer,
        dict(zip(ARMS,(dict(directory=args.bf16_directory,token_check=args.bf16_token_check),
                       dict(directory=args.q4_directory,token_check=args.q4_token_check)))),
        args.base_url,args.historical_reference,args.historical_candidate)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False)
        stream.write('\n')


if __name__ == '__main__':
    main()
