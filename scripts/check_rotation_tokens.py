"""Require original/GGUF token and text agreement for every diagnostic request."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, required=True)
    p.add_argument('--model', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    from llama_cpp import Llama
    from llama_cpp import llama_cpp as native
    import llama_cpp._internals as internals
    import llama_cpp.llama as wrapper
    def file_sha(path):
        h = hashlib.sha256()
        with Path(path).open('rb') as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                h.update(block)
        return h.hexdigest()
    files = [args.model, native._lib._name, internals.__file__, wrapper.__file__]
    runtime_files = {str(p): file_sha(p) for p in files}
    raw = args.lock.read_bytes()
    rows = json.loads(raw)['rows']
    assert len(rows) == 1200
    model = Llama(model_path=args.model, vocab_only=True, n_gpu_layers=0, verbose=False)
    failures = []
    contexts, candidates = 0, 0
    for row in rows:
        texts = [row['prompt']] + [row['prompt'] + c for c in row['candidates']]
        expected = [row['context_ids']] + row['token_ids']
        for i, (text, ids) in enumerate(zip(texts, expected, strict=True)):
            actual = model.tokenize(text.encode(), add_bos=True)
            roundtrip = model.detokenize(actual).decode('utf-8')
            if actual != ids or roundtrip != text:
                failures.append(dict(language=row['language'], index=row['index'],
                    shift=row['shift'], candidate=i-1, tokens_match=actual == ids,
                    roundtrip_match=roundtrip == text))
            elif i == 0:
                contexts += 1
            else:
                candidates += 1
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(dict(lock_sha256=hashlib.sha256(raw).hexdigest(), model=args.model,
            runtime_files=runtime_files,
            passed_contexts=contexts, passed_candidates=candidates, failures=failures), stream, indent=2)
    if failures:
        raise ValueError(f'{len(failures)} diagnostic token/roundtrip failures')
    print(f'Passed {contexts} contexts and {candidates} candidates; no scoring.')


if __name__ == '__main__':
    main()
