"""H-17 original-source GF(2) rejection of a seq56->57 recorder-stage bridge.
Run: python agents/agent18/k04_recorder_latch57_symbolic_sft.py
"""
import hashlib
import importlib.util
import struct
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
mod=ROOT/'agents/agent49/k04_p951_symbolic_basis.py'
spec=importlib.util.spec_from_file_location('source',mod)
source=importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
basis,states=source.source(ROOT/'resources')
raw=(ROOT/'resources/evidence/recorder/trip-recorder.raw').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
rows={}
for i in range(88):
 at=16+24*i
 ts,node,event,latch,seq,word,aux,crc=struct.unpack_from('<IHBBI4sII',raw,at)
 if node!=50:continue
 assert zlib.crc32(raw[at:at+20])==crc
 rows[seq]={'event':event-1,'latch':latch,'aux':aux-2000,'control':source.untemper(int.from_bytes(word,'little'))}
assert len(rows)==72

def add_word(at,value,bits,native):
 x=source.get(states,at)
 if not native:x=source.temper(x)
 for j in bits:basis.insert(x[j],(value>>j)&1)

# Candidate from source-matched control indexes, WITHOUT selected ACK or K04 hash:
# CTRL56(-447), EVENT56(-446), AUX56(-445), 2 opaque timestamp draws,
# LATCH57(-442), CTRL57(-441), within a frozen five-field writer model.
add_word(-447,rows[56]['control'],range(32),True)
add_word(-446,rows[56]['event']<<26,range(26,32),False)
add_word(-445,rows[56]['aux']<<19,range(19,32),False)
assert basis.rank>=15410
latch=rows[57]['latch']
assert latch==3
expr=source.temper(source.get(states,-442))[30]
predicted=basis.predict(expr)
print('SOURCE_RANK_AFTER_ORIGINAL_UPSTREAM',basis.rank)
print('SELECTED_K04_INDIVIDUALLY_FIXED_NATIVE_BITS',
      sum(basis.predict(x) is not None for at in range(951,955)
          for x in source.get(states,at)))
print('ORIGINAL_LATCH57',latch,'PREDICTED_LATCH_BIT0',predicted)
assert predicted==0 and (latch&1)==1
assert basis.predict(source.temper(source.get(states,-442))[31]) in (None,1)
# Independently planted alternate latch=2 is source-consistent; real latch=3 is not.
basis.insert(expr,0)
basis.insert(source.temper(source.get(states,-442))[31],1)
print('SYNTHETIC_LATCH2_PASSES, ORIGINAL_LATCH3_CONTRADICTS PASS')
print('Selected K04 omitted; no original coupon bytes or K08 words inferred')
