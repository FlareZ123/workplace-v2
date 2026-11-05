"""K04 XORWOW packet source: 1..4 additional hidden draws, arbitrary Weyl.

Run: python agents/agent3/k04_xorwow_four_extra_gap_sft.py
Imports deterministic pure GF2 source primitive in same agent directory.
Original selected 18:02 copied ACK excluded from fit; no evidence mutation.
"""
from itertools import product
import hashlib
from k04_xorwow_gap_weyl_sft import (
    MASK32, LAYOUTS, component, decode, encode,
    original_inputs, parity, xorwow_step,
)

MAX_STAGE = 16
WORDS = 32


def symbolic_rows():
    """Linear map for up to sixteen native XORWOW generator outputs."""
    rows = [0] * (MAX_STAGE * WORDS)
    for bit_index in range(160):
        state = tuple(
            1 << (bit_index % 32) if lane == bit_index // 32 else 0
            for lane in range(5)
        )
        for stage in range(MAX_STAGE):
            state, native = xorwow_step(state)
            for bit in range(WORDS):
                if native >> bit & 1:
                    rows[stage * WORDS + bit] |= 1 << bit_index
    return rows


def derive(rows, gap):
    stamps = (0, 1, 2, 3, 8 + gap, 9 + gap, 10 + gap, 11 + gap)
    pivot = {}
    checks = []
    for observed_idx, stage in enumerate(stamps):
        for bit in range(32):
            vector = rows[stage * 32 + bit]
            relation = 1 << (observed_idx * 32 + bit)
            while vector:
                p = vector.bit_length() - 1
                if p not in pivot:
                    pivot[p] = (vector, relation)
                    break
                a, b = pivot[p]
                vector ^= a
                relation ^= b
            if not vector:
                checks.append(relation)

    assert len(pivot) == 160 and len(checks) == 96, (gap, len(pivot), len(checks))

    def projection(vec):
        relation = 0
        while vec:
            p = vec.bit_length() - 1
            assert p in pivot, "Cannot reconstruct target from intact sources"
            a, b = pivot[p]
            vec ^= a
            relation ^= b
        return relation

    missing = [
        projection(rows[stage * 32 + bit])
        for stage in range(4, 8)
        for bit in range(32)
    ]
    return stamps, checks, missing


def lift(observed, stages, checks):
    grouped = [[] for _ in range(32)]
    for equation in checks:
        highest = max(index % 32 for index in range(256) if equation >> index & 1)
        grouped[highest].append(equation)
    possible = [(0, 0)]
    depth = 0
    for bit in range(32):
        next_states = []
        bit_value = 1 << bit
        for d0, step in possible:
            for add_d, add_step in product((0, bit_value), repeat=2):
                x, y = d0 | add_d, step | add_step
                native = [
                    (word - x - y * stage) & MASK32
                    for word, stage in zip(observed, stages)
                ]
                if all(parity(equation, native) == 0 for equation in grouped[bit]):
                    next_states.append((x, y))
        possible = next_states
        depth = bit
        if not possible:
            break
    return possible, depth


def recover(observed, stages, projections, d0, step):
    native = [
        (word - d0 - step * stage) & MASK32
        for word, stage in zip(observed, stages)
    ]
    return [
        (
            sum(
                parity(projections[word * 32 + bit], native) << bit
                for bit in range(32)
            ) + d0 + step * (word + 4)
        ) & MASK32
        for word in range(4)
    ]


def main():
    left, right, mask, original_target = original_inputs()
    rows = symbolic_rows()
    seed = (0x12345678, 0xABCDEF19, 0xDEADBEEF, 0xCAFEBABE, 0x875B29D4)
    step = 0xA5A5BEEF
    d0 = 0x00ABCDEF
    synthetic_controls = 0
    excluded = 0
    for gap in range(1, 5):
        stages, equations, projections = derive(rows, gap)
        state = seed
        full_sequence = []
        for t in range(12 + gap):
            state, native = xorwow_step(state)
            full_sequence.append((native + d0 + step * t) & MASK32)

        for layout in LAYOUTS:
            planted_before = encode(full_sequence[:4], *layout)
            planted_after = encode(full_sequence[8+gap:12+gap], *layout)
            planted = decode(planted_before, *layout) + decode(planted_after, *layout)
            recovered, depth = lift(planted, stages, equations)
            assert recovered == [(d0, step)], (gap, layout, recovered)
            coupon = encode(recover(planted, stages, projections, d0, step), *layout)
            expected = encode(full_sequence[4:8], *layout)
            assert coupon == expected
            expected_hash = hashlib.sha256(component(expected, mask)).digest()
            assert hashlib.sha256(component(coupon, mask)).digest() == expected_hash
            synthetic_controls += 1

            observed = decode(left, *layout) + decode(right, *layout)
            roots, depth = lift(observed, stages, equations)
            assert not roots, (gap, layout, roots)
            print("ORIGINAL_SOURCE_EXCLUDED", "gap", gap, "layout", layout,
                  "bit", depth, "all 2**64 Weyl parameter pairs")
            excluded += 1

    assert synthetic_controls == 32 and excluded == 32
    print("PASS: 32 whole-coupon planted positives, 32 original models exactly"
          " excluded, no original source or verifier mutations, K04 unresolved")


if __name__ == "__main__":
    main()
