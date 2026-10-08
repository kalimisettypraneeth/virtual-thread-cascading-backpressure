from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifact/results/netflix-validation/20261008-official'
lock=ROOT/'artifact/netflix-validation/locks/tooling.lock.json'
reference=json.loads(lock.read_text())['tooling_image_id'] if lock.exists() else 'vt-netflix-validation:local'
image=json.loads(subprocess.check_output(['docker','image','inspect',reference]))[0]
if lock.exists():assert image['Id']==reference, 'tooling image differs from lock'
(OUT/'tooling-image.json').write_text(json.dumps(image,indent=2)+'\n')
cmd=['docker','run','--rm','--platform','linux/amd64','--cpus','4','--memory','3g','--pids-limit','1024','-v',str(OUT/'upstream')+':/work','-v',str(OUT/'gradle-cache')+':/cache','-v',str(ROOT/'artifact/netflix-validation')+':/validation:ro','-w','/work','-e','GRADLE_USER_HOME=/cache',image['Id'],'bash','gradlew','--no-daemon','--no-watch-fs','--console','plain','--init-script','/validation/lock.init.gradle']
if len(sys.argv)>2 and sys.argv[2]=='offline':cmd+=['--offline','--rerun-tasks','--dependency-verification','strict']
else:cmd+=['--write-locks','--write-verification-metadata','sha256']
if len(sys.argv)>2 and sys.argv[2]=='offline':cmd[2:2]=['--network','none']
cmd+=[':concurrency-limits-core:test']
sys.exit(subprocess.call([sys.executable,str(ROOT/'artifact/netflix-validation/record.py'),sys.argv[1]]+cmd))
