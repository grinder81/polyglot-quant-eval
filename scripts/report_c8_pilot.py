"""Reconstruct the bounded investment decision and descriptive proxy agreement."""
import argparse
import json
import math
from pathlib import Path
from statistics import mean

from scripts.c8_pilot_decision import EPS,LANGS,nominate,read,sha,table


def ranks(values):
    order=sorted(range(len(values)),key=values.__getitem__)
    result=[0.]*len(values)
    start=0
    while start<len(order):
        end=start+1
        while end<len(order) and values[order[end]]==values[order[start]]:
            end+=1
        for index in order[start:end]:
            result[index]=(start+end-1)/2
        start=end
    return result


def spearman(left,right):
    a,b=ranks(left),ranks(right)
    ma,mb=mean(a),mean(b)
    numerator=math.fsum((x-ma)*(y-mb) for x,y in zip(a,b,strict=True))
    denominator=math.sqrt(math.fsum((x-ma)**2 for x in a)*math.fsum((y-mb)**2 for y in b))
    return numerator/denominator if denominator else None


def proxies(report,plan,repeats):
    if report['identity']['plan_sha256']!=plan['_sha256'] or report['identity']['repetitions']!=repeats:
        raise ValueError('Wrong proxy identity')
    records=report['records']
    expected={(rep,i,l) for rep in repeats for i in range(3) for l in LANGS[:3]}
    if len(records)!=len(expected) or {(r['repeat'],r['index'],r['language']) for r in records}!=expected:
        raise ValueError('Incomplete proxy source/language records')
    labels={e['tensor']+'::'+e['native_type'] for e in plan['diagnostics']}
    for row in records:
        if row['source']!=plan['construction_sources'][str(row['repeat'])][row['index']] or row['tokens']!=64:
            raise ValueError('Proxy construction source differs')
        if len(row['scores'])!=len(labels) or {s['tensor']+'::'+s['native_type'] for s in row['scores']}!=labels:
            raise ValueError('Incomplete proxy tensor/format scores')
        for score in row['scores']:
            if any(type(score[k]) not in (int,float) or not math.isfinite(score[k]) or score[k]<0 for k in ('fisher_score','activation_score')):
                raise ValueError('Invalid proxy score')
    result={}
    for rep in repeats:
        for lang in LANGS:
            rows=[r for r in records if r['repeat']==rep and (r['language']==lang if lang!='pooled' else r['language']==LANGS[r['index']])]
            if len(rows)!=3:
                raise ValueError('Proxy evidence budget differs')
            for label in labels:
                for metric in ('fisher_score','activation_score'):
                    result[rep,lang,label,metric]=mean(next(s[metric] for s in r['scores'] if s['tensor']+'::'+s['native_type']==label) for r in rows)
    return result


