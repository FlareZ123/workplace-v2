"""H17 K04 native MT19937 624-word preissued erasure hypothesis; original read-only.

A complete four-word coupon can be reconstructed if four preceding native
observations and 624 subsequent native observations genuinely share one
contiguous MT19937 stream. Applies a whole-coupon source holdout before target.
All source group sequencing and common-generator claims are hypothetical.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import re
from pathlib import Path

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT",
    Path(__file__).resolve().parents[2] / "resources"))
U32 = 0xFFFFFFFF
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
GROUPS = {
    "K01": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K02_PREHASH": bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
    "K06": bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
    "K07_PREHASH": bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9"),
    "MASK": MASK,
    "NONCE": bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497"),
}

def undo_right(y: int, n: int) -> int:
    x = y
    for _ in range(6):
        x = y ^ (x >> n)
    return x & U32

def undo_left(y: int, n: int, mask: int) -> int:
    x = y
    for _ in range(6):
        x = y ^ ((x << n) & mask)
    return x & U32

def untemper(y: int) -> int:
    y = undo_right(y, 18)
    y = undo_left(y, 15, 0xEFC60000)
    y = undo_left(y, 7, 0x9D2C5680)
    return undo_right(y, 11)

def temper(y: int) -> int:
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & U32

def inv_twist(q: int) -> int:
    bit = q >> 31
    return (((q ^ (0x9908B0DF if bit else 0)) << 1) | bit) & U32

def recover(prefix: list[int], subsequent: list[int]) -> list[int] | None:
    """Invert the eight recurrence constraints surrounding unknown x4..x7.

    Native x0..x3 are known, x4..x7 absent, x8..x631 known.
    The recurrence x[t+624] = x[t+397] XOR twist(x[t],x[t+1])
    determines every bit of x4..x7, or a known-source contradiction.
    """
    assert len(prefix) == 4 and len(subsequent) == 624
    x: list[int | None] = prefix + [None] * 4 + subsequent
    highs: dict[int, int] = {}
    lows: dict[int, int] = {}
    for t in range(7,-1,-1):
        assert x[t+624] is not None and x[t+397] is not None
        y = inv_twist(x[t+624] ^ x[t+397])
        high, low = y & 0x80000000, y & 0x7FFFFFFF
        if x[t] is None:
            highs[t] = high
        elif (x[t] & 0x80000000) != high:
            return None
        if x[t+1] is None:
            lows[t+1] = low
        elif (x[t+1] & 0x7FFFFFFF) != low:
            return None
    assert sorted(highs) == [4,5,6,7] and sorted(lows) == [4,5,6,7]
    return [highs[i] | lows[i] for i in range(4,8)]

def native(data: bytes, order: str) -> list[int]:
    assert len(data) % 4 == 0
    return [untemper(int.from_bytes(data[i:i+4],order))
            for i in range(0,len(data),4)]

def serialized(state: list[int], order: str) -> bytes:
    return b"".join(temper(y).to_bytes(4,order) for y in state)

def main() -> None:
    spool = (ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA256
    rows = [bytes.fromhex(x) for x in
            re.findall(r"PAYLOAD=([0-9A-F]{32})",spool.decode("ascii"))]
    assert len(rows) == 133
    recorder = (ROOT/"evidence/recorder/trip-recorder.raw").read_bytes()
    assert len(recorder) == 16+88*24 and recorder[:8] == b"TRP2DUMP"
    controls = [recorder[16+24*i+12:16+24*i+16] for i in range(88)]
    assert len(controls) == 88 and len(GROUPS) == 6

    for seed in (1,42,5489,0x89ABCDEF):
        rng = random.Random(seed)
        history = [untemper(rng.getrandbits(32)) for _ in range(632)]
        assert recover(history[:4],history[8:]) == history[4:8]
    print("FOUR_SEEDED_MT_FULL_COUPON_POSITIVE_CONTROLS PASS")

    # Exactly 4 unmodified late records. Index 1 is the disputed target and
    # intentionally excluded. Ordinary first packet is the genuine holdout.
    late = [(i,rows[128+i]) for i in (0,2,3,4)]
    holdout_models = holdout_compatible = holdout_exact = 0
    target_models = target_compatible = target_hits = 0
    for anchor_name,anchor in GROUPS.items():
        for printer_order,source_order,late_order in itertools.product(
            ("little","big"),repeat=3
        ):
            prefix = native(anchor,source_order)
            recorder_words = [x for c in controls for x in native(c,source_order)]
            other_words = [x for name,b in GROUPS.items()
                           if name!=anchor_name for x in native(b,source_order)]
            after_printer = [x for b in rows[1:128]
                             for x in native(b,printer_order)]
            base = after_printer+recorder_words+other_words
            assert len(base) == 616
            for (id1,b1),(id2,b2) in itertools.permutations(late,2):
                after = base + native(b1,late_order) + native(b2,late_order)
                assert len(after) == 624
                holdout_models += 1
                recovered = recover(prefix,after)
                if recovered is not None:
                    holdout_compatible += 1
                    if serialized(recovered,printer_order) == rows[0]:
                        holdout_exact += 1
                        print("GENUINE_HOLDOUT_PASS",anchor_name,
                              printer_order,source_order,late_order,id1,id2)
            target_base = ([x for b in rows[:128]
                            for x in native(b,printer_order)] +
                           recorder_words + other_words)
            assert len(target_base) == 620
            for late_id,b in late:
                after = target_base + native(b,late_order)
                assert len(after) == 624
                target_models += 1
                recovered = recover(prefix,after)
                if recovered is not None:
                    target_compatible += 1
                    coupon = serialized(recovered,printer_order)
                    slot = bytes(a^b for a,b in zip(coupon,MASK))
                    if hashlib.sha256(slot).digest() == TARGET:
                        target_hits += 1
                        print("ACTUAL_K04_PASS",slot.hex().upper())

    # More general native-state necessary tail search: x631 comes from
    # x404 and low31 of x8, with only one unknown high bit from x7.
    # Check all eight 4B LE/BE emitter candidates against source bytes.
    needed: set[bytes] = set()
    for printer_order in ("little","big"):
        stream = [x for b in rows[:128] for x in native(b,printer_order)]
        x8,x404 = stream[0],stream[396]
        for high in (0,0x80000000):
            y = (x8 & 0x7FFFFFFF) | high
            q = (y>>1) ^ (0x9908B0DF if y&1 else 0)
            for order in ("little","big"):
                needed.add(temper(x404^q).to_bytes(4,order))
    matches = [(str(p.relative_to(ROOT)),w.hex().upper())
               for p in ROOT.rglob("*") if p.is_file()
               for w in needed if w in p.read_bytes()]
    print(json.dumps({
        "calibration_hypotheses":holdout_models,
        "calibration_consistent":holdout_compatible,
        "calibration_full_original_coupon":holdout_exact,
        "K04_hypotheses":target_models,
        "K04_source_consistent":target_compatible,
        "K04_original_SHA256_hits":target_hits,
        "necessary_native_tail_fourbyte_values":
            sorted(w.hex().upper() for w in needed),
        "original_corpus_native_tail_matches":matches,
    },indent=2))
    assert (holdout_models,target_models)==(576,192)
    assert (holdout_compatible,holdout_exact,target_compatible,target_hits)==(0,0,0,0)
    assert not matches

if __name__=="__main__":
    main()
