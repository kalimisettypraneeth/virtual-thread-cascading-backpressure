"""Independent rational-arithmetic oracle derived from pinned Gradient2/ExpAvg source.
Never imports, calls, or reads output from the Java implementation under test.
"""
from fractions import Fraction as F
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifact/results/netflix-validation/20261008-official'
scenarios=[('transition',[8,2,16,'0.5',2,'1.5',20],[(10000000,100,False,'warmup')]*10+[(100000000,100,False,'sustained_increase')]*12+[(1000000,100,False,'decrease_recovery')]*16+[(50000000,0,False,'app_limited')]*4),('upper_bound',[4,2,8,'1',2,'1.5',20],[(10000000,100,False,'upper_bound')]*12),('lower_bound',[8,2,8,'1',0,'1',100],[(1000000,100,False,'warmup')]*10+[(1000000000,100,False,'lower_bound')]*8)]
for drop in [False,True]:scenarios.append(('drops_'+str(drop).lower(),[8,2,16,'0.5',1,'1.5',20],[(x,100,drop,'drop_flag') for x in [10000000]*10+[50000000]*4+[1000000]*4]))
lines=[];rows=[]
for name,c,inputs in scenarios:
 initial,minimum,maximum,smoothing,queue,tolerance,window=c;estimate=F(initial);average=F(0);total=0;count=0;published=initial;notifications=0
 lines.append('C,'+name+','+','.join(map(str,c)))
 for i,(rtt,inflight,drop,phase) in enumerate(inputs):
  lines.append(f'S,{rtt},{inflight},{str(drop).lower()}')
  if count<10:count+=1;total+=rtt;average=F(total,count)
  else:average=average*(1-F(2,window+1))+F(rtt)*F(2,window+1)
  snapshot=average
  recovery=snapshot/F(rtt)>2
  if recovery:average*=F(95,100)
  limited=F(inflight)<estimate/2
  if not limited:
   g=max(F(1,2),min(F(1),F(tolerance)*snapshot/rtt))
   estimate=max(F(minimum),min(F(maximum),estimate*(1-F(smoothing))+(estimate*g+queue)*F(smoothing)))
  limit=int(estimate)
  if limit!=published:notifications+=1;published=limit
  rows.append({'scenario':name,'index':i,'phase':phase,'rtt':rtt,'inflight':inflight,'didDrop':drop,'limit':limit,'longRttNs':int(average),'notifications':notifications,'recovery':recovery,'app_limited':limited})
(OUT/'trace-input.csv').write_text('\n'.join(lines)+'\n')
(OUT/'expected-traces.json').write_text(json.dumps({'derivation':'rational arithmetic from pinned Gradient2Limit._update, ExpAvgMeasurement.add/update, AbstractLimit.setLimit; no implementation output','tolerance':{'limit':0,'notification_count':0,'longRttNs_absolute':1},'rows':rows},indent=2)+'\n')
freeze={'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'upstream_revision':'78a74b9878d38c4c048b0304ce12a162ab7b7222','files':{}}
for p in [Path(__file__),OUT/'trace-input.csv',OUT/'expected-traces.json']:
 freeze['files'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'oracle-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n');print('Frozen',len(rows),'samples before conformance execution')
