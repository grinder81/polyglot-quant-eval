import copy
import unittest

from scripts.report import compare, index_rows


def fixture():
    rows = []
    for run, runtime, fmt, en, bn in [('original', 'vllm', 'bf16', .9, .7),
            ('control', 'llama_cpp_python', 'bf16', .8, .6),
            ('q4', 'llama_cpp_python', 'gguf-q4_k_m', .7, .55)]:
        for lang, value in [('en', en), ('bn', bn)]:
            rows.append(dict(run_id=run, runtime=runtime, runtime_version='pinned', format=fmt,
                model_id='tiny', model_revision='same-source', task='belebele', metric='acc',
                language=lang, mode='loglikelihood_mcq', fewshot=0, n=300, value=value,
                sample_set_hash='verified-membership', scoring_contract_hash='verified-contract',
                backend='cuda', device='rtx5090', os_version='pinned'))
    return rows


class ReportReferencesTest(unittest.TestCase):
    def test_three_distinct_comparisons_and_english_gap(self):
        result = compare(fixture(), 'original', 'control', ['q4'])
        bn = {r['comparison']: r for r in result if r['language'] == 'bn'}
        self.assertAlmostEqual(bn['runtime/conversion']['delta'], -.1)
        self.assertAlmostEqual(bn['same-runtime compression']['delta'], -.05)
        self.assertAlmostEqual(bn['total difference']['delta'], -.15)
        self.assertAlmostEqual(bn['same-runtime compression']['gap_vs_english'], .05)
        self.assertTrue(all(r['n'] == 300 and 'unavailable' in r['uncertainty'] for r in result))

    def test_incompatible_and_unknown_comparisons_fail(self):
        for field, value in [('n', 50), ('mode', 'generation'), ('fewshot', 5),
                             ('sample_set_hash', 'another-set'), ('scoring_contract_hash', 'chat-template'),
                             ('runtime_version', 'changed'), ('model_revision', None)]:
            rows = fixture()
            for row in rows:
                if row['run_id'] == 'q4':
                    row[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                compare(rows, 'original', 'control', ['q4'])

    def test_duplicates_and_missing_english_do_not_average(self):
        rows = fixture()
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            index_rows(rows + [copy.deepcopy(rows[0])])
        with self.assertRaisesRegex(ValueError, 'English'):
            compare([r for r in rows if r['language'] == 'bn'], 'original', 'control', ['q4'])


if __name__ == '__main__':
    unittest.main()
