"""Freeze hand-derived inputs/expectations before running the comparator."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results/envoy-validation'
OUT.mkdir(parents=True, exist_ok=True)
oracle = HERE / 'oracle.json'
record = {'oracle_sha256': hashlib.sha256(oracle.read_bytes()).hexdigest(),
          'frozen_at_utc': datetime.now(timezone.utc).isoformat(),
          'method': 'Literal expected states authored from pinned upstream source before comparator execution; no model import or output dependency.'}
with (OUT / 'oracle-freeze.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(record['oracle_sha256'])
