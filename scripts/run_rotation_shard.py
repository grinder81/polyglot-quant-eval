"""Score a locked five-question rotation using the unchanged upstream GGUF model."""
import argparse
import json
from pathlib import Path

from option_rotation import rotate_document
from prepare_pilot import tasks, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, required=True)
    p.add_argument('--language', choices=['eng_Latn', 'ben_Beng', 'hin_Deva'], required=True)
    p.add_argument('--shift', type=int, choices=range(4), required=True)
    p.add_argument('--start', type=int, required=True)
    p.add_argument('--arm', choices=['bf16-gguf', 'local-q4'], required=True)
    p.add_argument('--base-url', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.start not in range(0, 100, 5):
        p.error('start must be 0..95 in steps of five')
    if args.output.exists():
        raise FileExistsError(args.output)
    from datasets import Dataset
    from lm_eval import evaluator
    from lm_eval.models.gguf import GGUFLM
    lock = json.loads(args.lock.read_text(encoding='utf-8'))
    selected = [r for r in lock['rows'] if r['language'] == args.language and r['shift'] == args.shift
                and args.start <= r['index'] < args.start + 5]
    assert len(selected) == 5
    task = tasks()[args.language]
    docs = task.test_docs()
    rotated = []
    for row in selected:
        doc = docs[row['dataset_index']]
        assert (doc['link'], doc['question_number']) == (row['source'], row['question'])
        new = rotate_document(doc, args.shift)
        prompt = task.fewshot_context(new, num_fewshot=0)
        assert digest(prompt) == row['prompt_sha256']
        assert int(task.doc_to_target(new)) == row['target']
        assert [r.args[1] for r in task.construct_requests(new, prompt)] == row['candidates']
        rotated.append(new)
    # Only the selected development documents are transformed. The task's
    # template, choice likelihoods, target rendering and evaluator stay upstream.
    task.dataset[task.config.test_split] = Dataset.from_list(rotated)
    result = evaluator.simple_evaluate(model=GGUFLM(base_url=args.base_url, max_length=8192),
        tasks=[task], num_fewshot=0, apply_chat_template=False, log_samples=True,
        bootstrap_iters=1000, random_seed=42, numpy_random_seed=42, torch_random_seed=42,
        fewshot_random_seed=42, metadata=dict(arm=args.arm, shift=args.shift,
        start=args.start, scope='Diagnostic option rotation; not canonical baseline'))
    temporary = args.output.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    temporary.replace(args.output)


if __name__ == '__main__':
    main()
