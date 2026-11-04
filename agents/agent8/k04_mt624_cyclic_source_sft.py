"""Four-stream 624-word cyclic phase source emitter, unique K04 proposed coupons.
Freeze source group serializations as the earlier P/R/I/C block model, add
*all 624 within-state circular phase choices*. Original read-only source.
"""
from __future__ import annotations
from pathlib import Path
import itertools
import hashlib
import random
import re
import struct
import time
import argparse
args=argparse.ArgumentParser(description='Cyclic MT624 source-state K04 direct candidate test')
args.add_argument('--start',type=int,default=1)
args.add_argument('--stop',type=int,default=12289)
ns=args.parse_args()
begin,limit=ns.start,ns.stop
assert 1<=begin<limit<=12289
ROOT=Path(__file__).resolve().parents[2] / 'resources'
SPOOL=ROOT/'evidence/print/spool-reconstruction.log'
REC=ROOT/'evidence/recorder/trip-recorder.raw'
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
assert hashlib.sha256(REC.read_bytes()).hexdigest()=='5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
lines=SPOOL.read_text().splitlines()[1:]
sel=[x for x in lines if '2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in x]
assert len(sel)==1 and 'PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5' in sel[0]
P=[bytes.fromhex(re.search('PAYLOAD=([0-9A-F]{32})',x).group(1)) for x in lines if x!=sel[0]]
assert len(P)==132
raw=REC.read_bytes()
assert raw[:8]==b'TRP2DUMP' and struct.unpack_from('<HHI',raw,8)==(2,24,88)
R=[raw[16+i*24+12:16+i*24+16] for i in range(88)]
I=[bytes.fromhex(x) for x in ('049AAB2E','1CDE7A82','CD7C6023','4303C91A')]
C=[bytes.fromhex(x) for x in ('5DBF40EE','52FAAED9','A536D332','6CF0D95A')]
assert len(P)*4+len(R)+len(I)+len(C)==624
MASK=bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
TARGET=bytes.fromhex('930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0')
import json
acceptance=json.loads((ROOT/'acceptance.json').read_text())['slot_sha256']
assert hashlib.sha256(b''.join(I)).hexdigest()==acceptance['K01']
assert hashlib.sha256(b''.join(C)).hexdigest()==acceptance['K06']
assert TARGET.hex()==acceptance['K04']
router=json.loads((ROOT/'evidence/recovery-routing.json').read_text())
assert MASK.hex().upper()==router['K04']['masked_component']
M32=(1<<32)-1

def temper(y):
 y^=y>>11
 y^=(y<<7)&0x9D2C5680
 y^=(y<<15)&0xEFC60000
 y^=y>>18
 return y&M32

def untemper(y):
 x=y
 for _ in range(5):x=y^(x>>18)
 y=x;x=y
 for _ in range(5):x=y^((x<<15)&0xEFC60000)
 y=x;x=y
 for _ in range(7):x=y^((x<<7)&0x9D2C5680)
 y=x;x=y
 for _ in range(5):x=y^(x>>11)
 return x&M32

for _ in range(100):
 v=random.getrandbits(32)
 assert untemper(temper(v))==v
r=random.Random(1300199)
observed=[r.getrandbits(32) for _ in range(624)]
expected=[r.getrandbits(32) for _ in range(4)]
state=[untemper(x) for x in observed]
for j in range(4):
 y=(state[j]&0x80000000)|(state[j+1]&0x7fffffff)
 t=state[j+397]^(y>>1)^((0x9908b0df) if y&1 else 0)
 assert temper(t)==expected[j]

# Cache all native words for each byte and within-record-order interpretation.
def native_group(rows,endian,reverse_rows=False,reverse_words=False):
 rr=list(rows)
 if reverse_rows:rr.reverse()
 out=[]
 for row in rr:
  words=[row[i:i+4] for i in range(0,len(row),4)]
  if reverse_words:words.reverse()
  out.extend(untemper(int.from_bytes(w,endian)) for w in words)
 return tuple(out)
groups={
 'P':[native_group(P,e,rev,wr) for e in ('little','big') for rev in (False,True) for wr in (False,True)],
 'R':[native_group(R,e,rev) for e in ('little','big') for rev in (False,True)],
 'I':[native_group(I,e,rev) for e in ('little','big') for rev in (False,True)],
 'C':[native_group(C,e,rev) for e in ('little','big') for rev in (False,True)],
}
assert [len(groups[x]) for x in 'PRIC']==[8,4,4,4]
start=time.monotonic();hit=[];layouts=0;candidate_checks=0
for order in itertools.permutations('PRIC'):
 for variants in itertools.product(*(groups[x] for x in order)):
  state=variants[0]+variants[1]+variants[2]+variants[3]
  assert len(state)==624
  layouts+=1
  if layouts<begin or layouts>=limit:continue
  # Each rotation is a different cyclic source-state boundary.
  for phase in range(624):
   predicted=[]
   for j in range(4):
    a=state[(phase+j)%624]
    b=state[(phase+j+1)%624]
    c=state[(phase+j+397)%624]
    y=(a&0x80000000)|(b&0x7fffffff)
    predicted.append((c^(y>>1)^(0x9908b0df if y&1 else 0))&M32)
   for native in (False,True):
    words=predicted if native else [temper(x) for x in predicted]
    for reversal in (False,True):
     ordered=list(reversed(words)) if reversal else words
     for endian in ('little','big'):
      packet=b''.join(x.to_bytes(4,endian) for x in ordered)
      comp=bytes(a^b for a,b in zip(packet,MASK))
      candidate_checks+=1
      if hashlib.sha256(comp).digest()==TARGET:
       hit.append((order,phase,native,reversal,endian,comp.hex().upper()))
  if layouts%512==0:print('PROGRESS layouts',layouts,'checks',candidate_checks,'elapsed',round(time.monotonic()-start,2),flush=True)
assert layouts==12288 and candidate_checks==(limit-begin)*624*8
print('DONE',{'layouts_total':layouts,'layout_range':[begin,limit],'phases':624,'complete_checks':candidate_checks,'original_hits':hit,'elapsed':round(time.monotonic()-start,3)})
