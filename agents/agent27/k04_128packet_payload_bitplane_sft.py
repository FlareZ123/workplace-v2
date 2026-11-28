#!/usr/bin/env python3
"""K04: source-selected 128 ordinary printer packets as a 128-bit bit-plane.

Exploratory complete-coupon constructor, not an authenticated coupon producer.
Unlike pre-existing CLASS/DEST-only metadata maps, this uses actual payload
bit planes. Run locally only; never use original-bearing public CI.
Outputs aggregate counts, never original candidate bytes or target digests.
"""
import hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK128 = (1 << 128) - 1

def rotate(n, shift):
    return ((n << shift) | (n >> (128-shift))) & MASK128 if shift else n

def bit_reverse(n):
    return int(f"{n:0128b}"[::-1], 2)

def construct(bits):
    """All rotated, bit/byte-reversed 16-byte views of one 128-bit vector."""
    assert len(bits) == 128
    n = sum((int(bit)&1) << i for i, bit in enumerate(bits))
    out=set()
    for base in (n, bit_reverse(n)):
        for shift in range(128):
            b = rotate(base,shift).to_bytes(16,"little")
            out.update((b,b[::-1]))
    return out

def models(packets):
    assert len(packets)==128 and all(len(p)==16 for p in packets)
    yield "fixed-bit", ([
        (int.from_bytes(p,"little") >> bit)&1 for p in packets
    ] for bit in range(128))
    yield "packet-parity", ([p.bit_count()&1 for p in packets],)
    yield "indexed-byte", ([
        (p[(a*i+c)%16] >> bit)&1 for i,p in enumerate(packets)
    ] for a in (1,3,7) for c in range(16) for bit in (0,7))

def fixture():
    raw=(ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    pattern=re.compile(rb"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)")
    rows=[(int(m[1]),int(m[2]),m[3],bytes.fromhex(m[5].decode())) for m in pattern.finditer(raw)]
    assert len(rows)==133
    ordinary=rows[:128]
    assert [(r[0],r[1],r[2]) for r in ordinary]==[(300+i,1,b"ACK") for i in range(128)]
    route=json.loads((ROOT/"evidence/recovery-routing.json").read_text())
    acceptance=json.loads((ROOT/"acceptance.json").read_text())
    return [r[3] for r in ordinary],bytes.fromhex(route["K04"]["masked_component"]),bytes.fromhex(acceptance["slot_sha256"]["K04"])

def control():
    packets=[bytearray(16) for _ in range(128)]
    planted=bytes(range(16))
    for i in range(128):
        packets[i][0]=(planted[i//8]>>(i%8))&1
    recovered=bytes(sum((packets[i+j][0]&1)<<j for j in range(8)) for i in range(0,128,8))
    assert recovered==planted and planted in construct([p[0]&1 for p in packets])

def main():
    control()
    packets,mask,target=fixture()
    seen=set(); totals={}
    for family,vectors in models(packets):
        count=0
        for bits in vectors:
            count+=1
            seen.update(construct(bits))
        totals[family]=count
    hits=sum(hashlib.sha256(bytes(x^y for x,y in zip(p,mask))).digest()==target for p in seen)
    print({"pinned":True,"rows":len(packets),"model_vectors":totals,
           "distinct_complete_coupon_checks":len(seen),"original_hits":hits,
           "synthetic_full_coupon_positive":True})

if __name__=="__main__":main()
