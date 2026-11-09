"""H17 conditional p951 MT source: full-free K04-causal antecedent packet windows.

Reuses the original Agent49 source-only symbolic basis, with selected ACK2
excluded. Computes exact GF(2) residual rank at the two unprinted windows
newly localized by Agent23's unindexed stage-gap graph (9 November 2026).

Run from repository root: python agents/agent18/k04_mt_causal_gap_residual_sft.py
Reads original evidence and imported symbolics, writes nothing.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent49.k04_p951_symbolic_basis import STARTS, get, source


def residual_rank(existing, forms):
    pivots = {bit: relation for bit, (relation, _) in existing.rows.items()}
    additional = 0
    for equation in forms:
        while equation:
            highest = equation.bit_length() - 1
            if highest not in pivots:
                pivots[highest] = equation
                additional += 1
                break
            equation ^= pivots[highest]
    return additional


def window_forms(symbolic, begin, end):
    return (
        form
        for stage in range(begin, end + 1)
        for form in get(symbolic, stage)
    )


def main():
    basis, symbolic = source(ROOT)
    assert basis.rank == 15365
    assert STARTS[43] == 324 and STARTS[44] == 335
    assert STARTS[96] == 717 and STARTS[97] == 729
    assert STARTS[129] == 951

    for intact_row in (0, 43, 44, 96, 97, 128, 130):
        begin = STARTS[intact_row]
        assert residual_rank(
            basis, window_forms(symbolic, begin, begin + 3)
        ) == 0

    windows = {
        "predecessor gap row43->44": (328, 331, 128),
        "predecessor gap row96->97": (724, 727, 128),
        "selected ACK2": (951, 954, 128),
        "observed boundary + gap": (327, 331, 128),
    }
    for label, (begin, end, expected) in windows.items():
        residual = residual_rank(
            basis, window_forms(symbolic, begin, end)
        )
        assert residual == expected, (label, residual, expected)
        print(
            f"{label}: stages={begin}..{end}, "
            f"still-free GF2 bits={residual} of {(end-begin+1)*32}"
        )

    acquisition_rank_checks(basis, symbolic)
    print("Original 7 intact whole-packet controls: rank0 each; PASS")
    print("Source-only missing-window width: 128 bits each; no coupon")


def conditioned_target_rank(existing, symbolic, donor_windows):
    pivots = {bit: relation for bit, (relation, _) in existing.rows.items()}

    def add_equation(equation):
        while equation:
            highest = equation.bit_length() - 1
            if highest not in pivots:
                pivots[highest] = equation
                return 1
            equation ^= pivots[highest]
        return 0

    donor_gain = sum(
        add_equation(form)
        for begin, end in donor_windows
        for form in window_forms(symbolic, begin, end)
    )
    selected_gain = sum(
        add_equation(form)
        for form in window_forms(symbolic, 951, 954)
    )
    return donor_gain, selected_gain


def reconstruct_selected_native(known327, prior328, prior724):
    """Exact native MT coupon with two FULL unprinted 4-word antecedent blocks."""
    assert len(prior328) == 4 and len(prior724) == 4
    earlier = [known327, *prior328]
    result = []
    for j in range(4):
        y = (earlier[j] & 0x80000000) | (earlier[j+1] & 0x7FFFFFFF)
        twist = (y >> 1) ^ (0x9908B0DF if earlier[j+1] & 1 else 0)
        result.append((prior724[j] ^ twist) & 0xFFFFFFFF)
    return result


def synthetic_coupon_controls():
    import random
    from agents.agent49.k04_p951_symbolic_basis import untemper
    for seed in (1, 42, 0x12345678):
        rng = random.Random(seed)
        outputs = [rng.getrandbits(32) for _ in range(1000)]
        native = [untemper(x) for x in outputs]
        actual = native[951:955]
        predicted = reconstruct_selected_native(
            native[327], native[328:332], native[724:728]
        )
        assert predicted == actual, seed
    print("Genuine Python MT 3/3 unseen complete coupon controls: PASS")


def acquisition_rank_checks(basis, symbolic):
    cases = (
        ((), 0, 128),
        (((328, 331),), 128, 128),
        (((724, 727),), 128, 127),
        (((328, 331), (724, 727)), 256, 0),
        (((328, 330), (724, 727)), 224, 31),
        (((328, 331), (724, 726)), 224, 32),
    )
    for donor_windows, expected_gain, expected_remaining in cases:
        donor_gain, missing = conditioned_target_rank(
            basis, symbolic, donor_windows
        )
        assert (donor_gain, missing) == (
            expected_gain, expected_remaining
        ), (donor_windows, donor_gain, missing)
        print(
            f"Donor windows {donor_windows}: donor_gain={donor_gain}, "
            f"selected 128-bit coupon uncertainty={missing}"
        )
    synthetic_coupon_controls()


if __name__ == "__main__":
    main()
