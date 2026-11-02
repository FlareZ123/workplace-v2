"""Conditional selected K04 bit from original node50 seq47 at MT index -523.
No acceptance or combined commitment read. Selected printer row excluded from fit.
Run: python agents/agent49/k04_p951_seq47_523_target_parity_sft.py resources
"""
import hashlib,json,re,struct,sys,zlib
from pathlib import Path
from k04_p951_symbolic_basis import Basis,source,get,untemper
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
b,s=source(root)
record=(root/'evidence/recorder/trip-recorder.raw').read_bytes()
assert hashlib.sha256(record).hexdigest()=='5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
seq47=[]
for i in range(88):
 at=16+24*i
 ts,node,event,latch,seq,ctrl,aux,crc=struct.unpack_from('<IHBBI4sII',record,at)
 if node==50 and seq==47 and zlib.crc32(record[at:at+20])==crc:seq47.append(ctrl)
assert seq47==[bytes.fromhex('98535679')]
native=untemper(int.from_bytes(seq47[0],'little'))
aug=Basis();aug.rows=b.rows.copy();aug.rank=b.rank
for j,v in enumerate(get(s,-523)):aug.insert(v,(native>>j)&1)
assert aug.rank-b.rank==31
target=[get(s,951+j//32)[j%32] for j in range(128)]
assert all(b.predict(v) is None for v in target)
known=[(j,aug.predict(v)) for j,v in enumerate(target) if aug.predict(v) is not None]
assert known==[(30,1)],known
print('CONDITIONAL_SEQ47_AT_MINUS523','rank_delta',31,'selected_native_bit30',1)
selector=sum(((untemper(1<<j)>>30)&1)<<j for j in range(32))
assert selector==0x40008000
spool=(root/'evidence/print/spool-reconstruction.log').read_bytes()
assert hashlib.sha256(spool).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
packets=re.findall(rb'PAYLOAD=([0-9A-F]{32})',spool)
assert len(packets)==133
copy=bytes.fromhex(packets[129].decode())
mask=bytes.fromhex(json.loads((root/'evidence/recovery-routing.json').read_text())['K04']['masked_component'])
par=lambda data:(int.from_bytes(data[:4],'little')&selector).bit_count()&1
candidate=bytes(a^b for a,b in zip(copy,mask))
assert (1^par(mask))==0
assert par(candidate)==1
print('PARITY_SELECTOR',f'{selector:08X}','conditional_key_parity',0,'copied_key_parity',1)
print('No historical seq47 index authentication; K04 remains unresolved')
