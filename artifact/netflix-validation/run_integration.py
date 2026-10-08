from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time,uuid
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifact/results/netflix-validation/20261008-official';SRC=ROOT/'artifact/netflix-validation'
PIN=json.loads((ROOT/'artifact/runtime-validation/images.lock.json').read_text())['images']
REC=SRC/'record.py'
def rec(label,args,check=True):
 code=subprocess.call([sys.executable,str(REC),label]+list(map(str,args)))
 if code and check:raise RuntimeError(label+' exit '+str(code))
 return code

def container(label,image,args,network='none'):
 return rec(label,['docker','run','--rm','--platform','linux/amd64','--network',network,'--cpus','2','--memory','1g','--pids-limit','512','-v',str(OUT)+':/evidence','-v',str(SRC)+':/validation:ro','-w','/evidence',image]+args)
libs=OUT/'runtime-dependencies';libs.mkdir(exist_ok=True)
prior=ROOT/'artifact/results/runtime-validation/20261008T064525Z-e67bd535/dependencies'
entries=json.loads((ROOT/'artifact/runtime-validation/dependencies.lock.json').read_text())['artifacts']
for e in entries:
 data=(prior/e['filename']).read_bytes();assert hashlib.sha256(data).hexdigest()==e['sha256'];(libs/e['filename']).write_bytes(data)
slf=next((OUT/'gradle-cache/caches/modules-2/files-2.1/org.slf4j/slf4j-api/1.7.36').rglob('*.jar'));shutil.copy2(slf,libs/slf.name)
cp='/evidence/upstream/concurrency-limits-core/build/classes/java/main:/evidence/runtime-dependencies/*:/evidence/classes'
(OUT/'classes').mkdir(exist_ok=True)
container('compile-integration',PIN['jdk21']['reference'],['javac','-cp',cp,'-d','/evidence/classes']+['/validation/'+p.name for p in sorted(SRC.glob('*.java'))])
container('conformance',PIN['jdk21']['reference'],['java','-cp',cp,'OfficialProbe','/evidence/trace-input.csv'])
rec('check-conformance',['python3',SRC/'check_traces.py'])
prefix='vt-netflix-'+uuid.uuid4().hex[:8];net=prefix+'-net';db=prefix+'-db'
(OUT/'resource-names.json').write_text(json.dumps({'network':net,'database':db})+'\n')
try:
 rec('network-create',['docker','network','create','--internal',net])
 rec('database-start',['docker','run','-d','--name',db,'--platform','linux/amd64','--network',net,'--network-alias','db','--cpus','1','--memory','512m','--pids-limit','256','--tmpfs','/var/lib/postgresql/data','-e','POSTGRES_USER=smoke','-e','POSTGRES_PASSWORD=smoke','-e','POSTGRES_DB=smoke','-v',str(ROOT/'artifact/runtime-validation/fixture.sql')+':/docker-entrypoint-initdb.d/fixture.sql:ro',PIN['postgres']['reference']])
 for i in range(30):
  code=rec('database-ready-'+str(i),['docker','exec',db,'psql','-U','smoke','-d','smoke','-Atc','SELECT count(*) FROM fixture'],False)
  if code==0 and (OUT/'logs'/f'database-ready-{i}.stdout').read_text().strip()=='12':break
  time.sleep(1)
 else:raise RuntimeError('database readiness')
 for jdk in ['jdk21','jdk25']:
  container('integration-version-'+jdk,PIN[jdk]['reference'],['java','-XshowSettings:properties','-version'])
  for mode in ['platform','virtual','reactive']:
   name=jdk+'-'+mode
   container('workload-'+name,PIN[jdk]['reference'],['java','-Djdk.virtualThreadScheduler.parallelism=2','-Djdk.virtualThreadScheduler.maxPoolSize=2','-cp',cp,'OfficialWorkload',mode,'/evidence/cases/'+name],net)
finally:
 rec('database-logs',['docker','logs',db],False)
 rec('cleanup-db',['docker','rm','-f',db],False)
 rec('cleanup-network',['docker','network','rm',net],False)
