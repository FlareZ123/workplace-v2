"""Synthetic mechanics test for the eight-word p951 K04 recovery function.

Run from any directory:
    python agents/agent12/test_k04_p951_gap_word_recovery.py

The generated target is synthetic and is not an archive value. This test checks
only that eight consistent gap observations reconstruct the same target payload.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.agent49.k04_p951_symbolic_basis import ORIGIN, source, temper
from agents.agent12.k04_p951_gap_word_recovery import (
    GAP43_STAGES,
    GAP96_STAGES,
    recover_k04,
)


def consistent_assignment(basis) -> int:
    """Choose one state assignment by setting all free variables to zero."""
    assignment = 0
    for pivot in sorted(basis.rows):
        vector, observed = basis.rows[pivot]
        bit = observed ^ ((vector & assignment).bit_count() & 1)
        assignment |= bit << pivot
    return assignment


def output_word(state, stage: int, assignment: int) -> int:
    return sum(
        ((form & assignment).bit_count() & 1) << bit
        for bit, form in enumerate(temper(state[stage - ORIGIN]))
    )


def main() -> None:
    basis, state = source(REPO_ROOT)
    assignment = consistent_assignment(basis)

    gap43 = [output_word(state, stage, assignment) for stage in GAP43_STAGES]
    gap96 = [output_word(state, stage, assignment) for stage in GAP96_STAGES]
    expected_payload = b"".join(
        output_word(state, stage, assignment).to_bytes(4, "little")
        for stage in range(951, 955)
    )

    result = recover_k04(gap43, gap96)
    actual_payload = bytes.fromhex(str(result["coupon_payload"]))
    if actual_payload != expected_payload:
        raise AssertionError(
            f"recovered {actual_payload.hex().upper()}, expected {expected_payload.hex().upper()}"
        )

    print("Synthetic p951 recovery mechanics: PASS")
    print("Gap43 words:", " ".join(f"{word:08X}" for word in gap43))
    print("Gap96 words:", " ".join(f"{word:08X}" for word in gap96))
    print("Synthetic target:", expected_payload.hex().upper())
    print("K04 commitment match:", result["matches"])
    print("The synthetic target is not a recovered archive value.")


if __name__ == "__main__":
    main()
