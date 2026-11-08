"""Source-pinned all-state historian PV LCG producer with variable bounded skips.

Each consecutive PV row may consume any 1..16 native transitions. Exact
three-place rounding constrains native states; no K04/K08 target is used.
"""
import hashlib
import json
from pathlib import Path

from h17_pv_lcg_stride_sft import MODELS, SOURCE_SHA256, interval, milli_value


def search(values, modulus, a, c, max_skip=16):
    """Enumerate every initial state and every admissible gap up to max_skip."""
    low, high = interval(values[0], modulus)
    paths = [(state, state, ()) for state in range(low, high + 1)]
    depth, counts = 1, []
    for target in values[1:]:
        new_paths = []
        for initial, current, strides in paths:
            state = current
            for skip in range(1, max_skip + 1):
                state = (a * state + c) % modulus
                if milli_value(state, modulus) == target:
                    new_paths.append((initial, state, strides + (skip,)))
        paths = new_paths
        counts.append(len(paths))
        if not paths:
            break
        depth += 1
    return depth, paths, counts


def main():
    source = (
        Path(__file__).resolve().parents[2]
        / "resources" / "evidence" / "telemetry" / "freeze-export.jsonl"
    )
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
    pv = sorted(
        (json.loads(line) for line in raw.decode().splitlines()
         if '"field": "PV"' in line),
        key=lambda row: row["seq"],
    )
    assert len(pv) == 112 and [row["seq"] for row in pv] == list(range(100, 212))
    values = [round(row["value"] * 1000) for row in pv]

    # Independent LCG positive; recover unique initial state and first 7 gaps
    # before using a preregistered index-defined schedule for 16 unseen readings.
    modulus, a, c = 2**32, 1664525, 1013904223
    planted_seed = 0x13579BDF
    skips = [1 + (i * i + 7 * i) % 16 for i in range(1, 24)]
    state = planted_seed
    synthetic = [milli_value(state, modulus)]
    for skip in skips:
        for _ in range(skip):
            state = (a * state + c) % modulus
        synthetic.append(milli_value(state, modulus))
    depth, recovered, counts = search(synthetic[:8], modulus, a, c)
    assert depth == 8 and len(recovered) == 1
    assert recovered[0][0] == planted_seed
    assert recovered[0][2] == tuple(skips[:7])
    state, unseen_prediction = recovered[0][1], []
    for skip in skips[7:]:
        for _ in range(skip):
            state = (a * state + c) % modulus
        unseen_prediction.append(milli_value(state, modulus))
    assert unseen_prediction == synthetic[8:]
    print("SYNTHETIC_CONTROL PASS unique_seed_and_skips=True blind_suffix=16/16")

    original_best = (0, "")
    for name, modulus, a, c in MODELS:
        depth, survivors, counts = search(values[:8], modulus, a, c)
        print("ORIGINAL", name, "prefix", depth, "candidate_counts", counts)
        if depth > original_best[0]:
            original_best = depth, name
        assert not survivors, "unexpected source model fit"
    print("SOURCE_PIN PASS original_pv=112")
    print("ORIGINAL_BEST_PREFIX", original_best)
    print("ORIGINAL_EIGHT_VALUE_MODELS NONE")


if __name__ == "__main__":
    main()
