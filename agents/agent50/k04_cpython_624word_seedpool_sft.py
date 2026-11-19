#!/usr/bin/env python3
"""Source-pinned CPython MT19937 init_by_array seed-pool screen for H-17 K04.

Run: python agents/agent50/k04_cpython_624word_seedpool_sft.py resources
The argument must contain evidence/ and acceptance.json. No source or candidate is modified.
"""
import hashlib
import itertools
import json
import random
import re
import struct
import sys
import time
from pathlib import Path

MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET_ROW = 129
TARGET_WORD = TARGET_ROW * 4
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REC_HASH = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
SELECTED = "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench"
K01 = bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A")
K02_PRE = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
K02 = bytes.fromhex("0D7E3AB56FB75DA3EB0E2E06786D239E")
K03 = bytes.fromhex("1384AF96E25D6ADA666209CB55E062FA")
K05 = bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572")
K06 = bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A")
K07_PRE = bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9")
K07 = bytes.fromhex("93495F5E425AB8E592123DABAEB68545")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def words4(block, endian, reverse=False):
    chunks = [block[i:i+4] for i in range(0, len(block), 4)]
    if reverse:
        chunks.reverse()
    return [int.from_bytes(x, endian) for x in chunks]


def temper(y):
    y &= 0xffffffff
    y ^= y >> 11
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 15) & 0xefc60000
    y ^= y >> 18
    return y & 0xffffffff


def untemper(y):
    def right(v, n):
        x = v
        for _ in range(5):
            x = v ^ (x >> n)
        return x & 0xffffffff
    def left(v, n, m):
        x = v
        for _ in range(5):
            x = v ^ ((x << n) & m)
        return x & 0xffffffff
    y = right(y, 18)
    y = left(y, 15, 0xefc60000)
    y = left(y, 7, 0x9d2c5680)
    return right(y, 11)


def seed_int(words):
    assert len(words) == 624
    b = b"".join(w.to_bytes(4, "little") for w in words)
    n = int.from_bytes(b, "little")
    assert (n.bit_length() + 31) // 32 == 624
    return n


def serializers(out4):
    for raw in (False, True):
        ws = [untemper(w) for w in out4] if raw else out4
        for endian in ("little", "big"):
            for reverse in (False, True):
                seq = ws[::-1] if reverse else ws
                yield b"".join(w.to_bytes(4, endian) for w in seq)


def load_groups(root):
    e = root / "evidence"
    sp = (e / "print/spool-reconstruction.log").read_bytes()
    assert sha(sp) == SPOOL_HASH
    rows = [x for x in sp.decode().splitlines() if "PAYLOAD=" in x]
    assert len(rows) == 133 and rows[TARGET_ROW] == SELECTED
    packets = [bytes.fromhex(re.search(r"PAYLOAD=([0-9A-Fa-f]{32})", x).group(1))
               for i, x in enumerate(rows) if i != TARGET_ROW]
    assert len(packets) == 132

    rec = (e / "recorder/trip-recorder.raw").read_bytes()
    assert sha(rec) == REC_HASH and rec[:8] == b"TRP2DUMP"
    version, size, count = struct.unpack_from("<HHI", rec, 8)
    assert (version, size, count, len(rec)) == (2, 24, 88, 16 + 24*88)
    records = []
    for i in range(count):
        b = rec[16+24*i:16+24*(i+1)]
        ts, node, event, latch, seq = struct.unpack_from("<I H B B I", b)
        records.append((i, ts, node, event, latch, seq, b[12:16]))
    orders = {
        "physical": sorted(records, key=lambda r:r[0]),
        "reverse": sorted(records, key=lambda r:r[0], reverse=True),
        "timestamp": sorted(records, key=lambda r:(r[1],r[0])),
        "node-event-latch-seq": sorted(records, key=lambda r:(r[2],r[3],r[4],r[5],r[0])),
    }

    P, R = {}, {}
    for endian in ("little", "big"):
        for rr in (False, True):
            for rw in (False, True):
                ps = packets[::-1] if rr else packets
                P[(endian, rr, rw)] = [
                    int.from_bytes(c, endian)
                    for p in ps
                    for c in (([p[i:i+4] for i in range(0,16,4)][::-1])
                              if rw else [p[i:i+4] for i in range(0,16,4)])
                ]
        for name, rs in orders.items():
            R[(name, endian)] = [int.from_bytes(r[6], endian) for r in rs]

    def four_views(label, block):
        return {(label, endian, rev): words4(block, endian, rev)
                for endian in ("little", "big") for rev in (False, True)}

    return {
        "P": {("P",)+k:v for k,v in P.items()},
        "R": {("R",)+k:v for k,v in R.items()},
        "K02": four_views("K02", K02_PRE),
        "K07": four_views("K07", K07_PRE),
        "K01": four_views("K01", K01),
        "K06": four_views("K06", K06),
    }


