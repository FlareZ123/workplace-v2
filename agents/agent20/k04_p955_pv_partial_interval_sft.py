"""Necessary-condition (overapproximating) p955 known-bit PV rounded interval probe.
All actual target bytes and acceptance omitted. Layout historically unauthenticated.
"""
import runpy, json
from collections import defaultdict
from pathlib import Path
from functools import lru_cache
z=runpy.run_path(str(Path(__file__).with_name('k04_p955_pv_future_source_only_sft.py')))
state=z['state'];temper=z['temper'];known=z['known'];piv=z['piv'];pv=z['pv'];fixed=z['fixed']
MAX=(1<<53)-1

def interval(y,lo,hi):
 yi=round(y*1000)
 den=2000*(hi-lo)
 ln=(2*yi-1-2000*lo)*(1<<53)
 hn=(2*yi+1-2000*lo)*(1<<53)
 lower=max(0,-(-ln//den));upper=min(MAX,hn//den)
 return lower,upper


def compatible(lb,ub,m,v):
 if lb>ub:return False
 if not m:return True
 # Quickly exclude incompatible mandatory high 16 bits.
 mm=m>>37; vv=v>>37
 if mm and all(((q&mm)!=vv) for q in range(lb>>37,(ub>>37)+1)):
  return False
 @lru_cache(maxsize=None)
 def find(bit,gt):
  if bit<0:return 0
  l=(lb>>bit)&1
  for b in ((v>>bit)&1,) if (m>>bit)&1 else (0,1):
   if not gt and b<l:continue
   tail=find(bit-1,gt or b>l)
   if tail is not None:return (b<<bit)|tail
  return None
 z=find(52,False)
 return z is not None and z<=ub

views={}
for lo,hi in ((12,88),(10,90),(0,100),(15,85),(12,90)):
 feasible=defaultdict(list);under=0;tested=0
 for i in range(971,2249):
  a,b=fixed[i],fixed[i+1]
  mask=((a[1]>>5)<<26)|(b[1]>>6)
  value=((a[0]>>5)<<26)|(b[0]>>6)
  info=mask.bit_count()
  if info<12:continue
  tested+=1
  for seq,y in pv.items():
   lb,ub=interval(y,lo,hi)
   if compatible(lb,ub,mask,value):feasible[i].append(seq)
 pairs=[(i,seq) for i,ss in feasible.items() for seq in ss if seq+1 in feasible.get(i+2,())]
 triples=[(i,seq) for i,seq in pairs if seq+2 in feasible.get(i+4,())]
 print('RANGE',lo,hi,'INFORMATIVE_INDEX_PAIRS',tested,'ONE_POINT_COMPATIBILITIES',sum(map(len,feasible.values())), 'ADJACENT_PV_PAIRS',len(pairs),'TRIPLES',len(triples),'EXAMPLE_PAIR',pairs[:5])
 views[(lo,hi)]=(tested,sum(map(len,feasible.values())),len(pairs),len(triples))

# Source-generated q at known fully constrained index must always lie within
# rounded interval, with no assumption about unknown lower output bits.
i=next(i for i,v in fixed.items() if i+1 in fixed and (v[1]>>5)==(0xFFFFFFFF>>5) and (fixed[i+1][1]>>6)==(0xFFFFFFFF>>6))
q=((fixed[i][0]>>5)<<26)|(fixed[i+1][0]>>6)
y=round(12+76*q/(1<<53),3)
lb,ub=interval(y,12,88)
assert lb<=q<=ub
assert compatible(lb,ub,(((fixed[i][1]>>5)<<26)|(fixed[i+1][1]>>6)),q)
print('SYNTHETIC_PV_INTERVAL_POSITIVE',i,y,views)

# Construct a fully source-consistent 624-word MT state, with all independent
# unknown bits set to zero, and test three new PVs at an informative phase.
state_bits=0
for key,(coeff,value) in sorted(piv.items()):
 bit=value ^ (((coeff^(1<<key))&state_bits).bit_count()&1)
 state_bits |= bit<<key
def synthetic_word(i):
 return sum((((expr&state_bits).bit_count()&1)<<b) for b,expr in enumerate(temper(state[624+i])))
info={i:(((fixed[i][1]>>5)<<26)|(fixed[i+1][1]>>6)).bit_count() for i in range(971,2249)}
possible=[i for i in info if all(info.get(i+2*j,0)>=12 for j in range(3))]
assert len(possible)==200
for p in possible[:10]:
 vals=[]
 for j in range(3):
  x,y=synthetic_word(p+2*j),synthetic_word(p+2*j+1)
  u=(((x>>5)*(1<<26))+(y>>6))/(1<<53)
  vals.append(round(12+76*u,3))
  a,b=fixed[p+2*j],fixed[p+2*j+1]
  mask=((a[1]>>5)<<26)|(b[1]>>6)
  val=((a[0]>>5)<<26)|(b[0]>>6)
  lb,ub=interval(vals[-1],12,88)
  assert compatible(lb,ub,mask,val),(p,j,vals)
print('SYNTHETIC_FULL_MT_THREE_READING_POSITIVES',10,'of',len(possible))
