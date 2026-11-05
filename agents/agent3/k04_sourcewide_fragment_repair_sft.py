"""Original-source contiguous-block K04 copied-coupon repair, lengths 5..15.

Reproduce in workplace-v2: python agents/agent3/k04_sourcewide_fragment_repair_sft.py
No resource, verifier, acceptance or canonical-candidate mutation.
"""
import hashlib
import re
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
PAYLOAD=bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
MASK=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET=bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")

def streams():
    root=ROOT/"resources"/"evidence"
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        raw=path.read_bytes()
        yield "raw:"+str(path.relative_to(ROOT/"resources")).replace("\\","/"),raw
        for match in re.finditer(rb"(?<![0-9a-fA-F])[0-9a-fA-F]{16,}(?![0-9a-fA-F])",raw):
            if len(match.group())%2==0:
                yield "hex:"+str(path.relative_to(root))+":"+str(match.start()),bytes.fromhex(match.group().decode("ascii"))

def main():
    import json
    t0=time.monotonic()
    spool=(ROOT/"resources"/"evidence"/"print"/"spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest()==SOURCE_SHA
    assert b"2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD="+PAYLOAD.hex().upper().encode() in spool
    route=json.loads((ROOT/"resources"/"evidence"/"recovery-routing.json").read_text())
    accept=json.loads((ROOT/"resources"/"acceptance.json").read_text())
    assert route["K04"]["masked_component"]==MASK.hex().upper()
    assert accept["slot_sha256"]["K04"]==TARGET.hex()
    sources=list(streams())
    print("SOURCE_STREAMS",len(sources),"SOURCE_BYTES",sum(len(b) for _,b in sources),flush=True)
    assert len(sources)==189 and sum(len(b) for _,b in sources)==114964
    crew=next(b for name,b in sources if name=="raw:evidence/crew/noticeboard-and-desk-notes.txt")
    synthetic_coupon=PAYLOAD[:3]+crew[9:17]+PAYLOAD[11:]
    synthetic_target=hashlib.sha256(bytes(a^b for a,b in zip(synthetic_coupon,MASK))).digest()
    reconstructed=PAYLOAD[:3]+crew[9:17]+PAYLOAD[11:]
    assert hashlib.sha256(bytes(a^b for a,b in zip(reconstructed,MASK))).digest()==synthetic_target
    print("PLANTED_COMPLETE_POSITIVE PASS",flush=True)
    total=0
    expected=[1370496,1254209,1138300,1022769,907616,792841,678444,564425,450784,337521,224636]
    for length,expected_num in zip(range(5,16),expected):
        checks=0
        for source,raw in sources:
            if len(raw)<length:
                continue
            for pos in range(17-length):
                head=bytes(a^b for a,b in zip(PAYLOAD[:pos],MASK[:pos]))
                tail=bytes(a^b for a,b in zip(PAYLOAD[pos+length:],MASK[pos+length:]))
                keymask=MASK[pos:pos+length]
                for offset in range(len(raw)-length+1):
                    fragment=raw[offset:offset+length]
                    comp=head+bytes(a^b for a,b in zip(fragment,keymask))+tail
                    checks+=1
                    if hashlib.sha256(comp).digest()==TARGET:
                        raise AssertionError(f"ORIGINAL_K04_MATCH source={source} offset={offset} length={length} pos={pos} component={comp.hex().upper()}")
        assert checks==expected_num,(length,checks)
        total+=checks
        print("L",length,"CHECKS",checks,"CUMULATIVE",total,flush=True)
    assert total==8742041
    print("ORIGINAL_K04_NO_MATCH 8742041 CHECKS",round(time.monotonic()-t0,2),"seconds")

if __name__=="__main__":
    main()
