"""Reproduce installed harness labeling on five development records with DummyLM."""
import argparse
import hashlib
import json
from pathlib import Path

from prepare_pilot import tasks, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    import lm_eval
    from lm_eval import evaluator
    from lm_eval.models.dummy import DummyLM
    language = 'eng_Latn'
    selected = [g[language] for g in json.loads(args.lock.read_text(encoding='utf-8'))['items'][:5]]
    task = tasks()[language]
    result = evaluator.simple_evaluate(model=DummyLM(), tasks=[task], num_fewshot=0,
        samples={task.config.task: [r['index'] for r in selected]}, log_samples=True,
        apply_chat_template=False, bootstrap_iters=0, random_seed=42,
        numpy_random_seed=42, torch_random_seed=42, fewshot_random_seed=42)
    keys = {(r['source'], r['question']): r for r in selected}
    records = []
    for row in result['samples'][task.config.task]:
        member = keys[row['doc']['link'], row['doc']['question_number']]
        assert all(digest(a[0]) == member['prompt_sha256'] for a in row['arguments'])
        assert row['target'] == member['target']
        records.append(dict(actual_index=member['index'], raw_doc_id=row['doc_id']))
    base = Path(lm_eval.__file__).parent
    evidence = dict(scope='DummyLM logging reproduction; no model accuracy result',
        requested_indices=[r['index'] for r in selected], records=records,
        content_prompt_and_target_matches=len(records),
        source_sha256={str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in [base / 'evaluator.py', base / 'api/task.py']})
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(evidence, stream, indent=2)


if __name__ == '__main__':
    main()
