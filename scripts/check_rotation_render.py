"""Verify diagnostic rotations against upstream rendering without model inference."""
import argparse
import hashlib
import json
from pathlib import Path

from option_rotation import original_choice, rotate_document
from prepare_pilot import digest, tasks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, required=True)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.lock.read_bytes()
    lock = json.loads(raw)
    spec = json.loads(args.spec.read_text(encoding='utf-8'))
    assert hashlib.sha256(raw).hexdigest() == spec['original_lock_sha256']
    count = 0
    for lang, task in tasks().items():
        docs = task.test_docs()
        for group, member in zip(lock['items'][:100], spec['sample_membership'], strict=True):
            row = group[lang]
            doc = docs[row['index']]
            assert (doc['link'], doc['question_number']) == (member['source'], member['question'])
            for shift in range(4):
                rotated = rotate_document(doc, shift)
                prompt = task.fewshot_context(rotated, num_fewshot=0)
                requests = task.construct_requests(rotated, prompt)
                assert [r.args[1] for r in requests] == [' A', ' B', ' C', ' D']
                assert original_choice(int(task.doc_to_target(rotated)), shift) == row['target']
                if shift == 0:
                    assert digest(prompt) == row['prompt_sha256']
                count += 1
    result = dict(rendered_rotations=count, zero_rotation_prompt_hashes_matched=300,
                  candidate_contract=' A / B / C / D unchanged', model_requests=0,
                  tokenizer_validation='pending before inference',
                  spec_sha256=hashlib.sha256(args.spec.read_bytes()).hexdigest())
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
