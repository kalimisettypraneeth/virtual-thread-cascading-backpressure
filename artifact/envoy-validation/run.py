"""Verify pinned bytes, frozen oracle and all literal expectations; emit complete snapshots."""
import hashlib
import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from comparator import Comparator

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results/envoy-validation'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    freeze = json.loads((OUT / 'oracle-freeze.json').read_text())
    assert freeze['oracle_sha256'] == sha(HERE / 'oracle.json'), 'oracle changed after freeze'
    started = datetime.now(timezone.utc).isoformat()
    assert freeze['frozen_at_utc'] < started
    provenance = json.loads((HERE / 'provenance.json').read_text())
    for file in provenance['files']:
        path = HERE / file['file']
        data = path.read_bytes()
        assert sha(path) == file['sha256']
        assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == file['git_blob_sha1']
    rows = []
    checks = 0
    for case in json.loads((HERE / 'oracle.json').read_text())['cases']:
        model = Comparator(case['config'])
        events = [({'event': 'initial'}, case['initial'], model.snapshot())]
        for step in case['steps']:
            events.append(({k: v for k, v in step.items() if k != 'expected'}, step['expected'], model.step(step)))
        for index, (event, expected, actual) in enumerate(events):
            mismatches = {k: {'expected': v, 'actual': actual.get(k)} for k, v in expected.items() if actual.get(k) != v}
            checks += len(expected)
            rows.append({'case': case['name'], 'step': index, 'event': event,
                         'expected': expected, 'actual': actual, 'mismatches': mismatches})
    report = {'status': 'PASS' if not any(r['mismatches'] for r in rows) else 'FAIL',
              'scope': 'Reduced aggregate-boundary comparator only; no official binary execution or universal trace equivalence',
              'started_at_utc': started, 'oracle_freeze': freeze,
              'python': sys.version, 'platform': platform.platform(),
              'tool_availability': {t: shutil.which(t) for t in ['envoy', 'bazel', 'bazelisk', 'docker']},
              'upstream_revision': provenance['revision'],
              'inputs_sha256': {p.name: sha(p) for p in [HERE / n for n in ['oracle.json', 'comparator.py', 'run.py', 'provenance.json']]},
              'snapshots': len(rows), 'field_assertions': checks, 'traces': rows}
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['status']} {len(rows)} snapshots / {checks} field assertions")
    if report['status'] != 'PASS':
        print(json.dumps([r for r in rows if r['mismatches']], indent=2))
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
