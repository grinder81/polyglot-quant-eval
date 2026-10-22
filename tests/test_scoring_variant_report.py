"""Complete synthetic evidence exercises the report's actual lock/shard boundary."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import summarize_scoring_variants as report
from scripts.run_scoring_variants import task_document


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.rows = []
        for language in report.LANGUAGES:
            for variant in report.VARIANTS:
                for shift in range(4):
                    for index in range(100):
                        original = ['অ', 'bb', 'ccc', 'dddd']
                        choices = ([original[(p + shift) % 4] for p in range(4)]
                                   if variant == 'plain-option-text' else list('ABCD'))
                        special = language != 'hin_Deva' and shift == 0
                        size = 3 if special and index == 1 else 2 if special and index == 2 else 1
                        context = [] if special and index == 2 else [1] * (size - 1 if size > 1 else 1)
                        self.rows.append(dict(source=f's{index // 2}', question=str(index),
                            language=language, variant=variant, shift=shift, index=index,
                            original_target=0, target=(-shift) % 4, original_choices=original,
                            choices=choices, choice_character_lengths=list(map(len, choices)),
                            prompt=f'{language}/{index}/{shift}', candidates=[' ' + c for c in choices],
                            model_token_ids=[[1] * size] * 4, model_context_ids=context))
        tokenizer = self.root / 'tokenizer'
        tokenizer.mkdir()
        self.write(tokenizer / 'tokenizer.json', {'synthetic': True})
        tokenizer_files = {'tokenizer.json': report.sha(tokenizer / 'tokenizer.json')}
        self.lock = self.root / 'lock.json'
        self.write(self.lock, dict(rows=self.rows, provenance=dict(tokenizer_files=tokenizer_files)))
        self.lock_hash = report.sha(self.lock)
        self.lock_patch = patch.object(report, 'LOCK', self.lock_hash)
        self.lock_patch.start()
        self.addCleanup(self.lock_patch.stop)
        selection = report.validation_selection(self.rows)
        self.assertEqual(len(selection), 48)
        source = self.root / 'protocol.py'
        source.write_text('synthetic cold validation protocol', encoding='utf-8')
        protocol = report.sha(source)
        protocol_document = self.root / 'protocol.md'
        protocol_document.write_text('Protocol document differs from validator source.', encoding='utf-8')
        runner = Path(report.__file__).with_name('run_scoring_variants.py').resolve()
        self.arms = {}
        for arm in report.ARMS:
            directory = self.root / arm
            directory.mkdir()
            paths = dict(directory=directory, **{n: self.root / f'{arm}-{n}.json'
                for n in ('runtime', 'validation', 'oracle', 'order_validation')})
            paths.update(validator_script=source, protocol=protocol_document)
            self.arms[arm] = paths
            model = self.root / f'{arm}.gguf'
            model.write_text(arm, encoding='utf-8')
            runtime = dict(arm=arm, server_command=['python', '-m', 'server', '--model', str(model)],
                files={str(model): report.sha(model), str(source): protocol}, packages='synthetic',
                provenance=dict(protocol_sha256=report.sha(protocol_document),
                                patch_sha256=protocol, additional_patch_sha256=protocol))
            self.write(paths['runtime'], runtime)
            base = dict(lock_sha256=self.lock_hash, runtime_sha256=report.sha(paths['runtime']),
                script_sha256=protocol, selection=selection, failures=[], order_check=False)
            pairs = [(i, c) for i in selection for c in range(4)]
            self.write(paths['oracle'], base | dict(server_model_settings=dict(model=str(model), n_ctx=8192),
                records=[dict(row=i, candidate=c) for i, c in pairs]))
            gate = base | dict(oracle_sha256=report.sha(paths['oracle']),
                source_files={str(source): protocol}, tokenizer_files=tokenizer_files,
                versions=dict(client='synthetic'), a2_bridge_failures=[],
                records=[dict(row=i, candidate=c, errors=[]) for i, c in pairs],
                predictions=[dict(row=i) for i in selection])
            self.write(paths['validation'], gate)
            reverse = list(reversed([(i, c) for i in selection if self.rows[i]['index'] == 0
                and self.rows[i]['shift'] == 0 for c in range(4)]))
            self.write(paths['order_validation'], base | dict(order_check=True,
                oracle_sha256=report.sha(paths['oracle']), records=[dict(row=i,candidate=c,errors=[]) for i,c in reverse]))
            identity = dict(arm=arm, lock_sha256=self.lock_hash,
                runtime_sha256=report.sha(paths['runtime']), validation_sha256=report.sha(paths['validation']),
                order_validation_sha256=report.sha(paths['order_validation']), files={str(runner):report.sha(runner)},
                tokenizer=tokenizer_files, versions=gate['versions'], scorer='synthetic upstream scorer',
                endpoint_models=[str(model)],
                model_args=dict(model='a3-locked',base_url='http://localhost/v1/completions',
                    tokenizer=str(tokenizer), tokenizer_backend='huggingface',tokenized_requests=False,
                    add_bos_token=False,max_length=8192,batch_size=1))
            self.write(directory / 'identity.json', identity)
            shards = {}
            for row in self.rows:
                name = f"{row['language']}-{row['variant']}-r{row['shift']}-{row['index']//5*5:03}.json"
                scores = [0 if p == row['target'] else -10 for p in range(4)]
                sample = dict(doc=task_document(row), target=row['target'],
                    arguments=[[row['prompt'], c] for c in row['candidates']],
                    filtered_resps=[[score, False] for score in scores], acc=1, acc_norm=1)
                shards.setdefault(name, []).append(sample)
            for name, samples in shards.items():
                self.write(directory / name, dict(samples=dict(a3_locked=samples)))

    @staticmethod
    def write(path, value):
        Path(path).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')

    def test_complete_rotated_option_text_and_serialization(self):
        cells, evidence = report.load_evidence(self.lock, self.arms)
        self.assertEqual(len(cells), 18)
        self.assertTrue(all(len(rows) == 100 for rows in cells.values()))
        stats = report.joint_statistics(cells, replicates=2)
        self.assertEqual(stats['cells']['bf16-gguf', 'plain-option-text', 'ben_Beng'][
            'metrics']['acc_norm_accuracy_average'], 1)
        json.dumps(dict(evidence=evidence, statistics=report.json_ready(stats)), allow_nan=False)

    def test_missing_hindi_duplicate_shard_tampered_score_and_identity(self):
        directory = self.arms['bf16-gguf']['directory']
        shard = directory / 'hin_Deva-plain-letter-r0-000.json'
        original = shard.read_bytes()
        shard.unlink()
        with self.assertRaisesRegex(ValueError, 'shard files'):
            report.load_evidence(self.lock, self.arms)
        shard.write_bytes(original)
        duplicate = directory / 'duplicate.json'
        duplicate.write_bytes(original)
        with self.assertRaisesRegex(ValueError, 'shard files'):
            report.load_evidence(self.lock, self.arms)
        duplicate.unlink()
        data = report.read(shard)
        data['samples']['a3_locked'][0]['filtered_resps'][0][0] = float('nan')
        self.write(shard, data)
        with self.assertRaisesRegex(ValueError, 'Invalid shard'):
            report.load_evidence(self.lock, self.arms)
        shard.write_bytes(original)
        identity = report.read(directory / 'identity.json')
        identity['lock_sha256'] = 'changed'
        self.write(directory / 'identity.json', identity)
        with self.assertRaisesRegex(ValueError, 'identity lock'):
            report.load_evidence(self.lock, self.arms)


if __name__ == '__main__':
    unittest.main()
