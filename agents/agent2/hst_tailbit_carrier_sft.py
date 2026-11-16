#!/usr/bin/env python3
"""Bounded HST 128-record tail-bit carrier test for K04.

Hypothesis only: ATEALBIT/BETA TAIL might designate one low/tail bit from
each of the 128 HST rows left after excluding the 17 DIAG_WORD/GOOD/HOLD
rows belonging to the K02 diagnostic population. This is not a source-defined
K04 route: the HST readme says PV/engineering values are historian context,
not raw diagnostic words. Test a frozen set of order/packing views against the
unchanged K04 mask and commitment. No official file is modified.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from decimal import Decimal
from datetime import datetime
from pathlib import Path

PINS = {
    "telemetry": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "routing": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}

def pack_bits(bits, order):
    assert len(bits) == 128
    out = bytearray()
    for i in range(0, 128, 8):
        chunk = bits[i:i+8]
        shift = (lambda j: 7-j) if order == "msb" else (lambda j: j)
        out.append(sum(int(bit) << shift(j) for j, bit in enumerate(chunk)))
    return bytes(out)

def bit_value(row, method):
    value = row["value"]
    if row["field"] == "DIAG_WORD":
        return int(value) & 1
    if method == "decimal_tail":
        return int(Decimal(str(value)) * 1000) & 1
    if method == "float64_lsb":
        return struct.unpack(">Q", struct.pack(">d", float(value)))[0] & 1
    if method == "float32_lsb":
        return struct.unpack(">I", struct.pack(">f", float(value)))[0] & 1
    raise ValueError(method)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd(),
                    help="repository root or extracted archive root")
    root = ap.parse_args().root
    base = root / "resources" if (root / "resources/evidence").is_dir() else root
    evidence = base / "evidence"
    acceptance_path = root / "acceptance.json"
    telemetry_path = evidence / "telemetry/freeze-export.jsonl"
    routing_path = evidence / "recovery-routing.json"
    for label, path in (("telemetry", telemetry_path), ("routing", routing_path),
                        ("acceptance", acceptance_path)):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != PINS[label]:
            raise SystemExit(f"{label} SHA-256 pin mismatch: {digest}")

    records = [json.loads(line) for line in telemetry_path.read_text().splitlines() if line.strip()]
    excluded = [r for r in records if r.get("field") == "DIAG_WORD"
                and r.get("quality") == "GOOD" and r.get("state") == "HOLD"]
    selected = [r for r in records if not (
        r.get("field") == "DIAG_WORD" and r.get("quality") == "GOOD"
        and r.get("state") == "HOLD")]
    if (len(records), len(excluded), len(selected)) != (145, 17, 128):
        raise SystemExit(f"unexpected population: {len(records)}/{len(excluded)}/{len(selected)}")
    if (sum(r["field"] == "PV" for r in selected),
        sum(r["field"] == "DIAG_WORD" for r in selected)) != (112, 16):
        raise SystemExit("unexpected 128-row field mix")

    route = json.loads(routing_path.read_text())
    acceptance = json.loads(acceptance_path.read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    orders = {
        "retrieval": selected,
        "timestamp_asc": sorted(selected, key=lambda r: (
            datetime.fromisoformat(r["ts"]), r["seq"], r["tag"], r["field"])),
        "timestamp_desc": sorted(selected, key=lambda r: (
            datetime.fromisoformat(r["ts"]), r["seq"], r["tag"], r["field"]), reverse=True),
        "seq_asc": sorted(selected, key=lambda r: (r["seq"], r["ts"], r["tag"], r["field"])),
        "tag_seq": sorted(selected, key=lambda r: (r["tag"], r["seq"], r["ts"])),
    }
    hits, tested = [], 0
    for method in ("decimal_tail", "float64_lsb", "float32_lsb"):
        for order_name, rows in orders.items():
            source_bits = [bit_value(row, method) for row in rows]
            for reverse_rows in (False, True):
                bits = source_bits[::-1] if reverse_rows else source_bits
                for bit_order in ("msb", "lsb"):
                    candidate = pack_bits(bits, bit_order)
                    for masked in (False, True):
                        component = bytes(a ^ b for a, b in zip(candidate, mask)) if masked else candidate
                        tested += 1
                        if hashlib.sha256(component).hexdigest() == target:
                            hits.append({"method": method, "order": order_name,
                                         "reverse_rows": reverse_rows, "bit_order": bit_order,
                                         "masked": masked, "component": component.hex()})
    planted = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    planted_bits = [(byte >> (7-j)) & 1 for byte in planted for j in range(8)]
    assert pack_bits(planted_bits, "msb") == planted
    print(json.dumps({
        "source_sha256": PINS, "records_total": len(records),
        "excluded_k02_good_hold": len(excluded), "selected_records": len(selected),
        "selected_field_counts": {"PV": 112, "DIAG_WORD": 16},
        "candidate_checks": tested, "hits": hits,
        "synthetic_pack_control": "PASS",
        "interpretation": "bounded speculative cross-slot tail-bit test; no source-defined K04 rule",
    }, indent=2))

if __name__ == "__main__":
    main()
