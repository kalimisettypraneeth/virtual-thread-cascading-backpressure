"""Negative controls: verify the gate detects implementation/oracle/source tampering."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

class ValidationTests(unittest.TestCase):
    def run_copy(self, mutate):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'artifact'
            code = root / 'envoy-validation'
            result = root / 'results/envoy-validation'
            shutil.copytree(HERE, code, ignore=shutil.ignore_patterns('__pycache__'))
            result.mkdir(parents=True)
            shutil.copyfile(HERE.parent / 'results/envoy-validation/oracle-freeze.json', result / 'oracle-freeze.json')
            mutate(code)
            proc = subprocess.run([sys.executable, str(code / 'run.py')], capture_output=True, text=True)
            report = json.loads((result / 'validation.json').read_text()) if (result / 'validation.json').exists() else None
            return proc, report

    def test_clean_copy(self):
        proc, report = self.run_copy(lambda _: None)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(report['field_assertions'], 112)

    def test_oracle_mutation_rejected_before_run(self):
        def mutate(code):
            with (code / 'oracle.json').open('a') as stream:
                stream.write(' ')
        proc, report = self.run_copy(mutate)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('oracle changed after freeze', proc.stderr)
        self.assertIsNone(report)

    def test_upstream_mutation_rejected(self):
        def mutate(code):
            with (code / 'upstream/gradient_controller.cc').open('a') as stream:
                stream.write('// changed\n')
        proc, report = self.run_copy(mutate)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIsNone(report)

    def test_wrong_gradient_is_falsified(self):
        def mutate(code):
            p = code / 'comparator.py'
            p.write_text(p.read_text().replace('min(2.,', 'min(1.,'))
        proc, report = self.run_copy(mutate)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(report['status'], 'FAIL')
        self.assertTrue(any('gradient' in r['mismatches'] for r in report['traces']))

if __name__ == '__main__':
    unittest.main(verbosity=2)
