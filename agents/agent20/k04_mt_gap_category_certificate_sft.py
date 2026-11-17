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
        ((10,0),(10,1),(64,0),(94,3)),
        ((11,0),(11,1),(65,0),(95,2)),
        ((41,0),(41,1),(94,3),(125,1)),
        ((42,0),(42,1),(95,1),(126,2)),
        ((42,1),(42,2),(95,2),(126,3)),
    )
    def word(loc):
        return rows[loc[0]][1][loc[1]]
    for a,b,c,d in relations:
        recur(word(a),word(b),word(c),word(d))

    # Witnesses imply exact hypothetical native row-start differences:
    # s94-s10=621; s95-s11=622
    # s94-s41=394; s95-s42=396
    # s125-s41=623; s126-s42=622
    # With s[r+1]-s[r]=4+g[r], pairwise subtraction yields
    # g10-g94=-1, g41-g94=-2 and g41-g125=1;
    # hence g10-g41=1 and g41-g125=1.
    assert rows[10][0] == rows[41][0] == rows[125][0] == ("STORES","store")
    assert 621-4*(94-10) == 285
    assert 622-4*(95-11) == 286
    assert 394-4*(94-41) == 182
    assert 396-4*(95-42) == 184
    assert 623-4*(125-41) == 287
    assert 622-4*(126-42) == 286
    assert 285-286 == -1
    assert 182-184 == -2
    assert 287-286 == 1
    assert (285-286)-(182-184) == 1

    rng=Random(20261117)
    synth=[untemper(rng.getrandbits(32)) for _ in range(640)]
    for a,b,c,d in ((0,1,397,624),(7,8,404,631),(8,9,405,632)):
        recur(synth[a],synth[b],synth[c],synth[d])
    print("SOURCE_SHA_PASS original_fullword_relations=5 synthetic_positives=3")
    print("SOURCE_CONSTRAINT g10_minus_g41=1 g41_minus_g125=1")
    print("SOURCE_CONSTRAINT identical_metadata_rows=10,41,125 label=STORES/store")
    print("STATIONARY_CLASS_DEST_GAP_MODEL=AT_LEAST_TWO_EXCEPTIONS")
    print("K04_coupon_authenticated_bits=0")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("resources/evidence/print/spool-reconstruction.log"))
