"""Freeze diagnostic prompts and original-tokenizer IDs; never score a model."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from option_rotation import rotate_document
from prepare_pilot import tasks, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, required=True)
    p.add_argument('--spec', type=Path, required=True)
    p.add_argument('--tokenizer', required=True)
    p.add_argument('--tokenizer-python', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    raw = args.lock.read_bytes()
    lock, spec = json.loads(raw), json.loads(args.spec.read_text(encoding='utf-8'))
    assert hashlib.sha256(raw).hexdigest() == spec['original_lock_sha256']
    rows = []
    for lang, task in tasks().items():
        for i, member in enumerate(spec['sample_membership']):
            item = lock['items'][i][lang]
            assert (item['source'], item['question']) == (member['source'], member['question'])
            doc = task.test_docs()[item['index']]
            assert (doc['link'], doc['question_number']) == (item['source'], item['question'])
            for shift in spec['rotations']:
                rotated = rotate_document(doc, shift)
                prompt = task.fewshot_context(rotated, num_fewshot=0)
                candidates = [r.args[1] for r in task.construct_requests(rotated, prompt)]
                assert candidates == [' A', ' B', ' C', ' D']
                if shift == 0:
                    assert digest(prompt) == item['prompt_sha256']
                rows.append(dict(language=lang, index=i, dataset_index=item['index'],
                    source=item['source'], question=item['question'], shift=shift,
                    target=int(task.doc_to_target(rotated)), original_target=item['target'],
                    original_choices=[doc[f'mc_answer{j+1}'] for j in range(4)],
                    prompt=prompt, prompt_sha256=digest(prompt), candidates=candidates))
    assert len(rows) == 1200
    texts = [text for r in rows for text in [r['prompt']] + [r['prompt'] + c for c in r['candidates']]]
    code = ("import json,sys; from transformers import AutoTokenizer; "
            "t=AutoTokenizer.from_pretrained(sys.argv[1],local_files_only=True); "
            "print(json.dumps(t(json.load(sys.stdin),add_special_tokens=True)['input_ids']))")
    ids = json.loads(subprocess.check_output([args.tokenizer_python, '-c', code, args.tokenizer],
                                            input=json.dumps(texts).encode()))
    for i, row in enumerate(rows):
        prefix, *candidates = ids[i*5:(i+1)*5]
        assert all(c[:len(prefix)] == prefix and len(c) < 8192 for c in candidates)
        row.update(context_ids=prefix, token_ids=candidates)
    result = dict(spec_sha256=hashlib.sha256(args.spec.read_bytes()).hexdigest(),
                  original_lock_sha256=spec['original_lock_sha256'], context=8192, rows=rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False)
    print('Locked 1200 rotated contexts and 4800 candidates; no scoring.')


if __name__ == '__main__':
    main()
