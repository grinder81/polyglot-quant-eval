import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import summarize_t1_baselines as report
from scripts.run_scoring_variants import task_document


def records():
    return [dict(language=lang,source=f's{i//150}',question=i,index=i,
        variant='plain-letter',shift=0,target=0,original_target=0,
        choices=list('ABCD'),candidates=[' A',' B',' C',' D'],
        choice_character_lengths=[1]*4,scores=[0.,-1.,-2.,-3.])
        for lang in report.LANGS for i in range(300)]


class T1StatisticsTests(unittest.TestCase):
    def test_complete_source_paired_damage_and_english_interaction(self):
        reference=report.normalize(records())
        candidate=copy.deepcopy(reference)
        for row in candidate:
            if row['source']=='s0':
                row.update(scores=[-1.,0.,-2.,-3.],prediction=1,correct=0)
        result=report.paired_report(reference,candidate,replicates=80)
        self.assertEqual(result['source_clusters'],2)
        for row in result['languages'].values():
            self.assertEqual((row['reference_correct'],row['candidate_correct']), (300,150))
            self.assertEqual((row['changed_choices'],row['right_to_wrong'],row['wrong_to_right'],row['wrong_to_wrong']),
                             (150,150,0,0))
            self.assertEqual(row['accuracy_delta_candidate_minus_reference'],-.5)
            self.assertEqual(row['paired_cluster_95_delta_interval'],[-1.,0.])
            self.assertEqual(row['paired_cluster_95_delta_minus_english_interval'],[0.,0.])
            self.assertEqual(row['joint_source_95_intervals']['changed_choices_rate'],[0.,1.])
            self.assertEqual(row['candidate_predicted_letters'],{'A':150,'B':150,'C':0,'D':0})
        self.assertEqual(report.fresh_margin_report(reference,candidate)['input_schema'],
                         'validated-t1-original-order')

    def test_complete_identical_requests_candidate_and_margin_deltas(self):
        historical=report.normalize(records())
        fresh=copy.deepcopy(historical)
        for row in fresh:
            row['scores']=[x-.01 for x in row['scores']]
        result=report.historical_comparison(historical,fresh,replicates=5)
        self.assertEqual(len(result['records']),900)
        for lang,distributions in result['descriptive_distributions'].items():
            self.assertEqual(distributions['signed_candidate_delta_nats']['n'],1200)
            self.assertAlmostEqual(distributions['signed_candidate_delta_nats']['mean'],-.01)
            self.assertAlmostEqual(distributions['margin_delta_nats']['max'],0.)
            self.assertEqual(result['outcomes_historical_to_fresh']['languages'][lang]['changed_choices'],0)

    def test_reject_incomplete_rotated_bad_candidates_scores_and_targets(self):
        for kind in ('incomplete','duplicate','rotation','candidates','nan','question'):
            with self.subTest(kind=kind):
                rows=records()
                if kind=='incomplete':rows.pop()
                elif kind=='duplicate':rows[-1]=copy.deepcopy(rows[-2])
                elif kind=='rotation':rows[0]['shift']=1
                elif kind=='candidates':rows[0]['candidates'][0]='A'
                elif kind=='nan':rows[0]['scores'][0]=float('nan')
                elif kind=='question':rows[0]['question']=None
                with self.assertRaises(ValueError):report.normalize(rows)
        ref=report.normalize(records())
        cand=copy.deepcopy(ref)
        cand[0].update(target=1,correct=0)
        with self.assertRaisesRegex(ValueError,'Target mismatch'):
            report.paired_report(ref,cand,replicates=1)

    def test_tie_policy_and_fresh_margin_stays_descriptive(self):
        rows=records()
        for row in rows:row['scores']=[0.,0.,-1.,-2.]
        reference=report.normalize(rows)
        self.assertTrue(all(row['prediction']==0 for row in reference))
        result=report.fresh_margin_report(reference,reference)
        self.assertIn('exploratory',result['interpretation'])
        for value in result['results'].values():
            self.assertEqual(value['bins'][0]['n'],300)
            self.assertEqual(value['total_flips'],0)

    def test_historical_request_matching_rejects_changed_prompt_target_order_or_membership(self):
        fresh=records()
        for row in fresh:row['prompt_sha256']='a'*64
        membership=dict(items=[{lang:dict(source=f's{i//150}',question=i,target=0,
            prompt_sha256='a'*64,candidate_sha256=[hashlib.sha256(c.encode()).hexdigest()
                for c in [' A',' B',' C',' D']]) for lang in report.LANGS} for i in range(300)])
        report.verify_historical_requests(fresh,membership)
        for kind in ('prompt','target','order','missing','duplicate'):
            with self.subTest(kind=kind):
                changed=copy.deepcopy(membership)
                item=changed['items'][0]['eng_Latn']
                if kind=='prompt':item['prompt_sha256']='b'*64
                elif kind=='target':item['target']=1
                elif kind=='order':item['candidate_sha256'].reverse()
                elif kind=='missing':changed['items'].pop()
                elif kind=='duplicate':changed['items'][1]=copy.deepcopy(changed['items'][0])
                with self.assertRaises(ValueError):report.verify_historical_requests(fresh,changed)


