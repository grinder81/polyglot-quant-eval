"""Offline A3 prerequisite: inspect chat tokens and echoed character boundaries.

Run in the pinned llama-cpp-python environment. Loads vocabulary only; does not
send requests to the live server, calculate likelihoods, or modify scoring.
"""
import argparse
import hashlib
import json
import subprocess
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
    p.add_argument('--tokenizer', type=Path, required=True)
    p.add_argument('--tokenizer-python', required=True)
    p.add_argument('--model', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    # Use the original tokenizer's implementation, not a rewritten Jinja template.
    code = '''import json,sys
from transformers import AutoTokenizer
t=AutoTokenizer.from_pretrained(sys.argv[1],local_files_only=True)
group=json.load(sys.stdin)['items'][0]
rows=[]
for lang,row in group.items():
 s=t.apply_chat_template([{'role':'user','content':row['prompt']}],tokenize=False,add_generation_prompt=True)
 assert t.bos_token and s.startswith(t.bos_token)
 ids=t.encode(s,add_special_tokens=False)
 rows.append(dict(language=lang,source=row['source'],question=row['question'],text=s,
  expected=ids,bos=t.bos_token,bos_id=t.bos_token_id,
  auto_special_duplicates_bos=t.encode(s,add_special_tokens=True)[:2]==[t.bos_token_id]*2,
  candidate_boundaries_match=all(t.encode(s+c,add_special_tokens=False)[:len(ids)]==ids
   for c in [' A',' B',' C',' D'])))
print(json.dumps(rows))
'''
    rows = json.loads(subprocess.check_output(
        [args.tokenizer_python, '-c', code, str(args.tokenizer)], input=args.lock.read_bytes()))
    from llama_cpp import Llama, llama_cpp as native
    import llama_cpp._internals as internals
    import llama_cpp.llama as wrapper
    model = Llama(model_path=args.model, vocab_only=True, n_gpu_layers=0, verbose=False)
    records = []
    for row in rows:
        rendered = row['text']
        # Completion API adds BOS itself. Removing only the leading literal BOS
        # is a diagnostic check, not an implemented production prompt change.
        body = rendered[len(row['bos']):]
        ids = model.tokenize(body.encode(), add_bos=True, special=True)
        assert ids[0] == row['bos_id']
        without_bos = ids[1:]
        # This is the pinned wrapper's echoed offset calculation at the context
        # boundary. Special markers disappear with default detokenize settings.
        decoded = model.detokenize(without_bos).decode('utf-8')
        decoded_special = model.detokenize(without_bos, special=True).decode('utf-8')
        records.append(dict(language=row['language'], source=row['source'], question=row['question'],
            rendered_sha256=hashlib.sha256(rendered.encode()).hexdigest(),
            tokens_match_original=ids == row['expected'],
            candidate_boundaries_match=row['candidate_boundaries_match'],
            auto_special_duplicates_bos=row['auto_special_duplicates_bos'],
            context_characters=len(body), default_echo_boundary=len(decoded),
            special_preserving_boundary=len(decoded_special),
            default_roundtrip_matches=decoded == body,
            special_preserving_roundtrip_matches=decoded_special == body))
    files = [args.lock, args.tokenizer / 'tokenizer_config.json',
             args.tokenizer / 'tokenizer.json', args.model, native._lib._name,
             internals.__file__, wrapper.__file__, __file__]
    report = dict(scope='Offline first locked development item in each language; no inference',
        files={str(path): sha(path) for path in files},
        add_bos_metadata=model.metadata.get('tokenizer.ggml.add_bos_token'), records=records,
        conclusion='Do not launch chat likelihood scoring until actual endpoint offsets and tokens are validated.')
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
