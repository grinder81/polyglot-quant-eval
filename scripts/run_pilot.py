"""Run frozen samples through the unchanged upstream GGUF harness integration."""
import argparse
import json
from pathlib import Path

from lm_eval import evaluator
from lm_eval.models.gguf import GGUFLM
from prepare_pilot import tasks, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, required=True)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--arm', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    lock = json.loads(args.lock.read_text())
    loaded = tasks()
    samples = {}
    for language, task in loaded.items():
        selected = [group[language] for group in lock['items'][:50]]
        docs = task.test_docs()
        for row in selected:
            doc = docs[row['index']]
            prompt = task.fewshot_context(doc, num_fewshot=0)
            assert digest(prompt) == row['prompt_sha256']
            assert [r.args[1] for r in task.construct_requests(doc, prompt)] == row['candidates']
            assert int(task.doc_to_target(doc)) == row['target']
        samples[task.config.task] = [row['index'] for row in selected]
    result = evaluator.simple_evaluate(
        model=GGUFLM(base_url=args.base_url, max_length=8192),
        tasks=list(loaded.values()), samples=samples, num_fewshot=0,
        apply_chat_template=False, log_samples=True, bootstrap_iters=1000,
        random_seed=42, numpy_random_seed=42, torch_random_seed=42,
        fewshot_random_seed=42,
        metadata={'arm': args.arm, 'scope': '50 aligned development items per language; no speed claim'})
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
