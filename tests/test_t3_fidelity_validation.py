import json
from pathlib import Path
import tempfile
import unittest

from scripts import validate_t3_fidelity as v


class FidelityEvidence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/'arm'
        self.directory.mkdir()
        self.rows=[]
        files={}
        for language in ('eng_Latn','ben_Beng','hin_Deva'):
            for index in range(300):
                row=dict(language=language,index=index,source=str(index),question='q',prompt_sha256='p',model_context_ids=[1,2,3])
                self.rows.append(row)
                record={k:row[k] for k in ('language','index','source','question','prompt_sha256')}
                record.update(tokens=2,token_kl=[.1,.3],mean_kl_nats=.2,top1_agreement=.5,first_chunk_cpu_oracle_max_error=1e-15)
                file=self.directory/f'{language}-{index:03}.json'
                file.write_text(json.dumps(record))
                files[file.name]=v.sha(file)
        self.manifest=dict(questions=900,tokens=1800,per_question_files=files,
            identity=dict(mode='compare',model_sha256='model',lock_sha256='lock',runtime_sha256='runtime',
                implementation_sha256=v.CORE_SHA,math_module_sha256=v.MATH_SHA,
                reference_manifest_sha256=v.REFERENCE_SHA,backend='torch2.13-float64'),
            languages={lang:dict(mean_kl_nats=.2,p50_question_kl=.2,p95_question_kl=.2,mean_question_top1_agreement=.5)
                for lang in ('eng_Latn','ben_Beng','hin_Deva')})
        self.save()

    def save(self):
        file=self.directory/'manifest.json'
        file.write_text(json.dumps(self.manifest))
        receipt=dict(status='passed',manifest_sha256=v.sha(file),runtime_sha256='runtime',
            reference_manifest_sha256=v.REFERENCE_SHA,wrapper_sha256=v.WRAPPER_SHA,verification_sha256=v.VERIFICATION_SHA,
            native_backend_initialized_before_torch=True,torch_cpu_threads=1)
        (self.directory.parent/'arm-verified.json').write_text(json.dumps(receipt))

    def validate(self):
        return v.validate(self.directory,self.rows,'model','lock','runtime')

    def test_valid_and_tampered_question(self):
        self.validate()
        file=self.directory/'eng_Latn-000.json'
        record=json.loads(file.read_text())
        record['source']='different'
        file.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError,'hash'):
            self.validate()
        self.manifest['per_question_files'][file.name]=v.sha(file)
        self.save()
        with self.assertRaisesRegex(ValueError,'source'):
            self.validate()

    def test_aggregate_and_execution_receipt_are_required(self):
        self.manifest['languages']['ben_Beng']['mean_kl_nats']=.25
        self.save()
        with self.assertRaisesRegex(ValueError,'aggregates'):
            self.validate()
        self.manifest['languages']['ben_Beng']['mean_kl_nats']=.2
        self.save()
        (self.directory.parent/'arm-verified.json').unlink()
        with self.assertRaises(FileNotFoundError):
            self.validate()


if __name__=='__main__':
    unittest.main()
