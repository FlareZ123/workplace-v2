"""K04 conditional printer-gap source model, original source only.

Scan exact two-rejection-sampler producer hypotheses against the 127 ordinary
inter-packet gaps of Agent49's historically unverified p951 MT stage geometry.
The entire selected 18:02 attempt-2 coupon is excluded by the imported basis.
No candidate is constructed, and original acceptance is never consulted.
"""
from collections import Counter
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent49 import k04_p951_symbolic_basis as mt

ORDERS = ((4, 3), (3, 4), (3, 3), (4, 4),
          (5, 3), (3, 5), (5, 5))
EXPECTED = {(4, 3): (3720, 24), (3, 4): (3720, 14),
            (3, 3): (3844, 23), (4, 4): (3600, 18),
            (5, 3): (3720, 23), (3, 5): (3720, 17),
            (5, 5): (3600, 18)}


def compatible(outputs, first, second):
    """Does any split allocate all gap draws to two rejection samplers?"""
    for split in range(1, len(outputs)):
        a = outputs[:split]
        b = outputs[split:]
        if (all(o[first][1] for o in a[:-1])
                and a[-1][first][0]
                and all(o[second][1] for o in b[:-1])
                and b[-1][second][0]):
            return True
    return False


def options(predicted_bits, size, offset):
    """Allowed accepted codes and any allowed rejected code in k-bit slice."""
    k = size.bit_length()
    mask = value = 0
    for j, known in enumerate(predicted_bits[offset:offset + k]):
        if known is not None:
            mask |= 1 << j
            value |= known << j
    candidates = [v for v in range(1 << k) if (v & mask) == value]
    return (any(v < size for v in candidates),
            any(v >= size for v in candidates))


def run():
    basis, expression_words = mt.source(ROOT / "resources")
    assert basis.rank == 15365
    starts = mt.STARTS
    assert len(starts) == 133 and starts[129] == 951
    gaps = [tuple(range(starts[i] + 4, starts[i + 1])) for i in range(127)]
    assert len(gaps) == 127
    assert all(len(g) >= 2 for g in gaps)
    positions = sorted({i for g in gaps for i in g})
    assert len(positions) == 434

    # This is the actual existing original-source symbolic recurrence:
    # initial state word 0 is anchored at native stage -1100.
    predicted = {}
    for stage in positions:
        native = mt.get(expression_words, stage)
        predicted[stage] = {
            "native": [basis.predict(mask) for mask in native],
            "temper": [basis.predict(mask) for mask in mt.temper(native)],
        }

    fixed2 = sum(sum(v is not None for v in p["temper"][30:32])
                 for p in predicted.values())
    fixed3 = sum(sum(v is not None for v in p["temper"][29:32])
                 for p in predicted.values())
    assert (fixed2, fixed3) == (294, 464)
    print("SOURCE rank=15365 intact=132 target_row129=WITHHELD")
    print("GAPS", dict(sorted(Counter(map(len, gaps)).items())),
          "stages=434 fixed_top2=294 fixed_top3=464")

    # An independent positive for the sampler-split decision procedure.
    positive = [
        {3: (False, True), 4: (False, True)},
        {3: (True, False), 4: (False, True)},
        {3: (False, True), 4: (False, True)},
        {3: (False, True), 4: (True, False)}
    ]
    assert compatible(positive, 3, 4)
    assert not compatible(positive[:2], 4, 3)

    total = 0
    for first, second in ORDERS:
        minimum = 127
        configs = 0
        for mode_a, mode_b in product(("temper", "native"), repeat=2):
            for shift_a in range(33 - first.bit_length()):
                a = {i: options(predicted[i][mode_a], first, shift_a)
                     for i in positions}
                for shift_b in range(33 - second.bit_length()):
                    b = {i: options(predicted[i][mode_b], second, shift_b)
                         for i in positions}
                    bad = 0
                    for gap in gaps:
                        outputs = [
                            {first: a[i], second: b[i]} for i in gap
                        ]
                        # When sizes are equal, use distinct keys below.
                        if first == second:
                            outputs = [
                                {"a": a[i], "b": b[i]} for i in gap
                            ]
                            fits = compatible(outputs, "a", "b")
                        else:
                            fits = compatible(outputs, first, second)
                        bad += not fits
                    minimum = min(minimum, bad)
                    configs += 1
        assert (configs, minimum) == EXPECTED[first, second], (
            (first, second), configs, minimum)
        total += configs
        print(f"n={first}+{second} configurations={configs} "
              f"minimum_unsatisfiable_gaps={minimum} compatible=0")
    assert total == 25924
    print("FINISHED total_configurations=25924 universal_fit=NONE")


if __name__ == "__main__":
    run()
