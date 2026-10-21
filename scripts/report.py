#!/usr/bin/env python3
"""Report distinct runs; compare only explicitly identified, compatible arms."""
import argparse
import json
import math
from pathlib import Path

import pandas as pd

CONTRACT = ('model_id', 'model_revision', 'mode', 'fewshot', 'n',
            'sample_set_hash', 'scoring_contract_hash', 'backend', 'device', 'os_version')


def index_rows(rows):
    indexed = {}
    identities = {}
    for row in rows:
        key = row['run_id'], row['task'], row['metric'], row['language']
        if key in indexed:
            raise ValueError(f'Duplicate aggregate row: {key}; never average implicitly')
        if not math.isfinite(row['value']) or row['n'] <= 0:
            raise ValueError('Invalid value or sample count')
        identity = tuple(row.get(k) for k in ('model_id', 'model_revision', 'format', 'runtime',
                                              'runtime_version', 'backend', 'device', 'os_version'))
        if row['run_id'] in identities and identities[row['run_id']] != identity:
            raise ValueError('A run_id contains multiple model/runtime configurations')
        identities[row['run_id']] = identity
        indexed[key] = row
    return indexed


def compare(rows, canonical, control, candidates):
    indexed = index_rows(rows)
    if not candidates or len({canonical, control, *candidates}) != 2 + len(candidates):
        raise ValueError('Choose distinct canonical, control and candidate run IDs')
    available = {r['run_id'] for r in rows}
    if not {canonical, control, *candidates} <= available:
        raise ValueError('Selected run ID missing after filtering')
    for ref in (canonical, control):
        if any(r['format'] != 'bf16' for r in rows if r['run_id'] == ref):
            raise ValueError('Canonical/control references must be explicit BF16 runs')
    if any(r['runtime'] != 'vllm' for r in rows if r['run_id'] == canonical):
        raise ValueError('This project uses vLLM as the canonical BF16 reference')
    comparisons = [(control, canonical, 'runtime/conversion')]
    comparisons += [(candidate, control, 'same-runtime compression') for candidate in candidates]
    comparisons += [(candidate, canonical, 'total difference') for candidate in candidates]
    output = []
    for candidate, reference, label in comparisons:
        c = {(t, m, l): r for (run, t, m, l), r in indexed.items() if run == candidate}
        b = {(t, m, l): r for (run, t, m, l), r in indexed.items() if run == reference}
        if c.keys() != b.keys():
            raise ValueError('Arms have different task/metric/language coverage')
        deltas = {}
        for key, row in c.items():
            ref = b[key]
            fields = CONTRACT + (('runtime', 'runtime_version') if label == 'same-runtime compression' else ())
            for field in fields:
                if row.get(field) in (None, '') or ref.get(field) in (None, '') or row[field] != ref[field]:
                    raise ValueError(f'Incompatible or unknown {field} for {candidate} vs {reference}: {key}')
            deltas[key] = row['value'] - ref['value']
        for (task, metric, lang), delta in sorted(deltas.items()):
            en = (task, metric, 'en')
            if en not in deltas:
                raise ValueError(f'English comparison required for {task}/{metric}; filter the task explicitly')
            row, ref = c[task, metric, lang], b[task, metric, lang]
            output.append(dict(comparison=label, candidate_run=candidate, reference_run=reference,
                candidate_runtime=row['runtime'], reference_runtime=ref['runtime'],
                task=task, metric=metric, language=lang, n=row['n'],
                candidate_value=row['value'], reference_value=ref['value'],
                delta=delta, english_delta=deltas[en], gap_vs_english=delta-deltas[en],
                uncertainty='Paired delta interval unavailable from aggregate rows; use per-item paired analysis.'))
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rows', type=Path)
    ap.add_argument('--task')
    ap.add_argument('--metric')
    ap.add_argument('--canonical-run')
    ap.add_argument('--control-run')
    ap.add_argument('--candidate-run', action='append', default=[])
    ap.add_argument('--ref-format', help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.ref_format:
        ap.error('Format alone cannot select a reference; select explicit run IDs')
    rows = [json.loads(line) for line in a.rows.read_text(encoding='utf-8').splitlines() if line.strip()]
    rows = [r for r in rows if (not a.task or r['task'] == a.task) and (not a.metric or r['metric'] == a.metric)]
    if not rows:
        ap.error('No rows after filtering')
    try:
        index_rows(rows)
        selected = bool(a.canonical_run or a.control_run or a.candidate_run)
        if selected and not (a.canonical_run and a.control_run and a.candidate_run):
            raise ValueError('Comparisons require canonical-run, control-run and candidate-run')
        deltas = compare(rows, a.canonical_run, a.control_run, a.candidate_run) if selected else []
    except ValueError as error:
        ap.error(str(error))
    print('Distinct run results; no averaging across runs or runtimes')
    fields = ['run_id', 'format', 'runtime', 'runtime_version', 'task', 'metric', 'language', 'mode', 'fewshot', 'n', 'value', 'stderr']
    print(pd.DataFrame(rows).reindex(columns=fields).to_string(index=False))
    print('stderr is supplied aggregate metadata, not a paired interval or a source-cluster correction.')
    if deltas:
        print('Delta = candidate minus reference; gap vs English = delta minus English delta. Units match metric value.')
        print(pd.DataFrame(deltas).to_string(index=False))
    else:
        print('No deltas: select explicit run IDs with complete comparison provenance.')


if __name__ == '__main__':
    main()
