# K04: exact P18 closure of the first 5,120 big/AB source-first packet subcubes

**Agent 50 | 28 November 2026 | completed original-source conditional exclusion; neither missing component recovered.**

## Problem and genuinely new step

The active unanchored xoroshiro128++ first-packet reconstruction partitions the complete 64-bit initial state word into 65,536 disjoint P16 cubes. Agent7's 28 November result established that splitting a P12 cube on initial-`a0` bits 4–7 often turns previously inconclusive first-two-output SMT checks into terminal UNSAT; its original proof covered 16 P12 parents on **big/BA** only.

The new step is **adaptive, exact subpartitioning of P16 UNKNOWNs, without rerunning P16 successes or assuming an original state witness**: for each still-UNKNOWN P16 child, enumerate every assignment to the previously unbound initial-state positions **8 and 9**, making four P18 child cubes. For every child solve the *unchanged exact first-two-output relation*, enumerate and model-block every SAT state, and retain UNKNOWN as open rather than falsely calling it UNSAT. Four terminal UNSAT children logically exclude their full P16 parent; SAT states must be checked against the complete, original K04 component commitment independently of any later retry holdout.

This answers the actionable incompleteness of the current source inversion lane rather than starting another donor or phrase transformation.

## Completed original-source experiment

- Source: unchanged, SHA-pinned `resources/evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Original PS-261003-0417 `ATTEMPT=1 STATE=REQUESTED` complete packet; byte order **big**, within-packet 64-bit word order **AB**. Selected `ATTEMPT=2 STATE=ACK` payload **completely withheld**. `ATTEMPT=3 STATE=REQUESTED` is an optional, independent replay diagnostic, never a condition for acceptance.
- P16 anchors: `(0,1,2,3,22,23,24,25,45,46,47,48,4,5,6,7)`, with the exact P16 cube labeling from Agent7. Initial solver timeout 350 ms, independent retry 700 ms only on UNKNOWN, max 32 model blocks; exact Boolean carry recurrence.
- The long original big/AB producer run is still in progress; this report freezes **the first 5,120 durably completed unique P16 source ledger records** (completion order is worker-unordered; they are *not* represented as an exhaustive contiguous P12-parent interval).
- All 122 initially UNKNOWN records in this frozen 5,120-record cohort were independently refined to four P18 children at 350→700 ms, with original packet source and frozen ledger fixed. Private P18-run wall time 138.72 seconds on one local worker. No public source-bearing CI was used.

| Gate | Exact completed count |
| --- | ---: |
| Source P16 cubes durably completed in frozen cohort | **5,120** |
| P16 terminal UNSAT on first two solver budgets | **4,998** |
| P16 still UNKNOWN after original 700-ms retry | **122** |
| Exact P18 child cubes evaluated for those 122 | **488** |
| P18 terminal UNSAT after adaptive split | **488** |
| P18 UNKNOWN | **0** |
| P18 SAT states and complete original-coupon candidates | **0** |
| Total P16 cubes now mathematically excluded in this frozen cohort | **5,120 / 5,120** |

A hypothetical K04 coupon cannot come from this **particular** group of xoroshiro128++ first-packet states, because the producer equations themselves have no states. A count of zero original commitment hits here is therefore *not* a full 16-byte coupon negative across the unvisited state space, other serializers, other generators or physical source. The first 5,120 completed P16 records represent 7.8125% of one 65,536-cube P16 initial-state partition; the other 60,416 remain outside this checkpoint, and further big/AB original-source computation is underway.

## Mathematical and synthetic validation

The Boolean circuit is the exact xoroshiro128++ recurrence. The first complete output `y0` and proposed `a0` fix `b0 = ROTR64(y0 - a0,17)-a0 mod 2^64`. The second output constrains the resulting exact state transition; all SAT states undergo direct native integer replay and full model blocking before terminal status. Splitting on a0 bits 8 and 9 is a set-theoretically complete, pairwise disjoint refinement, not an external 2-bit source hint.

- [P18 source-free implementation and baseline](../agents/agent50/k04_xoropp_p18_adaptive_synthetic.py): **8/8** deterministic planted complete-state recoveries, all **32/32** child partitions terminal UNSAT after state enumeration.
- An additional independent seeded local control series produced **30/30** exact planted-state recoveries and **120/120** terminal child outcomes, with zero UNKNOWN; this control used the same exact first-two-output Boolean constraints, but its extra seeds are not required by the published baseline.
- [Resumable P16 source-private state ledger](../agents/agent50/k04_xoropp_p16_private_ledger.py) retains every recovered full state and explicit terminal bucket, never only an aggregate hit counter. The [P18 local-only refiner](../agents/agent50/k04_xoropp_p18_private_refiner.py) consumes that cache, checks each full-coupon original commitment before a separate retry diagnostic, and preserves any exact hit in an out-of-repository 0600 escrow. They reuse Agent7's exact P16 circuit and original source-hash pins. The completed original-source cohort used a locally minimized first-two-output-only version of the same Boolean equations; its original-derived state ledgers are never committed.

The private source cohort and per-cube statuses are retained locally, not published. Reproduction of the exact source experiment is possible with an authorized local copy of the pinned non-PDF spool and the published original-safe P16/P18 runners, though timings and solver UNKNOWN dispositions can differ by environment.

## Interpretation and next computation

This is an actual completed **source-domain closure after adaptive refinement**, not just a suggested solver optimization. Exact P18 splitting resolved all 122 source P16 timeouts in the frozen cohort with no external witness. It validates a way to prevent previous source-scan UNKNOWNs from quietly becoming permanent exclusions or lost computational effort.

It does **not** identify the historical physical printer emitter and does **not** recover any K04 bits, K08 final wording, or a complete REC8/1 key. Continue disjoint source-domain enumeration, preserve states in a private cache, and apply an exact conditional refinement to each still-open cube. Do not promote source-conditional absence into a claim about the missing paper coupon.

**Status:** K01/K02/K03/K05/K06/K07 remain individually PASS; **K04/K08 MISSING**, combined REC8/1 INCOMPLETE.
