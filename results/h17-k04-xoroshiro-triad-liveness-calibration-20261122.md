# K04 reverse-triad solver liveness calibration — 22 November 2026

## Question

Does the current unseeded xoroshiro128++ reverse-triad circuit reliably recover an unknown 128-bit state from outputs 3, 4 and 5, including exact replay of the withheld middle coupon and full six-output stream?

## Method

- Eight independent 128-bit states were generated once with the local OS CSPRNG and frozen in `agents/agent30/k04_xoropp_triad_calibration_sft.py` before execution.
- For each state, the solver received only the three consecutive outputs 3, 4 and 5. The initial state and outputs 2 and 3 (the withheld middle coupon) were not given to the solver.
- The same `run_triad` circuit and CryptoMiniSat configuration used by the historical source runner were used unchanged, with a 120-second per-state limit.
- A positive result required exact recovery of the planted initial state, exact replay of all six outputs, and exact recovery of both withheld middle words. No H-17 source bytes, candidate, route mask or K04 commitment were read by this calibration.

## Results

| Frozen state | Solver status | Elapsed seconds | Exact full recovery |
|---:|---|---:|---|
| 0 | UNKNOWN | 120.130 | — |
| 1 | UNKNOWN | 120.119 | — |
| 2 | UNKNOWN | 120.110 | — |
| 3 | SAT | 55.689 | Yes |
| 4 | UNKNOWN | 120.053 | — |
| 5 | UNKNOWN | 120.088 | — |
| 6 | UNKNOWN | 120.073 | — |
| 7 | UNKNOWN | 120.099 | — |

**Aggregate:** 1/8 exact SAT recoveries; 7/8 UNKNOWN; 0 UNSAT; 896.401 seconds total. Circuit sizes were 943–947 variables, 1,671–1,683 CNF clauses and 636 XOR clauses.

The sole SAT case recovered its exact planted state and both withheld middle words, and replayed all six outputs. It is a synthetic positive control, not an H-17 coupon.

## Interpretation and decision

The earlier single 91.019-second synthetic success established that this circuit can solve at least one planted instance. It did not establish reliable unseeded liveness. The frozen eight-state sample shows poor liveness under the same 120-second budget: seven cases timed out without a SAT or UNSAT disposition.

The two historical source views in the original reverse-triad run remain UNKNOWN after approximately 240 seconds each. This calibration does not prove the xoroshiro128++ source hypothesis false, and UNKNOWN is not UNSAT. It does show that the current CryptoMiniSat triad implementation is not a dependable recovery path under the demonstrated budget.

**Decision:** do not extend the timeout, repeat the same circuit, or launch a homogeneous Z3/Bitwuzla/Boolector backend matrix. Existing first-pair Z3/Bitwuzla and native-XOR attempts already have independent UNKNOWN controls at longer limits. Reopen this family only if a materially different inversion representation or a new source-authenticated constraint changes the problem.

## Reproduction

- Frozen states and exact per-case outputs: `agents/agent30/k04_xoropp_triad_calibration_sft.py`
- Optional calibration mode in the existing manual-only workflow: `.github/workflows/agent30-k04-reverse-triad.yml`
- GitHub Actions run: [45003513734](https://github.com/FlareZ123/workplace-v2/actions/runs/45003513734)
- Artifact: `k04-reverse-triad-calibration` (ID `14747670669`)

The calibration is source-independent. It changes no original source record, candidate, acceptance commitment or verifier.
