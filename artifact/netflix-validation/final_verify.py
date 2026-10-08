from pathlib import Path
import csv,hashlib,json,subprocess,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifact/results/netflix-validation/20261008-official'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
preserved=json.loads((OUT/'preservation.json').read_text())
for row in preserved['source_files']:assert sha(ROOT/row['file'])==row['expected']
assert sha(ROOT/'artifact/review/VT_BASELINE_VALIDATION_AUDIT_20261008.zip')==preserved['audit_zip_sha256']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='9de5ffcaf74c378134ff7132cc60186ce8f8803b'
assert not subprocess.check_output(['git','diff','--name-only'],cwd=ROOT).strip()
for name,h in json.loads((OUT/'oracle-freeze.json').read_text())['files'].items():assert sha(ROOT/name)==h
for name,h in json.loads((OUT/'listener-workload-freeze.json').read_text())['tests_sha256'].items():assert sha(ROOT/'artifact/netflix-validation'/name)==h
case_results=[]
for jdk in ['jdk21','jdk25']:
 for mode in ['platform','virtual','reactive']:
  p=OUT/'cases'/f'{jdk}-{mode}';a=json.loads((p/'assertions.json').read_text());assert a['status']=='PASS';assert a['borrows']==a['releases']==10 and a['active_at_end']==0
  expected=''.join(f'{i},REJECT,\n' if i%3==2 else f'{i},OK,{7*i+3}\n' for i in range(12));assert (p/'outcomes.csv').read_text()==expected
  case_results.append({'case':p.name,'status':'PASS'})
locks=ROOT/'artifact/netflix-validation/locks'
rows=json.loads((locks/'resolved-dependencies.json').read_text())['artifacts']
for r in rows:assert sha(OUT/r['cache_path'])==r['sha256']
for r in json.loads((locks/'integration-dependencies.json').read_text())['artifacts']:assert sha(OUT/'runtime-dependencies'/r['filename'])==r['sha256']
tests=json.loads((OUT/'official-test-summary.json').read_text());assert tests['passed']==56 and tests['failures']==tests['errors']==0
assert len(json.loads((OUT/'conformance-results.json').read_text()))==108
commands=[json.loads(l) for l in (OUT/'commands.jsonl').read_text().splitlines()]
for label in ['official-core-tests-jdk11','official-core-offline-locked','compile-integration','conformance','check-conformance','cleanup-db','cleanup-network']:
 assert next(c for c in commands if c['label']==label)['exit_code']==0,label
summary={'scope':'Official Netflix core build, deterministic Gradient2 conformance, and six bounded adapter correctness cases; no performance conclusion','status':'PASS','base_commit':'9de5ffcaf74c378134ff7132cc60186ce8f8803b','upstream_revision':'78a74b9878d38c4c048b0304ce12a162ab7b7222','new_checks':{'preserved_source_files':14,'synthetic_helper_tests':5,'official_core_tests':tests,'frozen_conformance_samples':108,'adapter_cases':case_results,'dependency_metadata_hashes':len(rows),'integration_jar_hashes':30},'historical_only':'Original 30-case matrix and 94 assertions were not rerun. Existing audit was not recreated. Initial/final source and ZIP integrity were newly verified.','resolved_failures':['initial upstream configuration failed because Git unavailable in base JDK image','next configuration failed because required JDK11 toolchain unavailable'],'unattempted':['non-core upstream module test suites','three upstream ignored executor simulations','active-server-query cancellation and network/connection-creation/cleanup-callback faults','dynamic database-driven adaptation under offered load','JNI/FFM coverage','performance benchmarks'],'blocked':[],'aggregate_scientific_readiness':'OPEN'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
