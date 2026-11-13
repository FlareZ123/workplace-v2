#!/usr/bin/env python3
"""Test 128-bit GF(2) linear and source-offset affine transitions in printer payloads.

Run from the repository root:
    python agents/agent6/k04_gf2_vector_transition_sft.py

Training: 128 transitions from the 128 regular records to the next record,
which is the first late REQUESTED event. The selected PS-0417 attempt-2 ACK
and the remaining late events are held out.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

WIDTH = 128
LOG = Path("resources/evidence/print/spool-reconstruction.log")
ROUTE = Path("resources/evidence/recovery-routing.json")
CANDIDATE = Path("candidate.json")


def parse_rows():
    rows = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        job = re.search(r"JOB=PS-261003-(\d{4})", line)
        payload = re.search(r"PAYLOAD=([0-9A-Fa-f]{32})", line)
        if job and payload:
            rows.append({
                "job": job.group(1),
                "payload": bytes.fromhex(payload.group(1)),
                "line": line,
            })
    return rows


def fit_transition(states: list[bytes], outputs: list[bytes]):
    """Solve y=A*x over GF(2), row-reducing [X|Y] together."""
    rows = [
        (int.from_bytes(x, "big"), int.from_bytes(y, "big"))
        for x, y in zip(states, outputs, strict=True)
    ]
    pivot_row = 0
    for col in range(WIDTH):
        pivot = next(
            (i for i in range(pivot_row, len(rows))
             if (rows[i][0] >> col) & 1),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        px, py = rows[pivot_row]
        for i in range(len(rows)):
            if i != pivot_row and ((rows[i][0] >> col) & 1):
                rx, ry = rows[i]
                rows[i] = (rx ^ px, ry ^ py)
        pivot_row += 1
        if pivot_row == len(rows):
            break

    rank = pivot_row
    if rank != WIDTH:
        raise RuntimeError(f"training state matrix is rank {rank}, not {WIDTH}")

    basis_outputs = [None] * WIDTH
    for x, y in rows:
        if x == 0 or x & (x - 1):
            raise RuntimeError("row reduction did not produce a standard basis")
        basis_outputs[x.bit_length() - 1] = y
    if any(value is None for value in basis_outputs):
        raise RuntimeError("incomplete basis")
    return basis_outputs


def predict(state: bytes, basis_outputs: list[int]) -> bytes:
    x = int.from_bytes(state, "big")
    y = 0
    while x:
        bit = (x & -x).bit_length() - 1
        y ^= basis_outputs[bit]
        x &= x - 1
    return y.to_bytes(WIDTH // 8, "big")


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b, strict=True))


def main():
    rows = parse_rows()
    if len(rows) != 133:
        raise RuntimeError(f"expected 133 payload rows, found {len(rows)}")
    if not all("+00:00" in row["line"] for row in rows[:128]):
        raise RuntimeError("first 128 records are not the expected regular block")
    if "18:01:00Z" not in rows[128]["line"]:
        raise RuntimeError("row 128 is not the first late REQUESTED event")
    if "18:02:00Z" not in rows[129]["line"]:
        raise RuntimeError("row 129 is not the selected PS-0417 attempt-2 ACK")

    states = [row["payload"] for row in rows[:128]]
    outputs = [row["payload"] for row in rows[1:129]]
    actual = rows[129]["payload"]

    # Homogeneous map: x[n+1] = A*x[n].
    basis = fit_transition(states, outputs)
    print("training_transitions=128")
    print("training_state_rank=128")
    predicted = predict(rows[128]["payload"], basis)
    print(
        f"homogeneous_target_predicted={predicted.hex().upper()} "
        f"actual={actual.hex().upper()} match={predicted == actual}"
    )

    # Affine maps with a fixed, source-supplied XOR offset:
    # x[n+1] = A*x[n] XOR c. The offset is removed from each training output,
    # then restored to the held-out prediction.
    route = json.loads(ROUTE.read_text(encoding="utf-8"))
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    offsets = {
        "K04_mask": bytes.fromhex(route["K04"]["masked_component"]),
        "K08_desk_nonce": bytes.fromhex(route["K08"]["desk_nonce"]),
    }
    for key in ("K01", "K02", "K03", "K05", "K06", "K07"):
        if candidate.get(key):
            offsets[key] = bytes.fromhex(candidate[key])

    for label, offset in offsets.items():
        transformed = [xor_bytes(y, offset) for y in outputs]
        affine_basis = fit_transition(states, transformed)
        affine_prediction = xor_bytes(
            predict(rows[128]["payload"], affine_basis), offset
        )
        print(
            f"{label}_affine_target_predicted={affine_prediction.hex().upper()} "
            f"actual={actual.hex().upper()} "
            f"match={affine_prediction == actual}"
        )

    # One-step predictions for the remaining late records under the unique
    # homogeneous map, using each actual preceding state as input.
    for index in range(129, 132):
        predicted = predict(rows[index]["payload"], basis)
        next_actual = rows[index + 1]["payload"]
        print(
            f"late_row={index + 1} job={rows[index + 1]['job']} "
            f"predicted={predicted.hex().upper()} "
            f"actual={next_actual.hex().upper()} "
            f"match={predicted == next_actual}"
        )


if __name__ == "__main__":
    main()
