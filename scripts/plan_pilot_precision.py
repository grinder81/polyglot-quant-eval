"""Plan paired accuracy precision from verified T1; no new model outcomes."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist

REPORT_SHA = 'c1ffee6b6030b1d5beb6c6afe3d855c1e1703df3e2fd6329270b06d55a1941a1'


def paired_scenario(n, discordance, true_delta=.03):
    if n <= 0 or not 0 <= abs(true_delta) <= discordance <= 1:
        raise ValueError('Impossible paired accuracy scenario')
    se = math.sqrt((discordance-true_delta**2)/n)
    if se == 0:
        raise ValueError('Degenerate planning scenario')
    normal=NormalDist()
    z=normal.inv_cdf(.975)
    power=1-normal.cdf(z-true_delta/se)+normal.cdf(-z-true_delta/se)
    return dict(n=n,assumed_discordance=discordance,assumed_true_delta=true_delta,
        standard_error=se,approximate_95_half_width=z*se,
        approximate_power_positive_or_negative_interval=power,
        note='Unclustered normal approximation; not power for the joint point-estimate>=3pp rule, not a forecast for future allocations.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    payload=gzip.decompress(a.report.read_bytes())
    if hashlib.sha256(payload).hexdigest()!=REPORT_SHA:
        raise ValueError('Unverified T1 report')
    report=json.loads(payload)
    languages={}
    for language,row in report['fresh_paired_GGUF']['languages'].items():
        n=300
        correctness=row['right_to_wrong']+row['wrong_to_right']
        languages[language]=dict(correctness_discordant=correctness,
            all_answer_churn=row['changed_choices'],
            actual_t1_paired_cluster_95_interval=row['paired_cluster_95_delta_interval'],
            illustrative_scenarios=[paired_scenario(size,correctness/n) for size in (300,424)])
    result=dict(verified_t1_report_sha256=REPORT_SHA,implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        development_questions_per_language=300,development_source_clusters=250,
        reserved_holdout_questions_per_language=424,reserved_holdout_source_clusters=238,
        languages=languages,
        interpretation='Task bootstrap uncertainty is conditional on constructed models; separately repeat construction samples. More bootstrap draws do not add observations. Holdout metadata only; no holdout outcomes read.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
        stream.write('\n')


if __name__=='__main__':
    main()
