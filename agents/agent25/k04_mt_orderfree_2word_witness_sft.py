"""Source-pinned order-free 2-word MT19937 recurrence witness for H17 printer.
Withhold disputed selected ACK2 and original K04 target. Exact 139-source-block
scan of all 8 word-endian triples; no stage indices or selected hash used.
"""
import hashlib
import itertools
import os
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT",
    Path(__file__).resolve().parents[2] / "resources"))
raw = (ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = [bytes.fromhex(s.decode()) for s in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
assert len(rows)==133
blocks = {f"printer_{i}":p for i,p in enumerate(rows) if i != 129}
blocks.update({
"K01":bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
"K02raw":bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
"K05":bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
"K06":bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
"K07raw":bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9"),
"nonce":bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497"),
"mask":bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")})
assert len(blocks)==139

U = 0xFFFFFFFF
def ur(y,n):
    x=y
    for _ in range(6): x=y^(x>>n)
    return x&U
def ul(y,n,m):
    x=y
    for _ in range(6): x=y^((x<<n)&m)
    return x&U
def untemper(y):
    return ur(ul(ul(ur(y,18),15,0xEFC60000),7,0x9D2C5680),11)
def twist(x,y):
    v=(x&0x80000000)|(y&0x7FFFFFFF)
    return (v>>1)^(0x9908B0DF if v&1 else 0)
def parsed(end):
    return {name:[untemper(int.from_bytes(data[i:i+4],end))
                  for i in (0,4,8,12)]
            for name,data in blocks.items()}

# The exact same recurrence predicts two consecutive native outputs of a
# genuine independently seeded MT stream (synthetic, unrelated to H17).
rng=random.Random(5489)
g=[untemper(rng.getrandbits(32)) for _ in range(626)]
assert tuple(g[397+i]^twist(g[i],g[i+1]) for i in (0,1)) == tuple(g[624:626])
print("GENUINE_MT_TWO_WORD_POSITIVE PASS")

observed=[]
for ao,bo,co in itertools.product(("little","big"), repeat=3):
    A,B,C=parsed(ao),parsed(bo),parsed(co)
    lookup=defaultdict(list)
    for name,seq in C.items():
        for off in range(3):
            lookup[(seq[off],seq[off+1])].append((name,off))
    matches=set(); comparisons=0
    for aname,a in A.items():
        for ai in range(2):
            for bname,b in B.items():
                if bname==aname: continue
                for bi in range(3):
                    key=tuple(b[bi+j]^twist(a[ai+j],a[ai+j+1])
                              for j in (0,1))
                    comparisons+=1
                    for cname,ci in lookup.get(key,()):
                        if cname not in (aname,bname):
                            matches.add((aname,ai,bname,bi,cname,ci))
    assert comparisons==115092
    print(ao,bo,co,"full_two_word_trials",comparisons,
          "exact_directed_matches",len(matches))
    if (ao,bo,co)==("little","little","little"):
        witness=[(8,0,62,1,92,2),(11,0,65,0,95,2),
                 (12,0,66,1,96,2),(21,1,74,0,105,1),
                 (22,1,75,0,106,0),(32,0,84,2,115,0),
                 (42,0,95,1,126,2)]
        expected=set()
        for a,ai,b,bi,c,ci in witness:
            expected.add((f"printer_{a}",ai,
                          f"printer_{b}",bi,f"printer_{c}",ci))
            expected.add((f"printer_{a}",ai,
                          f"printer_{c}",ci,f"printer_{b}",bi))
        assert matches==expected,(matches^expected)
        observed=witness
    else:
        assert not matches
assert len(observed)==7
print("SEVEN_2WORD_RECURRENCE_WITNESSES_PASS",observed)
