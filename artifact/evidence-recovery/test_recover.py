import hashlib
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import recover


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'root'; self.root.mkdir()
        (self.root / 'logs').mkdir()
        (self.root / 'logs/data').write_bytes(b'original\x00bytes\n')
        self.plan = {'schema': 1, 'files': {'logs/data': hashlib.sha256(b'original\x00bytes\n').hexdigest()}}
        self.path = self.base/'plan.json'
        self.path.write_text(json.dumps(self.plan))
        self.output = self.base/'out.tar'

    def test_complete_original_bytes_and_metadata(self):
        records = recover.collect(self.root, self.path, self.output)
        with tarfile.open(self.output) as tar:
            self.assertEqual(tar.extractfile('originals/logs/data').read(), b'original\x00bytes\n')
            self.assertEqual(tar.extractfile('RECOVERY_PLAN.json').read(), self.path.read_bytes())
            meta = json.load(tar.extractfile('RECOVERY_MANIFEST.json'))
            self.assertEqual(meta['files'], records)
            self.assertEqual(records[0]['observed_mtime_ns'], (self.root/'logs/data').stat().st_mtime_ns)
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o600)

    def test_dry_run_does_not_archive(self):
        recover.collect(self.root, self.path)
        self.assertFalse(self.output.exists())

    def test_missing(self):
        (self.root/'logs/data').unlink()
        with self.assertRaisesRegex(OSError, "missing or unsafe original logs/data"): recover.collect(self.root, self.path, self.output)
        self.assertFalse(self.output.exists())

    def test_mismatch(self):
        (self.root/'logs/data').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'): recover.collect(self.root, self.path, self.output)
        self.assertFalse(self.output.exists())

    def test_paths(self):
        for path in ['../escape', '/absolute', 'a/../b', 'a//b', './a', 'C:/x', 'a\\b', 'a\nb']:
            with self.subTest(path=path), self.assertRaises(ValueError): recover.safe_name(path)

    def test_file_link(self):
        (self.root/'logs/data').unlink()
        (self.root/'logs/data').symlink_to(self.path)
        with self.assertRaises(OSError): recover.collect(self.root, self.path, self.output)

    def test_parent_link(self):
        (self.root/'logs/data').unlink(); (self.root/'logs').rmdir()
        (self.root/'logs').symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(OSError): recover.collect(self.root, self.path, self.output)

    def test_never_overwrites(self):
        self.output.write_bytes(b'keep')
        with self.assertRaises(ValueError): recover.collect(self.root, self.path, self.output)
        self.assertEqual(self.output.read_bytes(), b'keep')

    def test_fifo_rejected_without_block(self):
        import os
        (self.root/'logs/data').unlink(); os.mkfifo(self.root/'logs/data')
        with self.assertRaises(ValueError): recover.collect(self.root, self.path, self.output)


if __name__ == '__main__': unittest.main()
