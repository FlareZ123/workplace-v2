"""H17 K04 source-only fiveword XORWOW + per-attempt xorshift32 XOR pad.

Original first REQUESTED and third REQUESTED are the source observations;
selected ACK2 18:02 copied value is excluded from inference.
Run: python agents/agent3/k04_xorwow_packet_xorshift_sft.py
"""
from hashlib import sha256
from k04_xorwow_gap_weyl_sft import (
    LAYOUTS, MASK32, component, decode, encode,
    original_inputs, xorwow_step,
)


def xorshift32(x):
    x ^= (x << 13) & MASK32
    x ^= x >> 17
    x ^= (x << 5) & MASK32
    return x & MASK32


def output_equations():
    """All 384 output bits as linear functions of 160+32 initial state bits."""
    coeff = [0] * (12 * 32)
    for unknown in range(192):
        state = tuple(
            1 << (unknown % 32) if lane == unknown // 32 else 0
            for lane in range(5)
        ) if unknown < 160 else (0, 0, 0, 0, 0)
        pad0 = 1 << (unknown - 160) if unknown >= 160 else 0
        pads = (pad0, xorshift32(pad0), xorshift32(xorshift32(pad0)))
        for stage in range(12):
            state, native = xorwow_step(state)
            value = native ^ pads[stage // 4]
            for bit in range(32):
                if value >> bit & 1:
                    coeff[stage * 32 + bit] |= 1 << unknown
    return coeff


def solve_source(equations, observed):
    """GF2 exact Gaussian elimination and conditional unique-state inversion."""
    bases = {}
    contradictions = 0
    for observation, stage in enumerate((0, 1, 2, 3, 8, 9, 10, 11)):
        for bit in range(32):
            vector = equations[stage * 32 + bit]
            rhs = (observed[observation] >> bit) & 1
            while vector:
                pivot = vector.bit_length() - 1
                if pivot not in bases:
                    bases[pivot] = (vector, rhs)
                    break
                a, b = bases[pivot]
                vector ^= a
                rhs ^= b
            if not vector and rhs:
                contradictions += 1

    assert len(bases) == 192
    if contradictions:
        return None, contradictions

    solution = 0
    for pivot in sorted(bases):
        vector, rhs = bases[pivot]
        value = rhs ^ ((solution & vector).bit_count() & 1)
        solution |= value << pivot
    return solution, 0


def reconstruct(equations, solution):
    return [
        sum(
            ((equations[stage * 32 + bit] & solution).bit_count() & 1) << bit
            for bit in range(32)
        )
        for stage in range(4, 8)
    ]


def main():
    equations = output_equations()
    first, last, mask, actual_target = original_inputs()
    seed = (0x12345678, 0xABCDEF19, 0xDEADBEEF, 0xCAFEBABE, 0x875B29D4)
    state = seed
    pad0 = 0xDEADBEEF
    pads = (pad0, xorshift32(pad0), xorshift32(xorshift32(pad0)))
    planted = []
    for step in range(12):
        state, native = xorwow_step(state)
        planted.append(native ^ pads[step // 4])

    expected_contradictions = (27, 30, 30, 29, 27, 30, 34, 28)
    planted_count = 0
    for layout, expected in zip(LAYOUTS, expected_contradictions):
        source = decode(first, *layout) + decode(last, *layout)
        reconstructed_state, contradictions = solve_source(equations, source)
        assert reconstructed_state is None and contradictions == expected
        print("ORIGINAL", layout, "exact_GF2_contradictions", contradictions)

        positive = decode(encode(planted[:4], *layout), *layout) + decode(
            encode(planted[8:], *layout), *layout
        )
        recovered_state, contradictions = solve_source(equations, positive)
        assert recovered_state is not None and contradictions == 0
        coupon = encode(reconstruct(equations, recovered_state), *layout)
        truth = encode(planted[4:8], *layout)
        assert coupon == truth
        planted_commitment = sha256(component(truth, mask)).digest()
        assert sha256(component(coupon, mask)).digest() == planted_commitment
        planted_count += 1

    assert planted_count == 8
    print("PASS eight genuine complete 16-byte synthetic coupon recoveries, "
          "eight 192-bit original-source full-state contradictions; "
          "original K04 remains missing")


if __name__ == "__main__":
    main()
