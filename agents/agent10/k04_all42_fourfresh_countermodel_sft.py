#!/usr/bin/env python3
"""Exact original-source 4-fresh-output MT chronology with 128-bit target ambiguity.

Use: python agents/agent10/k04_all42_fourfresh_countermodel_sft.py [resources-directory]
Read-only; the selected PS-0417 ACK2 copied PAYLOAD is never decoded.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from k04_all42_wholewindow_sft import (
    ALT_STAGES, SPOOL_SHA, build_basis, project, symbolic_words, temper, untemper
)

# Integer-gap delta from the previously published all42 complete-source chronology.
# The 84 stage graph equations remain exactly satisfied. A source-independent
# minimum-L1 integer schedule search first discovered this 4-fresh assignment.
GAP_DELTAS = {12: 2, 25: -2, 43: 2, 47: -2, 66: 2,
              79: -2, 96: 2, 109: -2, 128: 3, 129: -1}


def full_state(basis: dict[int, tuple[int, int]], free_values: int = 0) -> int:
    """Reconstruct all 19,968 initial-state bits, fixing unobserved bits."""
    state = free_values
    for pivot in sorted(basis):
        form, rhs = basis[pivot]
        bit = rhs ^ ((state & (form ^ (1 << pivot))).bit_count() & 1)
        state |= bit << pivot
    return state


def native_word(state: int, expressions: list[int]) -> int:
    return sum(((state & form).bit_count() & 1) << bit
               for bit, form in enumerate(expressions))


def packet(state: int, expressions: list[list[int]], phase: int) -> bytes:
    return b"".join(
        temper(native_word(state, expressions[phase + lane])).to_bytes(4, "little")
        for lane in range(4)
    )


def quotient_rank(forms: list[int]) -> int:
    basis = {}
    for form in forms:
        while form:
            pivot = form.bit_length() - 1
            if pivot in basis:
                form ^= basis[pivot]
            else:
                basis[pivot] = form
                break
    return len(basis)


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "resources"
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw, re.M,
    )
    assert len(rows) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    native = [
        None if i == 129 else tuple(
            untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4*j:4*j+4], "little"))
            for j in range(4)
        )
        for i, row in enumerate(rows)
    ]
    gaps = [b - a for a, b in zip(ALT_STAGES, ALT_STAGES[1:])]
    for index, delta in GAP_DELTAS.items():
        gaps[index] += delta
    assert min(gaps) >= 4 and max(gaps) <= 16
    assert sum(abs(v) for v in GAP_DELTAS.values()) == 20
    stages = [0]
    for gap in gaps:
        stages.append(stages[-1] + gap)
    assert stages[126:133] == [940, 947, 951, 955, 959, 963, 968]

    expressions = symbolic_words(0, max(stages) + 4)
    original_basis = build_basis(native, tuple(stages), expressions, 0)
    assert len(original_basis) == 15434
    origin_state = full_state(original_basis)
    selected = stages[129]
    residual = [project(form, original_basis)[0]
                for phase in range(selected, selected + 4)
                for form in expressions[phase]]
    assert quotient_rank(residual) == 128
    pivot = next(value.bit_length() - 1 for value in residual if value)
    assert pivot not in original_basis
    second_state = full_state(original_basis, 1 << pivot)

    for state in (origin_state, second_state):
        for i, original in enumerate(native):
            if original is None:
                continue
            for lane, stored_native in enumerate(original):
                assert native_word(state, expressions[stages[i] + lane]) == stored_native

    first = packet(origin_state, expressions, selected)
    second = packet(second_state, expressions, selected)
    assert first == bytes(16)
    assert second.hex().upper() == "91004000000000000000000000000000"
    assert first != second
    assert packet(origin_state, expressions, stages[128]) == bytes.fromhex(rows[128][5].decode())
    assert packet(second_state, expressions, stages[130]) == bytes.fromhex(rows[130][5].decode())
    print(json.dumps({
        "selected_payload_loaded": False,
        "all_historical_gap_counts_at_least_four": True,
        "original_source_consistent": True,
        "source_rank": len(original_basis),
        "full_original_native_words_reproduced_per_state": 528,
        "independent_source_consistent_full_states": 2,
        "selected_stage": selected,
        "selected_rank_remaining": quotient_rank(residual),
        "source_consistent_coupon_A": first.hex().upper(),
        "source_consistent_coupon_B": second.hex().upper(),
        "gaps_changed": GAP_DELTAS,
        "actual_k04_recovered": False
    }, indent=2))


if __name__ == "__main__":
    main()
