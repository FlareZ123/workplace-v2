"""H17 node50 printer-source chronology and metadata SFT, original K04 withheld.
Run from repo root: python agents/agent6/k04_node50_15anchors_sft.py.
Conditional on the p951 MT producer geometry; no historical firmware claim.
"""
import hashlib, json, random, struct, sys, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'agents/agent49'))
from k04_p951_symbolic_basis import source,get,temper,untemper,Basis

REC_SHA='5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
ANCHORS={7:-810,12:-775,13:-769,24:-683,25:-677,41:-568,44:-545,45:-540,70:-339}
EXPECTED=[(7,-810,32),(9,-793,17),(12,-775,32),(13,-769,32),(14,-759,13),(24,-683,32),(25,-677,32),(41,-568,32),(43,-552,13),(44,-545,32),(45,-540,26),(61,-417,13),(63,-397,15),(64,-390,13),(70,-339,32)]

def recorder():
 raw=(ROOT/'resources/evidence/recorder/trip-recorder.raw').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==REC_SHA
 assert raw[:8]==b'TRP2DUMP' and len(raw)==16+88*24
 rows={}
 for i in range(88):
  row=raw[16+i*24:16+(i+1)*24]
  ts,node,event,latch,seq=struct.unpack_from('<IHBBI',row)
  control,aux,crc=struct.unpack_from('<III',row,12)
  if node==50:
   assert zlib.crc32(row[:20])==crc
   rows[seq]=dict(time=ts-1791061740,event=event,latch=latch,control=control,aux=aux)
 assert set(rows)==set(range(72))
 return rows

def predicted(b,s):
 output={}
 for stage in range(-950,-250):
  mask=value=0
  for bit,eq in enumerate(temper(get(s,stage))):
   k=b.predict(eq)
   if k is not None:mask|=1<<bit;value|=k<<bit
  output[stage]=(mask,value)
 return output

def accepts(pred,index,k,v):
 mask,value=pred[index]
 mask>>=32-k;value>>=32-k
 return (v^value)&mask==0,mask.bit_count()

def rejects_possible(pred,index,k,bound):
 mask,value=pred[index]
 mask>>=32-k;value>>=32-k
 return value|(((1<<k)-1)^mask)>=bound

def metadata(pred,rec,seq,stage):
 ok,lbits=accepts(pred,stage-1,3,rec[seq]['latch'])
 if not ok:return []
 choices=[]
 for ra in range(4):
  apos=stage+1+ra
  if not all(rejects_possible(pred,i,13,6000) for i in range(stage+1,apos)):continue
  ok,abits=accepts(pred,apos,13,rec[seq]['aux']-2000)
  if not ok:continue
  for re in range(4):
   epos=apos+1+re
   if not all(rejects_possible(pred,i,6,40) for i in range(apos+1,epos)):continue
   ok,ebits=accepts(pred,epos,6,rec[seq]['event']-1)
   if ok:choices.append((lbits+abits+ebits,ra,re))
 return choices

def joint_rank(b,s,rec,found,opts):
 joint=Basis();joint.rows=dict(b.rows);joint.rank=b.rank
 for seq,index,_ in found:
  val=untemper(rec[seq]['control'])
  for bit,eq in enumerate(get(s,index)):joint.insert(eq,(val>>bit)&1)
 for seq,index in ANCHORS.items():
  _,ra,re=max(opts[seq],key=lambda x:(x[0],-x[1]-x[2]))
  for pos,k,val in ((index-1,3,rec[seq]['latch']),
                    (index+1+ra,13,rec[seq]['aux']-2000),
                    (index+2+ra+re,6,rec[seq]['event']-1)):
   for bit,eq in enumerate(temper(get(s,pos))[32-k:]):joint.insert(eq,(val>>bit)&1)
 span=Basis();span.rows={p:(eq,0) for p,(eq,_) in joint.rows.items()};span.rank=joint.rank
 for stage in range(951,955):
  for eq in get(s,stage):span.insert(eq,0)
 return joint.rank,span.rank-joint.rank

def sequence_control(found):
 rng=random.Random(20261103)
 positions=[stage for _,stage,_ in found]
 maximum=0
 for _ in range(100000):
  shuffled=sorted(zip(rng.sample(range(72),len(found)),positions))
  ranks=[1]*len(shuffled)
  for i,(seq,stage) in enumerate(shuffled):
   for j,(seq0,stage0) in enumerate(shuffled[:i]):
    if 4*(seq-seq0)<=stage-stage0<=11*(seq-seq0):
     ranks[i]=max(ranks[i],ranks[j]+1)
  maximum=max(maximum,max(ranks))
 return maximum

def main():
 rng=random.Random(2603)
 n=[untemper(rng.getrandbits(32)) for _ in range(625)]
 m=((n[0]&0x80000000)|(n[1]&0x7fffffff))>>1
 assert n[624]==(n[397]^m^(0x9908b0df if n[1]&1 else 0))
 b,s=source(ROOT/'resources')
 assert b.rank==15365
 rec=recorder();pred=predicted(b,s)
 found=[]
 for seq in range(72):
  v=rec[seq]['control']
  hits=[(pos,mask.bit_count()) for pos,(mask,known) in pred.items() if mask.bit_count()>=13 and (v^known)&mask==0]
  assert len(hits)<=1,(seq,hits)
  if hits:found.append((seq,*hits[0]))
 assert found==EXPECTED
 assert all(4*(y[0]-x[0])<=y[1]-x[1]<=11*(y[0]-x[0]) for x,y in zip(found,found[1:]))
 opts={seq:metadata(pred,rec,seq,pos) for seq,pos in ANCHORS.items()}
 assert all(opts.values())
 assert opts[44]==[(22,0,0)]
 assert accepts(pred,-542,9,rec[44]['time'])[0] is False
 rank,residual=joint_rank(b,s,rec,found,opts)
 assert (rank,residual)==(15459,128)
 shuffled_max=sequence_control(found)
 assert shuffled_max==7
 print(json.dumps(dict(source_rank=b.rank,matched_control_stages=found,heldout_seq44_metadata_bits=22,
  timestamp_next_draw_falsified=True,metadata_fixed_bits={i:max(o[0] for o in opts[i]) for i in opts},
  joint_rank=rank,increment=rank-b.rank,K04_unknown_bits=residual,
  source_label_shuffles=100000,largest_shuffled_smooth_chain=shuffled_max,
  seeded_control='PASS',original_recovery='INCOMPLETE'),sort_keys=True))

if __name__=='__main__':main()
