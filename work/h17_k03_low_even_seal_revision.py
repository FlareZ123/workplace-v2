#!/usr/bin/env python3
"""Test the source-ordered LOW-IF-EVEN side-channel on PTW-417 seal revisions."""
import argparse
import json
import re
from itertools import product
from pathlib import Path


def pack_lsb(serials):
    bits = []
    for serial in serials:
        match = re.fullmatch(r"SG-([0-9A-F]{8})", serial)
        if not match:
            raise ValueError(f"unexpected serial: {serial}")
        bits.append(int(match.group(1), 16) & 1)
    return sum(bit << i for i, bit in enumerate(bits)), bits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", default="resources/evidence")
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
        eligible = sorted(eligible, key=lambda row: int(row["revision"]))
        revisions = [int(row["revision"]) for row in eligible]
        expected = [1, 1, 2] if bay == "A" else [1, 2]
        if revisions != expected:
            raise SystemExit(
                f"expected signed CLOSED AS_LEFT revisions {expected} for {bay}, got {revisions}"
            )
        by_bay[bay] = eligible

    official = [by_bay[bay][-1]["serial"] for bay in order]

    # LOW IF EVEN: use the lower revision at zero-based even positions and
    # the higher revision at odd positions. Retain both A/rev1 source rows.
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
    zero_based_candidates = [list(values) for values in product(*options)]

    # One-based parity is reported only as a sensitivity control.
    one_based = [
        (by_bay[bay][0] if (index + 1) % 2 == 0 else by_bay[bay][-1])["serial"]
        for index, bay in enumerate(order)
    ]

    outputs = {}
    cases = [("official_highest_revision", official)]
    cases += [
        (f"zero_based_low_if_even_candidate_{i}", values)
        for i, values in enumerate(zero_based_candidates, start=1)
    ]
    cases.append(("one_based_sensitivity_control", one_based))
    for label, serials in cases:
        value, bits = pack_lsb(serials)
        outputs[label] = {
            "serials": serials,
            "lsb_bits_in_source_order": bits,
            "packed_integer_first_bit_lsb": value,
            "hex": f"{value:02X}",
        }

    print(json.dumps({
        "permit": "PTW-417",
        "order_from_MAIL04": order,
        "filter": "signed CLOSED AS_LEFT records; retain duplicate A/rev1 row and enumerate alternatives",
        "per_bay_revisions": {
            bay: [
                {"revision": int(row["revision"]), "serial": row["serial"]}
                for row in by_bay[bay]
            ]
            for bay in order
        },
        "outputs": outputs,
    }, indent=2))


if __name__ == "__main__":
    main()
