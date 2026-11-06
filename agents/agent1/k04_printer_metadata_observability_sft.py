"""Exact GF(2) MT source-only printer model; selected row129 omitted."""
from pathlib import Path
import re,hashlib
ORIGIN,LAST,U,MAG=-1100,1040,0xffffffff,0x9908b0df
STARTS=[0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
def untemper(x):
 for k,left,m in ((18,False,U),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,U)):
  y=x
  for _ in range(6):y=x^(((y<<k)&m) if left else y>>k)
  x=y&U
 return x
def words():
 a=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
 for i in range(624,LAST-ORIGIN+1):
  t=i-624
  a.append([a[t+397][j]^(a[t][31] if j==30 else (a[t+1][j+1] if j<30 else 0))^(a[t+1][0] if (MAG>>j)&1 else 0) for j in range(32)])
 return a
def get(a,i):
 assert ORIGIN<=i<=LAST,(i,ORIGIN,LAST)
 return a[i-ORIGIN]
class Basis:
 def __init__(self):self.rows={};self.rank=0
 def insert(self,v,b):
  while v:
   p=v.bit_length()-1
   if p not in self.rows:self.rows[p]=(v,b);self.rank+=1;return
   w,c=self.rows[p];v^=w;b^=c
  assert b==0,'original printer contradiction'
 def predict(self,v):
  b=0
  while v:
   p=v.bit_length()-1
   if p not in self.rows:return None
   w,c=self.rows[p];v^=w;b^=c
  return b
def temper(v):
 a=[v[j]^(v[j+11] if j+11<32 else 0) for j in range(32)]
 b=[a[j]^(a[j-7] if j>=7 and (0x9d2c5680>>j)&1 else 0) for j in range(32)]
 c=[b[j]^(b[j-15] if j>=15 and (0xefc60000>>j)&1 else 0) for j in range(32)]
 return [c[j]^(c[j+18] if j+18<32 else 0) for j in range(32)]
def source(root):
 raw=(Path(root)/'evidence/print/spool-reconstruction.log').read_bytes()
 assert hashlib.sha256(raw).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
 rows=[bytes.fromhex(x.decode()) for x in re.findall(rb'PAYLOAD=([0-9A-F]{32})',raw)]
 assert len(rows)==len(STARTS)==133
 s=words();b=Basis()
 for row,(payload,pos) in enumerate(zip(rows,STARTS)):
  if row==129:continue
  for lane in range(4):
   native=untemper(int.from_bytes(payload[lane*4:lane*4+4],'little'))
   for j,v in enumerate(get(s,pos+lane)):b.insert(v,(native>>j)&1)
 assert b.rank==15365
 try:get(s,ORIGIN-1)
 except AssertionError:pass
 else:raise AssertionError('negative source index alias')
 return b,s


# Stage-vector comparison and information-theoretic observability research, Agent 1.
# The p951 base functions above are preserved verbatim from Agent 49.
# This extra experiment never supplies a candidate from the disputed selected row.
import json, random, argparse
from collections import Counter

class RankBasis:
 def __init__(self): self.rows={}
 def add(self,v):
  while v:
   k=v.bit_length()-1
   if k not in self.rows:
    self.rows[k]=v
    return 1
   v^=self.rows[k]
  return 0
 def extend(self,vs): return sum(self.add(v) for v in vs)
 def copy(self):
  out=RankBasis()
  out.rows=self.rows.copy()
  return out
 def remainder(self,v):
  rem=0
  while v:
   k=v.bit_length()-1
   if k in self.rows: v^=self.rows[k]
   else:
    rem|=1<<k
    v^=1<<k
  return rem

def rank(vectors): return RankBasis().extend(vectors)

