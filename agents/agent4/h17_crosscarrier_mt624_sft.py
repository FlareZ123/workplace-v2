"""H-17 source-only six-carrier MT19937 624-word test (Agent 4, 5 Nov 2026).

Original sources are read-only. Run inside workplace-v2; optionally set
H17_RESOURCE_ROOT to the extracted original archive directory.
"""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import json
import os
import random
import re
import struct
import zlib

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
PINS = {
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/recorder/trip-recorder.raw": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
    "evidence/telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "evidence/transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
for path, expected in PINS.items():
    assert sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
spool_lines = [line for line in (ROOT / "evidence/print/spool-reconstruction.log").read_text().splitlines()
               if "PAYLOAD=" in line]
assert len(spool_lines) == 133
target_line = spool_lines[129]
assert all(s in target_line for s in (
    "2026-10-03T18:02:00Z", "JOB=PS-261003-0417",
    "ATTEMPT=2", "STATE=ACK", "CLASS=RECOVER",
    "PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5",
))
spool = [bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", line).group(1))
         for i, line in enumerate(spool_lines) if i != 129]
assert len(spool) == 132
record_bytes = (ROOT / "evidence/recorder/trip-recorder.raw").read_bytes()
assert struct.unpack_from("<8sHHI", record_bytes) == (b"TRP2DUMP", 2, 24, 88)
records = []
for i in range(88):
    off = 16 + 24 * i
    ts, node, event, latch, seq, word, aux, crc = struct.unpack_from("<IHBBI4sII", record_bytes, off)
    good = zlib.crc32(record_bytes[off:off + 20]) == crc
    records.append((i, ts, node, event, latch, seq, word, good))
assert sum(r[7] for r in records) == 84

# Two selected, accepted 16-byte prehash objects; pin their source files above.
k02 = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
k07 = bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9")
telemetry = [json.loads(line) for line in
             (ROOT / "evidence/telemetry/freeze-export.jsonl").read_text().splitlines()]
trows = [o for o in telemetry if o.get("tag") == "LT-204" and o.get("field") == "DIAG_WORD"
         and o.get("quality") == "GOOD" and o.get("state") == "HOLD"
         and datetime(2026, 10, 3, 21, 13, 40, tzinfo=timezone.utc)
             <= datetime.fromisoformat(o["ts"]) <
             datetime(2026, 10, 3, 21, 13, 48, tzinfo=timezone.utc)]
tbest = {i: max((o for o in trows if o["seq"] == i), key=lambda o: o["revision"]) for i in range(8)}
assert b"".join(tbest[i]["value"].to_bytes(2, "big") for i in range(8)) == k02
transfers = [json.loads(line) for line in
             (ROOT / "evidence/transfers/transfer-audit.jsonl").read_text().splitlines()]
qrows = [o for o in transfers if o["kind"] == "CHUNK" and o["transfer"] == "AX-7782"]
qbest = {i: max((o for o in qrows if o["seq"] == i), key=lambda o: o["attempt"]) for i in range(8)}
assert b"".join(bytes.fromhex(qbest[i]["checkpoint"]) for i in range(8)) == k07
acceptance = json.loads((ROOT / "acceptance.json").read_text())
k01 = bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A")
k06 = bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A")
assert sha256(k01).hexdigest() == acceptance["slot_sha256"]["K01"]
assert sha256(k06).hexdigest() == acceptance["slot_sha256"]["K06"]
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
want = bytes.fromhex(acceptance["slot_sha256"]["K04"])

def untemper(x):
    x ^= x >> 18
    x ^= (x << 15) & 0xefc60000
    for _ in range(6):
        x ^= (x << 7) & 0x9d2c5680
    for _ in range(3):
        x ^= x >> 11
    return x & 0xffffffff

def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    x ^= x >> 18
    return x & 0xffffffff

def twist_next(state, i):
    y = (state[i] & 0x80000000) | (state[i + 1] & 0x7fffffff)
    return temper(state[i + 397] ^ (y >> 1) ^ (0x9908b0df if y & 1 else 0))

def as_words(blocks, endian):
    return tuple(int.from_bytes(b[i:i + 4], endian)
                 for b in blocks for i in range(0, len(b), 4))

# Positive controls check actual seeded MT streams, nonzero origin, erasure
# placement, complete 16-byte prediction and unchanged K04-style reduction.
rng = random.Random(0x17A4)
for _ in range(1001):
    rng.getrandbits(32)
truth = [rng.getrandbits(32) for _ in range(636)]
native = list(map(untemper, truth))
assert all(twist_next(native, i) == truth[624 + i] for i in range(12))
assert all(twist_next(native, i) == truth[624 + i] for i in range(12)
           if i not in (516, 517, 518, 519))
assert all(twist_next(native, i) == truth[624 + i] for i in range(4, 8))
fake_coupon = b"".join(x.to_bytes(4, "little") for x in truth[624:628])
fake_component = bytes(x ^ y for x, y in zip(fake_coupon, mask))
assert sha256(fake_component).digest() == sha256(
    bytes(x ^ y for x, y in zip(mask,
        b"".join(twist_next(native, i).to_bytes(4, "little") for i in range(4))))).digest()

raw_groups = {
    "A": spool,
    "T": [k02],
    "Q": [k07],
    "I": [k01],
    "C": [k06],
}
def mode_list(label, recorder_good=False, erasure=False):
    if label == "R":
        rr = [r for r in records if r[7] or not recorder_good]
        sorts = [
            ("raw", rr),
            ("time", sorted(rr, key=lambda r: (r[1], r[0]))),
            ("seq", sorted(rr, key=lambda r: (r[5], r[0]))),
            ("event", sorted(rr, key=lambda r: (r[2], r[3], r[4], r[5], r[0]))),
        ]
        sources = [(name, [r[6] for r in group]) for name, group in sorts]
    else:
        sources = [("original", raw_groups[label])]
    result = []
    for order, blocks in sources:
        for endian in ("little", "big"):
            values = as_words(blocks, endian)
            if label == "A" and erasure:
                values = values[:516] + (None,) * 4 + values[516:]
            native_words = tuple(untemper(x) if x is not None else None for x in values)
            result.append((order + "." + endian, values, native_words))
    return result

for good_only in (False, True):
    variants = {name: mode_list(name, recorder_good=good_only, erasure=True)
                for name in ("A", "R", "T", "Q", "I", "C")}
    checks = 0
    models = 0
    hits = 0
    for group_order in permutations(variants):
        for selection in product(*(variants[name] for name in group_order)):
            outputs = tuple(x for v in selection for x in v[1])
            state = tuple(x for v in selection for x in v[2])
            assert len(outputs) == (632 if good_only else 636)
            models += 1
            for i in range(len(outputs) - 624):
                if any(state[j] is None for j in (i, i + 1, i + 397)) or outputs[i + 624] is None:
                    continue
                checks += 1
                hits += twist_next(state, i) == outputs[i + 624]
    assert models == 184320 and hits == 0
    assert checks == (1474560 if good_only else 2211840)
    print("SOURCE_ERASURE_MT", "VALID_RECORDER_ONLY" if good_only else "ALL_RECORDER",
          "models", models, "independent_fullword_comparisons", checks, "matches", hits)

# Different complete-target mechanism: hypothesize missing physical ESC-N coupon
# was generated immediately after the 624 source words from A, R, T and Q.
variants = {name: mode_list(name) for name in ("A", "R", "T", "Q")}
tested = 0
coupons = set()
found = []
for order in permutations(variants):
    for selection in product(*(variants[name] for name in order)):
        state = tuple(x for v in selection for x in v[2])
        assert len(state) == 624
        future = [twist_next(state, i) for i in range(4)]
        for endian in ("little", "big"):
            for reverse in (False, True):
                payload = b"".join(w.to_bytes(4, endian) for w in
                                   (future[::-1] if reverse else future))
                coupons.add(payload)
                tested += 1
                component = bytes(x ^ y for x, y in zip(mask, payload))
                if sha256(component).digest() == want:
                    found.append((order, [v[0] for v in selection], endian,
                                  reverse, payload.hex().upper(), component.hex().upper()))
assert tested == 6144 and len(coupons) == 872
print("TARGET_POST624", "assignments", tested, "distinct_coupons", len(coupons),
      "original_hits", len(found), "hit_details", found)
