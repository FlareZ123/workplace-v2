"""K04 candidate from original shuffled-record permutation ranks. Read-only."""
from pathlib import Path
import csv
import hashlib
import json
import math
import sys

MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
SHAS = {
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "evidence/transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "evidence/maintenance/seal-receipts.jsonl": "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    "evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv": "73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e",
    "evidence/recorder/trip-recorder.raw": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
}


def factoradic_rank(permutation):
    remaining = list(range(len(permutation)))
    rank = 0
    for element in permutation:
        index = remaining.index(element)
        rank = rank * len(remaining) + index
        del remaining[index]
    return rank


def source_rows(root):
    files = (
        ("telemetry", "evidence/telemetry/freeze-export.jsonl"),
        ("transfers", "evidence/transfers/transfer-audit.jsonl"),
        ("seals", "evidence/maintenance/seal-receipts.jsonl"),
        ("supplier", "evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv"),
    )
    for name, relative_path in files:
        source = (root / relative_path).read_text(encoding="utf-8")
        lines = [line for line in source.splitlines() if line and not line.startswith("#")]
        if name == "supplier":
            lines = lines[1:]
            records = [next(csv.reader([line])) for line in lines]
        else:
            records = [json.loads(line) for line in lines]
        yield name, lines, records
    raw = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert len(raw) == 16 + 88 * 24
    yield "recorder", [raw[16 + i * 24 : 16 + (i + 1) * 24].hex() for i in range(88)], None


def canonical_orders(name, lines, records):
    yield "raw", lines
    if name == "telemetry":
        yield "timestamp", [(r["ts"], r["tag"], r["field"], r["seq"], r["revision"], lines[i]) for i, r in enumerate(records)]
        yield "sequence", [(r["seq"], r["revision"], r["ts"], r["tag"], r["field"], lines[i]) for i, r in enumerate(records)]
    elif name == "transfers":
        yield "transfer", [(r.get("transfer", ""), r.get("seq", -1), r.get("attempt", -1), r.get("kind", ""), lines[i]) for i, r in enumerate(records)]
        yield "sequence", [(r.get("kind", ""), r.get("seq", -1), r.get("transfer", ""), r.get("attempt", -1), lines[i]) for i, r in enumerate(records)]
    elif name == "seals":
        yield "permit", [(r.get("permit", ""), r.get("bay", ""), r.get("revision", -1), lines[i]) for i, r in enumerate(records)]
        yield "serial", [(r.get("serial", ""), r.get("permit", ""), lines[i]) for i, r in enumerate(records)]
    elif name == "supplier":
        yield "line", [(r[0], r[2], r[3], lines[i]) for i, r in enumerate(records)]
        yield "account", [(r[4], r[0], r[2], lines[i]) for i, r in enumerate(records)]


def coupon_values(rank):
    encoded = rank.to_bytes(max(1, (rank.bit_length() + 7) // 8), "big")
    values = (
        (rank % (1 << 128)).to_bytes(16, "big"),
        (rank >> max(0, rank.bit_length() - 128)).to_bytes(16, "big"),
        hashlib.sha256(encoded).digest()[:16],
        hashlib.sha256(encoded).digest()[-16:],
        hashlib.blake2b(encoded, digest_size=16).digest(),
    )
    for value in values:
        yield value
        yield value[::-1]


def slot_hash(coupon):
    return hashlib.sha256(bytes(c ^ m for c, m in zip(coupon, MASK))).hexdigest()


def main(root):
    for name, sha in SHAS.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == sha, name
    assert factoradic_rank((2, 0, 3, 1)) == 13
    assert slot_hash((13).to_bytes(16, "big")) in {
        slot_hash(value) for value in coupon_values(13)
    }
    assignments = 0
    unique = set()
    per_source = []
    hits = []
    for name, lines, records in source_rows(root):
        count = 0
        for mode, items in canonical_orders(name, lines, records):
            assert len(set(map(repr, items))) == len(items), (name, mode)
            for descending in (False, True):
                ordered_indices = sorted(range(len(items)), key=lambda i: items[i], reverse=descending)
                inverse = {original_index: sorted_index for sorted_index, original_index in enumerate(ordered_indices)}
                permutation = [inverse[i] for i in range(len(items))]
                rank = factoradic_rank(permutation)
                assert 0 <= rank < math.factorial(len(permutation))
                for coupon in coupon_values(rank):
                    assignments += 1
                    count += 1
                    unique.add(coupon)
                    if slot_hash(coupon) == TARGET:
                        hits.append((name, mode, descending, coupon.hex().upper()))
        per_source.append((name, len(lines), count))
    output = {
        "assignments": assignments,
        "unique_complete_coupons": len(unique),
        "per_source": per_source,
        "original_hits": hits,
        "planted_control": "PASS",
    }
    print(json.dumps(output))
    assert assignments == 260 and len(unique) == 232
    assert not hits


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
