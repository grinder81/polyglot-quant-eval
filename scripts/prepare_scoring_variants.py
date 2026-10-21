"""Freeze A3 diagnostic text/token requests offline; never score a model."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


VARIANTS = ('plain-letter', 'chat-letter', 'plain-option-text')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def requests_for(row, tokenizer, variant):
    """Return wire text plus expected model tokens, accounting for server BOS."""
    if variant not in VARIANTS:
        raise ValueError(variant)
    plain = row['prompt']
    if digest(plain) != row['prompt_sha256']:
        raise ValueError('Rotation prompt hash mismatch')
    if variant == 'chat-letter':
        rendered = tokenizer.apply_chat_template([{'role': 'user', 'content': plain}],
            tokenize=False, add_generation_prompt=True)
        bos = tokenizer.bos_token
        if not bos or not rendered.startswith(bos):
            raise ValueError('Expected one leading literal BOS in original template')
        wire = rendered[len(bos):]
        if wire.startswith(bos):
            raise ValueError('Duplicated literal BOS')
        model_context = tokenizer.encode(rendered, add_special_tokens=False)
    else:
        rendered = wire = plain
        model_context = tokenizer.encode(plain, add_special_tokens=True)
        if model_context != row['context_ids']:
            raise ValueError('Original rotation context token mismatch')
    choices = ['A', 'B', 'C', 'D']
    if variant == 'plain-option-text':
        choices = [row['original_choices'][(position + row['shift']) % 4]
                   for position in range(4)]
    if any(not isinstance(c, str) or not c for c in choices):
        raise ValueError('Empty/non-string choice')
    candidates = [' ' + choice for choice in choices]
    wire_context = tokenizer.encode(wire, add_special_tokens=False)
    if [tokenizer.bos_token_id] + wire_context != model_context:
        raise ValueError('Implicit server BOS does not reproduce intended model context')
    model_tokens, wire_tokens = [], []
    for candidate in candidates:
        wire_ids = tokenizer.encode(wire + candidate, add_special_tokens=False)
        intended = tokenizer.encode(rendered + candidate,
                                    add_special_tokens=variant != 'chat-letter')
        if wire_ids[:len(wire_context)] != wire_context:
            raise ValueError('Candidate crosses context token boundary')
        if intended != [tokenizer.bos_token_id] + wire_ids:
            raise ValueError('Candidate tokens differ after implicit BOS insertion')
        if tokenizer.decode(wire_ids, skip_special_tokens=False,
                            clean_up_tokenization_spaces=False) != wire + candidate:
            raise ValueError('HF request encode/decode is not lossless')
        model_tokens.append(intended)
        wire_tokens.append(wire_ids)
    if variant == 'plain-letter' and (model_tokens != row['token_ids']
                                     or candidates != row['candidates']):
        raise ValueError('Plain-letter baseline changed')
    return dict(variant=variant, prompt=wire, prompt_sha256=digest(wire),
        rendered_sha256=digest(rendered), choices=choices, candidates=candidates,
        model_context_ids=model_context, model_token_ids=model_tokens,
        wire_context_ids=wire_context, wire_token_ids=wire_tokens,
        choice_character_lengths=[len(c) for c in choices],
        choice_utf8_lengths=[len(c.encode('utf-8')) for c in choices])


def validate_membership(rows):
    expected = {(lang, i, shift) for lang in ('eng_Latn', 'ben_Beng', 'hin_Deva')
                for i in range(100) for shift in range(4)}
    actual = [(r['language'], r['index'], r['shift']) for r in rows]
    if len(actual) != 1200 or set(actual) != expected:
        raise ValueError('Expected exact A2 membership: 100/language x four rotations')
    references = {}
    for row in rows:
        if len(row['original_choices']) != 4:
            raise ValueError('Expected four original choices')
        if row['target'] != (row['original_target'] - row['shift']) % 4:
            raise ValueError('Rotation target mismatch')
        key = (row['language'], row['index'])
        value = (row['source'], row['question'], row['original_target'], row['original_choices'])
        if key in references and references[key] != value:
            raise ValueError('Original item changed across rotations')
        references[key] = value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rotation-lock', type=Path, required=True)
    p.add_argument('--tokenizer', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--summary', type=Path, required=True)
    args = p.parse_args()
    if args.output == args.summary or args.output.exists() or args.summary.exists():
        raise FileExistsError('Both output paths must be distinct and new')
    from transformers import AutoTokenizer
    import transformers
    source = json.loads(args.rotation_lock.read_text(encoding='utf-8'))
    validate_membership(source['rows'])
    if source['context'] != 8192:
        raise ValueError('Unexpected context budget')
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True)
    rows = []
    for original in source['rows']:
        identity = {k: original[k] for k in ('language', 'index', 'dataset_index',
                    'source', 'question', 'shift', 'target', 'original_target', 'original_choices')}
        for variant in VARIANTS:
            row = identity | requests_for(original, tokenizer, variant)
            if max(map(len, row['model_token_ids'])) >= source['context']:
                raise ValueError('Context overflow; do not silently drop or truncate')
            rows.append(row)
    provenance = dict(rotation_lock_sha256=sha(args.rotation_lock),
        original_lock_sha256=source['original_lock_sha256'],
        a2_spec_sha256=source['spec_sha256'], transformers_version=transformers.__version__,
        tokenizer_files={name: sha(args.tokenizer / name) for name in
                         ('tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json')},
        preparer_sha256=sha(__file__), context=source['context'])
    report = dict(scope='Offline diagnostic requests only; no endpoint or accuracy validation',
        provenance=provenance, variants=list(VARIANTS), contexts=len(rows),
        candidates=len(rows) * 4, counts=dict(Counter(r['variant'] for r in rows)),
        max_model_tokens=max(len(ids) for r in rows for ids in r['model_token_ids']),
        upstream_acc_norm='sum continuation log probability / Unicode characters in choice; excludes delimiter',
        endpoint_validation_required=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(dict(provenance=provenance, rows=rows), stream, ensure_ascii=False)
    report['request_lock_sha256'] = sha(args.output)
    with args.summary.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
