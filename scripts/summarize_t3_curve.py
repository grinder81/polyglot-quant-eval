"""Report complete new precision arms using verified T1 source-paired statistics."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from scripts.run_t3_baselines import identity
from scripts.t1_baselines import load_shards
from scripts.summarize_t1_baselines import paired_report,normalize,historical_comparison
from scripts.plan_pilot_precision import REPORT_SHA


def read(path):
    return json.loads(Path(path).read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--t1-report',type=Path,required=True)
    p.add_argument('--arm',action='append',nargs=2,metavar=('CONFIG','DIRECTORY'),required=True)
    p.add_argument('--fidelity',action='append',nargs=2,metavar=('ARM','DIRECTORY'),default=[])
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--final',action='store_true')
    a=p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    payload=gzip.decompress(a.t1_report.read_bytes())
    if hashlib.sha256(payload).hexdigest()!=REPORT_SHA:
        raise ValueError('Wrong T1 reference report')
    t1=json.loads(payload)
    references=t1['fresh_rows']
    reference=references['bf16-gguf']
    q4=references['local-q4']
    evidence={}
    outcomes={}
    for config,directory in a.arm:
        frozen,rows=identity(config)
        directory=Path(directory)
        if read(directory/'identity.json')!=frozen:
            raise ValueError('Saved arm identity differs')
        records,hashes=load_shards(directory,rows,frozen['arm'],complete=True)
        candidate=normalize(records)
        paths=read(config)
        build=read(paths['build'])
        name=frozen['arm']
        if name in evidence:
            raise ValueError('Duplicate arm')
        evidence[name]=dict(identity=frozen,config=str(config),directory=str(directory),
            shard_sha256=hashes,build=build,records=candidate)
        score_delta=historical_comparison(reference,candidate,replicates=10000)
        outcomes[name]=dict(vs_bf16=paired_report(reference,candidate,replicates=10000),
            vs_local_q4=paired_report(q4,candidate,replicates=10000),
            descriptive_score_margin_deltas_vs_bf16=score_delta['descriptive_distributions'])
    fidelity={}
    for name,directory in a.fidelity:
        manifest=read(Path(directory)/'manifest.json')
        if manifest['questions']!=900 or 'languages' not in manifest:
            raise ValueError('Incomplete fidelity arm')
        expected=evidence[name]['build']['output_sha256'] if name in evidence else (
            '5823bd1e52be1027a7ba6f31b43edfd40ae1766020cddec967f0d76618948290' if name=='local-q4' else None)
        if manifest['identity']['model_sha256']!=expected:
            raise ValueError('Fidelity/model mismatch')
        fidelity[name]=dict(directory=str(directory),manifest_sha256=hashlib.sha256((Path(directory)/'manifest.json').read_bytes()).hexdigest(),manifest=manifest)
    predictions={}
    if 'diag-q3km' in outcomes:
        predictions['P1']={l:outcomes['diag-q3km']['vs_bf16']['languages'][l]['changed_choices']>
            t1['fresh_paired_GGUF']['languages'][l]['changed_choices'] for l in ('eng_Latn','ben_Beng','hin_Deva')}
    if 'diag-q6k' in outcomes:
        predictions['P3']={l:outcomes['diag-q6k']['vs_bf16']['languages'][l]['changed_choices']<
            t1['fresh_paired_GGUF']['languages'][l]['changed_choices'] for l in ('eng_Latn','ben_Beng','hin_Deva')}
    point=None
    if a.final:
        if not all(name in fidelity for name in evidence) or 'local-q4' not in fidelity:
            raise ValueError('Final operating-point report needs complete fidelity endpoints')
        options=[dict(arm=name,bytes=evidence[name]['build']['output_bytes'],
            english_correct=outcomes[name]['vs_bf16']['languages']['eng_Latn']['candidate_correct']) for name in evidence]
        options.append(dict(arm='local-q4',bytes=2143976960,english_correct=229))
        eligible=[row for row in options if row['english_correct']>=221 and row['bytes']<=2_200_000_000]
        point=min(eligible,key=lambda row:(row['bytes'],row['arm']))
    result=dict(schema='t3-complete-curve-v1',t1_report_sha256=REPORT_SHA,
        implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_clusters=250,questions_per_language=300,bootstrap_replicates=10000,bootstrap_seed=42,
        evidence=evidence,outcomes=outcomes,fidelity=fidelity,predictions=predictions,
        final_operating_point=point,
        interpretation='Development precision curve; no allocation, generation, phone or holdout result. BF16 GGUF is separate from original canonical BF16 vLLM.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(output=str(a.output),arms=list(evidence),operating_point=point)),flush=True)


if __name__=='__main__':
    main()
