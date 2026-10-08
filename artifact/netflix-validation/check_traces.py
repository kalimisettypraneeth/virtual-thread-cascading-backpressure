from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifact/results/netflix-validation/20261008-official'
freeze=json.loads((OUT/'oracle-freeze.json').read_text())
for name,h in freeze['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
expected=json.loads((OUT/'expected-traces.json').read_text())['rows']
actual=[line.split(',') for line in (OUT/'logs/conformance.stdout').read_text().splitlines()]
assert len(actual)==len(expected)
checks=[]
for e,a in zip(expected,actual):
 ok=a[0]==e['scenario'] and int(a[1])==e['index'] and int(a[2])==e['limit'] and abs(int(a[3])-e['longRttNs'])<=1 and int(a[4])==e['notifications']
 checks.append({'scenario':e['scenario'],'index':e['index'],'status':'PASS' if ok else 'FAIL','actual':a,'expected':e})
(OUT/'conformance-results.json').write_text(json.dumps(checks,indent=2)+'\n')
assert all(c['status']=='PASS' for c in checks)
print('PASS',len(checks),'frozen independently derived trace samples')
