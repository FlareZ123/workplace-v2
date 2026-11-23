#!/usr/bin/env python3
"""Leave-one-packet-out linear observability of the frozen all-42 MT schedule.

The selected row129 PAYLOAD is excluded before hex decoding. This measures
whether the frozen chronology predicts any intact 16-byte packet from the
other intact packets; it does not search the K04 commitment.
"""
from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent11"))
import k04_all42_fullsource_alternative_sft as model

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STAGES = model.STAGES
STAGES_SHA = "3c1f05604c059c6d23f361d45af5acb8f02b87f64bfb295d28ea016967e752dd"
assert hashlib.sha256(repr(STAGES).encode()).hexdigest() == STAGES_SHA


def reduce_form(form: int, rhs: int, basis: dict[int, tuple[int, int]]) -> tuple[int, int]:
    v = form
    while v:
        pivot = v.bit_length() - 1
        if pivot not in basis:
            break
        old, old_rhs = basis[pivot]
        v ^= old
        rhs ^= old_rhs
    return v, rhs


def build_basis(native, words, exclude_row=None):
    basis: dict[int, tuple[int, int]] = {}
    rank = 0
    for row, packet in enumerate(native):
        if packet is None or row == exclude_row:
            continue
        for lane, value in enumerate(packet):
            for bit, form in enumerate(words[STAGES[row] + lane]):
                v, rhs = reduce_form(form, (value >> bit) & 1, basis)
                if v:
                    basis[v.bit_length() - 1] = (v, rhs)
                    rank += 1
                elif rhs:
                    raise AssertionError(("inconsistent source", row, lane, bit))
    return basis, rank


def witness_rows(native):
    inverse = {}
    for row, packet in enumerate(native):
        if packet is None:
            continue
        for lane, value in enumerate(packet):
            inverse.setdefault(value, []).append((row, lane))
    full, partial = [], []
    for r, packet in enumerate(native):
        if packet is None:
            continue
        for k in range(r + 1, len(native)):
            if native[k] is None:
                continue
            for i, value in enumerate(native[k]):
                for p in (1, 2, 3):
                    for l, q in inverse.get(value ^ model.twist(packet[p - 1], packet[p]), ()):
                        if l > k:
                            assert STAGES[k] - STAGES[r] == 396 + p - i
                            assert STAGES[l] - STAGES[r] == 623 + p - q
                            full.append((r, k, l, p, i, q))
                for upper in (0, 0x80000000):
                    for l, q in inverse.get(value ^ model.twist(upper, packet[0]), ()):
                        if l > k:
                            assert STAGES[k] - STAGES[r] == 396 - i
                            assert STAGES[l] - STAGES[r] == 623 - q
                            partial.append((r, k, l, i, q, upper))
    return full, partial


def project_packet(row, basis, words, native):
    fixed_bits = 0
    unfixed_positions = 0
    free_rank = 0
    target_basis = dict(basis)
    fixed_values_match = True
    for lane, actual in enumerate(native[row]):
        for bit, form in enumerate(words[STAGES[row] + lane]):
            v, rhs = reduce_form(form, 0, basis)
            if not v:
                fixed_bits += 1
                if rhs != ((actual >> bit) & 1):
                    fixed_values_match = False
                continue
            unfixed_positions += 1
            v, _ = reduce_form(form, 0, target_basis)
            if v:
                target_basis[v.bit_length() - 1] = (v, 0)
                free_rank += 1
    return fixed_bits, unfixed_positions, free_rank, fixed_values_match


def project_target(words, basis):
    fixed = free = 0
    target_basis = dict(basis)
    for lane in range(4):
        for form in words[STAGES[129] + lane]:
            v, _ = reduce_form(form, 0, basis)
            if v:
                v, _ = reduce_form(form, 0, target_basis)
                if v:
                    target_basis[v.bit_length() - 1] = (v, 0)
                    free += 1
            else:
                fixed += 1
    return fixed, free


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "resources"
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw, re.M,
    )
    assert len(rows) == len(STAGES) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    # Exclude selected row129 before decoding its disputed PAYLOAD.
    native = [None if r == 129 else [
        model.untemper(int.from_bytes(bytes.fromhex(row[5].decode())[i:i+4], "little"))
        for i in range(0, 16, 4)
    ] for r, row in enumerate(rows)]
    assert native[129] is None

    words = model.symbolic_words(STAGES[-1] + 4)
    full, partial = witness_rows(native)
    assert (len(full), len(partial)) == (25, 17)
    used = {row for witness in full + partial for row in witness[:3]}
    unreferenced = [r for r in range(133) if r != 129 and r not in used]
    assert len(unreferenced) == 66

    full_basis, full_rank = build_basis(native, words)
    assert full_rank == 15434
    target_fixed, target_free = project_target(words, full_basis)
    assert (target_fixed, target_free) == (96, 32)

    free_rank_distribution = Counter()
    unfixed_position_distribution = Counter()
    unreferenced_distribution = Counter()
    max_fixed = 0
    max_rows = []
    full_packet_predictions = 0
    fixed_mismatch_rows = []
    for row in range(133):
        if row == 129:
            continue
        basis, _ = build_basis(native, words, exclude_row=row)
        fixed, unfixed, free_rank, matches = project_packet(row, basis, words, native)
        if not matches:
            fixed_mismatch_rows.append(row)
        free_rank_distribution[free_rank] += 1
        unfixed_position_distribution[unfixed] += 1
        if free_rank == 0:
            full_packet_predictions += 1
        if fixed > max_fixed:
            max_fixed, max_rows = fixed, [row]
        elif fixed == max_fixed:
            max_rows.append(row)
        if row in unreferenced:
            unreferenced_distribution[free_rank] += 1

    assert not fixed_mismatch_rows
    assert full_packet_predictions == 0
    assert max_fixed == 127 and sorted(max_rows) == [12, 41, 66, 95, 125]
    assert unreferenced_distribution == Counter({128: 54, 127: 12})
    assert free_rank_distribution == Counter({
        1: 5, 32: 2, 33: 10, 63: 6, 64: 6, 65: 18,
        95: 3, 96: 3, 97: 13, 127: 12, 128: 54,
    })
    assert unfixed_position_distribution == free_rank_distribution

    print("SOURCE_SHA256", SOURCE_SHA)
    print("FROZEN_STAGE_VECTOR", len(STAGES), "rows; selected row129 withheld")
    print("WITNESSES", len(full), "fullword +", len(partial), "firstword")
    print("WITNESS_UNREFERENCED_ROWS", len(unreferenced))
    print("FULL_SOURCE_RANK", full_rank)
    print("LOO_FREE_RANK_DISTRIBUTION", dict(sorted(free_rank_distribution.items())))
    print("LOO_FULL_128BIT_PACKET_PREDICTIONS", full_packet_predictions, "/ 132")
    print("LOO_MAX_FIXED_BITS", max_fixed, "rows", sorted(max_rows))
    print("UNREFERENCED_LOO_FREE_RANK", dict(sorted(unreferenced_distribution.items())))
    print("UNREFERENCED_TOTAL_FIXED_BITS", sum((128 - rank) * count for rank, count in unreferenced_distribution.items()))
    print("TARGET_STAGE952_PROJECTION", target_fixed, "fixed /", target_free, "free")
    print("FIXED_BIT_SOURCE_MISMATCHES", len(fixed_mismatch_rows))
    print("K04_MASK_OR_ACCEPTANCE_LOADED", "NO")


if __name__ == "__main__":
    main()
