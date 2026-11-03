"""Conditional H-17 p951/CPython n613: ANY 128-bit withheld coupon is seed-reachable.

Construct actual 613-word Python integer seeds matching every intact original
printer record and independently prescribed selected 16-byte coupon. Source
row129 remains withheld throughout fitting. This is a generator-model
identifiability theorem, NOT recovery of historical K04.

Depends on Agent14's original-source exact n613 constructive SFT and Agent39
GF(2) solver. Usage:
    python agents/agent14/k04_p951_cpython613_arbitrary_coupon_sft.py
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import k04_p951_cpython_n613_constructive_sft as proof

gf = proof.gf
ORIGINAL_SHA = proof.prior.SOURCE_SHA
PROBES = (
    ("all_zero", bytes(16)),
    ("all_one", bytes.fromhex("FF" * 16)),
    ("copied_ack", bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")),
    ("low_one", bytes.fromhex("00000000000000000000000000000001")),
)


def full_project(equation: int, basis: dict[int, int]) -> int:
    """Project through EVERY source pivot, unlike insert-only gf.reduce()."""
    residue = 0
    while equation > 1:
        pivot = equation.bit_length() - 1
        row = basis.get(pivot)
        if row is None:
            residue ^= 1 << pivot
            equation ^= 1 << pivot
        else:
            equation ^= row
    return residue | equation


def quotient_rank(expressions: list, basis: dict[int, int], idx: int) -> int:
    """Dimension of the 32-bit word given ALL source constraints."""
    rows = {}
    for bit_equation in expressions[idx]:
        v = full_project(bit_equation << 1, basis) >> 1
        while v:
            p = v.bit_length() - 1
            if p not in rows:
                rows[p] = v
                break
            v ^= rows[p]
    return len(rows)


def prescribe_coupon(source_basis: dict, expressions: list, payload: bytes) -> dict:
    assert len(payload) == 16
    basis = source_basis.copy()
    added = 0
    for lane in range(4):
        native = gf.prior.untemper(
            int.from_bytes(payload[4*lane:4*lane+4], "little")
        )
        for bit, equation in enumerate(expressions[624 + 951 + lane]):
            reduced = gf.reduce(
                (equation << 1) | ((native >> bit) & 1), basis
            )
            assert reduced != 1, ("unexpected inconsistent coupon", lane, bit)
            if reduced > 1:
                basis[reduced.bit_length() - 1] = reduced
                added += 1
    assert added == 128
    return basis


def main() -> None:
    proof.planted_controls()  # Eight genuine 613-word reverse-seed positives.
    values, masks, original, expressions = proof.prior.source_constraints()
    assert len(original) == 15397

    # Branch1 was found WITHOUT reading selected ACK or commitment. All its
    # repeated-key nonlinear initialization checks hold exactly.
    branch, s7, s623, s1, s612 = proof.BRANCHES[0]
    assert branch == 1
    state = values.copy()
    state[7], state[623] = s7, s623
    late = proof.wrap.invert_repeat(613, state)
    fixed = proof.make_late_words(state, late, s1)
    assert fixed[612] == s612
    source = proof.add_source_constraints(original, expressions, fixed)
    assert len(source) == 15718

    # Every 128-bit coupon vector is independent of the fixed original
    # generator/seed-wrap equations. Its 128-bit RHS can be prescribed freely.
    assert quotient_rank(expressions, source, 611) == 31
    root = proof.prior.ROOT
    spool = (root / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == ORIGINAL_SHA
    packets = [
        bytes.fromhex(x.decode())
        for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)
    ]
    assert len(packets) == 133

    for label, coupon in PROBES:
        basis = prescribe_coupon(source, expressions, coupon)
        assert len(basis) == 15846
        assert quotient_rank(expressions, basis, 611) == 31
        register = proof.solve_full_register(basis, 21412)
        assert all(register[i] == word for i, word in fixed.items())
        seed = proof.reverse_seed(register)
        selected = proof.verify_printer(seed, packets)
        assert selected == coupon
        print(
            "PASS", label, "selected", coupon.hex().upper(),
            "rank", len(basis), "S611_remaining_dimensions", 31,
            "seed_length_words", (seed.bit_length() + 31) // 32
        )

    print(
        "THEOREM: 128 independent coupon equations leave 31 free S611 "
        "dimensions. Key[612] is an injective function of S611 under "
        "both CPython rounds; at most one of its 2^31 values is zero. "
        "Therefore EVERY specified 128-bit coupon admits an exact "
        "613-word integer seed reproducing all 132 intact printer rows."
    )
    print("Historical K04 and K08 remain unverified; no slot PASS claimed")


if __name__ == "__main__":
    main()
