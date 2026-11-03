"""H-17 K04 printer cohort escrow parity/sum source model, read-only SFT.

Test every prefix-bounded contiguous source interval preceding selected ACK2,
every Boolean selector of nine CLASS x DEST metadata groups, and XOR or
modular-additive 128-bit aggregation. This producer is unverified.
Usage: python k04_escrow_cohort_aggregate_sft.py PATH_TO_ORIGINAL_RESOURCES
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK_128 = (1 << 128) - 1
CLASSES = ("LABEL", "STORES", "RECOVER")
DESTS = ("bench", "desk", "store")


def run(root: Path) -> None:
    spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    mask = int(route["K04"]["masked_component"], 16)
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    assert len(target) == 32
    rows = []
    for line in spool.decode("ascii").splitlines():
        if " PAYLOAD=" not in line:
            continue
        ts, *items = line.split()
        kv = dict(pair.split("=", 1) for pair in items)
        if ts == "2026-10-03T18:02:00Z":
            assert kv["JOB"] == "PS-261003-0417" and kv["ATTEMPT"] == "2"
            continue
        if ts > "2026-10-03T18:02:00Z":
            continue
        assert kv["CLASS"] in CLASSES and kv["DEST"] in DESTS
        rows.append((CLASSES.index(kv["CLASS"]) * 3 + DESTS.index(kv["DEST"]),
                     int(kv["PAYLOAD"], 16)))
    assert len(rows) == 129
    assert rows[0][1] == int("FBBBC54356483F5864BB3F06794518A5", 16)
    assert rows[-1][1] == int("CD3E4F216ADB2FB180DA2AA90B33F7A4", 16)

    # Planted independent source interval [3,41], selected groups 1,4,6.
    planted_x = 0
    for group, payload in rows[3:42]:
        if group in (1, 4, 6):
            planted_x ^= payload
    planted_digest = hashlib.sha256(((planted_x ^ mask) & MASK_128).to_bytes(16, "big")).digest()

    count = original_matches = controls = exact_planted = 0
    started = time.monotonic()
    for first in range(len(rows)):
        group_xor = [0] * 9
        group_sum = [0] * 9
        for last in range(first, len(rows)):
            category, value = rows[last]
            group_xor[category] ^= value
            group_sum[category] = (group_sum[category] + value) & MASK_128
            previous_gray = 0
            acc_x = acc_sum = 0
            for index in range(1, 512):
                gray = index ^ (index >> 1)
                changed = (gray ^ previous_gray).bit_length() - 1
                if gray & (1 << changed):
                    acc_x ^= group_xor[changed]
                    acc_sum = (acc_sum + group_sum[changed]) & MASK_128
                else:
                    acc_x ^= group_xor[changed]
                    acc_sum = (acc_sum - group_sum[changed]) & MASK_128
                previous_gray = gray
                for operation, aggregated in (("XOR", acc_x), ("ADD", acc_sum)):
                    component = (aggregated ^ mask).to_bytes(16, "big")
                    digest = hashlib.sha256(component).digest()
                    count += 1
                    if digest == target:
                        original_matches += 1
                        print("K04_ORIGINAL_PASS", operation, first, last, gray,
                              component.hex().upper(), flush=True)
                    if digest == planted_digest:
                        controls += 1
                        if (operation, first, last, gray) == (
                            "XOR", 3, 41, (1 << 1) | (1 << 4) | (1 << 6)
                        ):
                            exact_planted += 1
    assert count == (129 * 130 // 2) * 511 * 2
    assert controls >= 1 and exact_planted == 1
    print(json.dumps({
        "original_source_sha256": SOURCE_SHA,
        "groups": len(CLASSES) * len(DESTS),
        "source_rows": len(rows),
        "contiguous_windows": 129 * 130 // 2,
        "nonempty_group_selectors": 511,
        "complete_candidate_assignments": count,
        "original_k04_matches": original_matches,
        "planted_positive_hits": controls,
        "exact_planted_assignment": exact_planted,
        "seconds": round(time.monotonic() - started, 2),
    }, indent=2))


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else (
        Path(__file__).resolve().parents[2] / "resources"
    )
    run(root)
