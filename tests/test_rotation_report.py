import hashlib
import json
from pathlib import Path

import pytest

from scripts.summarize_rotations import ARMS, LANGS, load_arm, summarize


def save(path, data):
    path.write_text(json.dumps(data), encoding='utf-8')
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def evidence(tmp_path):
    spec_path = Path(__file__).resolve().parents[1] / 'configs/option-rotation.json'
    spec = json.loads(spec_path.read_text())
    rows = []
    for language in LANGS:
        for index in range(100):
            for shift in range(4):
                prompt = f'{language}:{index}:{shift}'
                member = spec['sample_membership'][index]
                rows.append(dict(language=language, index=index, source=member['source'],
                    question=member['question'], shift=shift, target=(-shift) % 4, original_target=0,
                    original_choices=['correct', 'same', 'same', 'other'],
                    prompt=prompt, prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                    candidates=[' A', ' B', ' C', ' D']))
    lock = {'rows': rows, 'spec_sha256': hashlib.sha256(spec_path.read_bytes()).hexdigest(),
            'original_lock_sha256': spec['original_lock_sha256']}
    lock_sha = save(tmp_path / 'rotation-lock.json', lock)
    for arm in ARMS:
        directory = tmp_path / arm
        directory.mkdir()
        files = {f'/{arm}.gguf': 'fake-model-hash', '/libllama.so': 'fake-library-hash'}
        runtime_sha = save(tmp_path / f'{arm}-runtime.json', dict(arm=arm,
            files=files, server_command=['server', '--model', f'/{arm}.gguf'], packages='fixture'))
        preflight_sha = save(tmp_path / f'{arm}-preflight.json', dict(lock_sha256=lock_sha,
            failures=[], passed_contexts=1200, passed_candidates=4800, runtime_files=files))
        save(directory / 'identity.json', dict(arm=arm, lock=lock_sha, runtime=runtime_sha,
             preflight=preflight_sha, code={'runner': 'fixture'}))
        for language in LANGS:
            for shift in range(4):
                for start in range(0, 100, 5):
                    selected = [r for r in rows if r['language'] == language and r['shift'] == shift
                                and start <= r['index'] < start + 5]
                    samples = [dict(doc={'link': r['source'], 'question_number': r['question']},
                        target=r['target'], arguments=[[r['prompt'], c] for c in r['candidates']],
                        filtered_resps=[[10 + int(shift == 0)]] + [[int((p + shift) % 4 == 0)] for p in range(1, 4)],
                        acc=int(shift == 0)) for r in selected]
                    save(directory / f'{language}-r{shift}-{start:03}.json', dict(
                        samples={'belebele_' + language: samples},
                        results={'belebele_' + language: {'acc,none': int(shift == 0)}}))
    return tmp_path, lock


def test_full_report_and_exact_choice_flags(evidence):
    root, _ = evidence
    report = summarize(root, replicates=5)
    assert len(report['items']) == 300
    assert all(r['identical_text_choice_pairs'] == [[2, 1]] for r in report['items'])
    for language in LANGS:
        assert report['statistics']['cells']['bf16-gguf'][language]['metrics']['raw_accuracy_average'] == .25
        assert report['statistics']['cells']['local-q4'][language]['metrics']['cross_fitted_accuracy_average'] == 1
        assert all(c['unchanged'] == 100 for c in report['paired_flip_counts'][language]['raw'])
    json.dumps(report)  # Full artifact is serializable, unlike internal tuple-key cells.


def test_missing_and_corrupted_raw_evidence_rejected(evidence):
    root, lock = evidence
    path = root / 'local-q4/eng_Latn-r0-000.json'
    original = path.read_text()
    data = json.loads(original)
    data['samples']['belebele_eng_Latn'][0]['arguments'][0][0] = 'changed'
    save(path, data)
    with pytest.raises(AssertionError):
        load_arm(root, 'local-q4', lock)
    path.unlink()
    with pytest.raises(AssertionError):
        load_arm(root, 'local-q4', lock)
