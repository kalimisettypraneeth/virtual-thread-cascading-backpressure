from pathlib import Path
import hashlib,json,shutil,subprocess,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifact/results/netflix-validation/20261008-official';UP=OUT/'upstream';LOCKS=ROOT/'artifact/netflix-validation/locks';LOCKS.mkdir(exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 return h.hexdigest()
rows=[]
cache=OUT/'gradle-cache/caches/modules-2/files-2.1'
for p in sorted(cache.rglob('*')):
 if p.is_file():
  parts=p.relative_to(cache).parts
  rows.append({'group':parts[0],'module':parts[1],'version':parts[2],'artifact':p.name,'sha256':sha(p),'cache_path':str(p.relative_to(OUT))})
(LOCKS/'resolved-dependencies.json').write_text(json.dumps({'scope':'Full downloaded Gradle module cache: build plugins/transitives and resolved project compile/runtime/test configurations; includes POM/module metadata. Gradle per-configuration locks and strict verification XML are authoritative. Superset of core dependencies.','artifacts':rows},indent=2)+'\n')
for p in UP.rglob('*.lockfile'):
 dest=LOCKS/'upstream'/p.relative_to(UP);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
shutil.copy2(UP/'gradle/verification-metadata.xml',LOCKS/'verification-metadata.xml')
image=json.loads((OUT/'tooling-image.json').read_text())
tools={'tooling_image_id':image['Id'],'tooling_image_archive':{'path':str((OUT/'tooling-image.tar').relative_to(ROOT)),'sha256':sha(OUT/'tooling-image.tar')},'gradle':json.loads((OUT/'gradle-distribution-verification.json').read_text()),'wrapper_jar_sha256':sha(UP/'gradle/wrapper/gradle-wrapper.jar'),'base_images':json.loads((ROOT/'artifact/runtime-validation/images.lock.json').read_text()),'notes':'Dockerfile is discovery recipe. Exact local replay uses preserved tooling-image.tar verified against this lock; apt package versions and downloaded .deb hashes in tooling-environment.stdout. No hosted image was published.'}
(LOCKS/'tooling.lock.json').write_text(json.dumps(tools,indent=2)+'\n')
(LOCKS/'integration-dependencies.json').write_text(json.dumps({'origin':'29 preserved runtime-validation JARs plus resolved official SLF4J API','artifacts':[{'filename':p.name,'sha256':sha(p)} for p in sorted((OUT/'runtime-dependencies').glob('*.jar'))]},indent=2)+'\n')
roots=[E.parse(p).getroot() for p in sorted((UP/'concurrency-limits-core/build/test-results/test').glob('TEST-*.xml'))]
totals={k:sum(int(r.get(k,'0')) for r in roots) for k in ['tests','failures','errors','skipped']}
totals['passed']=totals['tests']-totals['skipped']-totals['failures']-totals['errors']
totals['skipped_cases']=[{'suite':r.get('name'),'test':c.get('name')} for r in roots for c in r.findall('testcase') if c.find('skipped') is not None]
(OUT/'official-test-summary.json').write_text(json.dumps(totals,indent=2)+'\n')
assert not subprocess.check_output(['git','diff','--name-only'],cwd=UP).strip()
print('Captured',len(rows),'dependency/metadata files;',totals)
