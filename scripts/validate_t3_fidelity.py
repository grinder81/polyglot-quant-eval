"""Validate complete per-question KL evidence before reporting its aggregates."""
import hashlib
import json
import math
from pathlib import Path
import statistics

REFERENCE_SHA='9964b004736d733b872e3a4f2e294631f7b4744894d4626b60a928d2f193aa6e'
CORE_SHA='c1e2b8bddb935aaca6e3a564c55149029e8ba36ea80b60de69998923b9d44eba'
MATH_SHA='0348ebb38afb6911d2ea8ed3af95fdf84d054d5ab7fccf63485920cdf5f3ca0a'
WRAPPER_SHA='2c408498ce89673937ea62486bf02d9eb8ecc87cc5132f6426a6ec57ba2d0e3d'
VERIFICATION_SHA='bdbbd7b63df3ab5826157991981bd6ed208493f9c3662dcef74eddad7fb43562'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def close(a,b):
    return math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-14)


def quantile(values,q):
    ordered=sorted(values)
    position=(len(ordered)-1)*q
    lower=math.floor(position)
    upper=math.ceil(position)
    return ordered[lower]+(ordered[upper]-ordered[lower])*(position-lower)


def validate(directory,rows,model_sha,lock_sha,runtime_sha=None):
    directory=Path(directory)
    path=directory/'manifest.json'
    manifest=read(path)
    identity=manifest['identity']
    if (manifest['questions']!=900 or len(rows)!=900 or identity['mode']!='compare'
            or identity['model_sha256']!=model_sha or identity['lock_sha256']!=lock_sha
            or identity['implementation_sha256']!=CORE_SHA or identity['math_module_sha256']!=MATH_SHA
            or identity['reference_manifest_sha256']!=REFERENCE_SHA):
        raise ValueError('Wrong fidelity lineage or incomplete arm')
    if runtime_sha is not None and identity['runtime_sha256']!=runtime_sha:
        raise ValueError('Fidelity runtime differs from scored arm')
    expected={f"{r['language']}-{r['index']:03}.json":r for r in rows}
    if len(expected)!=900 or manifest['per_question_files'].keys()!=expected.keys():
        raise ValueError('Fidelity question membership differs')
    records=[]
    for name,row in expected.items():
        file=directory/name
        if sha(file)!=manifest['per_question_files'][name]:
            raise ValueError('Fidelity question hash differs')
        record=read(file)
        if any(record[k]!=row[k] for k in ('language','index','source','question','prompt_sha256')):
            raise ValueError('Fidelity source or prompt differs')
        values=record['token_kl']
        if record['tokens']!=len(row['model_context_ids'])-1 or len(values)!=record['tokens'] or not values:
            raise ValueError('Fidelity token coverage differs')
        if any(not math.isfinite(x) or x<0 for x in values) or not close(statistics.mean(values),record['mean_kl_nats']):
            raise ValueError('Fidelity mean does not match finite token values')
        if not 0<=record['top1_agreement']<=1 or not 0<=record.get('first_chunk_cpu_oracle_max_error',0)<=1e-10:
            raise ValueError('Invalid fidelity agreement or CPU oracle')
        records.append(record)
    if sum(r['tokens'] for r in records)!=manifest['tokens']:
        raise ValueError('Fidelity aggregate token count differs')
    for language in ('eng_Latn','ben_Beng','hin_Deva'):
        subset=[r for r in records if r['language']==language]
        values=[r['mean_kl_nats'] for r in subset]
        actual=dict(mean_kl_nats=statistics.mean(values),p50_question_kl=quantile(values,.5),
            p95_question_kl=quantile(values,.95),mean_question_top1_agreement=statistics.mean(r['top1_agreement'] for r in subset))
        if len(subset)!=300 or any(not close(value,manifest['languages'][language][key]) for key,value in actual.items()):
            raise ValueError('Fidelity language aggregates differ')
    receipt=None
    if identity['backend']=='torch2.13-float64':
        receipt=read(directory.parent/(directory.name+'-verified.json'))
        if (receipt['status']!='passed' or receipt['manifest_sha256']!=sha(path)
                or receipt['runtime_sha256']!=identity['runtime_sha256']
                or receipt['reference_manifest_sha256']!=REFERENCE_SHA
                or receipt['wrapper_sha256']!=WRAPPER_SHA or receipt['verification_sha256']!=VERIFICATION_SHA
                or receipt['native_backend_initialized_before_torch'] is not True or receipt['torch_cpu_threads']!=1):
            raise ValueError('Missing or inconsistent verified native-first execution')
        if any('first_chunk_cpu_oracle_max_error' not in r for r in records):
            raise ValueError('Missing per-question CPU oracle')
    elif identity['backend']!='numpy-float64':
        raise ValueError('Unrecognized fidelity backend')
    return dict(directory=str(directory),manifest_sha256=sha(path),manifest=manifest,verified_execution=receipt,
        validation='All900question hashes, prompt/source/token membership, token KL means and language aggregates verified')
