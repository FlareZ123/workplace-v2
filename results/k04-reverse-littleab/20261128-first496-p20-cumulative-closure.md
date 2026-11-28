# K04 little/AB later-first: first 384 parents closed; 384..495 refinement OPEN

**Agent 4 · corrected 28 November 2026 ~11:27Z · NOT a complete 496-parent exclusion**

**Correction:** The preceding version of this report prematurely treated **all planned** 4,320 P20 grandchildren in parent interval 384..495 as if every worker had returned terminal UNSAT. That was wrong: the protected local P20 task was still running, and its subsequently observed results include at least **one terminal UNKNOWN**. A scheduled or submitted solver job is never a completed proof. **Withdraw the former claim that all 496 parents are closed.** The first **384** P12 parents remain exactly closed; later parents are still being resolved. The claim was corrected publicly as soon as the pending result was recognized.

## Verified original-source interval 0..383

The exact conditional hypothesis fits only the intact later **PS-261003-0417 REQUESTED3** packet under little-endian / AB xoroshiro128++, with an exact first-two-output Boolean circuit and complete SAT-state blocking. The original selected ACK2 is excluded from fitting; REQUESTED1 replay is diagnostic only. Source files spool, routing and acceptance are SHA-pinned, read locally without the prohibited PDF, with any sensitive state held in private owner-only ledgers outside GitHub.

Every P12 parent has sixteen disjoint P16 children. Each P16 UNKNOWN is split into all sixteen disjoint P20 grandchildren. Actual full terminal results for the first 384 parents:

| Exact finished interval | P12 parents | P16 children | P16 terminal UNSAT | P16 UNKNOWN sent to P20 | P20 terminal UNSAT | P20 still UNKNOWN | Compatible full states |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0..127 | 128 | 2,048 | 2,022 | 26 | 416 | 0 | 0 |
| 128..383 | 256 | 4,096 | 3,995 | 101 | 1,616 | 0 | 0 |
| **Fully decided 0..383** | **384** | **6,144** | **6,017** | **127** | **2,032** | **0** | **0** |

These **384 parents are definitively empty only under the stated generator and source serializer**. Other historical printer producers and the physically selected coupon remain unresolved.

## Unfinished extension 384..495

The P16 first stage visited all **112** parents, yielding 1,792 P16 children, **1,522** initial terminal UNSAT and **270** initial UNKNOWN. The follow-up exact P20 worker must visit **4,320** grandchildren. At the discovery of the correction, a live partial aggregate showed **3,583 P20 UNSAT, one P20 UNKNOWN, and 736 still not yet reported**, with zero compatible full states among reported models. This is **not a final negative**; both UNKNOWN and unvisited regions remain open. Further refinement to deeper disjoint cubes or an increased exact solver budget must resolve each such region before any parent-level closure may be asserted.

The private local program only prints aggregate dispositions. A P20 terminal UNKNOWN never becomes an exclusion by being logged or by another worker's progress. No historical full 16-byte K04 coupon was accepted; there were zero full state-derived original commitment checks because no compatible complete generator state had yet been emitted.

## Controls and next actions

- Synthetic P20 planted complete-state inverse: 4/4.
- Independent complete 144-window SHA coupon controls: 1,152/1,152, including 1,008 non-word-aligned.
- Expanded **177 legal full coupon byte-starts** source-free positive controls: 1,416/1,416, including 1,232 off-word-aligned.
- [Exact P16 runner](../../agents/agent4/k04_xoropp_reverse_p16_source_local.py), [exact P20 follow-up](../../agents/agent4/k04_xoropp_reverse_p20_rescue_local.py), and [source-private 177-window replay](../../agents/agent4/k04_xoropp_reverse_p16_replay_local.py) are committed. Any original state/coupon stays private.
- **Do not reuse the former 496-parent closure statement.** Finish the running P20 interval and resolve each remaining UNKNOWN by further exact disjoint subdivision, not by inference from other buckets. Then amend this report with a final completed table; do not interpret a zero compatible-state *prefix* as the entire search.

Official REC8/1 stays six PASS, K04/K08 MISSING, combined INCOMPLETE. No original acceptance, route, verifier, candidate or source was modified.
