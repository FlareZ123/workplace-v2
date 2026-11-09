"""H-17 K04: alternate 9-word ancestor donor path with complete seeded controls.

Original selected row129 is excluded from the printer source model.
No absent donor words, recovery key, or official acceptance value is invented.
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents/agent49'))
from k04_p951_symbolic_basis import Basis, LAST, ORIGIN, STARTS, get, source, untemper

EARLY = list(range(-296, -291)) + list(range(497, 501))
PRIMARY = list(range(328, 332)) + list(range(724, 728))


class Span:
    def __init__(self, base):
        self.pivots = {p: eq for p, (eq, _) in base.rows.items()}
        self.rank = len(self.pivots)

    def add(self, equation):
        while equation:
            p = equation.bit_length() - 1
            if p not in self.pivots:
                self.pivots[p] = equation
                self.rank += 1
                return
            equation ^= self.pivots[p]

    def remaining_target_rank(self, symbolic):
        augmented = Span.__new__(Span)
        augmented.pivots = self.pivots.copy()
        augmented.rank = self.rank
        for stage in range(951, 955):
            for eq in get(symbolic, stage):
                augmented.add(eq)
        return augmented.rank - self.rank


def oracle_rank(base, symbolic, stages):
    augmented = Span(base)
    for stage in stages:
        for equation in get(symbolic, stage):
            augmented.add(equation)
    return augmented.rank - base.rank, augmented.remaining_target_rank(symbolic)


def temper_native(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    return (x ^ (x >> 18)) & 0xffffffff


def synthetic_whole_coupon(symbolic, seed):
    rng = random.Random(seed)
    raw_output = [rng.getrandbits(32) for _ in range(LAST - ORIGIN + 1)]
    native = [untemper(value) for value in raw_output]
    fitted = Basis()

    for row, stage in enumerate(STARTS):
        if row == 129:
            continue
        for lane in range(4):
            value = native[stage + lane - ORIGIN]
            for bit, equation in enumerate(get(symbolic, stage + lane)):
                fitted.insert(equation, (value >> bit) & 1)
    assert fitted.rank == 15365

    for stage in EARLY:
        value = native[stage - ORIGIN]
        for bit, equation in enumerate(get(symbolic, stage)):
            fitted.insert(equation, (value >> bit) & 1)
    assert fitted.rank == 15653

    recovered = []
    for stage in range(951, 955):
        value = 0
        for bit, equation in enumerate(get(symbolic, stage)):
            fixed = fitted.predict(equation)
            assert fixed is not None
            value |= fixed << bit
        recovered.append(temper_native(value))
    assert recovered == raw_output[951-ORIGIN:955-ORIGIN]
    return b''.join(value.to_bytes(4, 'little') for value in recovered)


def main():
    base, symbolic = source(ROOT / 'resources')
    assert base.rank == 15365
    assert oracle_rank(base, symbolic, []) == (0, 128)
    assert oracle_rank(base, symbolic, PRIMARY) == (256, 0)
    assert oracle_rank(base, symbolic, EARLY) == (288, 0)

    leave_one_out = {
        stage: oracle_rank(base, symbolic, [x for x in EARLY if x != stage])[1]
        for stage in EARLY
    }
    expected = dict(zip(EARLY, (2, 32, 32, 32, 30, 32, 32, 32, 32)))
    assert leave_one_out == expected, (leave_one_out, expected)

    for seed in (0, 12345, 0x12345678, 20261109):
        coupon = synthetic_whole_coupon(symbolic, seed)
        assert len(coupon) == 16
        print('SYNTHETIC complete withheld coupon recovered, seed', seed, coupon.hex().upper())

    print('ORIGINAL source rank', base.rank)
    print('ORIGINAL alternate native donor stages', EARLY)
    print('ORIGINAL hypothetical +288 word-bits => target quotient 0')
    print('ORIGINAL leave-one-donor-out remaining target bits', leave_one_out)
    print('No original donor values at these stages, no K04/K08 accepted component')


if __name__ == '__main__':
    main()
