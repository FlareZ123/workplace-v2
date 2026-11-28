#!/usr/bin/env python3
"""Source-independent P16 direct-two-output inversion on hard heldout controls.

Reuses Agent15's one-transition exact Boolean circuit, distinct from the
older six-stage representation with four unused successor round definitions.
The benchmark is deliberately conditional on supplying the planted true P16
anchor; this does NOT provide source-observed 16 state bits and does not
reconstruct any historical K04 component. UNKNOWN is unresolved, not UNSAT.
No original source, routing, target, nonce, PDF or candidate is read.
"""
from __future__ import annotations

import json
import random
import time

from agents.agent15.k04_laterfirst_p16_p20_source_local import (
    P16, exact_states, firstpair,
)

BUDGET_MS = 700


def planted(seed, wrong=False):
    rng = random.Random(seed)
    state = (rng.getrandbits(64), rng.getrandbits(64))
    observed = firstpair(*state)
    anchor = sum(((state[0] >> position) & 1) << bit
                 for bit, position in enumerate(P16))
    if wrong:
        # A deliberate falsifier: change one of the independently
        # conditioned full state-word bits, never the observed outputs.
        anchor ^= 1 << (seed % len(P16))
    models, terminal = exact_states(observed, anchor, BUDGET_MS)
    if terminal not in ("unsat", "unknown"):
        raise AssertionError(terminal)
    assert all(firstpair(*candidate) == observed for candidate in models)
    if not wrong:
        assert all(candidate == state for candidate in models) or (
            state not in models and terminal == "unknown")
    return state in models, terminal, len(models)


def main():
    totals = {
        "synthetic_only": True,
        "read_historical_source": False,
        "conditional_true_state_anchor": True,
        "solver_timeout_ms": BUDGET_MS,
        "cohorts": {},
    }
    t0 = time.monotonic()
    for label, start, count in (
        ("earlier_hard_holdout", 80903, 20),
        ("fresh_untrained", 90000, 20),
        ("additional_fresh", 90500, 12),
    ):
        recovered = unsat = unknown = nmodels = 0
        for seed in range(start, start+count):
            yes, status, n = planted(seed)
            recovered += int(yes)
            unsat += int(status == "unsat")
            unknown += int(status == "unknown")
            nmodels += n
        totals["cohorts"][label] = {
            "seed_range": [start, start+count],
            "cases": count,
            "complete_original_state_recovered": recovered,
            "terminal_unsat": unsat,
            "terminal_unknown": unknown,
            "models": nmodels,
        }
    wrong_counts = {"cases": 12, "terminal_unsat": 0,
                    "terminal_unknown": 0, "spurious_sat_models": 0}
    for seed in range(90500,90512):
        yes, status, nmodels = planted(seed, wrong=True)
        if yes:
            raise AssertionError("Poisoned anchor recovered planted state")
        wrong_counts["terminal_unsat"] += int(status == "unsat")
        wrong_counts["terminal_unknown"] += int(status == "unknown")
        wrong_counts["spurious_sat_models"] += nmodels
    totals["wrong_anchor_controls"] = wrong_counts
    totals["elapsed_seconds"] = round(time.monotonic()-t0, 2)
    print(json.dumps(totals, sort_keys=True))


if __name__ == "__main__":
    main()
