#!/usr/bin/env python3
"""Record local validation commands and exit codes without modifying original evidence."""
import datetime,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifact/results/netflix-validation/20261008-official'
label=sys.argv[1];argv=sys.argv[2:]
(OUT/'logs').mkdir(parents=True,exist_ok=True)
record={'label':label,'argv':argv,'cwd':os.getcwd(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (OUT/'logs'/f'{label}.stdout').open('wb') as a,(OUT/'logs'/f'{label}.stderr').open('wb') as b:
 try: result=subprocess.run(argv,stdout=a,stderr=b);code=result.returncode
 except OSError as e:b.write(str(e).encode());code=127
record.update(exit_code=code,ended=datetime.datetime.now(datetime.timezone.utc).isoformat())
with (OUT/'commands.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
print(json.dumps(record));sys.exit(code)
