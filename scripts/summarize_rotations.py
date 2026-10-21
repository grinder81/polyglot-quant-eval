"""Validate complete A2 evidence and report diagnostics without altering scores.

Run as python -m scripts.summarize_rotations ROOT --output NEW_REPORT.
ROOT contains rotation-lock.json, ARM-runtime.json, ARM-preflight.json and ARM/
shards for bf16-gguf and local-q4. Raw evidence must be retained alongside output.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from .rotation_statistics import joint_statistics, measure
from .run_rotation_shards import sha, validate_shard

LANGS = ('eng_Latn', 'ben_Beng', 'hin_Deva')
ARMS = ('bf16-gguf', 'local-q4')


def load_arm(root, arm, lock):
    directory = root / arm
    runtime_path = root / f'{arm}-runtime.json'
    preflight_path = root / f'{arm}-preflight.json'
    identity = json.loads((directory / 'identity.json').read_text())
    runtime = json.loads(runtime_path.read_text())
    preflight = json.loads(preflight_path.read_text())
    assert identity['arm'] == runtime['arm'] == arm
    assert identity['lock'] == preflight['lock_sha256'] == sha(root / 'rotation-lock.json')
    assert identity['runtime'] == sha(runtime_path) and identity['preflight'] == sha(preflight_path)
    assert preflight['runtime_files'] == runtime['files']
    assert not preflight['failures'] and preflight['passed_contexts'] == 1200 and preflight['passed_candidates'] == 4800
    filenames = {f'{lang}-r{s}-{i:03}.json' for lang in LANGS for s in range(4) for i in range(0, 100, 5)}
    assert {p.name for p in directory.glob('*.json')} == filenames | {'identity.json'}
    records = {lang: {} for lang in LANGS}
    hashes = {}
    for filename in sorted(filenames):
        lang, rotation, start = Path(filename).stem.split('-')
        shift, start = int(rotation[1:]), int(start)
        expected = [r for r in lock['rows'] if r['language'] == lang and r['shift'] == shift
                    and start <= r['index'] < start + 5]
        assert len(expected) == 5
        path = directory / filename
        data = json.loads(path.read_text(encoding='utf-8'))
        validate_shard(data, expected, lang)
        hashes[filename] = sha(path)
        lookup = {(r['source'], r['question']): r for r in expected}
        for sample in data['samples']['belebele_' + lang]:
            key = sample['doc']['link'], sample['doc']['question_number']
            item = lookup[key]
            assert item['target'] == (item['original_target'] - shift) % 4
            record = records[lang].setdefault(key, dict(source=key[0], question=key[1],
                target=item['original_target'], choices=item['original_choices'], rotations=[None] * 4))
            assert record['target'] == item['original_target'] and record['choices'] == item['original_choices']
            assert record['rotations'][shift] is None
            record['rotations'][shift] = [r[0] for r in sample['filtered_resps']]
    for language in LANGS:
        assert len(records[language]) == 100
        assert all(all(v is not None for v in r['rotations']) for r in records[language].values())
    return {lang: list(rows.values()) for lang, rows in records.items()}, dict(
        identity=identity, runtime=runtime, shard_sha256=hashes)


def summarize(root, replicates=10000):
    lock = json.loads((root / 'rotation-lock.json').read_text(encoding='utf-8'))
    assert len(lock['rows']) == 1200
    spec_path = Path(__file__).resolve().parents[1] / 'configs/option-rotation.json'
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    assert lock['spec_sha256'] == sha(spec_path)
    assert lock['original_lock_sha256'] == spec['original_lock_sha256']
    expected_keys = {(lang, index, shift) for lang in LANGS for index in range(100) for shift in range(4)}
    assert {(r['language'], r['index'], r['shift']) for r in lock['rows']} == expected_keys
    for row in lock['rows']:
        member = spec['sample_membership'][row['index']]
        assert (row['source'], row['question']) == (member['source'], member['question'])
    cells, evidence = {}, {}
    for arm in ARMS:
        records, evidence[arm] = load_arm(root, arm, lock)
        cells.update({(arm, lang): rows for lang, rows in records.items()})
    a, b = (evidence[arm] for arm in ARMS)
    assert a['identity']['code'] == b['identity']['code'], 'Different scoring code'
    def runtime_settings(runtime):
        command = list(runtime['server_command'])
        model = command[command.index('--model') + 1]
        command[command.index('--model') + 1] = '<model>'
        return command, runtime['packages'], {p: h for p, h in runtime['files'].items() if p != model}
    assert runtime_settings(a['runtime']) == runtime_settings(b['runtime']), 'Different runtime settings'
    stats = joint_statistics(cells, replicates=replicates)
    stats['cells'] = {arm: {lang: stats['cells'][arm, lang] for lang in LANGS} for arm in ARMS}
    detailed, flips = [], {}
    for language in LANGS:
        mappings = {arm: {(r['source'], r['question']): r for r in cells[arm, language]} for arm in ARMS}
        predictions = {arm: measure(cells[arm, language])[1] for arm in ARMS}
        tally = {mode: [Counter() for _ in range(4)] for mode in ('raw', 'cross_fitted')}
        for key, record in mappings['bf16-gguf'].items():
            other = mappings['local-q4'][key]
            assert record['choices'] == other['choices']
            item = dict(language=language, source=key[0], question=key[1], target=record['target'],
                        identical_text_choice_pairs=[[i, j] for i in range(4) for j in range(i)
                                                     if record['choices'][i] == record['choices'][j]], predictions={})
            for mode in tally:
                item['predictions'][mode] = {arm: predictions[arm][mode][key] for arm in ARMS}
                for shift in range(4):
                    x, y = (predictions[arm][mode][key][shift] for arm in ARMS)
                    kind = ('unchanged' if x == y else 'right_to_wrong' if x == record['target']
                            else 'wrong_to_right' if y == record['target'] else 'wrong_to_wrong')
                    tally[mode][shift][kind] += 1
            detailed.append(item)
        flips[language] = tally
    return dict(statistics=stats, paired_flip_counts=flips, items=detailed, evidence=evidence,
                lock_sha256=sha(root / 'rotation-lock.json'),
                interpretation='Diagnostic development results; raw and cross-fitted scores stay separate. '
                'No canonical scoring decision or causal mechanism is implied. Identical text flags use exact equality; '
                'semantic synonyms require manual review. Report invalid bootstrap counts with intervals.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = summarize(args.root)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
