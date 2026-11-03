"""K04 source-only node50 seq9..13 four-record-stage witness.

Run from checkout: python agents/agent25/k04_node50_seq9_13_four_stage_sft.py
Selected printer ACK row129, K04/K08 masks and commitments excluded.
"""
from pathlib import Path
import importlib.util
import struct
import zlib

ROOT=Path(__file__).resolve().parents[2]
bridge=Path(__file__).resolve().parent/"k04_seq46_47_joint_stage_sft.py"
spec=importlib.util.spec_from_file_location("source_model",bridge)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
b,s=m.source(ROOT/"resources")
assert b.rank==15365

raw=(ROOT/"resources/evidence/recorder/trip-recorder.raw").read_bytes()
c={}
for i in range(88):
    pos=16+i*24
    stamp,node,event,latch,seq,word,aux,crc=struct.unpack_from("<IHBBI4sII",raw,pos)
    if node==50 and zlib.crc32(raw[pos:pos+20])==crc:
        c[seq]={"stamp":stamp,"event":event,"latch":latch,"word":word,"aux":aux}
assert {9,10,11,12,13}.issubset(c)
fixed={9:-793,10:-788,11:-781,12:-775,13:-769}
joined=b
adds={}
for seq,at in fixed.items():
    updated=m.insert_control(joined,s,at,c[seq]["word"])
    assert updated is not None,(seq,at)
    adds[seq]=updated.rank-joined.rank
    joined=updated
assert adds=={9:1,10:32,11:32,12:0,13:0},adds
assert joined.rank==15430
selected=[term for i in range(951,955) for term in m.get(s,i)]
assert m.target_rank(joined,selected)==128

epoch=1791061742   # 21:09:02 UTC, the independently proposed epoch
# stage sequence: (record source,field,MT pos,max,observed value or None for rejection)
witness=[
 (9,"aux",-792,6000,c[9]["aux"]-2000),
 (10,"time",-791,400,c[10]["stamp"]-epoch),
 (10,"event",-790,39,c[10]["event"]-1),
 (10,"latch",-789,4,c[10]["latch"]),
 (10,"aux",-787,6000,c[10]["aux"]-2000),
 (11,"time",-786,400,c[11]["stamp"]-epoch),
 (11,"event",-784,39,c[11]["event"]-1),
 (11,"latch-reject",-783,4,None),
 (11,"latch",-782,4,c[11]["latch"]),
 (11,"aux",-780,6000,c[11]["aux"]-2000),
 (12,"time",-779,400,c[12]["stamp"]-epoch),
 (12,"event",-778,39,c[12]["event"]-1),
 (12,"latch-reject",-777,4,None),
 (12,"latch",-776,4,c[12]["latch"]),
 (12,"aux-reject",-774,6000,None),
 (12,"aux",-773,6000,c[12]["aux"]-2000),
 (13,"time",-772,400,c[13]["stamp"]-epoch),
 (13,"event",-771,39,c[13]["event"]-1),
 (13,"latch",-770,4,c[13]["latch"]),
]
assert len(witness)==19
known_total=0
for seq,field,pos,upper,observed in witness:
    assert observed is None or 0<=observed<upper,(seq,field,observed)
    terms=m.temper(m.get(s,pos))
    k=upper.bit_length()
    known=sum(b.predict(e) is not None for e in terms[32-k:])
    known_total+=known
    assert m.possible(b,s,pos,upper,observed),(seq,field,pos,observed)
    assert m.possible(joined,s,pos,upper,observed),(seq,field,pos,observed)
    print("source",seq,field,"at",pos,"known",known,"of",k,
          "value",observed if observed is not None else "REJECT")
assert known_total==69,known_total
assert sum(field.endswith("reject") for _,field,_,_,_ in witness)==3
# The negative source-known control index near K04 remains independently unselected.
print("PASS 19 feasible accepted/rejected stages, 69 printer-known field bits")
print("PASS 5 original CONTROL words add 65 source equations; selected quotient still 128")
print("CAUTION indices 10/-788 and 11/-781 were stage-selected at vacant slots.")
print("No K04 coupon authentication and no original K08 final caption.")
