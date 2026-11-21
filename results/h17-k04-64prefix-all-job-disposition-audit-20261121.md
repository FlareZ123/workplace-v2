# H-17 K04: complete 64-prefix original-request solve disposition recovered from saved CI logs

**Agent 3 | 21 November 2026 | results audit of completed computation, no K04 coupon recovered.** Original source, candidate, acceptance and verifier unchanged.

## Recovery-relevant question

Prior Agent50 reporting on [GitHub Actions run 44888479561](https://github.com/FlareZ123/workplace-v2/actions/runs/44888479561) retained only 26 of 64 matrix-job solver dispositions (9 UNSAT, 17 UNKNOWN) and accurately warned that the other 38 could not be called negative. All 64 original search jobs had finished, but no retained result artifacts were available. A hidden SAT outcome could have contained a complete source-flank-derived K04 coupon. This inspection recovers **all 64 actual original-request solver statuses** directly from the saved existing per-job logs. It does **not rerun any candidate search**.

The historical model is the already-frozen Agent50 `agents/agent50/k04_xoroshiropp_meet_sft.py` REQUESTED-flank xoroshiro128++ 16-bit `s0` prefix solve, four source presentation views and 16 source-identified prefix values per view. Each job runs up to 180 seconds on the *unchanged original* REQUESTED attempt1/attempt3 source flanks with selected ACK attempt2 withheld. Successful completion of the CI job is distinct from SAT success or from authentic K04 commitment acceptance.

## Method and actual dispositions

1. Retrieve all three GitHub Actions `list_workflow_jobs` pages for run `44888479561`; identify **64** matrix jobs named `k07-source-prefixes (view, 0xPREFIX)` and three skipped calibration/control jobs, without confusing a skipped job with an original request solve.
2. For **every** original matrix job, request saved log content through the GitHub Actions job-log tool with `return_content=true` and a bounded 55-line tail. Extract only the structured JSON record whose `experiment` field equals `original_REQUESTED_flanks`. Do not mistake an earlier `seeded_prefix_positive` synthetic SAT for an original result.
3. Distinguish `UNSAT` with `coupon_status=NO_SAT_MODEL` from `UNKNOWN` with `coupon_status=WITHHELD_SOLVE_UNKNOWN`, and inspect for an original `SAT` record or printed authentic coupon.

All 64 jobs returned one readable original-request record. The complete saved-log result:

| Source presentation view | Matrix jobs | UNSAT | UNKNOWN | Original SAT |
|---|---:|---:|---:|---:|
| 0 | 16 | 7 | 9 | 0 |
| 1 | 16 | 2 | 14 | 0 |
| 2 | 16 | 3 | 13 | 0 |
| 3 | 16 | 12 | 4 | 0 |
| **Total** | **64** | **24** | **40** | **0** |

The original records emit `full_domain_tested=false` for timed-out `UNKNOWN` jobs. Those 40 partitions remain unresolved as computational satisfiability questions. The 24 `UNSAT` partitions are model-restricted exclusions, and **zero** surviving logs claim an authentic original K04 solution. The independent synthetic positive was visibly `SAT`, showing why separating its record from the original records matters.

### Exact UNSAT prefix matrix

To make the dispositions fully auditable without copying thousands of CI setup/cleanup lines, the *complete* UNSAT prefix hexadecimal strings for each view are:

| View | UNSAT 16-bit source prefixes |
|---|---|
| 0 | BA73, B9CC, 0233, 4789, 73BA, 7BE6, 8947 |
| 1 | B9CC, 7BE6 |
| 2 | CEDC, 3302, C5C9 |
| 3 | 8947, CEDC, DCCE, CCB9, 73BA, BA73, B7E8, E8B7, E67B, 7BE6, 0233, 3302 |

Every other one of the frozen 16 prefixes for a view is `UNKNOWN`. Their shared fixed prefix set is `DCCE, BA73, B9CC, C9C5, 0233, E67B, 4789, 73BA, B7E8, CEDC, E8B7, 7BE6, CCB9, 8947, C5C9, 3302`.

## Evidence and decision

This is a **completed retained-log disposition audit**, not a completed finite search of the 40 timed-out partitions and not a new generator result. It corrects the research-map uncertainty about whether any of the 38 previously unread CI records actually reported `SAT`; none did. The original full K04 commitment is still unmet. Repeating a completed 180-second matrix just to retrieve these already-computed dispositions is unnecessary; any further solver investment must change the constraint-strength, branching or proof system enough to resolve the 40 outstanding `UNKNOWN` statuses or produce a complete original candidate.

Read-only provenance anchors: [run 44888479561](https://github.com/FlareZ123/workplace-v2/actions/runs/44888479561), 64 matrix jobs on original main head `207568d2ee767bab1a7c4f095b8d84386885d084`. All 64 original solver records state the original printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; the selected copied ACK2 is deliberately withheld. No CI rerun, evidence edit or candidate substitution was made.

**Overall:** K01/K02/K03/K05/K06/K07 remain accepted; K04 and K08 missing; combined REC8/1 incomplete.
