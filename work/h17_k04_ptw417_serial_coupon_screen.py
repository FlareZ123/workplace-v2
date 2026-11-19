#!/usr/bin/env python3
"""Exact PTW-417 serial-quartet-as-K04-coupon candidate check."""
import argparse
import hashlib
import itertools
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", default="resources/evidence")
    parser.add_argument("--acceptance", default="resources/acceptance.json")
    args = parser.parse_args()
    root = Path(args.evidence_root)

    mail4 = (root / "mail/04.eml").read_text(encoding="utf-8")
    match = re.search(
        r"witness walk\s+was\s+([A-D]),\s*([A-D]),\s*([A-D]),\s*([A-D])",
        mail4,
        re.I,
    )
    if not match:
        raise SystemExit("MAIL-04 witness-walk order not found")
    order = [value.upper() for value in match.groups()]

    rows = [
        json.loads(line)
        for line in (root / "maintenance/seal-receipts.jsonl")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ptw = [row for row in rows if row.get("permit") == "PTW-417"]
    by_bay = {}
    for bay in order:
        eligible = [
            row for row in ptw
            if row.get("bay") == bay
            and row.get("state") == "CLOSED"
            and row.get("fitment") == "AS_LEFT"
            and row.get("signed") is True
        ]
        by_bay[bay] = sorted(eligible, key=lambda row: int(row["revision"]))

    official = [by_bay[bay][-1]["serial"] for bay in order]
    options = []
    for index, bay in enumerate(order):
        if index % 2 == 0:
            low_revision = min(int(row["revision"]) for row in by_bay[bay])
            options.append([
                row["serial"] for row in by_bay[bay]
                if int(row["revision"]) == low_revision
            ])
        else:
            options.append([by_bay[bay][-1]["serial"]])
    alternates = [list(values) for values in itertools.product(*options)]

    routing = json.loads((root / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads(Path(args.acceptance).read_text(encoding="utf-8"))
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]

    candidates = [("official_highest_revision", official)]
    candidates += [
        (f"zero_based_low_if_even_{i}", serials)
        for i, serials in enumerate(alternates, start=1)
    ]
    results = []
    for label, serials in candidates:
        coupon = bytes.fromhex("".join(serial.split("-", 1)[1] for serial in serials))
        if len(coupon) != 16:
            raise SystemExit(f"{label}: serial block is not 16 bytes")
        component = bytes(a ^ b for a, b in zip(coupon, mask))
        digest = hashlib.sha256(component).hexdigest()
        results.append({
            "candidate": label,
            "serials": serials,
            "coupon_hex": coupon.hex().upper(),
            "component_coupon_xor_mask": component.hex().upper(),
            "sha256": digest,
            "matches_K04": digest == target,
        })

    print(json.dumps({
        "order_from_MAIL04": order,
        "mask": mask.hex().upper(),
        "target_K04_sha256": target,
        "tested_candidates": results,
        "candidate_count": len(results),
        "match_count": sum(result["matches_K04"] for result in results),
    }, indent=2))


if __name__ == "__main__":
    main()
