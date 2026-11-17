"""Source-only preflight: can one choices()+choice() pair fit every row gap?

A uniform CPython random.choices(..., k=1) consumes two MT outputs for its
53-bit random() float. random.choice() over a 3-item population consumes at
least one further MT output via getrandbits(2), with possible rejection.
If both calls are consecutive and attached to each row in the same gap between
4-word payloads, every such gap must contain >=3 MT outputs.

This script checks that necessary condition across all six published p950-p955
geometries and all physically valid one-group perturbations from Agent44.
It does not load payload values, the selected ACK2, any K04 mask, or any hash.

Run from the repository root:
    python agents/agent6/k04_mixed_sampler_gap_preflight.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent44"))
import k04_single_root_perturbations_sft as chronology
import k04_six_stage_sft as six
import k04_p951_hidden_stage_coupon_sft as mt


EXPECTED_VALID = {950: 104, 951: 103, 952: 89, 953: 89, 954: 93, 955: 79}
EXPECTED_MIN_SHORT_TRAIN = {950: 35, 951: 37, 952: 39, 953: 37, 954: 37, 955: 42}


def main() -> None:
    groups = chronology.GROUPS
    assert len(groups) == 133 and len(set(groups)) == 81
    summary = {}
    for selected, baseline in sorted(six.GEOMETRIES.items()):
        assert len(baseline) == 133 and baseline[129] == selected
        valid = []
        for group in range(81):
            for delta in (-2, -1, 1, 2):
                starts = [
                    start + (delta if groups[row] == group else 0)
                    for row, start in enumerate(baseline)
                ]
                if not chronology.physical(starts, selected):
                    continue
                gaps = [
                    starts[row + 1] - starts[row] - 4
                    for row in range(132)
                ]
                train_short = sum(gap < 3 for gap in gaps[:95])
                holdout_short = sum(gap < 3 for gap in gaps[95:127])
                valid.append((train_short, holdout_short))
        assert len(valid) == EXPECTED_VALID[selected], (selected, len(valid))
        minimum = min(train for train, _ in valid)
        assert minimum == EXPECTED_MIN_SHORT_TRAIN[selected], (selected, minimum)
        zero_short = sum(train == 0 for train, _ in valid)
        assert zero_short == 0, (selected, zero_short)
        summary[selected] = {
            "valid_variants": len(valid),
            "minimum_first_95_gaps_lt3": minimum,
            "variants_with_zero_short_training_gaps": zero_short,
            "holdout_gaps_lt3_range": (
                min(hold for _, hold in valid),
                max(hold for _, hold in valid),
            ),
        }
        print(
            f"GEOMETRY {selected}: valid={len(valid)} "
            f"min_train_gaps_lt3={minimum} zero_short_train_variants={zero_short} "
            f"holdout_short_range={summary[selected]['holdout_gaps_lt3_range']}"
        )

    assert sum(x["valid_variants"] for x in summary.values()) == 547
    assert all(x["minimum_first_95_gaps_lt3"] > 0 for x in summary.values())
    print("STRICT_SAME_GAP_CHOICES_PLUS_CHOICE", "FALSIFIED")
    print("SCOPE", "only both consecutive metadata calls in each same inter-payload gap")
    print("PAYLOAD_OR_TARGET_BYTES_LOADED", "NO")


if __name__ == "__main__":
    main()
