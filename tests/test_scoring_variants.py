import copy

import pytest

from scripts.prepare_scoring_variants import digest, requests_for, validate_membership


class Tokenizer:
    bos_token = '<BOS>'
    bos_token_id = 2

    def encode(self, text, add_special_tokens=False):
        prefix = [2] if add_special_tokens else []
        if text.startswith(self.bos_token):
            prefix.append(2)
            text = text[len(self.bos_token):]
        return prefix + [ord(c) + 10 for c in text]

    def decode(self, ids, **kwargs):
        return ''.join(self.bos_token if i == 2 else chr(i - 10) for i in ids)

    def apply_chat_template(self, messages, **kwargs):
        return self.bos_token + 'USER:' + messages[0]['content'] + '|ASSISTANT:'


def row():
    t = Tokenizer()
    prompt = 'প্রশ্ন\nAnswer:'
    candidates = [' A', ' B', ' C', ' D']
    return dict(prompt=prompt, prompt_sha256=digest(prompt), candidates=candidates,
        context_ids=t.encode(prompt, add_special_tokens=True),
        token_ids=[t.encode(prompt + c, add_special_tokens=True) for c in candidates],
        original_choices=['প্রথম', 'second', 'third', 'fourth'], shift=1)


def test_original_letter_request_remains_identical():
    r = row()
    actual = requests_for(r, Tokenizer(), 'plain-letter')
    assert actual['prompt'] == r['prompt']
    assert actual['model_token_ids'] == r['token_ids']
    assert actual['candidates'] == r['candidates']


def test_chat_has_one_implicit_bos_and_intact_assistant_boundary():
    actual = requests_for(row(), Tokenizer(), 'chat-letter')
    assert actual['prompt'] == 'USER:প্রশ্ন\nAnswer:|ASSISTANT:'
    assert actual['model_context_ids'].count(2) == 1
    assert 2 not in actual['wire_context_ids']
    assert actual['candidates'] == [' A', ' B', ' C', ' D']


def test_text_choices_follow_display_rotation_without_normalizing_unicode():
    actual = requests_for(row(), Tokenizer(), 'plain-option-text')
    assert actual['choices'] == ['second', 'third', 'fourth', 'প্রথম']
    assert actual['candidates'][-1] == ' প্রথম'
    assert actual['choice_utf8_lengths'][-1] > actual['choice_character_lengths'][-1]
    assert actual['choice_character_lengths'][-1] == len('প্রথম')


def test_changed_baseline_rejected():
    r = row()
    r['token_ids'][0].append(99)
    with pytest.raises(ValueError, match='baseline changed'):
        requests_for(r, Tokenizer(), 'plain-letter')


def test_membership_rejects_duplicate_and_wrong_rotation_target():
    rows = [dict(language=lang, index=i, shift=s, original_target=2, target=(2-s)%4,
                 source=f'source{i}', question=i, original_choices=['a', 'b', 'c', 'd'])
            for lang in ('eng_Latn', 'ben_Beng', 'hin_Deva')
            for i in range(100) for s in range(4)]
    validate_membership(rows)
    wrong = copy.deepcopy(rows)
    wrong[-1] = wrong[0]
    with pytest.raises(ValueError, match='exact A2 membership'):
        validate_membership(wrong)
    wrong = copy.deepcopy(rows)
    wrong[1]['target'] = 2
    with pytest.raises(ValueError, match='Rotation target mismatch'):
        validate_membership(wrong)
