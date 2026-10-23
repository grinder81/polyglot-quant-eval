"""Synthetic boundary tests: never import a model runtime or call an endpoint."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts import t1_baselines as t
from scripts.run_scoring_variants import task_document


def lock_fixture():
    rows=[]
    for language in t.LANGUAGES:
        for index in range(300):
            text=f'{language} question {index} Answer:'
            rows.append(dict(language=language,index=index,dataset_index=index,source=f'source{index//2}',
                question=index,target=index%4,original_target=index%4,variant='plain-letter',shift=0,
                prompt=text,prompt_sha256=hashlib.sha256(text.encode()).hexdigest(),
                choices=list('ABCD'),candidates=[' A',' B',' C',' D'],choice_character_lengths=[1]*4,
                model_context_ids=[5,10,20],wire_context_ids=[10,20],
                model_token_ids=[[5,10,20,c] for c in range(30,34)],
                wire_token_ids=[[10,20,c] for c in range(30,34)]))
    return dict(schema='t1-original-order-v1',context=8192,rows=rows)


def samples(rows):
    return dict(samples=dict(a3_locked=[dict(doc=copy.deepcopy(task_document(r)),target=r['target'],
        arguments=[[r['prompt'],c] for c in r['candidates']],
        filtered_resps=[[-2.],[-3.],[-4.],[-5.]],acc=int(r['target']==0),
        acc_norm=int(r['target']==0)) for r in rows]))


class T1Tests(unittest.TestCase):
    def test_exact900_and_shards(self):
        lock=lock_fixture()
        rows=t.validate_lock(lock)
        self.assertEqual(len(t.expected_shards(rows)),180)
        self.assertEqual(t.validation_selection(rows),[0,100,299,300,400,599,600,700,899])
        for change in ('missing','duplicate','target','continuation','bos','prompt','order'):
            bad=copy.deepcopy(lock)
            if change=='missing': bad['rows'].pop()
            if change=='duplicate': bad['rows'][1]['question']=0
            if change=='target': bad['rows'][0]['target']=True
            if change=='continuation': bad['rows'][0]['model_token_ids'][0].append(42)
            if change=='bos': bad['rows'][0]['wire_context_ids'].insert(0,5)
            if change=='prompt': bad['rows'][0]['prompt']+=' '
            if change=='order': bad['rows'][0],bad['rows'][1]=bad['rows'][1],bad['rows'][0]
            with self.subTest(change=change),self.assertRaises(ValueError): t.validate_lock(bad)

    def test_saved_shard_request_and_numeric_validation(self):
        rows=lock_fixture()['rows'][:5]
        self.assertEqual(len(t.validate(samples(rows),rows,'bf16-gguf')),5)
        for change in ('duplicate','missing','nan','boolean','wrong_prompt','wrong_choice','target','metric'):
            bad=samples(rows); s=bad['samples']['a3_locked'][0]
            if change=='duplicate': bad['samples']['a3_locked'][1]=copy.deepcopy(s)
            if change=='missing': bad['samples']['a3_locked'].pop()
            if change=='nan': s['filtered_resps'][0][0]=float('nan')
            if change=='boolean': s['filtered_resps'][0][0]=True
            if change=='wrong_prompt': s['arguments'][0][0]+=' '
            if change=='wrong_choice': s['doc']['choices'][0]='wrong'
            if change=='target': s['target']=3
            if change=='metric': s['acc']=1-s['acc']
            with self.subTest(change=change),self.assertRaises((AssertionError,ValueError,KeyError)):
                t.validate(bad,rows,'bf16-gguf')

    def test_overlap_intersection_and_inversion(self):
        rows=lock_fixture()['rows'][:1]
        cells={(a,'plain-letter',l):[] for a in t.ARMS for l in t.LANGUAGES}
        cells['bf16-gguf','plain-letter','eng_Latn']=[dict(source=rows[0]['source'],question=0,
            rotations=[[-1.,-2.,-3.,-4.]]*4)]
        row=rows[0]|dict(scores=[-1.0003,-2.,-3.,-4.])
        result=t.overlap_check([row],cells,'bf16-gguf')
        self.assertTrue(result['comparisons'][0]['sum_pass'])
        self.assertFalse(result['comparisons'][0]['token_pass'])
        self.assertEqual(len(result['failures']),1)
        cells['bf16-gguf','plain-letter','eng_Latn'][0]['rotations'][0]=[-1.,-1.0001,-3.,-4.]
        row['scores']=[-1.00015,-1.0001,-3.,-4.]
        result=t.overlap_check([row],cells,'bf16-gguf')
        self.assertFalse(result['failures'])
        self.assertEqual(len(result['inversions']),1)

    def test_all_present_shards_validated_even_after_missing(self):
        rows=lock_fixture()['rows']
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'eng_Latn-295.json'
            path.write_text(json.dumps(samples(rows[295:300])))
            records,hashes=t.load_shards(folder,rows,'local-q4')
            self.assertEqual(len(records),5)
            self.assertEqual(list(hashes),[path.name])
            with self.assertRaises(ValueError): t.load_shards(folder,rows,'local-q4',complete=True)
            path.with_suffix('.tmp').write_text('failure')
            with self.assertRaises(ValueError): t.load_shards(folder,rows,'local-q4')

    def test_optimized_python_rejected_before_loading(self):
        result=subprocess.run([sys.executable,'-O','-c',
            "from scripts.t1_baselines import load_shards;load_shards('.',[],'local-q4')"],
            capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('without -O',result.stderr)


if __name__=='__main__': unittest.main()
