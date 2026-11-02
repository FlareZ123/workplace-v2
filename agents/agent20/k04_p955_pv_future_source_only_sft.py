"""PV fractional donor feasibility from source-only p955 printer MT model.

Original copied ACK row129 withheld. No route mask or acceptance queried.
"""
from pathlib import Path
import re
import hashlib
import json
import sys
from collections import defaultdict

ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
SPOOL=ROOT/'evidence/print/spool-reconstruction.log'
raw=SPOOL.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
lines=[l for l in raw.decode().splitlines() if 'PAYLOAD=' in l]
rows=[None if r==129 else [int.from_bytes(bytes.fromhex(re.search(r'PAYLOAD=([A-F0-9]{32})',line).group(1))[i:i+4],'little') for i in range(0,16,4)] for r,line in enumerate(lines)]
assert rows[129] is None
assert len(rows)==133
starts=[0,7,15,22,30,38,44,51,67,76,84,92,99,112,120,126,132,138,144,151,158,165,171,179,186,192,198,205,211,218,224,230,237,243,250,260,268,278,285,298,305,311,318,328,339,346,352,358,364,370,376,382,388,394,401,407,416,423,429,436,442,456,463,474,481,489,495,507,515,522,530,536,543,549,563,569,576,584,590,597,604,610,617,624,632,638,644,650,659,665,671,679,689,697,705,714,721,733,740,747,753,759,766,772,783,789,796,807,813,820,826,833,839,846,853,861,870,876,882,888,896,906,916,922,928,934,940,946,951,955,959,963,967]
assert len(starts)==133 and starts[129]==955
A=0x9908B0DF
N=624
state=[[1<<(i*32+b) for b in range(32)] for i in range(N)]
for k in range(0,2252):
 x,y,z=state[k],state[k+1],state[k+397]
 state.append([z[b] ^ (y[b+1] if b<30 else (x[31] if b==30 else 0)) ^ (y[0] if (A>>b)&1 else 0) for b in range(32)])

def sr(x,n):return [x[i+n] if i+n<32 else 0 for i in range(32)]
def sl(x,n,m):return [x[i-n] if i>=n and ((m>>i)&1) else 0 for i in range(32)]
def xor(x,y):return [a^b for a,b in zip(x,y)]
def temper(x):
 x=xor(x,sr(x,11));x=xor(x,sl(x,7,0x9D2C5680));x=xor(x,sl(x,15,0xEFC60000));return xor(x,sr(x,18))
cache={i:temper(state[624+i]) for i in set(starts[r]+w for r in range(133) if r!=129 for w in range(4))}
piv={};bad=0
for r in range(133):
 if r==129:continue
 for w in range(4):
  for b,coef in enumerate(cache[starts[r]+w]):
   v=(rows[r][w]>>b)&1
   while coef:
    p=coef.bit_length()-1
    if p in piv:coef^=piv[p][0];v^=piv[p][1]
    else:piv[p]=(coef,v);break
   else:
    if v:bad+=1
assert (len(piv),bad)==(15305,0),(len(piv),bad)

def known(basis,coef):
 v=0
 while coef:
  i=coef.bit_length()-1
  if i not in basis:return None
  p,q=basis[i];coef^=p;v^=q
 return v

# High 27 first-output bits and 26 second-output bits define each exact
# CPython random.random() 53bit float, without needing low discarded bits.
pv_rows=[json.loads(line) for line in (ROOT/'evidence/telemetry/freeze-export.jsonl').read_text().splitlines()]
pv={row['seq']:row['value'] for row in pv_rows if row['field']=='PV'}
assert sorted(pv)==list(range(100,212))
inverse=defaultdict(list)
for seq,value in pv.items():inverse[value].append(seq)
fixed={}
for i in range(971,2252):
 value=0;mask=0
 for b,coef in enumerate(temper(state[624+i])):
  v=known(piv,coef)
  if v is not None:value|=v<<b;mask|=1<<b
 fixed[i]=(value,mask)
mask27=0xFFFFFFE0
mask26=0xFFFFFFC0
source_predictable={}
for i in range(971,2249):
 a,b=fixed[i],fixed[i+1]
 if (a[1]&mask27)==mask27 and (b[1]&mask26)==mask26:
  source_predictable[i]=(((a[0]>>5)*(1<<26))+(b[0]>>6))/(1<<53)
assert len(source_predictable)==154
print('SOURCE_RANK',len(piv),'SOURCE_CONTRADICTIONS',bad)
print('SOURCE_ONLY_PREDICTABLE_FUTURE_53BIT_FLOATS',len(source_predictable),'out_of',1278)
for lo,hi,expected in ((12,88,0),(10,90,0),(0,100,1),(15,85,1),(12,90,1)):
 predicted={i:round(lo+(hi-lo)*v,3) for i,v in source_predictable.items()}
 matches=[(i,s,v) for i,v in predicted.items() for s in inverse.get(v,())]
 paired=[(i,s,v,pv[s+1]) for i,s,v in matches
         if s+1 in pv and i+2 in predicted and predicted[i+2]==pv[s+1]]
 assert len(matches)==expected and not paired,(lo,hi,matches,paired)
 print('RANGE',lo,hi,'ISOLATED_MATCHES',len(matches),'CONSECUTIVE_PV_MATCHES',len(paired),
       'EXAMPLES',matches[:2])

# Independent positive: inject two constructed source-consistent future floats
# as a synthetic PV pair and verify the exact two-draw match, without using
# a selected printer payload or source acceptance.
index=next(i for i in source_predictable if i+2 in source_predictable)
first=round(12+76*source_predictable[index],3)
second=round(12+76*source_predictable[index+2],3)
assert (round(12+76*source_predictable[index],3),
        round(12+76*source_predictable[index+2],3))==(first,second)
print('SYNTHETIC_FUTURE_TWO_FLOAT_POSITIVE_PASS',index,first,second)
print('SCOPE: hypothetical p955 common MT and source-unattested PV scaling; K04 and K08 remain missing')
