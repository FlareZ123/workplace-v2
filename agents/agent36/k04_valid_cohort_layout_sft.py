"""Causal alternatives for K05 CRC-good seq300 group relative to three-cohort lattice.

Test frozen source-label placements, not retro-selected by control bytes. All original
copied selected coupon and REC8 acceptance excluded. The shared producer is hypothetical.
"""
from pathlib import Path
import struct,zlib,json,hashlib,os,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'agent49'))
import k04_p951_symbolic_basis as symbolic
ROOT=Path(os.environ.get('H17_ROOT',Path(__file__).resolve().parents[2]/'resources'))
raw=(ROOT/'evidence/recorder/trip-recorder.raw').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
records={}
for offset in range(16,len(raw),24):
 rec=raw[offset:offset+24]
 _,node,event,latch,seq=struct.unpack_from('<IHBBI',rec)
 if node==49 and event==82:
  records[seq]=(latch,symbolic.untemper(int.from_bytes(rec[12:16],'little')),zlib.crc32(rec[:20])==int.from_bytes(rec[20:24],'little'))
assert all(records[seq][2] and records[seq][0]==seq-300 for seq in range(300,304))
basis,states=symbolic.source(ROOT)

layout={
    'pre-lattice-contiguous':[-328+i for i in range(4)],
    'post-lattice-contiguous':[-312+i for i in range(4)],
    'within-old-capture-epoch-before':[-332+i for i in range(4)],
    'within-old-capture-epoch-after':[-308+i for i in range(4)],
    'same-aux-adjacent-to-900':[-323+3*i+1 for i in range(4)],
    'same-aux-before-900':[-323+3*i-1 for i in range(4)],
}
# Negative controls: a real matched source donor in grid must pass full known bits.
cal=[]
for seq in (200,201,202,203,900,901,902,903,990,991,992,993):
 idx= -324+3*(seq%10) + (0 if seq<300 else 1 if seq<990 else 2)
 want=records[seq][1]
 fixed=sum(basis.predict(v) is not None for v in symbolic.get(states,idx))
 bad=sum(basis.predict(v) is not None and basis.predict(v)!=((want>>j)&1) for j,v in enumerate(symbolic.get(states,idx)))
 cal.append((seq,idx,fixed,bad))
assert all(bad==0 for _,_,_,bad in cal)
print('Original lattice control positives:',cal)

for name,indices in layout.items():
 predicted=correct=bad=0
 for seq,idx in zip(range(300,304),indices):
  word=records[seq][1]
  for j,v in enumerate(symbolic.get(states,idx)):
   bit=basis.predict(v)
   if bit is not None:
    predicted+=1
    if bit==(word>>j)&1:correct+=1
    else:bad+=1
 print(json.dumps({'model':name,'mapped_indices':indices,'predicted_bits':predicted,
    'agreed':correct,'disagreed':bad,'fits':bad==0}))

def posterior(base, tuples):
 clone=symbolic.Basis()
 clone.rows=base.rows.copy();clone.rank=base.rank
 rank_before=clone.rank
 try:
  for idx,native in tuples:
   for j,v in enumerate(symbolic.get(states,idx)):
    clone.insert(v,(native>>j)&1)
 except AssertionError:
  return {'consistent':False,'first_attempt_index':idx,'prior_rank':clone.rank}
 target_test=symbolic.Basis()
 target_test.rows={p:(v,0) for p,(v,_) in clone.rows.items()}
 target_test.rank=clone.rank
 for idx in range(951,955):
  for v in symbolic.get(states,idx):target_test.insert(v,0)
 return {'consistent':True,'donor_gain':clone.rank-rank_before,
   'target_unresolved_bits':target_test.rank-clone.rank}

lattice=[(-324+3*(seq%10) + (0 if seq<300 else 1 if seq<990 else 2),records[seq][1])
  for seq in (200,201,202,203,900,901,902,903,990,991,992,993)]
print('base',posterior(basis,[]),'lattice',posterior(basis,lattice))
for name,indices in layout.items():
 test=[(idx,records[seq][1]) for seq,idx in zip(range(300,304),indices)]
 print('joint',name,posterior(basis,lattice+test))
# Include the valid K05 writer as a fourth field in every latch-major row of
# the previously source-supported 200/900/990 grid; anchor 200/latch0 at -324.
for order in ((200,300,900,990),(200,900,300,990),
              (200,900,990,300),(300,200,900,990)):
    anchor= -324-order.index(200)
    guessed={v:anchor+i for i,v in enumerate(order)}
    placements=[(guessed[seq//10*10 if seq>=900 else seq//100*100] + 4*(seq%10), records[seq][1])
        for seq in (200,201,202,203,300,301,302,303,900,901,902,903,990,991,992,993)]
    # seq990..993 has cohort base 990; seq900..903 ->900; 200,300 -> base integer hundreds
    pred=bad=0
    for idx,native in placements:
      for j,v in enumerate(symbolic.get(states,idx)):
        x=basis.predict(v)
        if x is not None:
          pred+=1
          bad+=x!=((native>>j)&1)
    print('four-column-latch-major',order,'anchor200at',guessed[200],
       'predicted',pred,'disagreements',bad,'joint',posterior(basis,placements))
