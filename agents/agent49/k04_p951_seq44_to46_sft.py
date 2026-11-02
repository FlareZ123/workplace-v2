"""SFT: p951 seq44->45 four-field source prediction and seq46 staging failure.
Run: python agents/agent49/k04_p951_seq44_to46_sft.py resources
Original sources only. Does not read selected row129, mask or any commitment.
"""
import hashlib,struct,sys,zlib
from pathlib import Path
from k04_p951_symbolic_basis import source,get,temper,untemper
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
b,s=source(root)
raw=(root/'evidence/recorder/trip-recorder.raw').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
rows={}
for row in range(88):
 at=16+24*row
 ts,node,event,latch,seq,ctrl,aux,crc=struct.unpack_from('<IHBBI4sII',raw,at)
 if node==50 and zlib.crc32(raw[at:at+20])==crc:
  rows[seq]=(ts,event,latch,ctrl,aux)
assert set((43,44,45,46)).issubset(rows)
def upper(pos,n):
 bits=[b.predict(v) for v in temper(get(s,pos))[32-n:]]
 return None if None in bits else sum(bit<<j for j,bit in enumerate(bits))
expected=[(-544,13,rows[44][4]-2000,'AUX44'),(-543,9,rows[45][0]-1791061742,'TIMESTAMP45'),(-542,6,rows[45][1]-1,'EVENT45'),(-541,3,rows[45][2],'LATCH45')]
assert [(pos,n,target) for pos,n,target,_ in expected]==[(-544,13,5700),(-543,9,217),(-542,6,25),(-541,3,0)]
for pos,n,target,label in expected:
 got=upper(pos,n)
 assert got==target,(label,got,target)
 print('ORIGINAL_HOLDOUT_PASS',label,'index',pos,'bits',n,'value',got)
native46=untemper(int.from_bytes(rows[46][3],'little'))
for gap in (4,5,6,7,8):
 at=-540+gap
 bits=[b.predict(v) for v in get(s,at)]
 known=sum(v is not None for v in bits)
 differences=sum(v is not None and v!=((native46>>j)&1) for j,v in enumerate(bits))
 assert differences>0
 print('SEQ46_CONTRADICTION','gap',gap,'index',at,'source_known',known,'different',differences)
assert rows[46][3].hex().upper()=='49B23079'
print('PASS source_rank',b.rank,'four independent field values; seq46 gaps4..8 falsified')
print('No historical producer or selected K04 bits authenticated; K08 unresolved')
