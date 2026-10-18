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
    parser.add_argument('--backend', choices=['gguf', 'local-completions'], default='gguf')
    parser.add_argument('--tokenizer')
    parser.add_argument('--language', choices=['eng_Latn', 'ben_Beng', 'hin_Deva'])
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--count', type=int)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--small-pilot', action='store_true',
                        help='Ten total: first four Bangla, three English and three Hindi locked items')
    args = parser.parse_args()
    if args.start < 0 or (args.count is not None and args.count < 1):
        parser.error('start must be nonnegative and count must be positive')
    if args.small_pilot and (args.start or args.count):
        parser.error('small-pilot cannot be combined with a sample range')
    if args.output.exists():
        raise FileExistsError(args.output)
    lock = json.loads(args.lock.read_text())
    loaded = tasks()
    if args.language:
        loaded = {args.language: loaded[args.language]}
    samples = {}
    for language, task in loaded.items():
        count = (4 if language == 'ben_Beng' else 3) if args.small_pilot else (args.count or 50)
        selected = [group[language] for group in lock['items'][args.start:args.start + count]]
        assert len(selected) == count
        docs = task.test_docs()
        for row in selected:
            doc = docs[row['index']]
            prompt = task.fewshot_context(doc, num_fewshot=0)
            assert digest(prompt) == row['prompt_sha256']
            assert [r.args[1] for r in task.construct_requests(doc, prompt)] == row['candidates']
            assert int(task.doc_to_target(doc)) == row['target']
        samples[task.config.task] = [row['index'] for row in selected]
    if args.backend == 'local-completions':
        from lm_eval.models.openai_completions import LocalCompletionsAPI
        model = LocalCompletionsAPI(model='tiny-aya-global', base_url=args.base_url,
            tokenizer_backend='huggingface', tokenizer=args.tokenizer,
            add_bos_token=True, max_length=8192)
        for language in loaded:
            count = (4 if language == 'ben_Beng' else 3) if args.small_pilot else (args.count or 50)
            for group in lock['items'][args.start:args.start + count]:
                row = group[language]
                assert model.tok_encode(row['prompt']) == row['context_ids']
                for candidate, ids in zip(row['candidates'], row['token_ids']):
                    assert model.tok_encode(row['prompt'] + candidate) == ids
    else:
        model = GGUFLM(base_url=args.base_url, max_length=8192)
    result = evaluator.simple_evaluate(
        model=model,
        tasks=list(loaded.values()), samples=samples, num_fewshot=0,
        apply_chat_template=False, log_samples=True, bootstrap_iters=1000,
        random_seed=42, numpy_random_seed=42, torch_random_seed=42,
        fewshot_random_seed=42,
        metadata={'arm': args.arm, 'start': args.start, 'count': args.count,
            'language': args.language, 'scope': (
            '10 total development items: 4 Bangla, 3 English, 3 Hindi; no speed claim'
            if args.small_pilot else 'Frozen development sample range; no speed claim')})
    temporary = args.output.with_suffix(args.output.suffix + '.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    temporary.replace(args.output)


if __name__ == '__main__':
    main()
