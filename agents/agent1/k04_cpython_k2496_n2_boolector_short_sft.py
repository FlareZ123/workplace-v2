"""K04 source-only CPython-k2496 two-word seed: short Boolector external solver.

Uses the independent Agent37 repaired Boolector-LIB2 parser and original
Agent1 S7-forward n2 source-only SMT. SAT is not a recovered historical seed.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent37"))
from k04_cpython_k2496_boolector_sft import boolector_check

sys.path.insert(0, str(ROOT / "agents/agent1"))
from k04_cpython_initarray_wrap_sft import direct_initialized
from k04_cpython_k2496_shortforward_source_sft import original_source, synthetic_controls
from k04_cpython_k2496_shortforward_smt import model_source


def boolector_original(model: str, timeout: int) -> str:
    # Original model includes (check-sat) and (get-value), which Agent37's
    # source-only parser handles itself after converting declare-const.
    source_constraints = model.split("(check-sat)", 1)[0]
    return boolector_check(source_constraints, timeout)


def main():
    synthetic_controls()
    masks = original_source()
    keys = [0x12345678, 0x1535AF52]
    _, _, state = direct_initialized(keys)
    seeded_masks = [(mask, state[i] & mask)
                    for i, (mask, _) in enumerate(masks)]
    # Check both nested conditional source models on actual genuine n2 state.
    for stop in (17, 41):
        positive = model_source(2, stop, seeded_masks, state[6], state[7],
                                frozen_keys=keys, timeout_ms=10000)
        result = boolector_original(positive, timeout=25)
        assert result == "SAT", ("Genuine source full-positive", stop, result)
        print("GENUINE_N2_CPYTHON_BOOLECTOR_SAT", stop, flush=True)

    for stop in (17, 41):
        original = model_source(2, stop, masks,
                                masks[6][1], masks[7][1], timeout_ms=420000)
        print("ORIGINAL_N2_SHORT_FORWARD", stop,
              "SMT_SHA256", hashlib.sha256(original.encode()).hexdigest(),
              flush=True)
        result = boolector_original(original, timeout=420)
        print("ORIGINAL_N2_BOOLECTOR_SOURCE_RESULT", stop, result, flush=True)
        if result == "UNSAT":
            print("CONDITIONAL_CPYTHON_N2_SOURCE_UNSAT", stop, flush=True)
            return
        if result in ("UNKNOWN_TIMEOUT", "UNKNOWN"):
            print("CONDITIONAL_N2_SOURCE_UNRESOLVED", stop, flush=True)
            return
        if result == "SAT":
            print("CONDITIONAL_N2_NECESSARY_SOURCE_SAT_ONLY", stop,
                  "not a full 132-packet seed", flush=True)


if __name__ == "__main__":
    main()
