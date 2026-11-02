"""H17 K04 source-selected 4x4 byte-lane interleaver recovery class.

Run: python agents/agent31/k04_lane_interleaver_sft.py [original-archive.zip]
Uses only the unchanged source files and original K04 commitment, with synthetic
positive controls. No source or candidate files are modified.
"""
from pathlib import Path
from itertools import permutations, product
import hashlib
import json
import re
import sys
import time
import zipfile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def read_case(archive=None):
    if archive:
        with zipfile.ZipFile(archive) as z:
            spool = z.read("evidence/print/spool-reconstruction.log")
            routing = json.loads(z.read("evidence/recovery-routing.json"))
            acceptance = json.loads(z.read("acceptance.json"))
    else:
        root = Path(__file__).resolve().parents[2] / "resources"
        spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
        routing = json.loads((root / "evidence/recovery-routing.json").read_text())
        acceptance = json.loads((root / "acceptance.json").read_text())
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    rows = [line for line in spool.decode().splitlines() if "PAYLOAD=" in line]
    assert len(rows) == 133
    selected = rows[129]
    assert all(field in selected for field in (
        "JOB=PS-261003-0417", "ATTEMPT=2", "STATE=ACK", "CLASS=RECOVER"))
    copied = bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", selected).group(1))
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    assert len(copied) == len(mask) == 16 and len(target) == 32
    return copied, mask, target


def enumerate_layout(copied, mask, target, transpose):
    if transpose:
        chunks = [bytes(copied[4*row+column] for row in range(4))
                  for column in range(4)]
    else:
        chunks = [copied[4*i:4*i+4] for i in range(4)]
    arrangements = [sorted(set(bytes(p) for p in permutations(chunk)))
                    for chunk in chunks]
    # Known legal rearrangement, distinct from identity; control validates
    # the same SHA256/mask path against an in-family synthetic target.
    control = (chunks[2][::-1] + chunks[0][1:] + chunks[0][:1]
               + chunks[3][::-1] + chunks[1][::-1])
    assert len(control) == 16
    positive = hashlib.sha256(bytes(a ^ b for a, b in zip(control, mask))).digest()
    control_hits = count = 0
    match = []
    for word_order in permutations(range(4)):
        adjusted = []
        for position, source in enumerate(word_order):
            lane_mask = mask[4*position:4*position+4]
            adjusted.append([bytes(a ^ b for a, b in zip(p, lane_mask))
                             for p in arrangements[source]])
        for a, b, c, d in product(*adjusted):
            component = a+b+c+d
            digest = hashlib.sha256(component).digest()
            count += 1
            if digest == positive:
                control_hits += 1
            if digest == target:
                match.append((word_order, component.hex().upper()))
    assert control_hits >= 1, "Synthetic source-origin rearrangement missed"
    assert count == (7962624 if transpose else 3981312)
    return count, control_hits, match


def main(archive=None):
    copied, mask, target = read_case(archive)
    print("SOURCE", copied.hex().upper(), "selected K04 ACK2 original spool SHA256 verified")
    total = 0
    started = time.monotonic()
    for transpose in (False, True):
        count, controls, matches = enumerate_layout(copied, mask, target, transpose)
        total += count
        print("TRANSPOSE", transpose, "distinct full-candidate assignments", count,
              "synthetic positive hits", controls, "original K04 PASS", matches,
              flush=True)
    print("TOTAL", total, "source-byte-only candidates; elapsed",
          round(time.monotonic()-started, 2), "s")
    print("Unchanged REC8 remains six PASS, two missing unless original hit reported")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
