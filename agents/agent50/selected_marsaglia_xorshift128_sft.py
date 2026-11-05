"""Source-constrained selected-job Marsaglia xor128 complete coupon SFT."""
import hashlib
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[2]
spool=(root/"resources/evidence/print/spool-reconstruction.log").read_bytes()
routing=json.loads((root/"resources/evidence/recovery-routing.json").read_text())
accept=json.loads((root/"resources/acceptance.json").read_text())
assert hashlib.sha256(spool).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
mask=bytes.fromhex(routing["K04"]["masked_component"])
target=accept["slot_sha256"]["K04"]
known=[]
for attempt in (1,3):
    items=[s for s in spool.decode().splitlines() if
           f"JOB=PS-261003-0417 ATTEMPT={attempt} STATE=REQUESTED CLASS=RECOVER" in s]
    assert len(items)==1
    known.append(bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",items[0]).group(1)))
M=(1<<32)-1

def next_word(st):
    x,y,z,w=st
    t=x^((x<<11)&M)
    x,y,z=y,z,w
    w=(w^(w>>19)^t^(t>>8))&M
    return w,(x,y,z,w)

def parse(buf,endian,reverse):
    values=[int.from_bytes(buf[i:i+4],endian) for i in range(0,16,4)]
    if reverse:values.reverse()
    return values

def emit(values,endian,reverse):
    values=list(values)
    if reverse:values.reverse()
    return b"".join(v.to_bytes(4,endian) for v in values)

# Plant exact generator history with two nonzero hidden draw gaps.
original=(0x12345678,0xFEDCBA98,0x13579BDF,0x2468ACE0)
initial=[]
state=original
for _ in range(4):
    out,state=next_word(state);initial.append(out)
assert state==tuple(initial)
history=initial[:]
for _ in range(4+31+48+4):
    out,state=next_word(state);history.append(out)
reconstructed=[];state=tuple(initial)
for _ in range(len(history)-4):
    out,state=next_word(state);reconstructed.append(out)
assert reconstructed[31:35]==history[35:39]
assert reconstructed[4+31+48:8+31+48]==history[8+31+48:12+31+48]
planted=bytes(a^b for a,b in zip(emit(reconstructed[31:35],"big",False),mask))
expected=bytes(a^b for a,b in zip(emit(history[35:39],"big",False),mask))
assert planted==expected

results={"generator":"Marsaglia original xor128 (11,8,19)",
         "safe_source_attempts":[1,3],"selected_attempt":2,
         "original_complete_K04_candidate_checks":0,
         "original_K04_matches":[],
         "source_attempt3_checks":0,"source_attempt3_matches":[],
         "synthetic_middle_and_later_source_positive":"PASS"}
for endian in ("big","little"):
    for reverse in (False,True):
        state=tuple(parse(known[0],endian,reverse))
        later=parse(known[1],endian,reverse)
        stream=[]
        for _ in range(4+512+4):
            out,state=next_word(state);stream.append(out)
        for gap in range(257):
            physical=emit(stream[gap:gap+4],endian,reverse)
            component=bytes(a^b for a,b in zip(physical,mask))
            results["original_complete_K04_candidate_checks"]+=1
            if hashlib.sha256(component).hexdigest()==target:
                results["original_K04_matches"].append([endian,reverse,gap,component.hex().upper()])
        for gap in range(513):
            results["source_attempt3_checks"]+=1
            if stream[4+gap:8+gap]==later:
                results["source_attempt3_matches"].append([endian,reverse,gap])
print(json.dumps(results,indent=2))
