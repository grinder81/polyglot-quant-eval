"""Raw expanded-gate revalidation rejects false empty-failure claims."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from scripts import t1_baselines as t
from tests.test_t1_runner import lock_fixture


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.lock=self.root/'lock.json';self.write(self.lock,lock_fixture())
        self.runtime=self.root/'runtime.json'
        source=self.root/'source.py';source.write_text('source')
        self.paths={n:str(self.root/(n+'.json')) for n in
            ('oracle','validation','order_validation','validator_script','protocol')}
        for n in ('validator_script','protocol'):Path(self.paths[n]).write_text(n)
        settings=dict(model='model.gguf',n_ctx=8192)
        self.write(self.runtime,dict(files={str(source):t.sha(source),'model.gguf':'modelhash'}))
        self.previous=dict(source_files={str(source):t.sha(source)},versions={'client':'1'},tokenizer_files={'tok':'hash'})
        self.oldoracle=dict(server_model_settings=settings,bos_id=5,eos_id=6)
        rows=lock_fixture()['rows'];selection=t.validation_selection(rows)
        common=dict(lock_sha256=t.sha(self.lock),runtime_sha256=t.sha(self.runtime),
            script_sha256=t.sha(self.paths['validator_script']),protocol_sha256=t.sha(self.paths['protocol']),
            selection=selection,failures=[])
        oracle=common|dict(server_model_settings=settings,bos_id=5,eos_id=6,
            imported_runtime_files={str(source.resolve()):t.sha(source)},records=[])
        client=common|self.previous|dict(order_check=False,records=[],predictions=[])
        for i in selection:
            for c in range(4):
                oracle['records'].append(dict(row=i,candidate=c,model_ids=rows[i]['model_token_ids'][c],
                    supplied_logprobs=[-1.,-1.,-1.-c],generated_id=40,generated_logprob=-.1,
                    echo_strings=['x','y','z','g'],repeat_max_logprob_error=0.))
                response=dict(choices=[dict(logprobs=dict(tokens=['x','y','z','g'],
                    token_logprobs=[None,-1.,-1.-c,-.1],top_logprobs=[{}]*4,text_offset=[0]*4))],
                    usage=dict(prompt_tokens=4,completion_tokens=1))
                client['records'].append(dict(row=i,candidate=c,errors=[],
                    payload=dict(model='t1-validation',prompt=rows[i]['prompt']+rows[i]['candidates'][c],
                        temperature=0,max_tokens=1,echo=True,logprobs=1,seed=1234),
                    response=response,parsed=[-1.-c,False],direct_sum=-1.-c))
            client['predictions'].append(dict(row=i,direct=dict(prediction=0,margin=1.),
                client=dict(prediction=0,margin=1.),inversion=False,tie_sensitive=False))
        self.write(self.paths['oracle'],oracle)
        client['oracle_sha256']=t.sha(self.paths['oracle'])
        self.client=client
        self.reset()

    @staticmethod
    def write(path,data):Path(path).write_text(json.dumps(data),encoding='utf-8')

    def reset(self):
        self.write(self.paths['validation'],self.client)
        order=copy.deepcopy(self.client);order['order_check']=True;order['records'].reverse()
        self.write(self.paths['order_validation'],order)

    def verify(self):
        return t.verify_expanded_gate(self.lock,self.runtime,self.paths,self.previous,self.oldoracle)

    def test_valid_raw_gate(self):
        self.assertEqual(set(self.verify()),set(self.paths))

    def test_empty_claims_cannot_hide_raw_corruption(self):
        for kind in ('token','nan','parser','payload','source','empty','prediction'):
            self.reset()
            data=t.read(self.paths['order_validation']);rec=data['records'][0]
            if kind=='token':rec['response']['choices'][0]['logprobs']['token_logprobs'][2]+=.0003
            if kind=='nan':rec['response']['choices'][0]['logprobs']['token_logprobs'][1]=float('nan')
            if kind=='parser':rec['parsed'][0]+=.0000001
            if kind=='payload':rec['payload']['seed']=0
            if kind=='source':data['source_files']={}
            if kind=='empty':data['records']=[]
            if kind=='prediction':data['predictions'][0]['direct']['margin']=99
            self.write(self.paths['order_validation'],data)
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.verify()

    def test_wrong_direct_settings_rejected(self):
        data=t.read(self.paths['oracle']);data['server_model_settings']['n_ctx']=512
        self.write(self.paths['oracle'],data)
        for n in ('validation','order_validation'):
            d=t.read(self.paths[n]);d['oracle_sha256']=t.sha(self.paths['oracle']);self.write(self.paths[n],d)
        with self.assertRaises(ValueError):self.verify()
