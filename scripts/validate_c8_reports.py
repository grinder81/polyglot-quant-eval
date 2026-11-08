"""Require successful bounded operations and original evidence behind C8 reports."""
import math
from pathlib import Path
from statistics import mean

from scripts.c8_pilot_decision import read,sha


def operation(plan,identity,category):
    ledger=read(Path(plan['artifact_workspace'])/'resource-ledger.json')
    if ledger['plan_sha256']!=plan['_sha256'] or any(row['status']=='active' for row in ledger['operations']):
        raise ValueError('Wrong or active C8 budget ledger')
    for kind in ('native','proxy'):
        rows=[row for row in ledger['operations'] if row['category']==kind]
        if any(not math.isfinite(row['seconds']) or row['seconds']<0 for row in rows) or sum(row['seconds'] for row in rows)>plan['cap'][kind+'_minutes']*60:
            raise ValueError('Cumulative C8 budget exceeded')
    matches=[row for row in ledger['operations'] if row['id']==identity['budget_operation_id']]
    if len(matches)!=1 or matches[0]['status']!='passed' or matches[0]['category']!=category:
        raise ValueError('C8 report operation did not pass its final budget check')
    if matches[0]['artifact_bytes']>plan['cap']['local_artifact_bytes']:
        raise ValueError('C8 report exceeded the artifact cap')


def identity(path,plan,category,repeats,nomination_sha):
    path=Path(path)
    report=read(path)
    value=report['identity']
    if read(path.parent/'identity.json')!=value or value['plan_sha256']!=plan['_sha256'] or value['repetitions']!=repeats or value.get('nomination_sha256')!=nomination_sha:
        raise ValueError('C8 report identity or frozen nomination differs')
    operation(plan,value,category)
    return report


def native(path,plan,repeats,mode,nomination_sha=None,reference=None):
    path=Path(path)
    report=identity(path,plan,'native',repeats,nomination_sha)
    value=report['identity']
    if value['mode']!=mode or len(report['cases'])!=len(value['cases']):
        raise ValueError('Native C8 case identity differs')
    for index,case in enumerate(report['cases']):
        if (case!=read(path.parent/f'case-{index:02}.json') or case['case']!=value['cases'][index]
                or case['identity_sha256']!=sha(path.parent/'identity.json')):
            raise ValueError('Native C8 case evidence differs')
        wanted={(rep,i,l) for rep in repeats for i in range(3) for l in ('eng_Latn','ben_Beng','hin_Deva')}
        rows=case['records']
        if len(rows)!=len(wanted) or {(r['repeat'],r['index'],r['language']) for r in rows}!=wanted:
            raise ValueError('Native C8 source coverage differs')
        for row in rows:
            if row['source']!=plan['probe_sources'][str(row['repeat'])][row['index']] or row['tokens']!=64:
                raise ValueError('Native C8 source or token evidence differs')
            if mode!='reference':
                tokens=row['token_kl']
                if (len(tokens)!=64 or any(not math.isfinite(x) or x<0 for x in tokens)
                        or not math.isclose(mean(tokens),row['mean_kl_nats'],rel_tol=1e-12,abs_tol=1e-14)):
                    raise ValueError('Native C8 token KL differs')
    if mode=='reference':
        if len(value['cases'])!=1 or value['cases'][0]['sha256']!=plan['source_sha256']:
            raise ValueError('Wrong native BF16 reference')
    else:
        if reference is None:
            raise ValueError('Native C8 report requires its reference lineage')
        prior=read(reference)['identity']
        if value['reference_report_sha256']!=sha(reference) or any(value[k]!=prior[k] for k in ('runtime_sha256','imported_runtime','implementation_sha256','math_sha256')):
            raise ValueError('Native C8 reference extraction lineage differs')
    return report


def proxy(path,plan,repeats,nomination_sha=None):
    path=Path(path)
    report=identity(path,plan,'proxy',repeats,nomination_sha)
    for row in report['records']:
        if read(path.parent/f"r{row['repeat']}-{row['index']}-{row['language']}.json")!=row:
            raise ValueError('Proxy C8 per-example evidence differs')
    return report
