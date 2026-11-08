"""H-17 read-only complete-coupon reconstruction from mixed-transfer AX checkpoints.
Usage: python agents/agent1/k04_ax_mixedtransfer_checkpoint_mosaic_sft.py resources
Windows 11 compatible, Python standard library only.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

PINS = {
    "evidence/transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}

def main(root: Path) -> None:
    def read(path: str) -> bytes:
        blob = (root / path).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == PINS[path], path
        return blob

    audit = [json.loads(line) for line in read("evidence/transfers/transfer-audit.jsonl").splitlines()]
    route = json.loads(read("evidence/recovery-routing.json"))
    acceptance = json.loads(read("acceptance.json"))
    rows = [row for row in audit if row["kind"] == "CHUNK"]
    assert len(rows) == 64
    transfers = sorted({row["transfer"] for row in rows})
    assert transfers == ["AX-7778", "AX-7781", "AX-7782", "AX-7783"]
    options = []
    for seq in range(8):
        selected = sorted((row for row in rows if row["seq"] == seq),
                          key=lambda row: (row["transfer"], row["attempt"]))
        assert [(row["transfer"], row["attempt"]) for row in selected] == [
            (t, a) for t in transfers for a in (1, 2)
        ]
        assert all(row["object"] == "IR-261003-H17" for row in selected)
        options.append([bytes.fromhex(row["checkpoint"]) for row in selected])

    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    assert len(mask) == 16 and len(target) == 32
    masked = [[bytes((x ^ mask[i * 2], y ^ mask[i * 2 + 1])) for x, y in group]
              for i, group in enumerate(options)]

    indexes = list(itertools.product(range(8), repeat=4))
    def half(groups: list[list[bytes]], offset: int) -> list[bytes]:
        return [b"".join(groups[offset+i][index] for i, index in enumerate(ix))
                for ix in indexes]
    first = half(options, 0)
    last = half(options, 4)
    first_mask = half(masked, 0)
    last_mask = half(masked, 4)
    planted_indices = tuple(range(8))
    planted = b"".join(options[i][index] for i, index in enumerate(planted_indices))
    planted_digest = hashlib.sha256(planted).digest()

    total = positive = direct_hits = coupon_hits = 0
    for a, prefix in enumerate(first):
        mask_prefix = first_mask[a]
        for b, suffix in enumerate(last):
            component = prefix + suffix
            direct_digest = hashlib.sha256(component).digest()
            total += 1
            if direct_digest == planted_digest:
                positive += 1
                assert indexes[a] + indexes[b] == planted_indices
            if direct_digest == target:
                direct_hits += 1
                print("K04_DIRECT_MATCH", indexes[a] + indexes[b], component.hex().upper())
            masked_component = mask_prefix + last_mask[b]
            if hashlib.sha256(masked_component).digest() == target:
                coupon_hits += 1
                print("K04_MASKED_MATCH", indexes[a] + indexes[b], masked_component.hex().upper())

    assert total == 8**8 and positive == 1
    print(json.dumps({
        "distinct_source_vectors": total,
        "full_sha256_comparisons": total * 2,
        "planted_full_vector_hits": positive,
        "original_direct_hits": direct_hits,
        "original_masked_hits": coupon_hits,
    }, sort_keys=True))

if __name__ == "__main__":
    main(Path(sys.argv[1]))
