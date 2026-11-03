"""Exact PCG64 known-increment three-output inverse-CVP proof and 1000 controls.

Source-independent. Does not use the original selected printer ACK or K04 hash.
"""
from fractions import Fraction
from random import Random
from pcg64_two_low_sft import MASK64, MASK128, MULTIPLIER as A, sequence, xsl_rr

B = ((-1241281756092, 3827459685972, -728312298332),
     (-5001120657083, -2117155768935, 5479732607037),
     (8655886039732, 3303731088004, 6319848582548))
N = ((-1706733, -1441724, 1053384),
     (4284673, -83512, 566185),
     (97768, 2018292, 1180131))


def rol(x: int, n: int) -> int:
    return ((x << n) | (x >> ((64 - n) % 64))) & MASK64


def nearest(x: int) -> int:
    return (x + 2**63) // 2**64 if x >= 0 else -((-x + 2**63) // 2**64)


def recover(values: list[int], rotations: list[int], low_bits: int,
            increment: int, ell: int = 19) -> int | None:
    assert len(values) == len(rotations) == 3
    known = [low_bits, (A * low_bits + increment) & MASK128,
             (A * A * low_bits + (A + 1) * increment) & MASK128]
    t, shift = ell + 6, 58 - ell
    centers = []
    for value, r, k in zip(values, rotations, known):
        y = rol(value, r)
        observed = ((r ^ (y >> 58)) & 63) | (((y ^ k) & ((1 << ell) - 1)) << 6)
        difference = (observed - ((k >> 58) & ((1 << t) - 1))) & ((1 << t) - 1)
        centers.append((difference << shift) + (1 << (shift - 1)))
    coeff = [nearest(sum(centers[i] * N[i][j] for i in range(3))) for j in range(3)]
    u0 = sum(coeff[j] * B[j][0] for j in range(3)) & MASK64
    low = (known[0] + ((u0 & ((1 << (64 - ell)) - 1)) << ell)) & MASK64
    high = low ^ rol(values[0], rotations[0])
    if high >> 58 != rotations[0]:
        return None
    state = (high << 64) | low
    next_state = (A * state + increment) & MASK128
    if xsl_rr(next_state)[0] != values[1]:
        return None
    third_state = (A * next_state + increment) & MASK128
    if xsl_rr(third_state)[0] != values[2]:
        return None
    return state


def main() -> None:
    for i in range(3):
        for j in range(3):
            assert sum(B[i][k] * N[k][j] for k in range(3)) == (2**64 if i == j else 0)
    for ell in (19, 20):
        k = 58 - ell
        # A missed borrow changes the truncated high-bit coordinate by <=1.
        # Centering that coordinate leaves an error <= 1.5 * 2^k.
        errors = [Fraction(3 * 2**k * sum(abs(N[i][j]) for i in range(3)),
                           2 * 2**64) for j in range(3)]
        assert max(errors) < Fraction(1, 2)
        print(f"ell={ell} exact inverse-lattice rounding maxima: {list(map(float, errors))}")
    initial = 0x160AD84006FE21EAF69B873D9FE45409
    increment = 0x50C8FB163C7CEA4ED0F51CE6006E4325
    states = sequence(initial, increment, 3)
    values, rotations = zip(*(xsl_rr(s) for s in states))
    assert list(values) == [0xFA08FEF3FAB6BBBA, 0x615481F7FCE9AC81,
                            0xEC59DD7C2BDE3CB4]
    assert recover(list(values), list(rotations), states[0] & ((1 << 19) - 1), increment) == states[0]
    rng = Random(20261103)
    for _ in range(1000):
        seed = rng.getrandbits(128)
        inc = rng.getrandbits(128) | 1
        states = sequence(seed, inc, 3)
        vals, rots = zip(*(xsl_rr(s) for s in states))
        got = recover(list(vals), list(rots), states[0] & ((1 << 19) - 1), inc)
        assert got == states[0]
    print("PASS genuine NumPy PCG64 control; 1000 random 128bit states and odd increments")
    print("SCOPE: known increment plus true low19 and three rotations; no K04 source fit")


if __name__ == "__main__":
    main()
