import gzip
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from scripts import archive_scoring_variants as arch


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.arms = {}
        evidence = {}
        for arm in arch.ARMS:
            directory = self.root / arm
            directory.mkdir()
            self.arms[arm] = directory
            identity = b'{"synthetic_identity":true}\r\n'
            (directory / 'identity.json').write_bytes(identity)
            hashes = {}
            for name in arch.shard_names():
                original = ('{"synthetic_shard":"' + name + '","unicode":"অ"}\r\n').encode('utf-8')
                (directory / name).write_bytes(original)
                hashes[name] = arch.digest(original)
            evidence[arm] = dict(identity_sha256=arch.digest(identity), shard_sha256=hashes)
        self.report = self.root / 'final-report.json'
        cells = [dict(key=[arm, variant, language], value=dict(unique_questions=100, rotation_contexts=400))
            for arm in arch.ARMS for variant in arch.VARIANTS for language in arch.LANGUAGES]
        self.report.write_text(json.dumps(dict(evidence=dict(lock_sha256=arch.LOCK, arms=evidence),
            statistics=dict(bootstrap_replicates=10000,bootstrap_seed=42,cells=cells))), encoding='utf-8')
        self.destination = self.root / 'archive'

    def create(self, destination=None):
        return arch.archive(self.report, self.arms, destination or self.destination,
            lock_location='/original/request-lock.json', evaluation_commit='1' * 40, runtime_commit='2' * 40)

    def test_lossless_deterministic_roundtrip_and_originals_unchanged(self):
        before = {p: p.read_bytes() for directory in self.arms.values() for p in directory.iterdir()}
        first = self.create()
        self.assertEqual(len(first['files']), 1443)
        self.assertEqual(len(first['archives']), 3)
        self.assertEqual(first, arch.verify_archive(self.destination))
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        second_directory = self.root / 'archive-second'
        second = self.create(second_directory)
        self.assertEqual(first, second)
        for name in first['archives']:
            self.assertEqual((self.destination / name).read_bytes(), (second_directory / name).read_bytes())
        with self.assertRaisesRegex(ValueError, 'must be new'):
            self.create()

    def test_missing_or_changed_shard_cannot_create_archive(self):
        source = self.arms['bf16-gguf'] / sorted(arch.shard_names())[0]
        original = source.read_bytes()
        source.unlink()
        with self.assertRaisesRegex(ValueError, 'source shard inventory'):
            self.create()
        self.assertFalse(self.destination.exists())
        source.write_bytes(original + b'changed')
        with self.assertRaisesRegex(ValueError, 'Original hash mismatch'):
            self.create()
        self.assertFalse(self.destination.exists())

    def test_corrupt_archive_and_unsafe_member_rejected_without_extraction(self):
        self.create()
        path = self.destination / 'local-q4.tar.gz'
        original = path.read_bytes()
        path.write_bytes(original + b'corruption')
        with self.assertRaisesRegex(ValueError, 'Compressed hash'):
            arch.verify_archive(self.destination)
        # Updating the outer hash cannot authorize traversal/links/duplicate names.
        for name, kind in (('../escape.json', tarfile.REGTYPE),
                           ('local-q4/identity.json', tarfile.SYMTYPE),
                           ('duplicate', tarfile.REGTYPE)):
            with self.subTest(member=name, kind=kind):
                buffer = io.BytesIO()
                with tarfile.open(fileobj=buffer, mode='w') as tar:
                    if name == 'duplicate':
                        for _ in range(2):
                            info = tarfile.TarInfo('local-q4/identity.json')
                            tar.addfile(info, io.BytesIO(b''))
                    else:
                        info = tarfile.TarInfo(name)
                        info.type = kind
                        tar.addfile(info, io.BytesIO(b''))
                packed = gzip.compress(buffer.getvalue(), mtime=0)
                path.write_bytes(packed)
                manifest_path = self.destination / 'archive-manifest.json'
                index = json.loads(manifest_path.read_text())
                index['archives']['local-q4.tar.gz'] = dict(bytes=len(packed),sha256=arch.digest(packed))
                manifest_path.write_text(json.dumps(index), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'tar member'):
                    arch.verify_archive(self.destination)
        self.assertFalse((self.root / 'escape.json').exists())


if __name__ == '__main__':
    unittest.main()
