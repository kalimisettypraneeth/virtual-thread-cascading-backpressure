#!/usr/bin/env python3
"""Build a compact, privacy-redacted audit from existing evidence; execute no workloads."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / 'artifact/review'
RUN = ROOT / 'artifact/results/runtime-validation/20261008T064525Z-e67bd535'
PREFIX = RUN.relative_to(ROOT).as_posix()
ZIP = REVIEW / 'VT_BASELINE_VALIDATION_AUDIT_20261008.zip'

def digest(data): return hashlib.sha256(data).hexdigest()
def file_digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''): h.update(chunk)
    return h.hexdigest()
def encode(value): return (json.dumps(value, indent=2, sort_keys=True)+'\n').encode()
def redact(data):
    text = data.decode('utf-8')
    text = text.replace(str(ROOT), '<REPO_ROOT>').replace(str(Path.home()), '<USER_HOME>')
    text = text.replace('POSTGRES_PASSWORD=smoke', 'POSTGRES_PASSWORD=<REDACTED_FIXTURE_PASSWORD>')
    return text.encode()

manifest = json.loads((RUN/'manifest.json').read_text())
assertions = json.loads((RUN/'assertions.json').read_text())
assert len(assertions) == 94 and all(a['status']=='PASS' for a in assertions)
assert json.loads((RUN/'summary.json').read_text())['status']=='PASS'
verified = []
for line in (RUN/'SHA256SUMS').read_text().splitlines():
    expected, name = line.split('  ', 1)
    assert file_digest(RUN/name)==expected, name
    verified.append({'path':name, 'sha256':expected, 'status':'PASS'})
assert len(verified)==408
matrix = manifest['matrix']
case_results = []
for jdk in matrix['jdk']:
    for control in matrix['controls']:
        expected = ''.join(f'{i},OK,{7*i+3}\n' if control=='pool-only' or i%3<2 else f'{i},REJECT,\n' for i in range(12))
        for mode in matrix['modes']:
            name=f'{jdk}-{control}-{mode}'; case=RUN/'cases'/name
            a=json.loads((case/'assertions.json').read_text())
            assert a['status']=='PASS' and a['active_at_end']==0 and a['observed_peak']<=2
            assert (case/'outcomes.csv').read_text()==expected, name
            case_results.append({'case':name, 'status':'PASS', 'exact_outcomes_verified':True})
assert len(case_results)==30
pins=[]
for jdk in matrix['jdk']:
    for mode in ['platform','virtual']:
        case=f'{jdk}-pin-{mode}'
        p=json.loads((RUN/'cases'/case/'pinning.json').read_text())
        events=json.loads(next((RUN/'logs').glob('*jfr-events-'+case+'.stdout')).read_text())['recording']['events']
        count=sum(e['type']=='jdk.VirtualThreadPinned' for e in events)
        markers=sum(e['type']=='validation.Scenario' for e in events)
        assert count==p['pin_events'] and markers==p['scenario_markers']==4
        assert count==(4 if jdk=='jdk21' and mode=='virtual' else 0)
        pins.append({'case':case, 'pins':count, 'markers':markers, 'status':'PASS'})
for path, expected in manifest['source_sha256'].items():
    assert file_digest(ROOT/path)==expected, path
patch=subprocess.run(['git','diff','--binary','--','artifact/runtime-validation/run.py'],cwd=ROOT,capture_output=True,check=True).stdout
assert patch and patch==(ROOT/'artifact/results/runtime-validation/20261008T064525Z-e67bd535-review/compatibility-fix.patch').read_bytes()
assert subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,check=True,text=True).stdout.strip()==manifest['source_head']
config_evidence=[]
config_blobs={}
for key, entry in manifest['images']['images'].items():
    with tarfile.open(RUN/f'image-{key}.tar') as t:
        index=json.load(t.extractfile('manifest.json'));assert len(index)==1
        config=t.extractfile(index[0]['Config']).read()
    assert 'sha256:'+digest(config)==entry['config_digest']
    facts=json.loads(config);assert facts['architecture']=='amd64' and facts['os']=='linux'
    config_blobs[f'artifact/review/image-configs/{key}.json']=config
    config_evidence.append({'image':key,'config_digest':'sha256:'+digest(config),'platform':'linux/amd64','status':'PASS'})
commands=[json.loads(line) for line in (RUN/'commands.jsonl').read_text().splitlines()]
nonzero=[c for c in commands if c['exit_code']]
assert len(nonzero)==1 and nonzero[0]['argv'][3]=='pg_isready' and nonzero[0]['exit_code']==2
info=json.loads((RUN/'logs/003-docker-info.stdout').read_text())
assert manifest['machine']=='arm64' and info['Architecture']=='aarch64'
for jdk, version in [('jdk21','21.0.12.1+1'),('jdk25','25.0.4.1+1')]:
    assert version in next((RUN/'logs').glob('*version-'+jdk+'.stderr')).read_text()
    assert 'os.arch = amd64' in next((RUN/'logs').glob('*version-'+jdk+'.stderr')).read_text()

entries=dict(config_blobs); inventory=[]
def add(path):
    original=path.read_bytes(); shared=redact(original); name=path.relative_to(ROOT).as_posix()
    entries[name]=shared
    inventory.append({'path':name,'original_sha256':digest(original),'package_sha256':digest(shared),'redacted':shared!=original})
for name in ['summary.json','assertions.json','manifest.json','commands.jsonl','SHA256SUMS','downloads.jsonl']:
    if (RUN/name).exists(): add(RUN/name)
# All ordered stdout/stderr logs are small text and avoid selective evidence omission.
for f in sorted((RUN/'logs').iterdir()): add(f)
for f in sorted((RUN/'cases').rglob('*')):
    if f.is_file() and f.suffix in {'.json','.csv','.txt'}: add(f)
for name in ['README.md','matrix.json','dependencies.lock.json','images.lock.json']:
    add(ROOT/'artifact/runtime-validation'/name)
# Context documents retain their historical wording; report flags stale readiness claims.
for name in ['artifact/baselines/README.md','artifact/REPRODUCIBILITY.md','research/BASELINE_ARTIFACTS.md','research/RESEARCH_PLAN.md']:
    add(ROOT/name)
entries['artifact/review/run.py.compatibility.patch']=patch
for case in case_results:
    rows=list(csv.reader((RUN/'cases'/case['case']/'outcomes.csv').read_text().splitlines()))
    entries[f"{PREFIX}/cases/{case['case']}/outcomes.json"]=encode({'provenance':'DERIVED: lossless conversion of included outcomes.csv; not an original runner output','requests':[{'id':int(row[0]),'status':row[1],'value':int(row[2]) if row[2] else None} for row in rows]})
excluded=[]
for f in sorted(RUN.rglob('*')):
    if f.is_file() and f.relative_to(ROOT).as_posix() not in entries:
        excluded.append({'path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'reason':'Docker image archive' if f.suffix=='.tar' else 'downloaded dependency binary' if f.suffix=='.jar' else 'JFR binary recording; no fixture failure' if f.suffix=='.jfr' else 'compiled class binary or nonessential generated binary','sha256':file_digest(f)})
entries['artifact/review/AUDIT_VERIFICATION.json']=redact(encode({'method':'Independent local read/hash audit; no Docker execution or matrix rerun','assertions':{'passed':94,'total':94},'cases':case_results,'checksums':verified,'monitor_fixtures':pins,'exported_image_configs':config_evidence,'source_hashes_match':True,'patch_matches_previous_preserved_patch':True,'nonzero_commands':nonzero}))
entries['artifact/review/EXCLUDED_EVIDENCE.json']=encode(excluded)
entries['artifact/review/PACKAGE_INVENTORY.json']=encode(inventory)
report='''# Virtual Thread baseline validation audit

## Decision and provenance

**Local deterministic correctness smoke gate: PASS. Aggregate scientific/selected-baseline readiness gate: OPEN.** Audited the existing run `artifact/results/runtime-validation/20261008T064525Z-e67bd535`; no matrix, container, benchmark, dependency resolution, or download was executed for this audit. Original raw evidence remains untouched.

Commit `5aabf1d18a4bbdc1dd66b101e4d603972a0bd9a4` plus the exact uncommitted runner compatibility patch. All source/config hashes recorded in manifest.json still match local files. Current Git diff is byte-identical to the patch preserved after execution and is included at `artifact/review/run.py.compatibility.patch`. The patch is unredacted and exact. No commit/push was performed.

## Independently verified in this audit

| Item | Status | Direct evidence |
|---|---|---|
| Top-level assertions | PASS: 94/94 | Parsed assertions.json; every entry PASS |
| Workload cases | PASS: 30/30 | Enumerated 2 JDKs × 5 controls × 3 modes; inspected per-case assertions and independently calculated all 12 expected requests per case |
| File integrity | PASS: 408/408 | Rehashed every original SHA256SUMS entry, including excluded binaries |
| Image integrity | PASS: 3/3 | Rehashed actual config bytes in local saved image archives against unchanged config locks; verified Linux/AMD64 |
| JDK observations | PASS | Version stderr and JVM properties: Temurin 21.0.12.1+1-LTS and 25.0.4.1+1-LTS |
| PostgreSQL observation | PASS | database-version stdout records PostgreSQL 16.15 |
| Monitor fixtures | PASS: 4/4 | Parsed pinning.json and independently counted retained JFR JSON events: four scenario markers each; JDK21 virtual 4 pins, other three fixtures 0 |
| Architecture | PASS, with scope limitation | Manifest macOS 26.6.2/arm64; Docker info aarch64; Docker command argv requests linux/amd64 and JVM os.arch is amd64. AMD64 emulation on ARM64 is established by these recorded architectures; specific emulation engine not recorded |
| Compatibility patch/source | PASS | Current SHA-256 matches execution manifest; diff matches previously preserved patch |
| Command failures | No unresolved failure | Only nonzero recorded command is initial pg_isready exit 2; later readiness succeeds. Build/case/cleanup commands exit zero |
| JNI compiler/native fixture | UNATTEMPTED | native-build stdout: NATIVE_UNAVAILABLE_NO_CC; no packages installed |
| Foreign calls and performance | UNATTEMPTED | No FFM fixture or performance experiment in this bundle |
| Mandatory checks blocked in this run | BLOCKED: none | All mandatory smoke checks completed |

Every workload outcome CSV was compared against an independently calculated oracle: IDs 0–11, value 7×ID+3, fixed/reduced controls reject each third held-batch request, pool-only accepts all. Per-case peak active operations are at most two and active_at_end is zero. Returned pool/admission capacity and interface identity are enforced by the executed harness; independent reinspection of their runtime internals was not performed. Passing recorded assertions is evidence of this contract, not a new execution.

Docker logs record client/engine 28.1.1, Desktop 4.41.1 (191279), Linux VM kernel 6.10.14-linuxkit. The run's resource limits, scheduler flags, start/end timestamps, dependency downloads and image references are preserved. Scope is constant-input, held-batch smoke validation; reduced Gradient2/Envoy/Breakwater comparators are not official upstream baselines.

## Facts inherited from prior reporting, not independently reobserved

The prior Codex report and session recorded outer command exit **0**. The bundle records PASS and contains runner source identity, but no raw outer-shell exit-code file; this audit did not reexecute the command to observe that code. Source logic maps PASS to zero. The prior report also recorded absence of live Docker resources after cleanup and 83 GiB free host space. This audit verifies successful historical cleanup commands only; it did not query live Docker or disk availability. Prior synthetic patch-unit-test results are historical, not rerun here. These claims are not needed to establish artifact integrity.

## Package contents, transformations, and exclusions

Repository-relative paths are preserved. All small successful-run logs are included, including both JDK version/flags/JFR metadata logs, JFR event JSON text, PostgreSQL readiness/version/database logs, image pull/inspect/save logs, and the transient failed-command logs. All 30 original assertion JSONs, outcome CSVs and JVM property texts are included. Original runner output has no outcome JSONs: 30 derived outcomes.json files are lossless CSV conversions with explicit provenance labels. Four pinning.json files are included.

Personal checkout paths become `<REPO_ROOT>`; user-home paths become `<USER_HOME>`; the disposable PostgreSQL fixture password is replaced by `<REDACTED_FIXTURE_PASSWORD>`. Redactions affect share copies only. No production credentials are needed. The exact compatibility patch contains neither credentials nor personal paths. Local uid/gid and technical host architecture remain as reproducibility metadata.

Original SHA256SUMS is included unchanged as the 408-file raw-evidence index. **It cannot validate this compact ZIP end-to-end**: some files are omitted and selected text copies are redacted. PACKAGE_INVENTORY.json maps original to packaged hashes and flags redactions. PACKAGE_SHA256SUMS verifies all packaged entries except itself. AUDIT_VERIFICATION.json captures independent verification. ZIP has a separate external .sha256 file.

EXCLUDED_EVIDENCE.json lists every omitted run file, size, reason, and raw hash: three Docker image TARs, 29 dependency JARs, 34 JFR binaries, and compiled classes. JFR binaries remain in the original run; no fixture failure required their inclusion. Excluding binaries limits remote review to preserved event extracts and audited hash assertions; ChatGPT cannot independently regenerate events or inspect the full excluded images from this ZIP. Three small config blobs extracted byte-for-byte from the saved images are included under artifact/review/image-configs; their SHA-256 values can be compared directly against the image lock, independently of Docker .Id. Unrelated files, prior runs, Git internals and the previous Codex narrative report are excluded. Raw evidence must remain available locally for deeper review.

Context README/research inventory documents are included as historical records. Their PREPARED/UNATTEMPTED and missing-local-Docker wording predates this successful run; the scoped runtime result above supersedes those specific historical environment statements, without upgrading official-baseline readiness.

## Next scientifically valid milestone (proposed, not executed)

**Pinned official Netflix Gradient2 build, smoke, and independent dynamic-trace conformance**, as already required by research/BASELINE_ARTIFACTS.md. This closes a concrete external-baseline gap without pretending the constant-capacity reduced adapter establishes adaptation or upstream equivalence.

Acceptance criteria:

1. Use recorded upstream revision `78a74b9878d38c4c048b0304ce12a162ab7b7222`; verify source identity and license from the pinned checkout before building. Existing inventory is historical evidence, not a fresh upstream verification.
2. Freeze build tooling and the full resolved dependency closure with versions/checksums; resolve documented dynamic ranges explicitly. Preserve upstream changes separately and justify them. Record commands, exit codes and full logs.
3. Run official tests and a minimal Gradient2 API/listener smoke test in a pinned local environment. Capture actual JDK and platform versions; do not call upstream failures comparator failures or hide build blockers.
4. Define fixed independent expected traces before testing: warm-up, sustained increase/decrease, EMA/recovery, app-limited suppression, clamps/bounds, drops, and completion/listener accounting. Obtain the expected decisions from the pinned specification/source through a separate oracle; do not use implementation outputs as expected values. Document tolerances and every adapter/reduced-comparator deviation.
5. Verify the official adapter against the same downstream resource/workload semantics, including error/cancellation lease release. Retain the current reduced comparator as separately labeled evidence. Publish PASS/FAIL/BLOCKED/UNATTEMPTED outcomes and hashes. No numeric performance conclusions at this gate.

This milestone does not by itself finish all selected baselines: official Envoy provenance/smoke/conformance, JNI/foreign coverage where selected, bounded platform worker-pool coverage, and stress/error/cancellation/saturation remain open. Before a performance milestone, preregister workload, warm-up/repetitions, offered-load measurement, coordinated-omission treatment, metrics/statistical analysis and hardware/resource controls; run on appropriate native hardware with complete provenance. AMD64-on-ARM64 smoke results do not support JDK latency rankings, throughput claims, overload collapse, fairness, or the paper's research conclusions.
'''
entries['artifact/review/VALIDATION_AUDIT_REPORT.md']=report.encode()
(REVIEW/'VALIDATION_AUDIT_REPORT.md').write_text(report)
entries['artifact/review/PACKAGE_SHA256SUMS']=''.join(f'{digest(data)}  {name}\n' for name,data in sorted(entries.items())).encode()
# Fixed member metadata makes repeated packaging byte reproducible for identical inputs.
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(entries.items()):
        assert b'/Users/' not in data and b'POSTGRES_PASSWORD=smoke' not in data,name
        item=zipfile.ZipInfo(name,date_time=(2026,10,8,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o100644<<16
        z.writestr(item,data)
with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None
    for line in z.read('artifact/review/PACKAGE_SHA256SUMS').decode().splitlines():
        h,name=line.split('  ',1);assert digest(z.read(name))==h
    assert len([n for n in z.namelist() if n.endswith('/outcomes.json')])==30
    assert not any(n.endswith(('.tar','.jar','.jfr','.class')) for n in z.namelist())
(REVIEW/(ZIP.name+'.sha256')).write_text(file_digest(ZIP)+'  '+ZIP.name+'\n')
print(json.dumps({'zip':ZIP.relative_to(ROOT).as_posix(),'bytes':ZIP.stat().st_size,'entries':len(entries),'excluded':len(excluded),'assertions':94,'cases':30,'checksums':408,'sha256':file_digest(ZIP)},indent=2))
