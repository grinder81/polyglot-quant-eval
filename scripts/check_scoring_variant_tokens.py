"""Check A3 locked model IDs against GGUF vocabulary; no inference or server."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, required=True)
    p.add_argument('--model', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    from llama_cpp import Llama, llama_cpp as native
    import llama_cpp._internals as internals
    import llama_cpp.llama as wrapper
    model = Llama(model_path=args.model, vocab_only=True, n_gpu_layers=0, verbose=False)
    data = json.loads(args.lock.read_text(encoding='utf-8'))
    if len(data['rows']) != 3600:
        raise ValueError('Expected all three variants and 1200 rotation contexts each')
    contexts = candidates = 0
    failures = []
    for row in data['rows']:
        texts = [row['prompt']] + [row['prompt'] + c for c in row['candidates']]
        expected = [row['model_context_ids']] + row['model_token_ids']
        for i, (text, ids) in enumerate(zip(texts, expected, strict=True)):
            actual = model.tokenize(text.encode('utf-8'), add_bos=True, special=True)
            decoded = model.detokenize(actual[1:], special=True).decode('utf-8')
            if actual != ids or actual[0] != model.token_bos() or decoded != text:
                failures.append(dict(language=row['language'], index=row['index'],
                    shift=row['shift'], variant=row['variant'], candidate=i-1,
                    tokens_match=actual == ids, special_roundtrip_matches=decoded == text))
            elif i == 0:
                contexts += 1
            else:
                candidates += 1
    files = [args.model, native._lib._name, internals.__file__, wrapper.__file__, __file__]
    report = dict(scope='Vocabulary-only token and special-preserving roundtrip check; no endpoint validation',
        lock_sha256=sha(args.lock), files={str(path): sha(path) for path in files},
        passed_contexts=contexts, passed_candidates=candidates, failures=failures)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
    if failures:
        raise ValueError(f'{len(failures)} token/roundtrip failures')
    print(f'Passed {contexts} contexts and {candidates} continuations; no inference')


if __name__ == '__main__':
    main()
