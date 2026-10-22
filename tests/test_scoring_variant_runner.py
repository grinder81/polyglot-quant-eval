import copy
import unittest
import tempfile
from pathlib import Path

from scripts.run_scoring_variants import task_document, validate, validate_directory_files


class RunnerValidationTests(unittest.TestCase):
    def setUp(self):
        self.rows=[]
        self.samples=[]
        for i in range(5):
            row=dict(source='passage',question=i,prompt='Question '+str(i),candidates=[' A',' B',' C',' D'],target=1,choice_character_lengths=[1]*4)
            self.rows.append(row)
            self.samples.append(dict(doc=row,target=1,arguments=[[row['prompt'],c] for c in row['candidates']],filtered_resps=[[-3,False],[-1,False],[-4,False],[-2,False]],acc=1,acc_norm=1))
        self.data=dict(samples=dict(a3_locked=self.samples))

    def test_valid_scores(self):
        result=validate(self.data,self.rows,'bf16-gguf')
        self.assertEqual(result[0]['scores'],[-3,-1,-4,-2])

    def test_projection_preserves_locked_tokens(self):
        self.rows[0]['model_token_ids']=[[2,7]]*4
        self.samples[0]['doc']=task_document(self.rows[0])
        result=validate(self.data,self.rows,'bf16-gguf')
        self.assertNotIn('model_token_ids',self.samples[0]['doc'])
        self.assertEqual(result[0]['model_token_ids'],[[2,7]]*4)

    def test_corruption(self):
        for failure in ('missing','duplicate','nan','prompt','choice','target','normalized'):
            with self.subTest(failure=failure):
                data=copy.deepcopy(self.data)
                samples=data['samples']['a3_locked']
                if failure=='missing': samples.pop()
                elif failure=='duplicate': samples[1]=copy.deepcopy(samples[0])
                elif failure=='nan': samples[0]['filtered_resps'][0][0]=float('nan')
                elif failure=='prompt': samples[0]['arguments'][0][0]='changed'
                elif failure=='choice': samples[0]['arguments'][0][1]='AA'
                elif failure=='target': samples[0]['target']=2
                elif failure=='normalized': samples[0]['acc_norm']=0
                with self.assertRaises((AssertionError,KeyError)):
                    validate(data,self.rows,'bf16-gguf')

    def test_directory_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            (path/'identity.json').write_text('{}')
            validate_directory_files(path)
            for name in ('unexpected.json','eng_Latn-plain-letter-r0-000.tmp'):
                target=path/name
                target.write_text('{}')
                with self.assertRaises(ValueError):
                    validate_directory_files(path)
                target.unlink()


if __name__=='__main__':
    unittest.main()
