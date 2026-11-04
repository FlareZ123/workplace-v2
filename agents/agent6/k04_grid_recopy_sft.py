"""Original H-17 K04 4x4 byte-grid copier hypothesis: read-only SFT."""
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import json
import re
import time

root = Path(__file__).resolve().parents[2] / "resources"
evidence = root / "evidence"
pins = {
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}
source = {}
for name, expected in pins.items():
    raw = (evidence / name).read_bytes()
    assert sha256(raw).hexdigest() == expected
    source[name] = raw
a = (root / "acceptance.json").read_bytes()
assert sha256(a).hexdigest() == "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
route = json.loads(source["recovery-routing.json"])
target = bytes.fromhex(json.loads(a)["slot_sha256"]["K04"])
found = []
for line in source["print/spool-reconstruction.log"].decode().splitlines():
    m = dict(re.findall(r"(JOB|ATTEMPT|STATE|CLASS|PAYLOAD|DEST)=([^ ]+)", line))
    if (m.get("JOB"), m.get("ATTEMPT"), m.get("STATE"), m.get("CLASS"), m.get("DEST")) == (
        "PS-261003-0417", "2", "ACK", "RECOVER", "bench"
    ):
        found.append(m["PAYLOAD"])
assert found == ["A9A9DC5731A5E2AE879C47215C2559D5"]
payload = bytes.fromhex(found[0])
mask = bytes.fromhex(route["K04"]["masked_component"])
def bxor(a,b):
    return bytes(x^y for x,y in zip(a,b))
unmasked = bxor(payload,mask)
assert sha256(unmasked).digest() != target
perms = list(permutations(range(4)))

def mapped(rows,cols,rf,cf,transpose):
    g = [[4*r+c for c in range(4)] for r in range(4)]
    if transpose:
        g = [list(v) for v in zip(*g)]
    g = [[g[rows[r]][cols[c]] for c in range(4)] for r in range(4)]
    for r in range(4):
        if rf>>r&1: g[r].reverse()
    for c in range(4):
        if cf>>c&1:
            for r in (0,1): g[r][c],g[3-r][c] = g[3-r][c],g[r][c]
    return tuple(i for row in g for i in row)

tables = {}
for nib, rev in product((False,True),repeat=2):
    nums = []
    for x in range(256):
        if nib: x = ((x&15)<<4)|(x>>4)
        if rev: x = int(f"{x:08b}"[::-1],2)
        nums.append(x)
    tables[nib,rev] = bytes.maketrans(bytes(range(256)),bytes(nums))
assert mapped((0,1,2,3),(0,1,2,3),0,0,False)==tuple(range(16))
positive_map = mapped(perms[7],perms[19],5,9,True)
positive = sha256(bxor(bytes(payload[i] for i in positive_map),mask)).digest()
assert positive != target
checks = positives = 0
hits = []
start = time.perf_counter()
for rp in perms:
    for cp in perms:
        for tr in (False,True):
            for rf in range(16):
                for cf in range(16):
                    idx = mapped(rp,cp,rf,cf,tr)
                    pp = bytes(payload[i] for i in idx)
                    mm = bytes(mask[i] for i in idx)
                    uu = bytes(unmasked[i] for i in idx)
                    for orient,tbl in tables.items():
                        candidates = (
                            bxor(pp.translate(tbl),mask),
                            bxor(payload,mm.translate(tbl)),
                            uu.translate(tbl)
                        )
                        for stage, candidate in enumerate(candidates):
                            d = sha256(candidate).digest()
                            checks += 1
                            if d == target:
                                hits.append((stage,orient,candidate.hex().upper()))
                            if stage==0 and orient==(False,False) and d==positive:
                                positives += 1
assert checks == 3538944
assert positives > 0
print(json.dumps({"checks":checks,"original_matches":hits,
                  "synthetic_positive_assignments":positives,
                  "elapsed_seconds":round(time.perf_counter()-start,3)},indent=2))
