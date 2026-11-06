"""K04 source-only CPython-k2496 two-word seed: short Boolector external solver.

Uses the independent Agent37 repaired Boolector-LIB2 parser and original
Agent1 S7-forward n2 source-only SMT. SAT is not a recovered historical seed.
"""
from __future__ import annotations

import hashlib
import re
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
    # Ubuntu's packaged Boolector 1.5 parses SMT-LIB2 but rejects define-fun.
    # Turn each nullary BitVec definition into a declaration and exact equality.
    # Source has one complete, singly nested definition per line.
    rebuilt = []
    count = 0
    for line in source_constraints.splitlines():
        m = re.fullmatch(r"\(define-fun ([^ ]+) \(\) \(_ BitVec 32\) (.+)\)", line)
        if m is not None:
            name, expression = m.groups()
            rebuilt.append(f"(declare-fun {name} () (_ BitVec 32))")
            rebuilt.append(f"(assert (= {name} {expression}))")
            count += 1
        else:
            rebuilt.append(line)
    assert count >= 17, count
    return boolector_check("\n".join(rebuilt), timeout)


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
