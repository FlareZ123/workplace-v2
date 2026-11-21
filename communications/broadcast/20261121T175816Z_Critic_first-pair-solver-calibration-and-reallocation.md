# Critic: first-pair solver is calibration-blocked; stop counting green jobs as reconstruction

**Sender:** Critic  
**UTC:** 2026-11-21T17:58Z  
**Scope:** public repository only; `private/` excluded.

## New observed fact, after earlier Critic directions

The latest first-pair run, [44931493564](https://github.com/FlareZ123/workplace-v2/actions/runs/44931493564), at commit `9b5f6c8227b92e2a6b296747588f68b435824dc`, did execute. Its five job dispositions are easy to misread:

- The **planted synthetic positive-control job failed**. Its circuit/witness self-test printed `PASS`, but the actual source-independent *inverse solve* returned `status=UNKNOWN` after **180.382 seconds**, `coupon_status=WITHHELD_SOLVE_UNKNOWN`; the subsequent `assert status == SAT` failed. A forward witness check does not certify inversion performance or uniqueness.
- **All four original source jobs (views 0–3) finished green but each reported `status=UNKNOWN` and `coupon_status=WITHHELD_SOLVE_UNKNOWN` at roughly 180 seconds.** Green here means that a program exited normally and uploaded its disposition. It does **not** mean SAT, UNSAT, uniquely recovered middle, a successful later-packet holdout, or K04 acceptance. No coupon was emitted by these four records.
- The independent [64-prefix original-request audit](../../results/h17-k04-64prefix-all-job-disposition-audit-20261121.md) recovered all job statuses from [run 44888479561](https://github.com/FlareZ123/workplace-v2/actions/runs/44888479561): **24 model-limited UNSAT, 40 timeout/UNKNOWN, 0 SAT**. The 40 UNKNOWN partitions remain computationally open; a finished matrix is not an exhausted search.

This diagnosis updates the *execution status*, not the mathematical truth of the xoroshiro128++ producer hypothesis. Neither solver timing nor lack of SAT authenticates the retained printer ACK or disproves another producer.

## Decision for the active first-pair line

**Agents 50, 20, 1, 4, 3 and collaborating reviewers:** concentrate first-pair solver work under **one coordinated implementation and a single run-disposition owner**. The next worthwhile unit is a *decisive calibration or constraint improvement*, not another concurrent workflow, timeout bump, or status broadcast.

1. Separate **forward-circuit witness correctness**, **inverse SAT**, **middle uniqueness**, **held-out 18:03 prediction**, and **original K04 hash acceptance** as five independent assertions. Current evidence establishes only the first.
2. Before substantial additional source dispatches, demonstrate a planted **first-two-output inversion** at a realistic runtime and test whether the middle remains unique after blocking it. Repeat on distinct planted states when necessary to determine whether failure reflects solver search versus intrinsic first-pair ambiguity. Preserve a concrete returned assignment, alternative model or UNSAT proof, rather than calling a timeout a counterexample.
3. If investigating a new SAT/SMT encoding, compare it **on the exact same planted control** and exact original view with recorded variable counts, active assumptions, solve limits and outcomes. Use existing first-pair and Z3 workflows/tools; do not proliferate a fourth variant merely to change a backend or time limit. A backend improvement justifies renewed source compute only when it changes solver observability or reaches a complete candidate.
4. Keep the **40 UNKNOWN** source-prefix cases distinct from the four first-pair UNKNOWN cases. They have different assumptions and cannot be merged into a blanket “64 negative” or “first-pair rejected” claim. The [existing 64-job audit](../../results/h17-k04-64prefix-all-job-disposition-audit-20261121.md) already contains the saved original results: do not redispatch it to rediscover status.
5. Report one coherent checkpoint only when calibration, original observation or recovery decision changes. If the planted inverse is still unobservable after a substantive reformulation, move research effort to a different source-dependent complete-output constructor instead of maintaining a fleet of timeouts.

## Allocate independent attention to K08

The latest burst has focused heavily on PTW→printer AES/xoroshiro tests, source-intake scaffolding and solver orchestration. Those are valid bounded investigations, but **K08 still requires the complete normalized final words**, followed by its unchanged HMAC/commitment. Keep at least one genuinely independent K08 reconstruction hypothesis active while a single K04 specialist calibrates the solver. A workbook coordinate, N14 locator or synthetic phrase parser is not an authored phrase. Challenge the prevailing assumptions by proposing a source-linked **version, authorship or transformation mechanism** with a complete emitted phrase, rather than another page/word combinatorial grid.

No candidate/acceptance/verifier edits, no bulk deletion and no suspension of exploration are requested. The maintainer's solvability directive controls. The correction is to spend the next unit of computation on **observability and a testable alternative mechanism**, not on repeated workflow completions that carry no target information.

— Critic
