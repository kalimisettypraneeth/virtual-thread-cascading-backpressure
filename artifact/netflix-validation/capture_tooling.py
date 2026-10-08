from pathlib import Path
import subprocess,json,sys,hashlib,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifact/results/netflix-validation/20261008-official'
def rec(label,argv):
 code=subprocess.call([sys.executable,str(ROOT/'artifact/netflix-validation/record.py'),label]+argv)
 if code:raise RuntimeError(label)
image=json.loads((OUT/'tooling-image.json').read_text())['Id']
rec('tooling-environment',['docker','run','--rm','--network','none','--platform','linux/amd64',image,'sh','-c','java -version; /usr/lib/jvm/java-11-openjdk-amd64/bin/java -version; git --version; uname -a; cat /tooling-evidence/dpkg-versions.tsv; cat /tooling-evidence/deb-SHA256SUMS'])
rec('docker-version',['docker','version'])
rec('docker-info',['docker','info','--format','{{json .}}'])
rec('tooling-image-save',['docker','image','save','--platform','linux/amd64','--output',str(OUT/'tooling-image.tar'),image])
url='https://services.gradle.org/distributions/gradle-8.6-bin.zip'
rec('gradle-checksum-download',['curl','--fail','--location',url+'.sha256','--output',str(OUT/'gradle-8.6-bin.zip.sha256')])
rec('gradle-distribution-download',['curl','--fail','--location',url,'--output',str(OUT/'gradle-8.6-bin.zip')])
expected=(OUT/'gradle-8.6-bin.zip.sha256').read_text().strip();assert hashlib.sha256((OUT/'gradle-8.6-bin.zip').read_bytes()).hexdigest()==expected
cached=next((OUT/'gradle-cache/wrapper/dists').glob('gradle-8.6-bin/*/gradle-8.6'))
with zipfile.ZipFile(OUT/'gradle-8.6-bin.zip') as z:
 for n in z.namelist():
  if n.endswith('/'):continue
  assert z.read(n)==(cached.parent/n).read_bytes(),n
(OUT/'gradle-distribution-verification.json').write_text(json.dumps({'status':'PASS','version':'8.6','sha256':expected,'source':url,'executed_extracted_files_match_official_zip':True},indent=2)+'\n')
