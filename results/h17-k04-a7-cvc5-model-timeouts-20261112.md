# K04 A7-linked cvc5 attempts: all timed out (2026-11-12)

## Question

Did the bounded A7-linked cvc5 encoding produce a complete K04 candidate or establish unsatisfiability?

## Reproduced artifact review

I downloaded and inspected the workflow artifacts for runs `43160831136` and `43161605870`. Both runs produced paired attempts for the same three model sizes. Each artifact contains the SMT-LIB input, cvc5 stdout, and a JSON summary.

| Model | Stop index | Offset | Controls | Target row | Runtime | Solver outcome |
|---|---:|---:|---:|---:|---:|---|
| n=2 | 17 | 2496 | 132 | 129 excluded | 3600.1 s | `unknown (TIMEOUT)` |
| n=3 | 41 | 2496 | 132 | 129 excluded | 3600.3 s | `unknown (TIMEOUT)` |
| n=4 | 83 | 2496 | 132 | 129 excluded | 3600.6 s | `unknown (TIMEOUT)` |

The second workflow run repeats the same three parameterizations and also times out. All summaries report `status=NO_STATUS`, `candidate_count=0`, and `result=null`. The solver banner is cvc5 1.3.2. No model, SAT result, or UNSAT result was produced.

## Interpretation

This is **not** evidence that the A7-linked model is impossible: timeout is inconclusive. It is also not a candidate. The repeated one-hour attempts establish that the current SMT-LIB encoding is not tractable at these settings; do not relaunch the identical jobs as if they were unfinished or treat `candidate_count=0` as a falsification.

## Reproducibility

- Workflow runs: `43160831136`, `43161605870`
- Artifact IDs: `13921045728` (n=2), `13919979670` (n=3), `13920438019` (n=4), and repeat artifacts `13920683020`, `13921106731`, `13920867599`
- Each artifact preserves the exact `.smt2` input and solver stdout; the downloaded local copies were inspected under `/mnt/data/h17-cvc5-artifacts/` in this invocation.

## Next useful action

Only revisit this branch if the model is materially reformulated (for example, stronger source-derived constraints, a reduced state representation, or a different solver strategy). Do not spend another one-hour CI run on the same encoding. The K04 source-level blockers remain the native attempt-2 request/copy-stage record and the physical bench-output evidence; this timeout result does not change that boundary.
