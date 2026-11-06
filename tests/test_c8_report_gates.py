import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_c8_reports import identity,native
from scripts.c8_pilot_decision import sha
from scripts.report_c8_pilot import confirmed_pair


class ReportGates(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.plan=dict(artifact_workspace=str(self.root),_sha256='plan',source_sha256='bf16',
            cap=dict(native_minutes=90,proxy_minutes=30,local_artifact_bytes=400_000_000_000),
            probe_sources={'3':['a','b','c']},operating_point={'bytes':100})
        self.directory=self.root/'report'
        self.directory.mkdir()
        self.value=dict(plan_sha256='plan',repetitions=[3],nomination_sha256='nomination',
            budget_operation_id='id',mode='reference',cases=[dict(sha256='bf16')])
        self.ledger=dict(plan_sha256='plan',operations=[dict(id='id',category='native',status='passed',seconds=1.,artifact_bytes=10)])
        self.save()

    def save(self):
        (self.root/'resource-ledger.json').write_text(json.dumps(self.ledger))
        (self.directory/'identity.json').write_text(json.dumps(self.value))
        records=[dict(repeat=3,index=i,language=language,source=self.plan['probe_sources']['3'][i],tokens=64)
            for i in range(3) for language in ('eng_Latn','ben_Beng','hin_Deva')]
        case=dict(identity_sha256=sha(self.directory/'identity.json'),case=self.value['cases'][0],records=records)
        (self.directory/'case-00.json').write_text(json.dumps(case))
        self.report=dict(identity=self.value,cases=[case])
        (self.directory/'report.json').write_text(json.dumps(self.report))

    def test_failed_final_budget_and_wrong_nomination_are_rejected(self):
        path=self.directory/'report.json'
        native(path,self.plan,[3],'reference','nomination')
        self.ledger['operations'][0]['status']='failed'
        self.save()
        with self.assertRaisesRegex(ValueError,'budget check'):
            native(path,self.plan,[3],'reference','nomination')
        self.ledger['operations'][0]['status']='passed'
        self.save()
        with self.assertRaisesRegex(ValueError,'nomination'):
            identity(path,self.plan,'native',[3],'different')

    def test_case_token_coverage_is_checked_even_when_files_agree(self):
        case=self.report['cases'][0]
        case['records'][0]['tokens']=63
        (self.directory/'case-00.json').write_text(json.dumps(case))
        (self.directory/'report.json').write_text(json.dumps(self.report))
        with self.assertRaisesRegex(ValueError,'token'):
            native(self.directory/'report.json',self.plan,[3],'reference','nomination')

    def test_confirmation_requires_both_language_directions(self):
        nomination_path=self.root/'nomination.json'
        nomination_path.write_text('{}')
        nomination=dict(pair={'map_a_bytes':90},signs={'eng_Latn':1,'ben_Beng':-1})
        report=dict(identity=dict(mode='pair',plan_sha256='plan',repetitions=[3],nomination_sha256=sha(nomination_path)),cases=[])
        for label in ('mapA','mapB'):
            records=[dict(repeat=3,index=i,language=language,source=self.plan['probe_sources']['3'][i],
                mean_kl_nats=1. if label=='mapA' else (2. if language=='eng_Latn' else .5))
                for i in range(3) for language in ('eng_Latn','ben_Beng','hin_Deva')]
            report['cases'].append(dict(case=dict(label=label,bytes=90),records=records))
        self.assertTrue(confirmed_pair(report,self.plan,nomination,nomination_path)['promising'])
        for row in report['cases'][1]['records']:
            row['mean_kl_nats']=2.
        self.assertFalse(confirmed_pair(report,self.plan,nomination,nomination_path)['promising'])


if __name__=='__main__':
    unittest.main()
