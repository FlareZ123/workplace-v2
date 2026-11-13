#!/usr/bin/env python3
"""Test an affine GF(2) emitter from recorded printer metadata to 16-byte payloads.

Run from the repository root:
    python agents/agent6/k04_metadata_gf2_linear_emitter_sft.py

Features: 10-bit job suffix, 11-bit minute-of-day, one-hot CLASS/DEST
contrasts, and an affine bias. ATTEMPT and STATE are constant in the 128-row
regular training block and therefore cannot identify a target-attempt effect.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

LOG = Path("resources/evidence/print/spool-reconstruction.log")
MIDNIGHT = datetime(2026, 10, 3, tzinfo=timezone.utc)


def parse_rows():
    rows = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        job = re.search(r"JOB=PS-261003-(\d{4})", line)
        payload = re.search(r"PAYLOAD=([0-9A-Fa-f]{32})", line)
        if not job or not payload:
            continue
        fields = {}
        for item in line.split()[1:]:
            if "=" in item:
                key, value = item.split("=", 1)
                fields[key] = value
        timestamp = line.split()[0].replace("Z", "+00:00")
        dt = datetime.fromisoformat(timestamp)
        rows.append({
            "jobnum": int(job.group(1)),
            "minutes": int((dt - MIDNIGHT).total_seconds() // 60),
            "class": fields["CLASS"],
            "dest": fields["DEST"],
            "attempt": fields["ATTEMPT"],
            "state": fields["STATE"],
            "payload": bytes.fromhex(payload.group(1)),
            "line": line,
        })
    return rows


def feature(row):
    # LABEL and bench are baselines; RECOVER/STORES and desk/store are contrasts.
    value = row["jobnum"]
    value |= row["minutes"] << 10
    value |= int(row["class"] == "RECOVER") << 21
    value |= int(row["class"] == "STORES") << 22
    value |= int(row["dest"] == "desk") << 23
    value |= int(row["dest"] == "store") << 24
    value |= 1 << 25  # affine bias
    return value


def fit(rows):
    # Row-echelon basis of (feature vector, 128-bit output) equations.
    basis = {}
    inconsistent = []
    for index, row in enumerate(rows):
        f = feature(row)
        y = int.from_bytes(row["payload"], "big")
        while f:
            pivot = f.bit_length() - 1
            if pivot in basis:
                bf, by = basis[pivot]
                f ^= bf
                y ^= by
            else:
                basis[pivot] = (f, y)
                break
        if f == 0 and y != 0:
            inconsistent.append(index)
    return basis, inconsistent


def predict(row, basis):
    f = feature(row)
    y = 0
    while f:
        pivot = f.bit_length() - 1
        if pivot not in basis:
            return None
        bf, by = basis[pivot]
        f ^= bf
        y ^= by
    return y.to_bytes(16, "big")


def main():
    rows = parse_rows()
    if len(rows) != 133:
        raise RuntimeError(f"expected 133 payload rows, found {len(rows)}")
    regular = rows[:128]
    late = rows[128:]
    if not all(row["attempt"] == "1" and row["state"] == "ACK" for row in regular):
        raise RuntimeError("regular training block is not all attempt-1 ACK")
    if late[1]["jobnum"] != 417 or late[1]["attempt"] != "2" or late[1]["state"] != "ACK":
        raise RuntimeError("late row 1 is not the selected PS-0417 attempt-2 ACK")

    for count in (64, 96, 128):
        basis, inconsistent = fit(regular[:count])
        print(
            f"train_rows={count} feature_rank={len(basis)} "
            f"inconsistent_rows={len(inconsistent)} "
            f"first_inconsistent_index={inconsistent[0] if inconsistent else 'none'}"
        )
        target = predict(late[1], basis)
        print(
            f"  target_feature_observable={target is not None} "
            f"target_prediction={target.hex().upper() if target else 'none'}"
        )


if __name__ == "__main__":
    main()
