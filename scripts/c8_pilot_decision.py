"""Freeze one discovery nominee before reading independent C8 confirmation."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean

LANGS=('eng_Latn','ben_Beng','hin_Deva','pooled')
EPS=1e-5


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def table(report,plan,repeats):
    if report['identity']['plan_sha256']!=plan['_sha256'] or report['identity']['mode']!='diagnostics' or report['identity']['repetitions']!=repeats:
        raise ValueError('Wrong discovery/confirmation identity')
    expected={entry['tensor']+'::'+entry['native_type'] for entry in plan['diagnostics']}
    cases={entry['case']['label']:entry for entry in report['cases']}
    if cases.keys()!=expected or len(cases)!=len(report['cases']):
        raise ValueError('Incomplete diagnostic cost table')
    result={}
    for label,case in cases.items():
        rows=case['records']
        wanted={(r,i,l) for r in repeats for i in range(3) for l in LANGS[:3]}
        if {(x['repeat'],x['index'],x['language']) for x in rows}!=wanted or len(rows)!=len(wanted):
            raise ValueError('Incomplete source/language repetitions')
        if any(type(x['mean_kl_nats']) not in (int,float) or not math.isfinite(x['mean_kl_nats']) or x['mean_kl_nats']<0 or x['tokens']!=64 for x in rows):
            raise ValueError('Invalid per-example KL')
        if any(x['source']!=plan['probe_sources'][str(x['repeat'])][x['index']] for x in rows):
            raise ValueError('Frozen probe source identity differs')
        for rep in repeats:
            for lang in LANGS:
                selected=[row['mean_kl_nats'] for row in rows if row['repeat']==rep and
                    (row['language']==lang if lang!='pooled' else row['language']==LANGS[row['index']])]
                if len(selected)!=3:
                    raise ValueError('Mismatched evidence budget')
                result[rep,lang,label]=mean(selected)
    return result


def nominate(plan,costs):
    low,high=plan['formats']['lower'],plan['formats']['higher']
    candidates=[]
    for pair in plan['pairs']:
        first,second=pair['first'],pair['second']
        margins={str(rep):{lang:(costs[rep,lang,first+'::'+low]-costs[rep,lang,first+'::'+high])-
            (costs[rep,lang,second+'::'+low]-costs[rep,lang,second+'::'+high]) for lang in LANGS} for rep in (1,2)}
        en=[margins[str(r)]['eng_Latn'] for r in (1,2)]
        bn=[margins[str(r)]['ben_Beng'] for r in (1,2)]
        qualifies=pair['eligible'] and min(map(abs,en+bn))>EPS and en[0]*en[1]>0 and bn[0]*bn[1]>0 and en[0]*bn[0]<0
        candidates.append(dict(pair=pair,margins=margins,nominatable=bool(qualifies)))
    nominee=next((row for row in candidates if row['nominatable']),None)
    return dict(pair=nominee['pair'] if nominee else None,
        signs={lang:1 if nominee['margins']['1'][lang]>0 else -1 for lang in ('eng_Latn','ben_Beng')} if nominee else None,
        candidates=candidates,epsilon_nats=EPS,
        interpretation='Discovery screen only; first qualifying feasible pair. No repetition3data used. None means inconclusive, not language equivalence.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--discovery',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    plan=read(a.plan)|{'_sha256':sha(a.plan)}
    decision=nominate(plan,table(read(a.discovery),plan,[1,2]))
    decision.update(plan_sha256=sha(a.plan),discovery_report_sha256=sha(a.discovery),
        implementation_sha256=sha(__file__),schema='c8-discovery-nomination-v1')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x') as stream:
        json.dump(decision,stream,indent=2,allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(pair=decision['pair'],signs=decision['signs'])),flush=True)


if __name__=='__main__':
    main()
