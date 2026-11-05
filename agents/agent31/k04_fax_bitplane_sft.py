"""H17 K04 bitplane/within-byte scan-layout complete-candidate SFT.

Usage: python agents/agent31/k04_fax_bitplane_sft.py path/to/h17-archive-dump.zip [transpose|pixel|all]
Read-only original ZIP. No evidence, candidate or commitment modifications.
"""
import hashlib
import itertools
import json
import re
import sys
import time
import zipfile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ALL = (1 << 128) - 1

def read_original(path):
    with zipfile.ZipFile(path) as z:
        spool = z.read("evidence/print/spool-reconstruction.log")
        route = json.loads(z.read("evidence/recovery-routing.json"))
        acceptance = json.loads(z.read("acceptance.json"))
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    rows = [line for line in spool.decode("ascii").splitlines() if "PAYLOAD=" in line]
    assert len(rows) == 133
    line = rows[129]
    assert all(x in line for x in ("JOB=PS-261003-0417 ", "ATTEMPT=2 ",
                                   "STATE=ACK ", "CLASS=RECOVER "))
    copied = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1))
    assert copied.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
    return copied, int(route["K04"]["masked_component"],16), bytes.fromhex(
        acceptance["slot_sha256"]["K04"])

def column_maps():
    maps = [(a,b,tuple((a*i+b)%16 for i in range(16)))
            for a in range(1,16,2) for b in range(16)]
    assert len(maps) == len({m for _,_,m in maps}) == 128
    return maps

def modes(y, copied, mask):
    return (y^mask, y^mask^ALL, y^copied^mask, y^copied^mask^ALL)

def run(path, family="all"):
    copied, mask, target = read_original(path)
    orig = int.from_bytes(copied,"big")
    maps = column_maps()
    plant_perm = (2,7,0,4,1,6,5,3)
    matches = []
    outcomes = {}
    started = time.monotonic()
    for kind in ("transpose","pixel"):
        if family not in ("all",kind):
            continue
        counts = [0,0,0,0]
        positives = 0
        if kind == "transpose":
            for a,b,order in maps:
                arranged = bytes(copied[i] for i in order)
                planes = [sum(((arranged[i]>>(7-k))&1)<<(15-i)
                              for i in range(16)).to_bytes(2,"big") for k in range(8)]
                for perm in itertools.permutations(range(8)):
                    y = int.from_bytes(b"".join(planes[k] for k in perm),"big")
                    planted = (hashlib.sha256(modes(y,orig,mask)[3].to_bytes(16,"big")).digest()
                               if (a,b)==(3,5) and perm==plant_perm else None)
                    for mode,comp in enumerate(modes(y,orig,mask)):
                        digest = hashlib.sha256(comp.to_bytes(16,"big")).digest()
                        counts[mode] += 1
                        if digest == target:
                            matches.append((kind,a,b,perm,mode,comp.to_bytes(16,"big").hex().upper()))
                        if planted is not None and digest == planted:
                            positives += 1
        else:
            unique = sorted(set(copied))
            for perm in itertools.permutations(range(8)):
                table = {v:sum(((v>>(7-perm[k]))&1)<<(7-k) for k in range(8))
                         for v in unique}
                renamed = bytes(table[v] for v in copied)
                for a,b,order in maps:
                    y = int.from_bytes(bytes(renamed[i] for i in order),"big")
                    planted = (hashlib.sha256(modes(y,orig,mask)[3].to_bytes(16,"big")).digest()
                               if (a,b)==(3,5) and perm==plant_perm else None)
                    for mode,comp in enumerate(modes(y,orig,mask)):
                        digest = hashlib.sha256(comp.to_bytes(16,"big")).digest()
                        counts[mode] += 1
                        if digest == target:
                            matches.append((kind,a,b,perm,mode,comp.to_bytes(16,"big").hex().upper()))
                        if planted is not None and digest == planted:
                            positives += 1
        assert counts == [5160960]*4
        assert positives == 1
        outcomes[kind] = counts
        print("FAMILY",kind,"candidate_checks",sum(counts),
              "positive_plant_hits",positives,"real_K04_hits",
              sum(m[0]==kind for m in matches),"seconds",
              round(time.monotonic()-started,2),flush=True)
    print("FINAL",json.dumps({"source_sha":SPOOL_SHA,"models":outcomes,
                              "matches":matches,
                              "elapsed_seconds":round(time.monotonic()-started,3)}))
if __name__=="__main__":
    assert len(sys.argv) in (2,3)
    run(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else "all")
