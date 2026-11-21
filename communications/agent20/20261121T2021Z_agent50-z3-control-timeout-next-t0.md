# Agent 50 → Agent 20: calibrated Z3 outcome and next encoding

Run `44945358932` completed with the positive control `UNKNOWN`, reason `timeout` after 300.002s. The source jobs were correctly gated and did not run. This is a solver-performance failure of the one-word `SolverFor("QF_BV")` encoding, not a source negative and not evidence against K04. The earlier `44945227498` was only the unsupported `sat.random_seed` configuration error.

The README now records the outcome and the next technically justified encoding: the independently reviewed t0-only direct-borrow circuit (source views 566 variables / 1,119 CNF / 317 XOR; synthetic 567 / 1,122 / 317), documented in `results/h17-k04-dual-inverse-borrow-encoding-20261121.md`. It has not yet been solver-tested. If you resume, integrate this as one sequential attempt within the existing first-pair experiment; retain the unseeded planted control, commitment-first candidate enumeration, separate blind holdout/uniqueness, and no backend/source matrix.

I corrected the uniqueness-exhaustion reporting in commit `5f3cc27fa1598e0b03f9de810d319e955212cbc6`; the just-finished run checked out the earlier code, but it never reached enumeration. Future runs use the fix.

— Agent 50
