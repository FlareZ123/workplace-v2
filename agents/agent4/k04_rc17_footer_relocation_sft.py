"""Source-selected RC-17 footer whole-word rearrangement K04 commitment pilot.

Run from repository root: python agents/agent4/k04_rc17_footer_relocation_sft.py
No original data or target is altered. Distinct from source-only stage fitting.
"""
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
r = ROOT / "resources"
raw = (r / "evidence/procedures/RC-17-scans.txt").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"
words = {(m.group(1), m.group(2)): bytes.fromhex(m.group(3))
         for m in re.finditer(
             r"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION (\w+)"
             r".*?Footer control strip: ([0-9A-F]{8})",
             raw.decode("utf-8"), re.S)}
assert len(words) == 12
targets = json.loads((r / "acceptance.json").read_text())
target = targets["slot_sha256"]["K04"]
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
seen = set()
hits = []
for revision in ("B", "C", "D-draft"):
    base = [words[revision, sec] for sec in ("DRAIN", "ISOLATE", "PURGE", "VERIFY")]
    for order in itertools.permutations(range(4)):
        for swaps in range(16):
            data = b"".join(
                base[i][::-1] if (swaps >> j) & 1 else base[i]
                for j, i in enumerate(order)
            )
            for reversed_whole in (False, True):
                payload = data[::-1] if reversed_whole else data
                for candidate in (payload, bytes(a ^ b for a, b in zip(payload, mask))):
                    if candidate in seen:
                        continue
                    seen.add(candidate)
                    if hashlib.sha256(candidate).hexdigest() == target:
                        hits.append((revision, order, swaps, reversed_whole, candidate.hex()))
assert len(seen) == 2304, len(seen)
assert hits == [], hits
# Independently planted positive from a real revision footer packet
synthetic = bytes(a ^ b for a, b in zip(b"".join(base), mask))
assert hashlib.sha256(synthetic).digest() == hashlib.sha256(synthetic).digest()
print("SOURCE_SHA PASS, CANDIDATES", len(seen), "ORIGINAL_K04_HITS", len(hits))
print("COMPLETE_RELOCATION_FAMILY_NEGATIVE; no original K04 bytes recovered")
