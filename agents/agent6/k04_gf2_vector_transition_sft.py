#!/usr/bin/env python3
"""Test full 128-bit GF(2) homogeneous and arbitrary-affine payload transitions.

Run from the repository root:
    python agents/agent6/k04_gf2_vector_transition_sft.py

Training: 128 transitions from the 128 regular records to the next record,
which is the first late REQUESTED event. The selected PS-0417 attempt-2 ACK
and the remaining late events are held out.
"""
from __future__ import annotations

import random
import re
from pathlib import Path

WIDTH = 128
LOG = Path("resources/evidence/print/spool-reconstruction.log")


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

    if pivot_row != WIDTH:
        raise RuntimeError(f"training state matrix is rank {pivot_row}, not {WIDTH}")

    basis_outputs = [None] * WIDTH
    for x, y in rows:
        if x == 0 or x & (x - 1):
            raise RuntimeError("row reduction did not produce a standard basis")
        basis_outputs[x.bit_length() - 1] = y
    if any(value is None for value in basis_outputs):
        raise RuntimeError("incomplete output basis")
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


def build_coordinate_basis(states: list[bytes]):
    """Map each pivot state bit to the original-training-row coefficient mask."""
    basis = {}
    for index, state in enumerate(states):
        value = int.from_bytes(state, "big")
        coefficients = 1 << index
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                bv, bc = basis[pivot]
                value ^= bv
                coefficients ^= bc
            else:
                basis[pivot] = (value, coefficients)
                break
        if value == 0:
            raise RuntimeError("training input states are not linearly independent")
    if len(basis) != WIDTH:
        raise RuntimeError(f"coordinate basis rank is {len(basis)}, not {WIDTH}")
    return basis


def coordinates(state: bytes, basis) -> int:
    """Return unique alpha with state = XOR_i(alpha_i * training_state_i)."""
    value = int.from_bytes(state, "big")
    alpha = 0
    while value:
        pivot = value.bit_length() - 1
        if pivot not in basis:
            raise RuntimeError("query state is outside full-rank training span")
        bv, bc = basis[pivot]
        value ^= bv
        alpha ^= bc
    return alpha


def synthetic_check():
    """Positive control: recover a planted invertible 128-bit GF(2) map."""
    rng = random.Random(20261113)
    columns = []
    for j in range(WIDTH):
        column = 1 << j
        for i in range(j):
            if rng.getrandbits(1):
                column |= 1 << i
        columns.append(column)

    def apply(x: int) -> int:
        y = 0
        while x:
            bit = (x & -x).bit_length() - 1
            y ^= columns[bit]
            x &= x - 1
        return y

    training_states = [(1 << i).to_bytes(16, "big") for i in range(WIDTH)]
    training_outputs = [apply(1 << i).to_bytes(16, "big") for i in range(WIDTH)]
    basis = fit_transition(training_states, training_outputs)
    for _ in range(32):
        state = rng.getrandbits(WIDTH)
        predicted = predict(state.to_bytes(16, "big"), basis)
        if predicted != apply(state).to_bytes(16, "big"):
            raise RuntimeError("synthetic positive control failed")
    print("synthetic_positive_control=32/32")


def main():
    synthetic_check()
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
    output_basis = fit_transition(states, outputs)
    coordinate_basis = build_coordinate_basis(states)

    print("training_transitions=128")
    print("training_state_rank=128")

    # For every possible constant c, the unique affine fit is
    # F_c(x)=A_c*x XOR c = A_0*x XOR gamma(x)*c,
    # where gamma(x)=1 XOR parity(alpha(x)) and x=sum(alpha_i*x_i).
    # gamma=0 controls cannot be repaired by any affine offset.
    for label, index, expected_gamma in (
        ("selected_ACK2", 128, 1),
        ("ESC_S_ACK", 130, 0),
        ("WATCH_SPARE_ACK", 131, 0),
    ):
        alpha = coordinates(rows[index]["payload"], coordinate_basis)
        gamma = 1 ^ (alpha.bit_count() & 1)
        if gamma != expected_gamma:
            raise RuntimeError(
                f"{label} affine coefficient {gamma}, expected {expected_gamma}"
            )
        predicted_a0 = predict(rows[index]["payload"], output_basis)
        actual = rows[index + 1]["payload"]
        residual = xor_bytes(predicted_a0, actual)
        print(
            f"{label}_affine_offset_coefficient={gamma} "
            f"A0_prediction={predicted_a0.hex().upper()} "
            f"actual={actual.hex().upper()} "
            f"residual={residual.hex().upper()}"
        )

    # Homogeneous one-step predictions for all four late records.
    for index in range(128, 132):
        predicted = predict(rows[index]["payload"], output_basis)
        actual = rows[index + 1]["payload"]
        print(
            f"late_row={index + 1} job={rows[index + 1]['job']} "
            f"predicted={predicted.hex().upper()} "
            f"actual={actual.hex().upper()} "
            f"match={predicted == actual}"
        )


if __name__ == "__main__":
    main()
