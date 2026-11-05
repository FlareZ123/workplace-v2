"""H17 K04 source-pinned inverse plane serialization and XOR-order SFT.

Usage: python agents/agent31/k04_fax_inverse_stage_sft.py path/to/h17.zip [pre|post]
Reads original ZIP and leaves all acceptance evidence unchanged.
"""
import hashlib
import itertools
import json
import re
import sys
import time
import zipfile

SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FULL=(1<<128)-1
def run(path,stages=("pre","post")):
    with zipfile.ZipFile(path) as z:
        raw=z.read("evidence/print/spool-reconstruction.log")
        route=json.loads(z.read("evidence/recovery-routing.json"))
        acceptance=json.loads(z.read("acceptance.json"))
    assert hashlib.sha256(raw).hexdigest()==SPOOL_SHA
    rows=[x for x in raw.decode().splitlines() if "PAYLOAD=" in x]
    assert len(rows)==133 and "ATTEMPT=2 STATE=ACK CLASS=RECOVER" in rows[129]
    copied=bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",rows[129]).group(1))
    mask=int(route["K04"]["masked_component"],16)
    target=bytes.fromhex(acceptance["slot_sha256"]["K04"])
    assert copied.hex().upper()=="A9A9DC5731A5E2AE879C47215C2559D5"
    maps=[(a,b,tuple((a*i+b)%16 for i in range(16)))
          for a in range(1,16,2) for b in range(16)]
    assert len(maps)==128
    orig=int.from_bytes(copied,"big")
    start=time.monotonic()
    def decode(pairs,perm):
        words=[int.from_bytes(pairs[2*i:2*i+2],"big") for i in perm]
        return bytes(sum(((words[k]>>(15-j))&1)<<(7-k) for k in range(8))
                     for j in range(16))
    for stage in stages:
        input_data=copied if stage=="post" else (orig^mask).to_bytes(16,"big")
        reference=orig if stage=="post" else orig^mask
        counts=[0]*4
        hits=[]
        planted=0
        for perm in itertools.permutations(range(8)):
            decoded=decode(input_data,perm)
            for a,b,order in maps:
                y=int.from_bytes(bytes(decoded[i] for i in order),"big")
                values=(y,y^FULL,y^reference,y^reference^FULL)
                digest_planted=(hashlib.sha256((values[3]^(mask if stage=="post" else 0)).to_bytes(16,"big")).digest()
                                if perm==(2,7,0,4,1,6,5,3) and (a,b)==(3,5) else None)
                for mode,val in enumerate(values):
                    component=val^(mask if stage=="post" else 0)
                    digest=hashlib.sha256(component.to_bytes(16,"big")).digest()
                    counts[mode]+=1
                    if digest==target:
                        hits.append((stage,a,b,perm,mode,component.to_bytes(16,"big").hex().upper()))
                    if digest_planted is not None and digest==digest_planted:
                        planted+=1
        assert counts==[5160960]*4 and planted==1
        print("STAGE",stage,"hash_checks",sum(counts),"planted",planted,
              "real_hits",hits,"elapsed",round(time.monotonic()-start,2),flush=True)

if __name__=="__main__":
    assert len(sys.argv) in (2,3)
    run(sys.argv[1],(sys.argv[2],) if len(sys.argv)==3 else ("pre","post"))
