"""Agent49 single-nibble slip and same-job nibble-boundary splice K04 SFT."""
import hashlib
import json
import re
import sys
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
HEX = "0123456789ABCDEF"

def digest(s: str, mask: bytes) -> bytes:
    return hashlib.sha256(bytes(x ^ y for x,y in zip(bytes.fromhex(s),mask))).digest()

def slips(s: str):
    for delete in range(32):
        remainder = s[:delete] + s[delete+1:]
        for insert in range(32):
            for digit in HEX:
                yield (delete,insert,digit), remainder[:insert] + digit + remainder[insert:]

def main(root: Path):
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    rt = json.loads((root / "evidence/recovery-routing.json").read_text())
    acc = json.loads((root / "acceptance.json").read_text())
    mask = bytes.fromhex(rt["K04"]["masked_component"])
    target = bytes.fromhex(acc["slot_sha256"]["K04"])
    rows = []
    for line in raw.decode().splitlines():
        if "JOB=PS-261003-0417" in line and "PAYLOAD=" in line:
            rows.append(dict(re.findall(r"([A-Z]+)=([^\s]+)",line)))
    assert len(rows)==4
    selected = [r for r in rows if r["CLASS"]=="RECOVER" and r["ATTEMPT"]=="2" and r["STATE"]=="ACK"]
    assert len(selected)==1
    s=selected[0]["PAYLOAD"]
    assert s=="A9A9DC5731A5E2AE879C47215C2559D5"
    planted = s[1:21] + "F" + s[21:]
    positive = digest(planted,mask)
    assert positive != target
    count=0
    seen=set()
    positives=0
    hits=[]
    for operation,c in slips(s):
        count+=1
        seen.add(c)
        if digest(c,mask)==positive:
            assert c==planted
            positives+=1
        if digest(c,mask)==target:
            hits.append(("slip",operation,c))
    assert count==16384 and positives>0

    others = [r["PAYLOAD"] for r in rows if r is not selected[0]]
    splice_count=0
    for j,t in enumerate(others):
        for cut in range(1,32):
            for arrangement,c in (("selected/other",s[:cut]+t[cut:]),("other/selected",t[:cut]+s[cut:])):
                splice_count+=1
                if digest(c,mask)==target:
                    hits.append(("splice",(j,cut,arrangement),c))
    assert splice_count==186
    print(json.dumps({
        "source_sha256":SPOOL_SHA,
        "single_nibble_assignments":count,
        "distinct_single_nibble_candidates":len(seen),
        "synthetic_positive_matches":positives,
        "attempt_splice_assignments":splice_count,
        "original_hits":hits,
    }))

if __name__ == "__main__":
    assert len(sys.argv)==2
    main(Path(sys.argv[1]))