def run_pool(name, names, groups, target_hash):
    views = {g:list(groups[g].items()) for g in names}
    hits, layouts, checks, start = [], 0, 0, time.perf_counter()
    for order in itertools.permutations(names):
        for pk, pv in views["P"]:
            for rk, rv in views["R"]:
                for ak, av in views[names[2]]:
                    for bk, bv in views[names[3]]:
                        source = {"P":pv, "R":rv, names[2]:av, names[3]:bv}
                        seed = seed_int([w for g in order for w in source[g]])
                        rng = random.Random(seed)
                        out = [rng.getrandbits(32) for _ in range(TARGET_WORD+4)]
                        out4 = out[TARGET_WORD:TARGET_WORD+4]
                        for coupon in serializers(out4):
                            checks += 1
                            component = bytes(a ^ b for a,b in zip(coupon, MASK))
                            if sha(component) == target_hash:
                                hits.append((order,pk,rk,ak,bk,coupon.hex(),component.hex()))
                        layouts += 1
    return {"pool":name,"layouts":layouts,"candidate_checks":checks,
            "hits":hits,"seconds":round(time.perf_counter()-start,3)}


def synthetic_control():
    seed_words = [((i*0x9e3779b9)^0xa5a5a5a5)&0xffffffff for i in range(624)]
    rng = random.Random(seed_int(seed_words))
    out = [rng.getrandbits(32) for _ in range(TARGET_WORD+4)][TARGET_WORD:]
    planted = b"".join(w.to_bytes(4,"little") for w in out)
    component = bytes(a^b for a,b in zip(planted,MASK))
    digest = sha(component)
    assert planted in [c for c in serializers(out)
                       if sha(bytes(a^b for a,b in zip(c,MASK))) == digest]
    changed = bytearray(component); changed[0] ^= 1
    assert sha(component) != sha(changed)
    return "PASS"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: k04_cpython_624word_seedpool_sft.py <archive-root-or-resources>")
    root = Path(sys.argv[1])
    acceptance = json.loads((root/"acceptance.json").read_text())
    target = acceptance["slot_sha256"]["K04"]
    assert target == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
    for value, slot in ((K01,"K01"),(K03,"K03"),(K05,"K05"),(K06,"K06")):
        assert sha(value) == acceptance["slot_sha256"][slot]
    for pre, component, slot in ((K02_PRE,K02,"K02"),(K07_PRE,K07,"K07")):
        assert hashlib.sha256(pre).digest()[:16] == component
        assert sha(component) == acceptance["slot_sha256"][slot]
    assert all(temper(untemper(x)) == x
               for x in (0,1,0x12345678,0xffffffff,0xa9a9dc57))
    assert synthetic_control() == "PASS"

    groups = load_groups(root)
    results = [
        run_pool("P+R+K02+K07", ("P","R","K02","K07"), groups, target),
        run_pool("P+R+K01+K06", ("P","R","K01","K06"), groups, target),
    ]
    assert [x["layouts"] for x in results] == [24576,24576]
    assert [x["candidate_checks"] for x in results] == [196608,196608]
    assert not any(x["hits"] for x in results)
    print(json.dumps({"synthetic_control":"PASS","selected_row":TARGET_ROW,
                      "output_word_offset":TARGET_WORD,"pools":results,
                      "total_layouts":sum(x["layouts"] for x in results),
                      "total_candidate_checks":sum(x["candidate_checks"] for x in results),
                      "original_K04_hits":0}, indent=2))


if __name__ == "__main__":
    main()
