#!/usr/bin/env python3
"""Zero-cost local Docker validation. Does not need host Java, Maven or Compose."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'artifact/runtime-validation'

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, obj): path.write_text(json.dumps(obj, indent=2) + '\n')

class Failure(Exception): pass

class Run:
    def __init__(self, output):
        self.out = output.resolve() / (dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8])
        snapshots=[]
        for argv,label in [(['git','rev-parse','HEAD'],'source-head'),(['git','status','--porcelain'],'source-status')]:
            started=now()
            try:
                result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=20)
                snapshots.append((argv,label,started,now(),result.returncode,result.stdout,result.stderr))
            except (OSError,subprocess.TimeoutExpired) as error:
                snapshots.append((argv,label,started,now(),127,'',str(error)))
        self.out.mkdir(parents=True)
        self.prefix = 'vt-'+uuid.uuid4().hex[:10]
        self.network = self.prefix+'-net'
        self.db = self.prefix+'-db'
        self.containers = []
        self.commands = []
        self.assertions = []
        self.manifest = {'started': now(), 'platform': platform.platform(), 'machine':platform.machine(), 'python':sys.version, 'host_cpu_count':os.cpu_count(), 'host_cpu_model':next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')),None) if Path('/proc/cpuinfo').exists() else None, 'host_memory_info':Path('/proc/meminfo').read_text() if Path('/proc/meminfo').exists() else None,
                         'scope':'correctness smoke only', 'runtime_status':'UNATTEMPTED', 'uid':getattr(os,'getuid',lambda:None)(),
                         'resources':{'cpus':2,'memory':'1g','pids_limit':512,'postgres_memory':'512m'}}
        (self.out/'logs').mkdir()
        for argv,label,started,ended,code,stdout,stderr in snapshots:
            stem=f'{len(self.commands):03d}-{label}'
            a='logs/'+stem+'.stdout'; b='logs/'+stem+'.stderr'
            (self.out/a).write_text(stdout); (self.out/b).write_text(stderr)
            record={'argv':argv,'cwd':str(ROOT),'started':started,'ended':ended,'exit_code':code,'stdout':a,'stderr':b}
            self.commands.append(record)
            with (self.out/'commands.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
        self.manifest.update(source_head=snapshots[0][5].strip(),source_status=snapshots[1][5],source_snapshot='before output directory creation')
    def command(self, argv, label, timeout=120, check=True):
        logdir=self.out/'logs'; logdir.mkdir(exist_ok=True)
        stem=f'{len(self.commands):03d}-{label}'
        stdout=logdir/(stem+'.stdout'); stderr=logdir/(stem+'.stderr')
        record={'argv':list(map(str,argv)),'cwd':str(ROOT),'started':now(),'stdout':str(stdout.relative_to(self.out)),'stderr':str(stderr.relative_to(self.out))}
        code=127
        with stdout.open('wb') as a, stderr.open('wb') as b:
            try:
                p=subprocess.run(record['argv'],cwd=ROOT,stdout=a,stderr=b,timeout=timeout)
                code=p.returncode
            except subprocess.TimeoutExpired: code=124; b.write(b'COMMAND TIMEOUT\n')
            except OSError as error: b.write(str(error).encode())
        record.update(ended=now(),exit_code=code)
        self.commands.append(record)
        with (self.out/'commands.jsonl').open('a') as f: f.write(json.dumps(record)+'\n')
        if code and check: raise Failure(f'{label} exit {code}; see {record["stderr"]}')
        return code,stdout.read_text(errors='replace')
    def container(self,image,args,label,network=False,timeout=120):
        name=self.prefix+'-'+str(len(self.containers));self.containers.append(name)
        cmd=['docker','run','--rm','--name',name,'--platform','linux/amd64','--cpus','2','--memory','1g','--pids-limit','512',
             '--user',f'{os.getuid()}:{os.getgid()}', '-v',f'{ROOT}:/src:ro','-v',f'{self.out}:/out','-w','/out']
        cmd += ['--network',self.network if network else 'none',image]+args
        return self.command(cmd,label,timeout)
    def assertion(self,ok,name,detail=''):
        self.assertions.append({'name':name,'status':'PASS' if ok else 'FAIL','detail':detail})
        if not ok: raise Failure(name+': '+detail)
    def finish(self,status,reason):
        self.manifest.update(ended=now(),runtime_status=status)
        write(self.out/'manifest.json',self.manifest)
        write(self.out/'assertions.json',self.assertions)
        write(self.out/'summary.json',{'status':status,'reason':reason,'scope':'correctness smoke; not official baseline builds or performance',
            'native_foreign':self.manifest.get('native_fixture', 'UNATTEMPTED: preflight did not reach native compiler check'),
            'foreign_calls':'UNATTEMPTED: JNI callback does not cover foreign calls'})
        files=sorted(p for p in self.out.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
        (self.out/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(self.out)}\n' for p in files))
        print(json.dumps({'output':str(self.out),'status':status,'reason':reason}))
    def cleanup(self):
        if not shutil.which('docker'): return
        if self.db in self.containers: self.command(['docker','logs',self.db],'database-logs',check=False)
        for name in reversed(self.containers): self.command(['docker','rm','-f',name],'cleanup-container',timeout=20,check=False)
        self.command(['docker','network','rm',self.network],'cleanup-network',timeout=20,check=False)

def download_dependencies(run):
    deps=json.loads((BUNDLE/'dependencies.lock.json').read_text())
    dest=run.out/'dependencies';dest.mkdir()
    for entry in deps['artifacts']:
        path=dest/entry['filename']; start=now()
        request=urllib.request.Request(entry['url'],headers={'User-Agent':'vt-runtime-validation/1'})
        with urllib.request.urlopen(request,timeout=60) as r: path.write_bytes(r.read())
        run.assertion(sha(path)==entry['sha256'],'dependency hash '+entry['filename'])
        with (run.out/'downloads.jsonl').open('a') as f: f.write(json.dumps({'url':entry['url'],'started':start,'ended':now(),'sha256':sha(path)})+'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'artifact/results/runtime-validation')
    p.add_argument('--matrix',type=Path,default=BUNDLE/'matrix.json')
    args=p.parse_args();run=Run(args.output)
    status='UNATTEMPTED'; reason='preflight incomplete'; attempted=False
    def interrupted(signum,frame): raise Failure('interrupted by signal '+str(signum))
    signal.signal(signal.SIGTERM,interrupted)
    try:
        # Capture local source identity even when Docker is absent.
        inputs=list(BUNDLE.glob('*'))+list((ROOT/'artifact/baselines').glob('*.java'))+[ROOT/'artifact/scripts/validate-runtime.sh']
        run.manifest['source_sha256']={str(f.relative_to(ROOT)):sha(f) for f in inputs if f.is_file()}
        locks=json.loads((BUNDLE/'images.lock.json').read_text()); matrix=json.loads(args.matrix.read_text())
        run.manifest.update(images=locks,matrix=matrix,matrix_sha256=sha(args.matrix))
        run.assertion(matrix==json.loads((BUNDLE/'matrix.json').read_text()),'supported fixed smoke contract')
        for entry in locks['images'].values():
            run.assertion(bool(re.fullmatch(r'[^@]+@sha256:[0-9a-f]{64}',entry['reference'])),'immutable image pin '+entry['source_tag'])
        if not shutil.which('docker'): raise Failure('Docker executable unavailable; no container, JDK21/25 or database execution attempted')
        run.command(['docker','version'],'docker-version')
        run.command(['docker','info','--format','{{json .}}'],'docker-info')
        download_dependencies(run)
        for key,entry in locks['images'].items():
            run.command(['docker','pull','--platform','linux/amd64',entry['reference']],'pull-'+key,timeout=600)
            _,inspection=run.command(['docker','image','inspect',entry['reference']],'inspect-'+key)
            facts=json.loads(inspection)[0]
            run.assertion(facts['Id']==entry['config_digest'],'image config digest '+key)
        sources=['/src/artifact/runtime-validation/RuntimeSmoke.java']+['/src/artifact/baselines/'+name for name in ['NativeControls.java','BreakwaterInspired.java','AdaptiveControllerComparators.java']]
        (run.out/'classes').mkdir()
        run.container(locks['images']['jdk21']['reference'],['javac','--release','17','-cp','/out/dependencies/*','-d','/out/classes']+sources,'compile')
        run.command(['docker','network','create','--internal',run.network],'network-create')
        run.containers.append(run.db)
        run.command(['docker','run','-d','--name',run.db,'--network',run.network,'--network-alias','db','--platform','linux/amd64','--cpus','1','--memory','512m','--pids-limit','256',
            '-e','POSTGRES_USER=smoke','-e','POSTGRES_PASSWORD=smoke','-e','POSTGRES_DB=smoke','--tmpfs','/var/lib/postgresql/data',
            '-v',f'{BUNDLE / "fixture.sql"}:/docker-entrypoint-initdb.d/fixture.sql:ro',locks['images']['postgres']['reference']],'database-start')
        for attempt in range(30):
            code,_=run.command(['docker','exec',run.db,'pg_isready','-U','smoke','-d','smoke'],'database-ready',check=False,timeout=10)
            if not code:
                code,text=run.command(['docker','exec',run.db,'psql','-U','smoke','-d','smoke','-Atc','SELECT count(*) FROM fixture'],'fixture-ready',check=False)
                if not code and text.strip()=='12': break
            time.sleep(1)
        else: raise Failure('database readiness/fixture timeout')
        run.command(['docker','exec',run.db,'psql','-U','smoke','-d','smoke','-Atc','SELECT version()'],'database-version')
        attempted=True;references={}
        (run.out/'native').mkdir()
        _,native_status=run.container(locks['images']['jdk21']['reference'],['sh','-c','if command -v cc >/dev/null 2>&1; then cc -shared -fPIC -I"$JAVA_HOME/include" -I"$JAVA_HOME/include/linux" /src/artifact/runtime-validation/native_pinning.c -o /out/native/libvtpin.so && echo NATIVE_READY; else echo NATIVE_UNAVAILABLE_NO_CC; fi'],'native-build')
        native_ready='NATIVE_READY' in native_status
        run.manifest['native_fixture']='JNI callback isolated' if native_ready else 'UNATTEMPTED: cc unavailable in pinned JDK21 image; no package installation attempted' 
        flags=['--enable-native-access=ALL-UNNAMED','-Djdk.virtualThreadScheduler.parallelism=2','-Djdk.virtualThreadScheduler.maxPoolSize=2','-Xms64m','-Xmx512m']
        for jdk in matrix['jdk']:
            image=locks['images'][jdk]['reference']
            run.container(image,['java','-XshowSettings:properties','-version'],'version-'+jdk)
            run.container(image,['java','-XX:+PrintFlagsFinal','-version'],'flags-'+jdk)
            run.container(image,['jfr','metadata'],'jfr-metadata-'+jdk)
            for mode in ['platform','virtual']:
                case=f'{jdk}-pin-{mode}';(run.out/'cases'/case).mkdir(parents=True)
                run.container(image,['java']+flags+['-cp','/out/classes:/out/dependencies/*','RuntimeSmoke','/out/cases/'+case,'pin',mode],case)
                run.container(image,['jfr','print','--json','--events','jdk.VirtualThreadPinned,validation.Scenario','/out/cases/'+case+'/pinning.jfr'],'jfr-events-'+case)
            if native_ready:
                for mode in ['platform','virtual']:
                    case=f'{jdk}-native-{mode}';(run.out/'cases'/case).mkdir(parents=True)
                    run.container(image,['java']+flags+['-cp','/out/classes:/out/dependencies/*','RuntimeSmoke','/out/cases/'+case,'pin',mode,'native'],case)
                    run.container(image,['jfr','print','--json','--events','jdk.VirtualThreadPinned,validation.Scenario','/out/cases/'+case+'/pinning.jfr'],'jfr-events-'+case)
            for control in matrix['controls']:
                for mode in matrix['modes']:
                    case=f'{jdk}-{control}-{mode}';folder=run.out/'cases'/case;folder.mkdir(parents=True)
                    run.container(image,['java']+flags+['-XX:StartFlightRecording=filename=/out/cases/'+case+'/workload.jfr,settings=profile,dumponexit=true','-cp','/out/classes:/out/dependencies/*','RuntimeSmoke','/out/cases/'+case,mode,control],case,network=True)
                    actual=(folder/'outcomes.csv').read_text()
                    if control in references: run.assertion(actual==references[control],'matched outcomes '+case)
                    else: references[control]=actual
                    run.assertion(json.loads((folder/'assertions.json').read_text())['status']=='PASS','case assertions '+case)
        status='PASS';reason='all mandatory smoke cases passed; inspect native_fixture availability and unattempted foreign-call coverage'
    except (KeyboardInterrupt,Exception) as error:
        status='UNATTEMPTED' if not shutil.which('docker') else 'FAIL';reason=str(error) or type(error).__name__
    finally:
        try: run.cleanup()
        finally: run.finish(status,reason)
    return 0 if status=='PASS' else 2

if __name__=='__main__': sys.exit(main())
