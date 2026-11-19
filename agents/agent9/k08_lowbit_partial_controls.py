#!/usr/bin/env python3
"""Reproduce bounded LOW BIT controls for accepted components, transfer retries, and print payloads.

This is deliberately a partial control harness, not the full end-to-end K08 benchmark.
Run from the workplace-v2 repository root:
    python agents/agent9/k08_lowbit_partial_controls.py
Only standard-library modules are used. Source files are hash-pinned.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources/evidence"
EXPECTED_SHA = {
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}
SLOTS = ("K01", "K02", "K03", "K05", "K06", "K07")
TRANSFERS = ("AX-7778", "AX-7781", "AX-7782", "AX-7783")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def low_value(text: str) -> int:
    return sum((ord(ch) & 1) << i for i, ch in enumerate(text))


def low_pack(raw: bytes) -> bytes:
    if len(raw) % 8:
        raise ValueError(f"low_pack requires a multiple of 8 bytes, got {len(raw)}")
    return bytes(
        sum((raw[i + j] & 1) << j for j in range(8))
        for i in range(0, len(raw), 8)
    )


def selector(raw: bytes) -> tuple[str, int]:
    packed_hex = low_pack(raw).hex().upper()
    return packed_hex, low_value(packed_hex)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def component_controls() -> dict:
    candidate = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text(encoding="utf-8"))
    values = {}
    for slot in SLOTS:
        value = candidate.get(slot)
        if not isinstance(value, str) or len(value) != 32:
            raise AssertionError(f"missing or malformed accepted {slot}")
        raw = bytes.fromhex(value)
        if sha256(raw).upper() != acceptance["slot_sha256"][slot].upper():
            raise AssertionError(f"{slot} does not match its unchanged slot commitment")
        values[slot] = raw

    def half_char(raw: bytes, lower: bool) -> str:
        part = raw[8:] if lower else raw[:8]
        return chr(low_pack(part)[0])

    lower = []
    upper = []
    for slots in itertools.permutations(SLOTS, 3):
        lower_text = "".join(half_char(values[s], True) for s in slots)
        upper_text = "".join(half_char(values[s], False) for s in slots)
        lower.append((slots, lower_text))
        upper.append((slots, upper_text))

    selected = ("K01", "K06", "K02")
    selected_lower = "".join(half_char(values[s], True) for s in selected)
    selected_upper = " ".join(low_pack(values[s][:8]).hex().upper() for s in selected)
    return {
        "assignments": len(lower),
        "exact_YEA_lower_assignments": [list(slots) for slots, value in lower if value.upper() == "YEA"],
        "printable_alpha_lower_assignments": sum(value.isascii() and value.isalpha() for _, value in lower),
        "exact_YEA_upper_assignments": [list(slots) for slots, value in upper if value.upper() == "YEA"],
        "selected_order": list(selected),
        "selected_lower": selected_lower,
        "selected_upper_lowpack_hex": selected_upper,
        "lower_half_chars": {s: half_char(values[s], True) for s in SLOTS},
    }


def transfer_controls() -> dict:
    path = EVIDENCE / "transfers/transfer-audit.jsonl"
    rows = load_jsonl(path)
    out = {}
    for transfer in TRANSFERS:
        chunks = [r for r in rows if r.get("transfer") == transfer and r.get("kind") == "CHUNK"]
        by_seq: dict[int, dict[int, bytes]] = {}
        for row in chunks:
            by_seq.setdefault(int(row["seq"]), {})[int(row["attempt"])] = bytes.fromhex(row["checkpoint"])
        if set(by_seq) != set(range(8)) or any(set(attempts) != {1, 2} for attempts in by_seq.values()):
            raise AssertionError(f"unexpected chunk/attempt structure for {transfer}")
        mask_rows = []
        for mask in range(256):
            raw = b"".join(by_seq[i][2 if (mask >> i) & 1 else 1] for i in range(8))
            packed, selected = selector(raw)
            mask_rows.append((mask, packed, selected, raw))
        official = next(row for row in mask_rows if row[0] == 255)
        exact_53d5 = [row[0] for row in mask_rows if row[1] == "53D5"]
        masks_to_11 = [row[0] for row in mask_rows if row[2] == 11]
        out[transfer] = {
            "official_mask": 255,
            "official_lowpack": official[1],
            "official_selector": official[2],
            "masks_to_selector_11": len(masks_to_11),
            "masks_to_exact_53D5": len(exact_53d5),
            "exact_53D5_masks": exact_53d5,
            "mixed_even_odd_mask170": next({"lowpack": r[1], "selector": r[2]} for r in mask_rows if r[0] == 170),
        }
        if transfer == "AX-7782":
            candidate = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
            if sha256(official[3])[:32].upper() != candidate["K07"].upper():
                raise AssertionError("AX-7782 official source bytes do not reproduce accepted K07")
            if official[1] != "53D5":
                raise AssertionError("AX-7782 official LOW BIT output changed")
    return out


def print_controls() -> dict:
    path = EVIDENCE / "print/spool-reconstruction.log"
    rows = []
    pattern = re.compile(r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)")
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = pattern.search(line)
        if not match:
            continue
        job, attempt, state, cls, payload, dest = match.groups()
        packed, selected = selector(bytes.fromhex(payload))
        rows.append({"line": line_no, "job": job, "attempt": int(attempt), "state": state,
                     "class": cls, "dest": dest, "lowpack": packed, "selector": selected})
    if len(rows) != 133:
        raise AssertionError(f"expected 133 print payload rows, got {len(rows)}")
    counts = Counter(row["selector"] for row in rows)
    selected_rows = [row for row in rows if row["job"] in {"PS-261003-0417", "PS-261003-0448", "PS-261003-0420"}]
    recover_fives = [row for row in rows if row["class"] == "RECOVER" and row["selector"] == 5]
    return {
        "rows": len(rows),
        "selector_counts": {str(k): counts[k] for k in sorted(counts)},
        "valid_note_ids_1_to_15": sum(counts[i] for i in range(1, 16)),
        "valid_note_id_fraction": sum(counts[i] for i in range(1, 16)) / len(rows),
        "selector_5_rows": counts[5],
        "recover_selector_5_rows": [
            {"job": r["job"], "attempt": r["attempt"], "state": r["state"], "line": r["line"]}
            for r in recover_fives
        ],
        "late_job_rows": selected_rows,
    }


def main() -> None:
    for relative, expected in EXPECTED_SHA.items():
        actual = sha256((EVIDENCE / relative).read_bytes())
        if actual != expected:
            raise AssertionError(f"source hash mismatch for {relative}: {actual}")
    acceptance_sha = sha256((ROOT / "resources/acceptance.json").read_bytes())
    if acceptance_sha != "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f":
        raise AssertionError(f"acceptance hash mismatch: {acceptance_sha}")
    result = {
        "source_sha256": {**EXPECTED_SHA, "acceptance.json": acceptance_sha},
        "low_value_hex_selector_range": [0, 15],
        "uniform_note_namespace_hit_probability_for_1_to_15": 15 / 16,
        "components": component_controls(),
        "transfers": transfer_controls(),
        "print_payloads": print_controls(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
