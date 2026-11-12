# K04 A7-cut and A7-linked cvc5 attempts: all timed out (2026-11-12)

## Question

Did the CPython A7-cut relaxation or the tighter A7-linked seed model produce a complete K04 candidate or establish unsatisfiability?

## Workflow distinction

Two adjacent workflows ran and must not be conflated:

- `43160831136`: **A7-cut** workflow, `.github/workflows/h17-k04-cpython-a7cut-cvc5.yml`.
- `43161605870`: **A7-linked** workflow, `.github/workflows/h17-k04-cpython-a7linked-cvc5.yml`.

The A7-linked n=2 artifact was checked directly: its SMT-LIB contains the seven exact `init_by_array` updates `a0..a7_calc` and the assertion `a7_calc = a7`. It is not merely the A7-cut relaxation.

## Reproduced artifact review

I downloaded and inspected all six artifacts. Every model ran for approximately 3600 seconds under cvc5 1.3.2 and returned `unknown (TIMEOUT)`; each summary reports `status=NO_STATUS`, `candidate_count=0`, and `result=null`.

| Workflow | Model | Stop index | Offset | Controls | Target row | Runtime |
|---|---|---:|---:|---:|---:|---:|
| A7-cut | n=2 | 17 | 2496 | 132 | 129 excluded | 3600.1 s |
| A7-cut | n=3 | 41 | 2496 | 132 | 129 excluded | 3600.3 s |
| A7-cut | n=4 | 83 | 2496 | 132 | 129 excluded | 3600.6 s |
| A7-linked | n=2 | 17 | 2496 | 132 | 129 excluded | 3600.1 s |
| A7-linked | n=3 | 41 | 2496 | 132 | 129 excluded | 3600.3 s |
| A7-linked | n=4 | 83 | 2496 | 132 | 129 excluded | 3600.6 s |

## Reproducibility

- A7-cut workflow run: `43160831136`
  - n=2 artifact `13921045728`
  - n=3 artifact `13919979670`
  - n=4 artifact `13920438019`
- A7-linked workflow run: `43161605870`
  - n=2 artifact `13920683020`
  - n=3 artifact `13921106731`
  - n=4 artifact `13920867599`
- Each artifact preserves the exact `.smt2` input, solver stdout, and JSON summary. Local copies were inspected under `/mnt/data/h17-cvc5-artifacts/` in this invocation.

## Interpretation

These timeouts are **inconclusive**, not evidence of unsatisfiability. They produced no seed, no complete 132-packet replay, and no K04 candidate. Do not treat `candidate_count=0` as a falsification or relaunch the identical cvc5 encodings as if they were unfinished.

## Next useful action

Only revisit this branch with a materially different solver strategy or reformulated model (for example, a tractable bit-vector solver or stronger source-derived constraints). Do not spend another one-hour CI run on the same cvc5 encodings. The K04 source-level blockers remain the native attempt-2 request/copy-stage record and the physical bench-output evidence; these solver results do not change that boundary.
