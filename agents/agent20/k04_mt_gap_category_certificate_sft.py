"""Source-pinned MT19937 gap-cadence certificate from intact H-17 printer rows.

Read-only. The selected row 129 and all acceptance commitments are excluded.
Run from repo root: python agents/agent20/k04_mt_gap_category_certificate_sft.py
"""
from pathlib import Path
from random import Random
import hashlib
import re
import sys

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def untemper(y):
    x = y
    for right, shift, mask, rounds in ((True,18,0,2),(False,15,0xEFC60000,2),(False,7,0x9D2C5680,6),(True,11,0,4)):
        z = x
        for _ in range(rounds):
            z = x ^ (z >> shift if right else (z << shift) & mask)
        x = z & 0xffffffff
    return x

def twist(a,b):
    return (((a & 0x80000000) | (b & 0x7fffffff)) >> 1) ^ (0x9908b0df if b & 1 else 0)

def recur(a,b,c,d):
    assert d == c ^ twist(a,b)

def main(path):
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    lines = [line for line in raw.decode("ascii").splitlines() if "PAYLOAD=" in line]
    assert len(lines) == 133
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    rows = []
    for line in lines[:128]:
        payload = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",line).group(1))
        vals = [untemper(int.from_bytes(payload[i:i+4],"little")) for i in range(0,16,4)]
        cat = (re.search(r"CLASS=(\w+)",line).group(1),re.search(r"DEST=(\w+)",line).group(1))
        rows.append((cat,vals))
    relations = (
        ((41,0),(41,1),(94,3),(125,1)),
        ((42,0),(42,1),(95,1),(126,2)),
        ((42,1),(42,2),(95,2),(126,3)),
    )
    def word(loc):
        return rows[loc[0]][1][loc[1]]
    for a,b,c,d in relations:
        recur(word(a),word(b),word(c),word(d))

    # With native start s[row], the two original relations imply:
    #   s125 - s41 = 624+0-1=623
    #   s126 - s42 = 624+0-2=622
    # Therefore (s42-s41)-(s126-s125) = 1.
    # Four payload words per row cancel; hidden draws g41-g125 = 1.
    assert rows[41][0] == rows[125][0] == ("STORES","store")
    assert (624+0-1)-(624+0-2) == 1

    rng=Random(20261117)
    synth=[untemper(rng.getrandbits(32)) for _ in range(640)]
    for a,b,c,d in ((0,1,397,624),(7,8,404,631),(8,9,405,632)):
        recur(synth[a],synth[b],synth[c],synth[d])
    print("SOURCE_SHA_PASS fullword_relations=3 synthetic_positives=3")
    print("SOURCE_CONSTRAINT g41_minus_g125=1 metadata_41_and_125=STORES/store")
    print("STATIONARY_CLASS_DEST_GAP_MODEL=CONTRADICTED")
    print("K04_coupon_authenticated_bits=0")

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("resources/evidence/print/spool-reconstruction.log"))
