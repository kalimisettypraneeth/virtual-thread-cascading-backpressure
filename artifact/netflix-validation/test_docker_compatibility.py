"""Synthetic regression tests against preserved helper and its actual platform guard."""
import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'artifact/runtime-validation/run.py'
spec = importlib.util.spec_from_file_location('runtime_validation', PATH)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class ConfigTests(unittest.TestCase):
    def config(self, data, count=1):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'saved.tar'
            with tarfile.open(p, 'w') as t:
                for name, body in [('manifest.json', json.dumps([{'Config':'actual.json'}]*count).encode()), ('actual.json',data)]:
                    member=tarfile.TarInfo(name); member.size=len(body); t.addfile(member,io.BytesIO(body))
            return runner.saved_image_config(p)
    def test_actual_bytes_not_reserialized_json(self):
        b=b'{ "architecture": "amd64", "os": "linux" }\n'
        h,c=self.config(b)
        self.assertEqual(h,'sha256:'+hashlib.sha256(b).hexdigest())
        self.assertNotEqual(h,'sha256:'+hashlib.sha256(json.dumps(c).encode()).hexdigest())
    def test_changed_byte_changes_digest(self):
        self.assertNotEqual(self.config(b'{"os":"linux"}')[0], self.config(b'{"os":"linux"} ')[0])
    def test_ambiguous_manifest_rejected(self):
        with self.assertRaises(runner.Failure): self.config(b'{}',2)
    def test_empty_manifest_rejected(self):
        with self.assertRaises(runner.Failure): self.config(b'{}',0)
    def test_actual_linux_amd64_guard(self):
        tree=ast.parse(PATH.read_text())
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='assertion' and len(n.args)>1 and isinstance(n.args[1],ast.BinOp) and isinstance(n.args[1].left,ast.Constant) and n.args[1].left.value=='saved image platform ']
        self.assertEqual(len(calls),1)
        code=compile(ast.Expression(calls[0].args[0]),str(PATH),'eval')
        for config,valid in [({'os':'linux','architecture':'amd64'},True),({'os':'linux','architecture':'arm64'},False),({'os':'windows','architecture':'amd64'},False),({},False)]:
            with self.subTest(config=config):
                run=runner.Run.__new__(runner.Run);run.assertions=[]
                if valid: run.assertion(eval(code,{'config':config}),'platform')
                else:
                    with self.assertRaises(runner.Failure):run.assertion(eval(code,{'config':config}),'platform')
if __name__=='__main__': unittest.main(verbosity=2)
