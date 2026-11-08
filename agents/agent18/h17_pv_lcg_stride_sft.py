"""Source-pinned HST-4 PV full-state LCG producer and blind suffix test.

Hypothesis: PV(seq) = round(12+76*(state/modulus), 3), where state comes
from a classical LCG and every row advances a constant 1..16 draws.
This is a bounded separate-historian producer test, not a K04 coupon claim.
"""
import hashlib
import json
from pathlib import Path

SOURCE_SHA256 = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
MODELS = (
    ("park-miller-16807", 2147483647, 16807, 0),
    ("park-miller-48271", 2147483647, 48271, 0),
    ("nr-1664525", 4294967296, 1664525, 1013904223),
    ("ansi-1103515245", 2147483648, 1103515245, 12345),
    ("msvc-multiplier-full-state", 2147483648, 214013, 2531011),
    ("borland-22695477", 4294967296, 22695477, 1),
    ("randu-65539", 2147483648, 65539, 0),
)


def interval(milli, modulus):
    """Inclusive native states satisfying three-place PV rounding."""
    diff = milli - 12000
    low = -(-((2 * diff - 1) * modulus) // 152000)
    high = -(-((2 * diff + 1) * modulus) // 152000) - 1
    return max(0, low), min(modulus - 1, high)


def step_parameters(modulus, multiplier, increment, stride):
    a, c = 1, 0
    for _ in range(stride):
        a, c = a * multiplier % modulus, (c * multiplier + increment) % modulus
    return a, c


def milli_value(state, modulus):
    return 12000 + (152000 * state + modulus) // (2 * modulus)


def evaluate(values, modulus, multiplier, increment, stride):
    """Enumerate ALL internal states consistent with first rounded PV."""
    a, c = step_parameters(modulus, multiplier, increment, stride)
    low, high = interval(values[0], modulus)
    best, survivors, states = 1, 0, []
    for initial_state in range(low, high + 1):
        x, streak = initial_state, 1
        for target in values[1:]:
            x = (a * x + c) % modulus
            if milli_value(x, modulus) != target:
                break
            streak += 1
        best = max(best, streak)
        if streak >= min(8, len(values)):
            survivors += 1
            states.append(initial_state)
    return best, survivors, states


def main():
    source = Path(__file__).resolve().parents[2] / "resources" / "evidence" / "telemetry" / "freeze-export.jsonl"
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source changed"
    pv = sorted(
        (json.loads(line) for line in raw.decode().splitlines()
         if '"field": "PV"' in line),
        key=lambda row: row["seq"],
    )
    assert len(pv) == 112
    assert [row["seq"] for row in pv] == list(range(100, 212))
    values = [round(row["value"] * 1000) for row in pv]
    assert all(
        milli_value(x, modulus) == values[0]
        for modulus in (2147483647, 4294967296)
        for x in interval(values[0], modulus)
    )

    # Real native LCG generator, first 8 rounded readings fitted and 16 withheld.
    modulus, multiplier, increment = 4294967296, 1664525, 1013904223
    chosen_seed, stride = 0x13579BDF, 7
    a, c = step_parameters(modulus, multiplier, increment, stride)
    synthetic_states = [chosen_seed]
    for _ in range(23):
        synthetic_states.append((a * synthetic_states[-1] + c) % modulus)
    synthetic = [milli_value(s, modulus) for s in synthetic_states]
    best, count, candidate_states = evaluate(
        synthetic[:8], modulus, multiplier, increment, stride
    )
    assert best == 8 and chosen_seed in candidate_states
    state, prediction = chosen_seed, []
    for _ in range(24):
        prediction.append(milli_value(state, modulus))
        state = (a * state + c) % modulus
    assert prediction[8:] == synthetic[8:]
    print("SYNTHETIC_CONTROL PASS seeded_state_recovered=True heldout_suffix=16/16")

    best_original, best_model = 0, None
    scanned = 0
    full_fits = []
    for name, modulus, multiplier, increment in MODELS:
        for stride in range(1, 17):
            streak, count, states = evaluate(
                values, modulus, multiplier, increment, stride
            )
            scanned += 1
            if streak > best_original:
                best_original, best_model = streak, (name, stride)
            if count:
                full_fits.append((name, stride, count, states[:10]))
    print("SOURCE_PIN PASS pv_rows=112 models=", scanned)
    print("ORIGINAL_BEST_PREFIX", best_original, best_model)
    print("ORIGINAL_EIGHT_VALUE_MODELS", full_fits or "NONE")
    assert not full_fits, "Unexpected source fit: investigate before interpreting"


if __name__ == "__main__":
    main()
