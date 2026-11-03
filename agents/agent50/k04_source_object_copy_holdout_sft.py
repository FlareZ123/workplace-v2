"""H17 read-only whole-record printer object-replay holdout.

Checks deterministic source-metadata selectors on 132 intact printer ACKs.
Withhold selected original row129 entirely, including its payload. No K04
mask, acceptance commitment, or verifier is accessed. Positive fake-copy
fixture validates the selector. Run from repository root:
    python agents/agent50/k04_source_object_copy_holdout_sft.py
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
rows = []
for line in raw.decode("utf-8").splitlines():
    if "PAYLOAD=" not in line:
        continue
    fields = dict(
        re.findall(r"(JOB|ATTEMPT|STATE|CLASS|PAYLOAD|DEST)=([^ ]+)", line)
    )
    fields["payload"] = bytes.fromhex(fields.pop("PAYLOAD"))
    rows.append(fields)
assert len(rows) == 133
assert rows[129]["JOB"] == "PS-261003-0417"
assert rows[129]["STATE"] == "ACK"
assert rows[129]["ATTEMPT"] == "2"
assert rows[129]["CLASS"] == "RECOVER"
intact = [row for idx, row in enumerate(rows) if idx != 129]
assert len(intact) == 132

selectors = {
    "previous_same_class_dest": ("CLASS", "DEST"),
    "previous_same_class": ("CLASS",),
    "previous_same_dest": ("DEST",),
    "previous_same_job": ("JOB",),
    "prior_packet": (),
}


def prior_match(records: list[dict], index: int, keys: tuple[str, ...]):
    expected = records[index]
    return next(
        (
            prior for prior in reversed(records[:index])
            if all(prior[key] == expected[key] for key in keys)
        ),
        None,
    )


for name, keys in selectors.items():
    opportunities = [0, 0]
    full_matches = [0, 0]
    byte_matches = [0, 0]
    aligned_word_matches = [0, 0]
    for index, row in enumerate(intact):
        donor = prior_match(intact, index, keys)
        if donor is None:
            continue
        split = int(index >= 64)
        opportunities[split] += 1
        x, y = row["payload"], donor["payload"]
        full_matches[split] += x == y
        byte_matches[split] += sum(a == b for a, b in zip(x, y))
        aligned_word_matches[split] += sum(
            x[step:step+4] == y[step:step+4]
            for step in range(0, 16, 4)
        )
    assert full_matches == [0, 0]
    print(name, "train/holdout opportunities", opportunities,
          "full packets", full_matches, "bytes", byte_matches,
          "aligned words", aligned_word_matches)

assert len({record["payload"] for record in intact}) == 132
native_words = [
    int.from_bytes(record["payload"][pos:pos+4], "little")
    for record in intact for pos in (0, 4, 8, 12)
]
assert len(native_words) == 528 and len(set(native_words)) == 528
print("All 528 intact original aligned 32-bit printer words distinct")

planted = [row.copy() for row in intact]
target_index = 70
old = prior_match(planted, target_index, ("CLASS", "DEST"))
assert old is not None
planted[target_index]["payload"] = old["payload"]
retrieved = prior_match(planted, target_index, ("CLASS", "DEST"))
assert retrieved is not None
assert planted[target_index]["payload"] == retrieved["payload"]
print("Synthetic source-key-selected exact copied-record positive PASS")
print("ORIGINAL source-exact replay models unsuccessful; K04 still MISSING")
