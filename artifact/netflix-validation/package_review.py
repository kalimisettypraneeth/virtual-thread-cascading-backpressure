"""Create only the NEW Netflix review package; never rebuild the original audit."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifact/results/netflix-validation/20261008-official';SRC=ROOT/'artifact/netflix-validation';UP=OUT/'upstream';REVIEW=ROOT/'artifact/review';ZIP=REVIEW/'NETFLIX_GRADIENT2_BASELINE_REVIEW_20261008.zip'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def raw_selected(p):
 rel=p.relative_to(OUT)
 return p.is_file() and 'gradle-cache' not in rel.parts and '.git' not in rel.parts and '.gradle' not in rel.parts and p.name!='RAW_SHA256SUMS'
# Includes retained large tooling/dependency files as original-evidence hashes.
raw=sorted(p for p in OUT.rglob('*') if raw_selected(p))
(OUT/'RAW_SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(OUT)}\n' for p in raw))
selected=set(p for p in SRC.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
selected.update(p for p in OUT.iterdir() if p.is_file() and p.suffix in {'.json','.jsonl','.csv','.txt','.sha256'})
selected.add(OUT/'RAW_SHA256SUMS')
selected.update(p for p in (OUT/'logs').iterdir() if p.is_file())
selected.update(p for p in (OUT/'cases').rglob('*') if p.is_file())
for name in subprocess.check_output(['git','ls-files'],cwd=UP,text=True).splitlines():
 p=UP/name
 if p.is_file():selected.add(p)
selected.update((UP/'concurrency-limits-core/build/test-results/test').glob('TEST-*.xml'))
entries={};inventory=[]
for p in sorted(selected):
 data=p.read_bytes();shared=data
 if p.suffix not in {'.jar','.png','.jpg'}:
  text=data.decode();text=text.replace(str(ROOT),'<REPO_ROOT>').replace(str(Path.home()),'<USER_HOME>')
  if p.parent.name=='logs' or p.name=='commands.jsonl':text=text.replace('POSTGRES_PASSWORD=smoke','POSTGRES_PASSWORD=<LOCAL_FIXTURE_PASSWORD>')
  shared=text.encode()
 name=p.relative_to(ROOT).as_posix();entries[name]=shared
 inventory.append({'path':name,'original_sha256':hashlib.sha256(data).hexdigest(),'package_sha256':hashlib.sha256(shared).hexdigest(),'redacted':shared!=data})
entries['PACKAGE_INVENTORY.json']=(json.dumps(inventory,indent=2)+'\n').encode()
entries['PACKAGE_SHA256SUMS']=''.join(f'{hashlib.sha256(data).hexdigest()}  {name}\n' for name,data in sorted(entries.items())).encode()
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,data in sorted(entries.items()):
  assert (b'/' + b'Users/') not in data,name
  i=zipfile.ZipInfo(name,date_time=(2026,10,8,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data)
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 for line in z.read('PACKAGE_SHA256SUMS').decode().splitlines():
  h,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==h
(ZIP.with_name(ZIP.name+'.sha256')).write_text(sha(ZIP)+'  '+ZIP.name+'\n')
print(json.dumps({'zip':str(ZIP.relative_to(ROOT)),'bytes':ZIP.stat().st_size,'entries':len(entries),'sha256':sha(ZIP),'package_checksums':'PASS'},indent=2))
