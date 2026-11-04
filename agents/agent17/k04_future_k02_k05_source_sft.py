"""H17 source-only p951 future-stage screen, 4 Nov 2026 (Agent17).

Original selected K02/K05 records are held constant after pinning their evidence
files and independently established recovery selectors. Selected 18:02 K04 ACK2,
route mask, K04/K08 commitments and verifier are excluded from model fitting.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents/agent49'))
import k04_p951_symbolic_basis as mt

PINS = {
 'print/spool-reconstruction.log':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
 'telemetry/freeze-export.jsonl':'3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f',
 'recorder/trip-recorder.raw':'5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba',
}
K02 = bytes.fromhex('E1A5E474BAD7E853A2E8C71D3317D507')
K05 = bytes.fromhex('FF8B78200A56E8586DCDA00EF01E4572')
BEGIN, END, THRESHOLD = 1041, 4000, 20
mt.LAST = END + 3

def formats(raw):
 chunks = [raw[i:i+4] for i in range(0,16,4)]
 for endian in ('big','little'):
  for reverse in (False,True):
   for swap in (False,True):
    words = [w[2:]+w[:2] if swap else w for w in chunks]
    yield (endian,reverse,swap),[int.from_bytes(w,endian) for w in (words[::-1] if reverse else words)]

def main():
 for rel,want in PINS.items():
  got=hashlib.sha256((ROOT/'resources/evidence'/rel).read_bytes()).hexdigest()
  assert got==want,(rel,got)
 assert hashlib.sha256(K02).digest()[:16].hex().upper()=='0D7E3AB56FB75DA3EB0E2E06786D239E'
 assert K05.hex().upper()=='FF8B78200A56E8586DCDA00EF01E4572'
 b,s = mt.source(ROOT/'resources')
 assert b.rank==15365
 projected=[]
 for stage in range(BEGIN,END+4):
  native=mt.get(s,stage)
  pairs=[]
  for output in (native,mt.temper(native)):
   mask=value=0
   for bit,vector in enumerate(output):
    v=b.predict(vector)
    if v is not None:
     mask |= 1<<bit
     value |= v<<bit
   pairs.append((mask,value))
  projected.append(pairs)
 count={'K02':0,'K05':0}
 matches={'K02':[],'K05':[]}
 best={'K02':(129,0,None),'K05':(33,0,None)}
 for stage in range(BEGIN,END+1):
  for label,group in formats(K02):
   for view in range(2):
    known=errors=0
    for lane,actual in enumerate(group):
     mask,value=projected[stage-BEGIN+lane][view]
     known+=mask.bit_count()
     errors+=((value^actual)&mask).bit_count()
    if known>=THRESHOLD:
     count['K02']+=1
     if errors<best['K02'][0]:best['K02']=(errors,known,(stage,label,view))
     if errors==0:matches['K02'].append((stage,label,view,known))
  for view in range(2):
   mask,value=projected[stage-BEGIN][view]
   if mask.bit_count()<THRESHOLD:continue
   for latch in range(4):
    for endian in ('big','little'):
     actual=int.from_bytes(K05[4*latch:4*latch+4],endian)
     errors=((value^actual)&mask).bit_count()
     count['K05']+=1
     if errors<best['K05'][0]:best['K05']=(errors,mask.bit_count(),(stage,latch,endian,view))
     if errors==0:matches['K05'].append((stage,latch,endian,view,mask.bit_count()))
 spool=(ROOT/'resources/evidence/print/spool-reconstruction.log').read_bytes()
 packets=[bytes.fromhex(h.decode()) for h in re.findall(rb'PAYLOAD=([0-9A-F]{32})',spool)]
 assert len(packets)==133
 for lane in range(4):
  original=int.from_bytes(packets[110][4*lane:4*lane+4],'little')
  predicted=mt.temper(mt.get(s,mt.STARTS[110]+lane))
  assert all(b.predict(vector)==((original>>i)&1) for i,vector in enumerate(predicted))
 assert count=={'K02':25368,'K05':10584},count
 assert not matches['K02'] and not matches['K05'],matches
 assert best['K02'][:2]==(4,22) and best['K05'][:2]==(4,22),best
 print('NO_SOURCE_MATCH',count,'BEST',best,'CONTROLS_PASS')

if __name__=='__main__':main()
