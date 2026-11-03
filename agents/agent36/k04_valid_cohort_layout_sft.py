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

# Independent AX-7778 transfer checkpoint family: does it constrain the single
# previously source-invisible pre-lattice valid K05 four-word stage?
transfer_raw=(ROOT/'evidence/transfers/transfer-audit.jsonl').read_bytes()
assert hashlib.sha256(transfer_raw).hexdigest()=='32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'
chunks=sorted((json.loads(line) for line in transfer_raw.splitlines()
               if json.loads(line).get('kind')=='CHUNK'
               and json.loads(line).get('transfer')=='AX-7778'),
              key=lambda x:(x['seq'],x['attempt']))
assert len(chunks)==16
ax=symbolic.Basis();ax.rows=basis.rows.copy();ax.rank=basis.rank
for i,ch in enumerate(chunks):
  x=int(ch['checkpoint'],16)
  upper16=(x>>8)|((x&255)<<8)
  for bit,expr in enumerate(symbolic.temper(symbolic.get(states,-157+i))[16:]):
    ax.insert(expr,(upper16>>bit)&1)
assert ax.rank==15495,ax.rank
assert posterior(ax,lattice)=={'consistent':True,'donor_gain':127,'target_unresolved_bits':128}
for name,indices in layout.items():
  layout_sample=[(idx,records[seq][1]) for seq,idx in zip(range(300,304),indices)]
  result=posterior(ax,lattice+layout_sample)
  assert result['consistent'] is False,(name,result)
  print('ax+grid+300',name,result)
# Identify which original source-labelled K05 bits are individually predicted
# by AX and grid before ever adding any K05 source words.
ax_grid=symbolic.Basis();ax_grid.rows=ax.rows.copy();ax_grid.rank=ax.rank
for idx,native in lattice:
    for j,expr in enumerate(symbolic.get(states,idx)):
        ax_grid.insert(expr,(native>>j)&1)
assert ax_grid.rank==15622,ax_grid.rank
predictions={}
for seq,idx in zip(range(300,304),layout['pre-lattice-contiguous']):
    original=records[seq][1]
    bits=[(j,ax_grid.predict(expr),(original>>j)&1)
          for j,expr in enumerate(symbolic.get(states,idx))
          if ax_grid.predict(expr) is not None]
    predictions[seq]=bits
    print('AX+GRID individually predicted K05',seq,idx,bits)
assert predictions[300]==[] and predictions[301]==[]
assert predictions[302]==[(10,1,1),(25,0,0)]
assert predictions[303]==[(10,0,1)]
# There is an independently predicted *single-bit* contradiction for seq303,
# and an extra interword parity contradiction already at seq302 after
# adding original seq300/301 source bytes. Trace the earliest parity failure.
aug=symbolic.Basis();aug.rows=ax_grid.rows.copy();aug.rank=ax_grid.rank
conflict=None
for seq,idx in zip(range(300,304),layout['pre-lattice-contiguous']):
    native=records[seq][1]
    for bit,expr in enumerate(symbolic.get(states,idx)):
        pred=aug.predict(expr)
        if pred is not None and pred!=((native>>bit)&1):
            conflict={'seq':seq,'native_index':idx,'native_bit':bit,
                      'predicted':pred,'recorded':(native>>bit)&1,
                      'source_rank':aug.rank}
            break
        aug.insert(expr,(native>>bit)&1)
    if conflict is not None:
        break
assert conflict=={'seq':302,'native_index':-326,'native_bit':20,
                  'predicted':1,'recorded':0,'source_rank':15701}
print('AX+GRID+300 first multiword parity contradiction',conflict)
