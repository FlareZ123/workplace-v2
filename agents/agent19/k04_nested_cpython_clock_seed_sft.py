"""K04 source-only: nested Python binary seed from small/incident-clock scalar.

Conditional model: original printer source was p951 CPython Random(B),
and B was produced by Random(scalar).randbytes(length), length 4*n-64
for n609..623. First complete parent words from original source are
at relative positions 0,1,12,579,580. No K04 acceptance hash consulted.

Run: python agents/agent19/k04_nested_cpython_clock_seed_sft.py
"""
from __future__ import annotations

import hashlib
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents/agent15"))
from k04_p951_sparse_seed_donor_sft import recover_original_map

SOURCE_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET={
  0:{0x64589c88,0xe4589c88},
  1:{0x49342ec0},
  12:{0x6425cf5b,0xe425cf5b},
  579:{0x06edcdad},
  580:{0xfd6a4cf7}
}
QS=range(6,21)

def swapped(value):
    return int.from_bytes(value.to_bytes(4,"little"),"big")

def check_seed(seed,known):
    gen=random.Random(seed)
    prefix=[gen.getrandbits(32) for _ in range(22)]
    first=second=0
    successes=[]
    for endian in ("little","big"):
        vals=prefix if endian=="little" else [swapped(v) for v in prefix]
        for q in QS:
            if vals[q] not in known[0]:continue
            first+=1
            if vals[q+1] not in known[1]:continue
            second+=1
            # Original source requires five widely separated outputs.
            further=prefix+[gen.getrandbits(32) for _ in range(22,q+581)]
            v=further if endian=="little" else [swapped(x) for x in further]
            if all(v[q+i] in allowed for i,allowed in known.items()):
                successes.append((seed,q,endian))
    return first,second,successes

def controls():
    passed=0
    for seed in (0,1,0x1234,0xdeadbeef,1791050520000):
        for q in (6,11,20):
            gen=random.Random(seed)
            original=[gen.getrandbits(32) for _ in range(q+581)]
            for endian in ("little","big"):
                vals=original if endian=="little" else [swapped(v) for v in original]
                known={j:{vals[q+j]} for j in TARGET}
                assert (seed,q,endian) in check_seed(seed,known)[2]
                assert not check_seed(seed+1,known)[2]
                passed+=1
    assert passed==30
    print("PLANTED 30 full-history positives, 30 changed-seed negatives PASS")

def main():
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    original=recover_original_map()
    assert original[602]==[bytes.fromhex("64589C88"),bytes.fromhex("E4589C88")]
    assert original[601]==[bytes.fromhex("49342EC0")]
    assert original[590]==[bytes.fromhex("6425CF5B"),bytes.fromhex("E425CF5B")]
    assert original[23]==[bytes.fromhex("06EDCDAD")]
    assert original[22]==[bytes.fromhex("FD6A4CF7")]
    controls()
    epoch=int(datetime(2026,10,3,tzinfo=timezone.utc).timestamp())
    ack_ms=int(datetime(2026,10,3,18,2,tzinfo=timezone.utc).timestamp()*1000)
    classes=(
      ("all_16bit",range(65536)),
      ("incident_UTC_seconds",range(epoch,epoch+86400)),
      ("ACK2_UTC_milliseconds",range(ack_ms-180000,ack_ms+180001)),
    )
    total=0
    for label,seeds in classes:
        first=second=0
        survivors=[]
        for seed in seeds:
            a,b,c=check_seed(seed,TARGET)
            first+=a;second+=b;survivors+=c
        count=len(seeds)
        total+=count
        print(label,"seeds",count,"first_word_hits",first,
              "first_two_word_hits",second,"five_word_hits",len(survivors))
        assert not survivors and not first and not second
    assert total==511937
    print("ORIGINAL",total,"inner seed values,",
          30*total,"offset/view first-word predictions, zero hits")

if __name__=="__main__":main()
