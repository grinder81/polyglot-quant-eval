import copy
import json
from pathlib import Path

import unittest
from scripts.reserve_holdout import LANGUAGES, REVISION, digest, reserve


def fixture():
    rows = [dict(link=f'source-{i}', question_number='1') for i in range(300)]
    lock = dict(revision=REVISION, items=[{l: dict(source=r['link'], question='1')
                for l in LANGUAGES} for r in rows])
    rows += [dict(link='source-0', question_number='2'), dict(link='unseen', question_number='1')]
    return {l: copy.deepcopy(rows) for l in LANGUAGES}, lock


def test_excludes_other_questions_from_development_sources():
    metadata, lock = fixture()
    result = reserve(metadata, lock, 'test-hash')
    assert result['members'] == [dict(source='unseen', question='1')]
    assert result['counts_per_language']['excluded_shared_development_source'] == 1
    metadata['ben_Beng'].append(metadata['ben_Beng'][0])
    with unittest.TestCase().assertRaisesRegex(ValueError, 'Duplicate'):
        reserve(metadata, lock, 'test-hash')


def test_rejects_cross_language_missing_identity():
    metadata, lock = fixture()
    metadata['ben_Beng'].pop()
    with unittest.TestCase().assertRaisesRegex(ValueError, 'aligned'):
        reserve(metadata, lock, 'test-hash')


def test_frozen_membership_has_no_answers_and_no_development_sources():
    root = Path(__file__).resolve().parents[1]
    held = json.loads((root / 'configs/belebele-final-holdout.json').read_text(encoding='utf-8'))
    development = json.loads((root / 'results/stage1/local-q4-three-hundred/sample-identities.json').read_text(encoding='utf-8'))
    sources = {g[l]['source'] for g in development['items'] for l in LANGUAGES}
    assert len(held['members']) == 424
    assert len({(m['source'], m['question']) for m in held['members']}) == 424
    assert all(set(m) == {'source', 'question'} and m['source'] not in sources for m in held['members'])
    assert held['membership_sha256'] == digest(held['members'])
    assert held['development_lock_sha256'] == development['original_lock_sha256']


if __name__ == "__main__":
    test_excludes_other_questions_from_development_sources()
    test_rejects_cross_language_missing_identity()
    test_frozen_membership_has_no_answers_and_no_development_sources()
    print("3 holdout checks passed")