class CompleteT1EvidenceTests(unittest.TestCase):
    """Real T1 saved-shard/identity validator; only external environment is mocked.

    run_identity's byte-pinned installed-client/A3 environment is independently
    tested by the runner. These tests keep its expected identity fixed while
    passing actual 360 raw five-question shards through verify_run_identity.
    """
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.rows=records()
        for row in self.rows:
            i=row['index']
            row.update(dataset_index=i,prompt=f"{row['language']} question {i}",
                model_context_ids=[2,10+i],wire_context_ids=[10+i],
                model_token_ids=[[2,10+i,100+c] for c in range(4)],
                wire_token_ids=[[10+i,100+c] for c in range(4)])
            row['prompt_sha256']=hashlib.sha256(row['prompt'].encode()).hexdigest()
            row.pop('scores')
        self.lock=self.root/'lock.json'
        self.write(self.lock,dict(schema='t1-original-order-v1',context=8192,rows=self.rows))
        self.inputs={}
        self.identities={}
        self.runtimes={}
        self.cells={}
        for arm in report.ARMS:
            directory=self.root/arm;directory.mkdir()
            self.inputs[arm]=dict(directory=directory,token_check=self.root/f'{arm}-tokens.json')
            runtime=dict(arm=arm,server_command=['python','--model',arm+'.gguf'],
                files={arm+'.gguf':'a'*64,'native.so':'b'*64},packages='pinned',
                provenance=dict(original_runtime_sha256=arm,patch_sha256='c'*64,
                                additional_patch_sha256='d'*64,protocol_sha256='e'*64))
            identity=dict(schema='t1-cold-original-order-v1',arm=arm,
                lock_sha256=hashlib.sha256(self.lock.read_bytes()).hexdigest(),
                readiness_sha256='a'*64,a3_record_sha256='b'*64,a3_evidence=dict(synthetic=True),
                model_args=dict(base_url='http://synthetic/v1/completions',batch_size=1),versions=dict(synthetic='1'),
                tokenizer=dict(synthetic='c'*64),files={'synthetic.py':'d'*64},scorer='unchanged upstream',
                endpoint_models=[arm+'.gguf'],expanded_gate_sha256=dict(synthetic='e'*64),
                expanded_gate_paths=dict(synthetic='unused; external environment mocked'))
            self.identities[arm]=identity;self.runtimes[arm]=runtime
            self.write(directory/'identity.json',identity)
            for lang in report.LANGS:
                self.cells[arm,'plain-letter',lang]=[dict(source=r['source'],question=r['question'],
                    rotations=[[0.,-1.,-2.,-3.]]*4) for r in self.rows if r['language']==lang and r['index']<100]
                for start in range(0,300,5):
                    samples=[]
                    for row in self.rows:
                        if row['language']==lang and start<=row['index']<start+5:
                            samples.append(dict(doc=task_document(row),target=0,
                                arguments=[[row['prompt'],c] for c in row['candidates']],
                                filtered_resps=[[score,False] for score in (0.,-1.,-2.,-3.)],acc=1,acc_norm=1))
                    self.write(directory/f'{lang}-{start:03}.json',dict(samples=dict(a3_locked=samples)))
        def environment(*args,**kwargs):
            arm=args[6]
            return copy.deepcopy(self.identities[arm]),self.rows,self.cells,copy.deepcopy(self.runtimes[arm])
        self.environment=patch('scripts.t1_baselines.run_identity',side_effect=environment)
        self.environment.start();self.addCleanup(self.environment.stop)

    @staticmethod
    def write(path,data):path.write_text(json.dumps(data),encoding='utf-8')

    def load(self):
        return report.load_complete(self.lock,'ready','a3lock','a3record','tokenizer',
                                    self.inputs,'http://synthetic/v1/completions')

    def test_complete_actual_shard_schema_and_full_report_pipeline(self):
        fresh,provenance=self.load()
        self.assertEqual(len(fresh['bf16-gguf']),900)
        self.assertTrue(all(p['complete'] and len(p['shard_sha256'])==180 for p in provenance.values()))
        self.assertEqual(len(provenance['bf16-gguf']['overlap']['comparisons']),300)
        with patch.object(report,'load_historical',return_value=(fresh,dict(synthetic=True))):
            final=report.build_report(self.lock,'ready','a3lock','a3record','tokenizer',self.inputs,
                'http://synthetic/v1/completions','historical-ref','historical-q4',replicates=5)
        self.assertEqual(final['schema'],'t1-complete-report-v1')
        self.assertEqual(final['fresh_margin']['input_schema'],'validated-t1-original-order')
        self.assertEqual(final['historical_to_fresh_by_arm']['local-q4']['records'][0]['candidate_deltas_nats'],[0.]*4)
        json.dumps(final,allow_nan=False)

    def test_incomplete_corrupt_requests_scores_targets_and_checkpoint_rejected(self):
        directory=self.inputs['local-q4']['directory'];shard=directory/'hin_Deva-000.json'
        original=shard.read_bytes();marker=directory/'identity.json';identity_bytes=marker.read_bytes()
        for kind in ('missing','unexpected','duplicate','nan','target','arguments','identity','gate','bool_batch_size'):
            with self.subTest(kind=kind):
                extra=directory/'extra.json';data=json.loads(original)
                if kind=='missing':shard.unlink()
                elif kind=='unexpected':self.write(extra,data)
                elif kind in ('identity','gate','bool_batch_size'):
                    identity=json.loads(identity_bytes)
                    if kind=='identity':identity['files']['synthetic.py']='changed'
                    elif kind=='gate':identity['expanded_gate_sha256']['synthetic']='changed'
                    else:identity['model_args']['batch_size']=True
                    self.write(marker,identity)
                else:
                    samples=data['samples']['a3_locked']
                    if kind=='duplicate':samples[1]=copy.deepcopy(samples[0])
                    elif kind=='nan':samples[0]['filtered_resps'][0][0]=float('nan')
                    elif kind=='target':samples[0]['target']=1
                    elif kind=='arguments':samples[0]['arguments'][0][1]=' B'
                    self.write(shard,data)
                with self.assertRaises((ValueError,AssertionError,KeyError)):self.load()
                shard.write_bytes(original);marker.write_bytes(identity_bytes)
                if extra.exists():extra.unlink()

    def test_mismatched_paired_runtime_is_rejected(self):
        self.runtimes['local-q4']['packages']='different'
        with self.assertRaisesRegex(ValueError,'paired runtime/client'):self.load()

    def test_historical_adapter_rejects_model_change_after_validated_old_inputs(self):
        fresh_rows=report.normalize([row|dict(scores=[0.,-1.,-2.,-3.]) for row in self.rows])
        mapped={('belebele_'+row['language'],row['source'],row['question']):(row['scores'],row['target'])
                for row in fresh_rows}
        roots=[self.root/'old-reference',self.root/'old-candidate']
        by_index={(row['language'],row['index']):row for row in self.rows}
        membership=dict(items=[{lang:dict(source=by_index[lang,i]['source'],question=i,target=0,
            prompt_sha256=by_index[lang,i]['prompt_sha256'],candidate_sha256=[
                hashlib.sha256(c.encode()).hexdigest() for c in [' A',' B',' C',' D']])
            for lang in report.LANGS} for i in range(300)])
        for root,arm in zip(roots,report.ARMS):
            root.mkdir()
            self.write(root/'sample-identities.json',membership)
            self.write(root/f'{arm}-runtime.json',self.runtimes[arm])
        with patch.object(report,'load_historical_pair',return_value=(mapped,mapped,dict(synthetic=True))):
            historical,_=report.load_historical(*roots,self.rows,self.runtimes)
            self.assertEqual(len(historical['local-q4']),900)
            self.runtimes['local-q4']['files']['local-q4.gguf']='f'*64
            with self.assertRaisesRegex(ValueError,'model artifact changed'):
                report.load_historical(*roots,self.rows,self.runtimes)


if __name__=='__main__':unittest.main()
