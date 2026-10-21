import copy
import hashlib
import unittest

from scripts.run_rotation_shards import validate_shard


class RotationShardTest(unittest.TestCase):
    def fixture(self):
        expected = [dict(source=f's{i}', question='1', target=i % 4,
                    prompt_sha256=hashlib.sha256(f'prompt{i}'.encode()).hexdigest(),
                    candidates=[' A', ' B', ' C', ' D']) for i in range(5)]
        samples = [dict(doc=dict(link=r['source'], question_number=r['question']),
                       target=r['target'], acc=1,
                       arguments=[[f'prompt{i}', c] for c in r['candidates']],
                       filtered_resps=[[0 if j == r['target'] else -1, False] for j in range(4)])
                   for i, r in enumerate(expected)]
        return expected, dict(samples={'belebele_ben_Beng': samples},
                              results={'belebele_ben_Beng': {'acc,none': 1}})

    def test_reordered_rows_join_by_source_question(self):
        expected, data = self.fixture()
        data['samples']['belebele_ben_Beng'].reverse()
        validate_shard(data, expected, 'ben_Beng')

    def test_rejects_stale_rotation_wrong_score_and_duplicate(self):
        expected, data = self.fixture()
        for mutation in ('prompt', 'target', 'score', 'duplicate'):
            changed = copy.deepcopy(data)
            rows = changed['samples']['belebele_ben_Beng']
            if mutation == 'prompt':
                rows[0]['arguments'][0][0] += ' rotated'
            elif mutation == 'target':
                rows[0]['target'] = 2
            elif mutation == 'score':
                rows[0]['filtered_resps'][0][0] = float('nan')
            else:
                rows[-1] = rows[0]
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                validate_shard(changed, expected, 'ben_Beng')


if __name__ == '__main__':
    unittest.main()
