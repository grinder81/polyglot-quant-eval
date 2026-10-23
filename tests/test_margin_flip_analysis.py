import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import margin_flip_analysis as mfa


class MarginTests(unittest.TestCase):
    def records(self):
        ref = {('t', 's1', '1'): ([0., -.1, -5, -6], 0),
               ('t', 's1', '2'): ([0., -3., -5, -6], 0),
               ('t', 's2', '1'): ([-.7, 0., -5, -6], 1)}
        cand = copy.deepcopy(ref)
        cand['t', 's1', '1'] = ([-.2, 0., -5, -6], 0)
        return ref, cand

    def test_bins_flips_ties_absolute_success_and_empty_bins(self):
        ref, cand = self.records()
        result = mfa.analyze(ref, cand)['t']
        self.assertEqual((result['n'], result['total_flips'], result['source_clusters']), (3, 1, 2))
        self.assertEqual((result['reference_correct'], result['candidate_correct']), (3, 2))
        self.assertEqual(result['bins'][0]['flips'], 1)
        self.assertIsNone(result['bins'][1]['flip_rate'])
        self.assertEqual(result['bins'][-1]['n'], 1)
        self.assertAlmostEqual(result['share_margin_below_1_nat'], 2/3)
        self.assertEqual(mfa.argmax([0., 0., -1, -2]), 0)
        tie = {('t', 's', 'q'): ([0., 0., -1, -2], 0)}
        self.assertEqual(mfa.analyze(tie, tie)['t']['bins'][0]['n'], 1)

    def test_partial_overlap_targets_missing_identity_and_nonfinite_rejected(self):
        for kind in ('missing', 'extra', 'target', 'question', 'nan', 'infinity', 'bool', 'overflow'):
            with self.subTest(kind=kind):
                ref, cand = self.records()
                key = next(iter(cand))
                if kind == 'missing': cand.pop(key)
                elif kind == 'extra': cand['t', 'other', '1'] = cand[key]
                elif kind == 'target': cand[key] = (cand[key][0], 1)
                elif kind == 'question':
                    ref['t', 's', None] = ref.pop(key)
                    cand['t', 's', None] = cand.pop(key)
                else:
                    bad = {'nan': float('nan'), 'infinity': float('inf'), 'bool': True,
                           'overflow': 1e308}[kind]
                    cand[key] = ([bad, -1e308, -1e308, -1e308], 0)
                with self.assertRaises(ValueError): mfa.analyze(ref, cand)

    def test_english_relative_accuracy_delta_is_paired(self):
        ref = {(f'belebele_{lang}', 's', 'q'): ([0., -1, -2, -3], 0) for lang in mfa.LANGS}
        cand = copy.deepcopy(ref)
        cand['belebele_ben_Beng', 's', 'q'] = ([-1., 0., -2, -3], 0)
        result = mfa.analyze(ref, cand)
        self.assertEqual(result['belebele_ben_Beng']['accuracy_delta_minus_english'], -1)


class InputBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.roots = [self.root/'ref', self.root/'cand']
        self.rows = {}
        candidates = [' A', ' B', ' C', ' D']
        digest = lambda text: hashlib.sha256(text.encode()).hexdigest()
        membership = dict(original_lock_sha256='a'*64, items=[{lang: dict(index=i,
            source=f's{i//2}',question=i,target=0,prompt_sha256=digest(f'{lang}-{i}'),
            candidate_sha256=list(map(digest,candidates))) for lang in mfa.LANGS} for i in range(300)])
        for root, arm in zip(self.roots, ('bf16-gguf', 'local-q4')):
            (root/arm).mkdir(parents=True)
            self.write(root/'sample-identities.json', membership)
            runtime=dict(arm=arm,server_command=['python','--model',arm+'.gguf'], packages='pinned',
                         files={arm+'.gguf':'b'*64,'native.so':'c'*64})
            self.write(root/f'{arm}-runtime.json',runtime)
            self.write(root/arm/'identity.json',dict(arm=arm,backend='gguf',count_per_language=300,
                shard_size=5,lock='a'*64,runner='d'*64,runtime=mfa.sha(root/f'{arm}-runtime.json'),tokenizer=None))
            for lang in mfa.LANGS:
                for start in range(0,300,5):
                    samples=[]
                    for i in range(start,start+5):
                        samples.append(dict(doc=dict(link=f's{i//2}',question_number=i), target=0,
                            doc_id=i,arguments=[[f'{lang}-{i}', c] for c in candidates],
                            filtered_resps=[[score,False] for score in (0.,-1.,-2.,-3.)],acc=1))
                    self.write(root/arm/f'{lang}-{start:03}.json',dict(
                        samples={'belebele_'+lang:samples},results={'belebele_'+lang:{'acc,none':1.}}))

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value),encoding='utf-8')

    def test_complete_existing_schema_passes_reused_validator(self):
        # Keep this test about the loader; bootstrap estimates belong to its
        # existing test suite, and random.choices can use one deterministic draw.
        with patch('scripts.summarize_expanded_local.random.Random.choices',
                   side_effect=lambda population,k: population):
            ref,cand,provenance=mfa.load_pair(*self.roots)
        self.assertEqual(len(ref),900)
        self.assertEqual(ref,cand)
        self.assertEqual(len(provenance['bf16-gguf']['shard_sha256']),180)

    def test_input_corruptions_are_rejected_without_intersection(self):
        root=self.roots[1]; directory=root/'local-q4'
        shard=directory/'eng_Latn-000.json'
        original=shard.read_bytes()
        for kind in ('missing_shard','extra_shard','missing_question','duplicate_question',
                     'nan','target','candidate_order','prompt','task','membership','runner','runtime'):
            with self.subTest(kind=kind):
                data=json.loads(original)
                backup={p:p.read_bytes() for p in (shard,root/'sample-identities.json',
                    directory/'identity.json',root/'local-q4-runtime.json')}
                extra=directory/'extra.json'
                if kind=='missing_shard': shard.unlink()
                elif kind=='extra_shard': self.write(extra,data)
                elif kind=='membership':
                    membership=mfa.read(root/'sample-identities.json')
                    membership['items'][0]['eng_Latn']['question']=999
                    self.write(root/'sample-identities.json',membership)
                elif kind=='runner':
                    identity=mfa.read(directory/'identity.json');identity['runner']='e'*64
                    self.write(directory/'identity.json',identity)
                elif kind=='runtime':
                    runtime=mfa.read(root/'local-q4-runtime.json');runtime['packages']='different'
                    self.write(root/'local-q4-runtime.json',runtime)
                else:
                    sample=data['samples']['belebele_eng_Latn'][0]
                    if kind=='missing_question': sample['doc'].pop('question_number')
                    elif kind=='duplicate_question': data['samples']['belebele_eng_Latn'][1]=copy.deepcopy(sample)
                    elif kind=='nan': sample['filtered_resps'][0][0]=float('nan')
                    elif kind=='target': sample['target']=1
                    elif kind=='candidate_order': sample['arguments'][0],sample['arguments'][1]=sample['arguments'][1],sample['arguments'][0]
                    elif kind=='prompt': sample['arguments'][0][0]='changed'
                    elif kind=='task': data['samples']['unexpected']=[]
                    self.write(shard,data)
                with self.assertRaises((ValueError,KeyError)):
                    mfa.load_pair(*self.roots)
                if extra.exists():extra.unlink()
                for path,content in backup.items():path.write_bytes(content)


if __name__=='__main__':
    unittest.main()
