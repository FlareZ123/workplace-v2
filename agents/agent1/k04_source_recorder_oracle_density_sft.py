"""Exact K04 coupon observability under hypothetical native recorder oracles.

Read-only source geometry. Synthetic/native stage oracles have no historical
word values and do not recover the original missing physical K04 coupon.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents/agent49'))
from k04_p951_symbolic_basis import source, get

ANCHORS = [-810, -793, -775, -769, -759, -683, -677, -568, -552,
           -545, -540, -417, -397, -390, -339]


class Span:
    def __init__(self, source_basis):
        self.pivots = {p: equation for p, (equation, _) in source_basis.rows.items()}
        self.rank = len(self.pivots)

    def add(self, equation):
        while equation:
            p = equation.bit_length() - 1
            if p not in self.pivots:
                self.pivots[p] = equation
                self.rank += 1
                return
            equation ^= self.pivots[p]

    def selected_unknown(self, symbolic):
        with_target = Span.__new__(Span)
        with_target.pivots = self.pivots.copy()
        with_target.rank = self.rank
        for stage in range(951, 955):
            for equation in get(symbolic, stage):
                with_target.add(equation)
        return with_target.rank - self.rank


def simulate_oracle(basis, symbolic, stages):
    augmented = Span(basis)
    for stage in stages:
        for equation in get(symbolic, stage):
            augmented.add(equation)
    return augmented.rank - basis.rank, augmented.selected_unknown(symbolic)


def main():
    b, symbolic = source(ROOT / 'resources')
    assert b.rank == 15365
    cases = {
        'source only': ([], (0, 128)),
        '15 matched node50 stages as fullword oracle': (ANCHORS, (10, 128)),
        '72 evenly spaced -860..-330 fullword oracles':
            ([round(-860 + 530 * i / 71) for i in range(72)], (954, 128)),
        '72 native 4-word blocks, seven-draw record stride':
            ([t + i for t in range(-860, -860 + 72 * 7, 7)
              for i in (-1, 0, 1, 2)], (3482, 124)),
        '531 consecutive native fullword oracles -860..-330':
            (list(range(-860, -329)), (4540, 0)),
        'alternative nine-word ancestral oracle':
            (list(range(-296, -291)) + list(range(497, 501)), (288, 0)),
        'original two-gap 8-word native oracle':
            (list(range(328, 332)) + list(range(724, 728)), (256, 0)),
    }
    for name, (positions, expected) in cases.items():
        result = simulate_oracle(b, symbolic, positions)
        assert result == expected, (name, result, expected)
        print(name, 'positions', len(positions), '+rank', result[0],
              'selected bits free', result[1])

    for stride, expected in ((10, (785, 128)), (8, (904, 128)),
                             (6, (1163, 128)), (5, (1456, 128)),
                             (4, (1656, 128)), (3, (2346, 127)),
                             (2, (3087, 65)), (1, (4540, 0))):
        positions = list(range(-860, -329, stride))
        result = simulate_oracle(b, symbolic, positions)
        assert result == expected, (stride, result, expected)
        print('native fullword grid stride', stride, len(positions),
              '+rank', result[0], 'selected bits free', result[1])

    print('No original unknown K04 bit recovered. All oracles are hypothetical.')


if __name__ == '__main__':
    main()