def synthetic_control():
 rng=random.Random(0x732F1337)
 v=[untemper(rng.getrandbits(32)) for _ in range(680)]
 for i in range(56):
  y=(v[i]&0x80000000)|(v[i+1]&0x7fffffff)
  got=v[i+397]^(y>>1)^(MAG if y&1 else 0)
  assert got==v[i+624],i
 print("Synthetic native MT recurrence: 56/56 PASS")

def audit(root):
 path=Path(root)/"evidence/print/spool-reconstruction.log"
 raw=path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
 payloads=[bytes.fromhex(s.decode()) for s in re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)]
 assert len(payloads)==133
 fixtures=json.loads((Path(__file__).with_name("k04_prior_six_stage_fixtures.json")).read_text())["row_starts"]
 st=words()
 synthetic_control()
 for name in sorted(fixtures,key=int):
  starts=fixtures[name]
  assert len(starts)==133 and starts[0]==0 and starts[-1]+3<=LAST
  measured={start+j for row,start in enumerate(starts) if row!=129 for j in range(4)}
  selected={starts[129]+j for j in range(4)}
  assert len(measured)==528 and not measured.intersection(selected)
  hidden=[p for p in range(starts[-1]+4) if p not in measured and p not in selected]
  known=RankBasis()
  checked=Basis()
  for row,(payload,start) in enumerate(zip(payloads,starts)):
   if row==129: continue
   for k in range(4):
    native=untemper(int.from_bytes(payload[4*k:4*k+4],"little"))
    for j,v in enumerate(get(st,start+k)):
     known.add(v)
     checked.insert(v,(native>>j)&1)
  assert checked.rank==len(known.rows)
  target=[v for p in sorted(selected) for v in get(st,p)]
  target_residual=known.copy().extend(target)
  print("Fixture",name,"known rank",len(known.rows),"hidden",len(hidden),"selected residual",target_residual,flush=True)
  # Unrealistically generous metadata: disclose 8 most significant bits
  # of EVERY hidden nonselected native MT output, not just true CLASS/DEST draws.
  expanded=known.copy()
  for p in hidden: expanded.extend(temper(get(st,p))[24:32])
  left=expanded.copy().extend(target)
  print(" all-hidden 8-MSB leak: rank",len(expanded.rows),"remaining selected",left,flush=True)
  # The direct getrandbits(2) model is weaker than the above bound.
  assert 0<=left<=target_residual
  # Which single omitted native full32 word *could* supply selected information?
  tquot=[known.remainder(v) for v in target]
  assert rank(tquot)==target_residual
  hits=[]
  for p in hidden:
   wquot=[known.remainder(v) for v in get(st,p)]
   r=rank(wquot)
   gain=target_residual+r-rank(tquot+wquot)
   if gain: hits.append((p,gain))
  print(" single fullword donors:",len(hits),"positions with nonzero K04 gain; top",sorted(hits,key=lambda z:(-z[1],z[0]))[:30],flush=True)

  # Hypothetically source the complete native words at both causal
  # four-word donor quartets, using each frozen chronology's own stage.
  # These sites are algebraic hypothetical oracles, never observed coupons.
  start=starts[129]
  low=[start-623+i for i in range(4)]
  high=[start-227+i for i in range(4)]
  assert set(low+high).issubset(set(hidden))
  with_first=known.copy()
  for p in low: with_first.extend(get(st,p))
  first_free=with_first.copy().extend(target)
  with_second=known.copy()
  for p in high: with_second.extend(get(st,p))
  second_free=with_second.copy().extend(target)
  for p in high: with_first.extend(get(st,p))
  both_free=with_first.copy().extend(target)
  print(" causal 4+4 fullword donor quartets:",low,high,
        "target residual after first / second / both:",
        first_free,second_free,both_free,flush=True)
  assert both_free==0

  assert name!="951" or (len(known.rows)==15365 and target_residual==128 and left==128 and hits==[(724,1)])
 print("All fixture source fits and observability audits PASS")

if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--root",default=str(Path(__file__).resolve().parents[2]/"resources"))
 audit(parser.parse_args().root)
