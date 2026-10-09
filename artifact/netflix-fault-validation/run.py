"""Offline correctness runner. Requires preserved official classes and JARs."""
import argparse, datetime, hashlib, json, shutil, subprocess, sys, uuid
from pathlib import Path
from check_events import check, read
ROOT=Path(__file__).resolve().parents[2]; SRC=Path(__file__).resolve().parent
STATE={'status':'UNATTEMPTED','runtime_status':'UNATTEMPTED','java_compilation':'UNATTEMPTED','last_command':None}; OUTPUT=None

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    global OUTPUT
    parser=argparse.ArgumentParser();parser.add_argument('--official-evidence',type=Path,required=True);parser.add_argument('--preflight',action='store_true');args=parser.parse_args()
    out=ROOT/'artifact/results/netflix-fault-validation'/('run-'+uuid.uuid4().hex);out.mkdir(parents=True); OUTPUT=out
    blockers=[]; official=args.official_evidence.resolve()
    freeze=json.loads((ROOT/'artifact/results/netflix-fault-validation/oracle-freeze.json').read_text())
    if sha(SRC/'expected.json')!=freeze['sha256']:blockers.append('frozen oracle changed')
    if not shutil.which('docker'):blockers.append('Docker CLI unavailable')
    classes=json.loads((SRC/'official-classes.lock.json').read_text())['files']
    jars=json.loads((ROOT/'artifact/netflix-validation/locks/integration-dependencies.json').read_text())['artifacts']
    for rel,want in classes.items():
        p=official/rel
        if not p.is_file() or sha(p)!=want:blockers.append('missing/mismatched official class: '+rel)
    for entry in jars:
        p=official/'runtime-dependencies'/entry['filename']
        if not p.is_file() or sha(p)!=entry['sha256']:blockers.append('missing/mismatched JAR: '+entry['filename'])
    manifest={'status':'UNATTEMPTED','scope':'correctness only; no performance','blockers':blockers,'official_evidence':str(official),'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in list(SRC.glob('*.java'))+list(SRC.glob('*.py'))+[ROOT/'artifact/netflix-validation/OfficialAdmission.java',SRC/'expected.json']},'checkout_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out/'preflight.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(out)
    if blockers or args.preflight:
        STATE['blockers']=blockers;STATE['scope']='preflight only';return 2 if blockers else 0
    def run(label,cmd,required=True):
        STATE['last_command']=label
        (out/(label+'.command.json')).write_text(json.dumps(cmd)+'\n')
        with (out/(label+'.stdout')).open('w') as stdout,(out/(label+'.stderr')).open('w') as stderr:
            result=subprocess.run(cmd,stdout=stdout,stderr=stderr)
        (out/(label+'.exitcode')).write_text(str(result.returncode)+'\n')
        STATE['last_exit_code']=result.returncode
        if required and result.returncode:
            STATE['failed_command']=label;STATE['failed_exit_code']=result.returncode
            if label=='compile':STATE['java_compilation']='FAIL'
            raise RuntimeError(label+' failed')
        return result.returncode
    images=json.loads((ROOT/'artifact/runtime-validation/images.lock.json').read_text())['images']
    for name in ('jdk21','jdk25','postgres'):run('inspect-'+name,['docker','image','inspect',images[name]['reference']])
    run('docker-version',['docker','version']);run('docker-info',['docker','info'])
    (out/'classes').mkdir()
    cp='/official/upstream/concurrency-limits-core/build/classes/java/main:/official/runtime-dependencies/*:/output/classes'
    prefix='vt-fault-'+uuid.uuid4().hex[:8];net=prefix+'-net';db=prefix+'-db'
    def container(label,jdk,command,network='none'):
        return run(label,['docker','run','--rm','--pull=never','--platform','linux/amd64','--network',network,'--cpus','2','--memory','1g','--pids-limit','512','-v',str(official)+':/official:ro','-v',str(out)+':/output','-v',str(SRC)+':/validation:ro','-v',str(ROOT/'artifact/netflix-validation')+':/adapter:ro',images[jdk]['reference']]+command)
    STATE['java_compilation']='ATTEMPTED'
    container('compile','jdk21',['javac','-cp',cp,'-d','/output/classes','/adapter/OfficialAdmission.java','/validation/ActiveQueryFault.java'])
    STATE['java_compilation']='PASS'
    try:
        run('network-create',['docker','network','create','--internal',net])
        run('db-start',['docker','run','-d','--pull=never','--name',db,'--platform','linux/amd64','--network',net,'--network-alias','db','--tmpfs','/var/lib/postgresql/data','--memory','512m','--cpus','1','-e','POSTGRES_USER=smoke','-e','POSTGRES_PASSWORD=smoke','-e','POSTGRES_DB=smoke',images['postgres']['reference']])
        import time
        for attempt in range(30):
            if run('ready-'+str(attempt),['docker','exec',db,'pg_isready','-U','smoke','-d','smoke'],False)==0:break
            time.sleep(1)
        else:raise RuntimeError('database not ready')
        results=[]
        for jdk in ('jdk21','jdk25'):
            container('version-'+jdk,jdk,['java','-XshowSettings:properties','-version'])
            for mode in ('platform','virtual','reactive'):
                for scenario in ('before-query','server-cancel','server-timeout'):
                    name=jdk+'-'+mode+'-'+scenario
                    STATE['runtime_status']='PARTIAL';STATE['runtime_case']=name
                    container(name,jdk,['java','-cp',cp,'ActiveQueryFault',mode,scenario],net)
                    result=check(read(out/(name+'.stdout')),scenario,mode);results.append({'case':name,**result})
        (out/'results.json').write_text(json.dumps({'status':'PASS','scope':'18 server-fault correctness cases; not client-cancel or native performance','cases':results},indent=2)+'\n')
    finally:
        run('db-logs',['docker','logs',db],False);run('cleanup-db',['docker','rm','-f',db],False);run('cleanup-network',['docker','network','rm',net],False)
    STATE.update(status='PASS',runtime_status='PASS',scope='18 server-fault correctness cases only')
    return 0

def finalize(out,state):
    out.mkdir(parents=True,exist_ok=True)
    (out/'outcome.json').write_text(json.dumps(state,indent=2)+'\n')
    (out/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(out))+'\n' for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))

def entry():
    code=1
    try:
        code=main();STATE['exit_code']=code
    except Exception as error:
        STATE.update(status='FAIL',error=repr(error),exit_code=1)
        print(str(error),file=sys.stderr)
    finally:
        if OUTPUT is not None:finalize(OUTPUT,STATE)
    return code
if __name__=='__main__':sys.exit(entry())