def confirmed_pair(report,plan,nomination,nomination_path):
    if report['identity']['mode']!='pair' or report['identity']['plan_sha256']!=plan['_sha256'] or report['identity']['repetitions']!=[3] or report['identity']['nomination_sha256']!=sha(nomination_path):
        raise ValueError('Confirmation does not bind the frozen nominee')
    cases={r['case']['label']:r for r in report['cases']}
    if cases.keys()!={'mapA','mapB'} or len(report['cases'])!=2:
        raise ValueError('Two complete confirmation maps required')
    if any(row['case']['bytes']!=nomination['pair']['map_a_bytes'] or row['case']['bytes']>plan['operating_point']['bytes'] for row in cases.values()):
        raise ValueError('Confirmation maps violate the matched-byte budget')
    measured={}
    for label,case in cases.items():
        rows=case['records']
        if len(rows)!=9 or {(r['repeat'],r['index'],r['language']) for r in rows}!={(3,i,l) for i in range(3) for l in LANGS[:3]}:
            raise ValueError('Incomplete confirmation sample')
        if any(r['source']!=plan['probe_sources']['3'][r['index']] for r in rows):
            raise ValueError('Confirmation source identity differs')
        for lang in LANGS:
            selected=[r['mean_kl_nats'] for r in rows if (r['language']==lang if lang!='pooled' else r['language']==LANGS[r['index']])]
            if len(selected)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in selected):
                raise ValueError('Invalid confirmation KL')
            measured[label,lang]=mean(selected)
    margins={lang:measured['mapB',lang]-measured['mapA',lang] for lang in LANGS}
    passed=all(abs(margins[lang])>EPS and (1 if margins[lang]>0 else -1)==nomination['signs'][lang] for lang in ('eng_Latn','ben_Beng'))
    return dict(promising=passed,margin_mapB_minus_mapA_nats=margins,
        mean_kl_by_map={label:{lang:measured[label,lang] for lang in LANGS} for label in cases})


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('plan','discovery','nomination','confirmation-diagnostics','proxy-discovery','proxy-confirmation','output'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--pair-confirmation',type=Path)
    a=p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    plan=read(a.plan)|{'_sha256':sha(a.plan)}
    first=table(read(a.discovery),plan,[1,2])
    nominee=read(a.nomination)
    rebuilt=nominate(plan,first)
    if nominee['plan_sha256']!=sha(a.plan) or nominee['discovery_report_sha256']!=sha(a.discovery) or any(nominee[k]!=rebuilt[k] for k in rebuilt):
        raise ValueError('Discovery nomination cannot be reconstructed')
    third=table(read(a.confirmation_diagnostics),plan,[3])
    costs=first|third
    predicted=proxies(read(a.proxy_discovery),plan,[1,2])|proxies(read(a.proxy_confirmation),plan,[3])
    labels=sorted(e['tensor']+'::'+e['native_type'] for e in plan['diagnostics'])
    subsets={'all':labels}|{kind:[label for label in labels if label.endswith('::'+kind)] for kind in plan['formats'].values() if kind in (plan['formats']['lower'],plan['formats']['higher'])}
    agreement={}
    ranges={}
    for lang in LANGS:
        agreement[lang]={}
        ranges[lang]={}
        for subset,selected in subsets.items():
            agreement[lang][subset]={}
            for metric in ('fisher_score','activation_score'):
                correlations=[spearman([costs[r,lang,label] for label in selected],[predicted[r,lang,label,metric] for label in selected]) for r in (1,2,3)]
                valid=[v for v in correlations if v is not None]
                agreement[lang][subset][metric]=dict(n_tensor_formats=len(selected),repetitions=correlations,
                    observed_repeat_range=[min(valid),max(valid)] if valid else None)
        ranges[lang]=dict(native_kl=[min(costs[r,lang,label] for r in (1,2,3) for label in labels),max(costs[r,lang,label] for r in (1,2,3) for label in labels)],
            **{metric:[min(predicted[r,lang,label,metric] for r in (1,2,3) for label in labels),max(predicted[r,lang,label,metric] for r in (1,2,3) for label in labels)] for metric in ('fisher_score','activation_score')})
    confirmation=None
    if nominee['pair'] is not None:
        if not a.pair_confirmation:
            raise ValueError('Nominated pair requires actual complete-map confirmation')
        confirmation=confirmed_pair(read(a.pair_confirmation),plan,nominee,a.nomination)
        status='promising_screen' if confirmation['promising'] else 'inconclusive'
    else:
        if a.pair_confirmation:
            raise ValueError('Cannot invent a nominee using confirmation outcomes')
        status='inconclusive' if any(pair['eligible'] for pair in plan['pairs']) else 'do_not_proceed_with_this_implementation'
    result=dict(schema='c8-bounded-decision-v1',status=status,nomination=nominee,confirmation=confirmation,
        proxy_rank_agreement=agreement,raw_score_ranges=ranges,
        native_cost_table=[dict(repeat=r,language=lang,tensor_format=label,mean_kl_nats=costs[r,lang,label]) for r in (1,2,3) for lang in LANGS for label in labels],
        inputs={key:sha(getattr(a,key)) for key in ('plan','discovery','nomination','confirmation_diagnostics','proxy_discovery','proxy_confirmation')},
        implementation_sha256=sha(__file__),
        interpretation='Investment screen on three short source samples. Repeat ranges are descriptive, not confidence intervals or evidence of generality. Sequence Fisher and activation magnitudes are uncalibrated proxies; no absolute-KL or proxy-substitution claim. Full task/generation and final confirmation remain future work.')
    if a.pair_confirmation:
        result['inputs']['pair_confirmation']=sha(a.pair_confirmation)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x') as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(status=status,pair=nominee['pair'],confirmation=confirmation)),flush=True)


if __name__=='__main__':
    main()
