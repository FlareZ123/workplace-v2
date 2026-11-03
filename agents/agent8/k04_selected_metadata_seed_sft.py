"""H17 selected-only special-event coupon: source-labelled small-seed producer.

This is a bounded, speculative alternative to the ordinary spool generator,
not a claim that the 2025 scanner code controls the 2026 printer.
From repository root: python agents/agent8/k04_selected_metadata_seed_sft.py
Requires Python 3 and NumPy. Read-only. Never alters acceptance/source.
"""
import hashlib
import json
import random
import re
import struct
from datetime import datetime
from pathlib import Path

import numpy as np

root = Path(__file__).resolve().parents[2] / "resources"
spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
text = spool.decode()
rows = [line for line in text.splitlines() if line.startswith("2026-")]
selected = [row for row in rows if "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER " in row]
assert len(selected) == 1
copied = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", selected[0]).group(1))
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
routing = json.loads((root / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((root / "acceptance.json").read_text())
assert bytes.fromhex(routing["K04"]["masked_component"]) == mask
target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
assert target.hex() == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
late = {
    r.split("JOB=")[1].split(" ")[0]: bytes.fromhex(
        re.search(r"PAYLOAD=([0-9A-F]{32})", r).group(1))
    for r in rows[-2:]
}
assert set(late) == {"PS-261003-0448", "PS-261003-0420"}

def iso_epoch(t):
    return int(datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp())

nvalues = {
    8131, 417, 420, 448, 20261003, 20261004, 2025, 2026, 261003,
    2610030417, 2610030420, 2610030448, 171, 29, 17, 6, 3, 8, 49,
    82, 0x31, 0x52, 1802, 180200, 1003, 1004, 180201, 64920, 64921,
    iso_epoch("2026-10-03T18:02:00Z"),
    iso_epoch("2026-10-03T18:01:00Z"),
    iso_epoch("2026-10-03T18:03:00Z"),
    iso_epoch("2026-10-03T18:24:00Z"),
    iso_epoch("2026-10-03T18:25:00Z"),
}
strvalues = {
    "8131", "0417", "417", "PS-261003-0417", "2026-10-03T18:02:00Z",
    "202610031802", "20261003", "261003", "H17-IR-261003", "FA-17",
    "H17-POL-17/A3", "IR-261003-H17", "ESC-N", "L-29/N",
    "0417:2", "417:2", "PS-261003-0417:2", "RECOVER",
    "PS-261003-0417-RECOVER", "PS-261003-0417-2",
}
seed_specs = [
    ("int:" + str(n), n) for n in sorted(nvalues)
] + [
    ("str:" + s, s) for s in sorted(strvalues)
]
max_windows = 8192
trials = 0
hits = []
selected_copy_hits = []
late_hits = []
synthetic_hits = 0

seed_rng = random.Random(8131)
for _ in range(17):
    seed_block = b"".join(struct.pack("<I", seed_rng.getrandbits(32)) for _ in range(4))
planted_digest = hashlib.sha256(bytes(x ^ y for x, y in zip(seed_block, mask))).digest()

def assess(name, kind, pos, orientation, payload):
    global trials, synthetic_hits
    digest = hashlib.sha256(bytes(a ^ b for a, b in zip(payload, mask))).digest()
    trials += 1
    if digest == target:
        hits.append((name, kind, pos, orientation, payload.hex().upper()))
    if payload == copied:
        selected_copy_hits.append((name, kind, pos, orientation))
    for job, retained in late.items():
        if payload == retained:
            late_hits.append((name, kind, pos, orientation, job))
    if digest == planted_digest and name == "int:8131" and kind == "cpython":
        synthetic_hits += 1

for name, seed in seed_specs:
    rng = random.Random(seed)
    for pos in range(max_windows):
        words = [rng.getrandbits(32) for _ in range(4)]
        chunks = (
            struct.pack("<4I", *words),
            struct.pack(">4I", *words),
            struct.pack("<4I", *words[::-1]),
            struct.pack(">4I", *words[::-1]),
        )
        for orientation, payload in enumerate(chunks):
            assess(name, "cpython", pos, orientation, payload)

for name, seed in seed_specs:
    nseed = seed if isinstance(seed, int) else int.from_bytes(
        hashlib.sha256(seed.encode()).digest(), "big"
    )
    for kind, generator in (
        ("numpy-mt", np.random.MT19937(nseed)),
        ("numpy-pcg", np.random.PCG64(nseed)),
    ):
        rng = np.random.Generator(generator)
        for pos in range(max_windows):
            source = rng.bytes(16)
            orientations = (
                source,
                source[::-1],
                b"".join(source[i:i + 4][::-1] for i in range(0, 16, 4)),
            )
            for orientation, payload in enumerate(orientations):
                assess(name, kind, pos, orientation, payload)

assert len(seed_specs) == 52 and trials == 4259840 and synthetic_hits == 1
print(json.dumps({
    "named_source_seeds": len(seed_specs),
    "complete_candidates": trials,
    "original_target_matches": hits,
    "copied_selected_ACK_matches": selected_copy_hits,
    "original_intact_late_ACK_matches": late_hits,
    "planted_source_seed_positive": synthetic_hits,
}, indent=2))
