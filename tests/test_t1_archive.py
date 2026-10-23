"""Synthetic byte-preservation tests, not a T1 numerical result or inference."""
import copy
import gzip
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from scripts import archive_t1_baselines as archive


class T1ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.destination=self.root/'package'
        self.preparation=self.root/'preparation.json'
        self.write(self.preparation,dict(synthetic=True))
        self.report=dict(schema='t1-complete-report-v1',provenance=dict(fresh={}),fresh_rows={},
            fresh_paired_GGUF=self.summary(),historical_to_fresh_by_arm={},
            fresh_margin=dict(input_schema='validated-t1-original-order'))
        self.record=dict(arms={},report_command=['python','-m','scripts.summarize_t1_baselines'])
        for arm,prefix in zip(archive.ARMS,('bf16','q4')):
            directory=self.root/arm;directory.mkdir()
            hashes={}
            for name in archive.shard_names():
                data=('synthetic raw shard '+arm+'/'+name+'\r\n').encode()
                (directory/name).write_bytes(data);hashes[name]=archive.digest(data)
            gate_paths={};gate_hashes={}
            for name,member in archive.GATES.items():
                path=self.root/f'{arm}-{member}'
                path.write_bytes(('synthetic '+name+' '+arm+'\n').encode())
                gate_paths[name]=str(path);gate_hashes[name]=archive.digest(path.read_bytes())
            runtime=dict(arm=arm,server_command=['python','--model',arm+'.gguf'],
                files={arm+'.gguf':'a'*64,'native.so':'b'*64})
            runtime_path=self.root/f'{arm}-runtime.json';self.write(runtime_path,runtime)
            token_path=self.root/f'{arm}-tokens.json';self.write(token_path,dict(synthetic=True,arm=arm))
            identity=dict(schema='t1-cold-original-order-v1',arm=arm,lock_sha256='c'*64,
                model_args=dict(base_url='http://synthetic/v1/completions',batch_size=1),
                expanded_gate_paths=gate_paths,expanded_gate_sha256=gate_hashes,
                runtime_sha256=archive.digest(runtime_path.read_bytes()),
                token_check_sha256=archive.digest(token_path.read_bytes()),
                readiness_sha256=archive.digest(self.preparation.read_bytes()))
            self.write(directory/'identity.json',identity)
            self.report['provenance']['fresh'][arm]=dict(identity=identity,runtime=runtime,
                complete=True,shard_sha256=hashes)
            self.report['fresh_rows'][arm]=[dict(language=lang,source=f's{i//2}',question=str(i))
                for lang in archive.LANGS for i in range(300)]
            self.report['historical_to_fresh_by_arm'][arm]=dict(outcomes_historical_to_fresh=self.summary())
            self.record['arms'][arm]=dict(runtime_manifest=str(runtime_path),
                runtime_manifest_sha256=identity['runtime_sha256'])
            self.record['report_command'] += ['--'+prefix+'-directory',str(directory),
                                             '--'+prefix+'-token-check',str(token_path)]
        self.record['report_command'] += ['--readiness',str(self.preparation),'--base-url',
            'http://synthetic/v1/completions','--lock','/retained/request-lock-not-opened.json']
        self.report_path=self.root/'report.json';self.record_path=self.root/'execution-record.json'
        self.write(self.report_path,self.report)
        self.record['archive_completion']=dict(schema='t1-completed-execution-receipt-v1',
            collection_complete=True,report_exit_code=0,
            report_sha256=archive.digest(self.report_path.read_bytes()),report_bytes=len(self.report_path.read_bytes()),
            arms={arm:dict(validated_shards=180,validated_questions=900,runner_exit_code=0,server_stopped=True)
                  for arm in archive.ARMS})
        self.write(self.record_path,self.record)

    @staticmethod
    def summary():return dict(bootstrap_replicates=10000,bootstrap_seed=42,
        languages={lang:dict(n=300) for lang in archive.LANGS})

    @staticmethod
    def write(path,data):path.write_text(json.dumps(data,indent=2)+'\r\n',encoding='utf-8')

    def create(self,destination=None):
        return archive.create(self.report_path,archive.digest(self.report_path.read_bytes()),
            self.record_path,archive.digest(self.record_path.read_bytes()),destination or self.destination)

    def test_complete_lossless_deterministic_and_portable_verification(self):
        originals={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        first=self.create()
        self.assertEqual(len(first['files']),379)
        self.assertEqual(set(first['archives']),set(archive.groups()))
        self.assertFalse(first['lock_reference']['included'])
        self.assertEqual(originals,{p:p.read_bytes() for p in originals})
        second_path=self.root/'second';second=self.create(second_path)
        self.assertEqual(first,second)
        for name in archive.groups():
            self.assertEqual((self.destination/name).read_bytes(),(second_path/name).read_bytes())
        # Verification never opens the original paths: only package streams.
        for p in originals:p.unlink()
        self.assertEqual(archive.verify(self.destination),first)
        with self.assertRaisesRegex(ValueError,'identity mismatch'):
            archive.verify(self.destination,expected_report_sha256='0'*64)

    def test_missing_changed_source_typed_identity_and_partial_report_rejected(self):
        directory=self.root/'local-q4';shard=directory/sorted(archive.shard_names())[0]
        identity=directory/'identity.json'
        for kind in ('missing','changed','identity_bool','gate','partial_report'):
            with self.subTest(kind=kind):
                backups={p:p.read_bytes() for p in (shard,identity,self.report_path,self.record_path)}
                gate=Path(self.report['provenance']['fresh']['local-q4']['identity']['expanded_gate_paths']['oracle'])
                backups[gate]=gate.read_bytes()
                if kind=='missing':shard.unlink()
                elif kind=='changed':shard.write_bytes(b'changed')
                elif kind=='identity_bool':
                    data=json.loads(identity.read_bytes());data['model_args']['batch_size']=True
                    self.write(identity,data)
                elif kind=='gate':gate.write_bytes(b'changed gate')
                else:
                    data=copy.deepcopy(self.report);data['fresh_rows']['local-q4'].pop()
                    self.write(self.report_path,data)
                    record=copy.deepcopy(self.record)
                    record['archive_completion'].update(report_sha256=archive.digest(self.report_path.read_bytes()),
                                                       report_bytes=len(self.report_path.read_bytes()))
                    self.write(self.record_path,record)
                with self.assertRaises(ValueError):self.create()
                self.assertFalse(self.destination.exists())
                for p,data in backups.items():p.write_bytes(data)

    def test_proposal_failed_report_or_partial_completion_receipts_rejected(self):
        original=self.record_path.read_bytes()
        for kind in ('proposal','report_exit_bool','report_hash','collection_bool','partial_arm','live_server'):
            with self.subTest(kind=kind):
                record=copy.deepcopy(self.record);proof=record['archive_completion']
                if kind=='proposal':record.pop('archive_completion')
                elif kind=='report_exit_bool':proof['report_exit_code']=False
                elif kind=='report_hash':proof['report_sha256']='0'*64
                elif kind=='collection_bool':proof['collection_complete']=1
                elif kind=='partial_arm':proof['arms']['local-q4']['validated_shards']=179
                else:proof['arms']['local-q4']['server_stopped']=False
                self.write(self.record_path,record)
                with self.assertRaises(ValueError):self.create()
                self.assertFalse(self.destination.exists())
                self.record_path.write_bytes(original)

    def test_archive_corruption_unsafe_link_duplicate_and_overwrite_rejected(self):
        self.create()
        with self.assertRaisesRegex(ValueError,'must be new'):self.create()
        packed_path=self.destination/'validation.tar.gz';packed=packed_path.read_bytes()
        packed_path.write_bytes(packed+b'corruption')
        with self.assertRaisesRegex(ValueError,'Compressed hash'):archive.verify(self.destination)
        for kind in ('traversal','symlink','duplicate'):
            with self.subTest(kind=kind):
                buffer=io.BytesIO()
                with tarfile.open(fileobj=buffer,mode='w') as tar:
                    for _ in range(2 if kind=='duplicate' else 1):
                        name='../escape.json' if kind=='traversal' else 'validation/preparation.json'
                        info=tarfile.TarInfo(name)
                        if kind=='symlink':info.type=tarfile.SYMTYPE;info.linkname='../escape.json'
                        tar.addfile(info,io.BytesIO(b''))
                data=gzip.compress(buffer.getvalue(),mtime=0);packed_path.write_bytes(data)
                manifest_path=self.destination/'archive-manifest.json'
                manifest=json.loads(manifest_path.read_bytes())
                manifest['archives']['validation.tar.gz']=dict(bytes=len(data),sha256=archive.digest(data))
                self.write(manifest_path,manifest)
                with self.assertRaisesRegex(ValueError,'tar member'):archive.verify(self.destination)
        self.assertFalse((self.root/'escape.json').exists())


if __name__=='__main__':unittest.main()
