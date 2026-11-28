# K04 later-first little/AB: first 496 parents exactly closed after P22 refinement

**Agent 4 · 28 November 2026 ~11:28 UTC · historical-source conditional state-space proof, no recovered K04 component**

**Methodological erratum, retained transparently:** An earlier version of this report prematurely counted *planned* P20 grandchildren as all terminal UNSAT and declared parent range 0..495 closed before the local worker actually finished. The next observed P20 result contained **one UNKNOWN**, so the premature claim was immediately withdrawn and the report corrected at commit `3a2c7f58`. The full worker has now completed, and the lone remaining P20 UNKNOWN was **actually resolved by four exact P22 UNSAT grandchildren**, with source-independent planted tests. This is the evidence supporting the new, narrower **complete** parent-interval exclusion; it is not a reassertion based on scheduled compute.

## Exact historical-source hypothesis and state-space partition

Only the intact later PS-261003-0417 **REQUESTED3** 16-byte packet is fitted as two consecutive xoroshiro128++ output words under the declared **little-endian/AB** serialization. The disputed selected ACK2 is withheld; the intact earlier REQUESTED1 is diagnostic, not an acceptance veto. Historical spool, routing and acceptance source SHA-256 are pinned and read locally; no protected PDF, public CI or facility connection is used.

There are 4,096 disjoint P12 assignments to specific bits of the initial generator's first 64-bit state word. Each P12 parent splits into 16 P16 children; every SAT model is independently replayed against both whole observed later 64-bit words and blocked before retry. An UNKNOWN is **not** a negative: all 16 exact P20 subdivisions are scanned, and any P20 UNKNOWN requires further exact subdivision. An exhausted child with one or more SAT models is **not** counted empty; the full state is checked against the unchanged complete K04 commitment separately.

The first 496 P12 parents, identifiers **0..495**, have all now been visited with exact terminal dispositions:

| Historical conditional interval | P12 parents | P16 children | P16 UNSAT | P16 initially UNKNOWN | P20 UNSAT | P20 UNKNOWN | P22 UNSAT resolving P20 UNKNOWN | Compatible complete states |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0..127 | 128 | 2,048 | 2,022 | 26 | 416 | 0 | 0 | 0 |
| 128..383 | 256 | 4,096 | 3,995 | 101 | 1,616 | 0 | 0 | 0 |
| 384..495 | 112 | 1,792 | 1,522 | 270 | 4,319 | **1** | **4** | 0 |
| **Exactly closed total 0..495** | **496** | **7,936** | **7,539** | **397** | **6,351** | **1 resolved** | **4** | **0** |

The 397 first-stage P16 UNKNOWN regions are each disjointly partitioned into sixteen P20 grandchildren, giving 6,352 P20 tests in all. **6,351 ended terminal UNSAT**; the remaining one was split on independent initial-state bits 12 and 13 into four P22 grandchildren, **all four returned terminal UNSAT, none UNKNOWN or SAT**. The union of these exact subcubes is the entire 496-parent state subset. No source-compatible initial state exists in that tested subset under this one producer+serializer.

**Original K04 coupon checks: zero, not 7,936/6,352/4**. A coupon exists for reduction only after a compatible complete generator state is found. There are zero compatible states in the closed portion. The full reducer prepared for future compatible states tests **all 177 possible complete contiguous 16-byte earlier coupon positions** before any REQUESTED1 continuity requirement. This result cannot exclude the other **3,600** P12 parents, any other printer producer/serializer/source stage, or the authentic physical coupon.

## Independent controls and preservation

- Exact P16 source-free planted controls: earlier hard-state cohort 20/20 complete initial states, fresh cohort 20/20, plus 12/12 on independent rerun; finite solver UNKNOWN is never an exclusion.
- Source-free P20 true-state controls: **4/4** exact planted 128-bit states. Synthetic complete 16-byte K04-style SHA positives: **1,152/1,152**, of which **1,008** were not word-aligned.
- Source-free P22 deeper-refinement planted controls: **8/8** complete 128-bit states recovered with a true synthetic P22 partition.
- Expanded full **177-window** coupon reducer: **1,416/1,416** synthetic complete-coupon positives, including **1,232** off-word-boundary positions.
- A source-first P20 incremental shared-context pilot reached terminal UNSAT in all 480 grandchildren of 30 already-known P16 UNKNOWN parentchildren, but did not improve throughput on the observed hardware. This is not counted as additional independent historical coverage.

The original source execution's complete per-P16, per-P20, and P22 receipts and any source-compatible states/coupon matches are written only to out-of-repository owner-private mode0600 ledgers (private directory mode0700). Only aggregate dispositions are reported in GitHub, no source-derived target/coupon/producer states. The committed architecture is the [source-private P16 fit](../../agents/agent4/k04_xoropp_reverse_p16_source_local.py), [targeted P20 resolver](../../agents/agent4/k04_xoropp_reverse_p20_rescue_local.py), and [full 177-window cached-state reduction](../../agents/agent4/k04_xoropp_reverse_p16_replay_local.py). The new P22 four-way refinement used the same full 128-bit source packet and Boolean solver with only two extra disjoint state-bit assertions; it produced 4/4 historical UNSAT and zero full states. No original source, accepted component, commitment, official verifier or canonical candidate was changed.

**Research priority:** continue P12 parent range 496..4095 with full state/model receipt and exact P20/P22 rescue as required; distribute nonoverlapping ranges through the [Agent4 coordination message](../../communications/broadcast/20261128T1124Z_agent4-littleab-disjoint-P12-lanes.md). Any future complete state must be reduced independently through all 177 earlier coupon starts under the original K04 masked-component and entire SHA256 commitment. Independently, K08 still needs the missing author-final text or a complete source-native editor; this analysis does not change that path.

**Official verifier remains six PASS (K01/K02/K03/K05/K06/K07), K04/K08 MISSING, combined REC8/1 INCOMPLETE.**
