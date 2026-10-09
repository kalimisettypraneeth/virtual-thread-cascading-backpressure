"""Synthetic failure/preflight packaging checks; not runtime validation."""
import hashlib,json,tempfile,unittest
from pathlib import Path
import run
from run import finalize
from unittest.mock import patch
class Finalization(unittest.TestCase):
    def test_preflight_and_failure_raw_hashes(self):
        for status in ('UNATTEMPTED','FAIL'):
            with tempfile.TemporaryDirectory() as tmp:
                out=Path(tmp);(out/'failed-command.stdout').write_text('raw retained\n');(out/'failed-command.exitcode').write_text('2\n')
                finalize(out,{'status':status,'runtime_status':'UNATTEMPTED','last_command':'failed-command','last_exit_code':2})
                self.assertEqual(json.loads((out/'outcome.json').read_text())['status'],status)
                entries=(out/'SHA256SUMS').read_text().splitlines();self.assertEqual(len(entries),3)
                for entry in entries:
                    digest,name=entry.split('  ',1);self.assertEqual(digest,hashlib.sha256((out/name).read_bytes()).hexdigest())
    def test_entry_finalizes_compile_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            def failed():
                run.OUTPUT=out;(out/'compile.stderr').write_text('synthetic compile error\n')
                run.STATE.update(java_compilation='FAIL',runtime_status='UNATTEMPTED',failed_command='compile',failed_exit_code=1)
                raise RuntimeError('synthetic compile failed')
            with patch.object(run,'main',failed):self.assertEqual(run.entry(),1)
            state=json.loads((out/'outcome.json').read_text());self.assertEqual(state['status'],'FAIL');self.assertEqual(state['runtime_status'],'UNATTEMPTED')
            self.assertIn('compile.stderr',(out/'SHA256SUMS').read_text())
if __name__=='__main__':unittest.main(verbosity=2)
