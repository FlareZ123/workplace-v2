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

    print("Original 7 intact whole-packet controls: rank0 each; PASS")
    print("Source-only missing-window width: 128 bits each; no coupon")


if __name__ == "__main__":
    main()
