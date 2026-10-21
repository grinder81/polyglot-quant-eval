import json

from scripts.prepare_negation_review import hints, public_document


def test_review_fields_do_not_expose_answers_or_predictions():
    doc = dict(flores_passage='A passage', question='Which is not supported?',
               correct_answer_num='3', prediction='B', scores=[1, 2, 3, 4],
               mc_answer1='one', mc_answer2='two', mc_answer3='three', mc_answer4='four')
    out = public_document(doc, 'eng_Latn')
    assert set(out) == {'passage', 'question', 'choices', 'screening_hints', 'review'}
    assert out['choices'] == ['one', 'two', 'three', 'four']
    assert all(value is None for value in out['review'].values())
    assert 'correct_answer_num' not in json.dumps(out)
    assert 'prediction' not in json.dumps(out)
    assert 'scores' not in json.dumps(out)


def test_bangla_marker_boundary_preserves_combining_characters():
    assert hints('কোনটি সত্য নয়?', 'ben_Beng') == ['নয়']
    assert hints('কোনটি সত্য নয়?', 'ben_Beng') == ['নয়']
    assert hints('ঘটনা কী?', 'ben_Beng') == []
    assert hints('কোনটি ব্যতিক্রম?', 'ben_Beng') == ['ব্যতিক্রম']


def test_keyword_hints_are_not_semantic_labels():
    assert hints('Which is notable?', 'eng_Latn') == []
    assert hints('Which is NOT supported?', 'eng_Latn') == ['not']
    assert hints('Which is least expensive?', 'eng_Latn') == ['least']
    # A minimum-price question is not automatically negation. Human fields stay empty.
    doc = dict(flores_passage='x', question='Which is least expensive?',
               **{f'mc_answer{i}': str(i) for i in range(1, 5)})
    assert public_document(doc, 'eng_Latn')['review']['selection_polarity'] is None
