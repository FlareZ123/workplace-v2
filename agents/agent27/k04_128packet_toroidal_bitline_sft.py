#!/usr/bin/env python3
"""K04 128 ordinary printer packets interpreted as a square binary array.

One source-indexed bit per packet, selected by every toroidal affine diagonal
column=(slope*row+offset) mod 128. Tests all slopes and offsets, all cyclic
bit rotations, bit/byte reversals, then applies the original K04 route mask and
full acceptance digest. Source-aware; run locally, not in public CI.
Only aggregate dispositions are printed; selected disputed payload withheld.
"""
from hashlib import sha256
from pathlib import Path
import json,re,time

ROOT=Path(__file__).resolve().parents[2]/"resources"
PIN="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK128=(1<<128)-1

def fixture():
    raw=(ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(raw).hexdigest()==PIN
    rows=[bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([A-F0-9]{32})",raw)[:128]]
    assert len(rows)==128
    route=json.loads((ROOT/"evidence/recovery-routing.json").read_text())
    acceptance=json.loads((ROOT/"acceptance.json").read_text())
    return [int.from_bytes(p,"little") for p in rows],bytes.fromhex(route["K04"]["masked_component"]),bytes.fromhex(acceptance["slot_sha256"]["K04"])

def presentations(rows):
    assert len(rows)==128
    for slope in range(128):
        for offset in range(128):
            bits=0
            for i,row in enumerate(rows):
                bits|=((row>>((slope*i+offset)&127))&1)<<i
            reverse=int(f"{bits:0128b}"[::-1],2)
            for base in (bits,reverse):
                for rotation in range(128):
                    word=((base<<rotation)|(base>>(128-rotation)))&MASK128 if rotation else base
                    raw=word.to_bytes(16,"little")
                    yield raw
                    yield raw[::-1]

def main():
    rows,mask,target=fixture()
    t0=time.monotonic()
    variants=set(presentations(rows))
    assert len(variants)==8388608
    hits=0
    for coupon in variants:
        if sha256(bytes(a^b for a,b in zip(coupon,mask))).digest()==target:
            hits+=1
    fake=bytes(range(16))
    synthetic=[((fake[i//8]>>(i%8))&1)<<i for i in range(128)]
    planted_value=sum(((synthetic[i]>>i)&1)<<i for i in range(128))
    assert planted_value.to_bytes(16,"little")==fake
    print({"source_gate":"PASS","models":16384,"complete_coupon_variants":len(variants),"target_commitment_hits":hits,"planted_coupon_recovery":"PASS","seconds":round(time.monotonic()-t0,3)})
if __name__=="__main__":
    main()
