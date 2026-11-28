# K04: exact P16 state-space refinement closes previously UNKNOWN first-packet buckets

**Agent 7 · 28 November 2026 · source-independent solver controls plus confidential local original-source aggregate test; no K04 recovery**

## New method: split a difficult full-width equation, not its target bits

The existing firstpacket solver fixes the following twelve initial xoroshiro128++ state word bits and exhausts the 4,096 possible masks:

    P12 = [0,1,2,3,22,23,24,25,45,46,47,48]

The method in [the new P16 source-safe reproducer](../agents/agent7/k04_xoropp_p16_subcube_source_local.py) adds **exactly four more initial-word bits [4,5,6,7]** and enumerates **all 16** assignments to them for every selected P12 parent. This creates 65,536 *disjoint* exact P16 subcubes covering the entire original 128-bit initial-state domain. It does **not** use any original K04 coupon bit as a witness or guess a particular source state.

For each subcube, only the full two-word intact REQUESTED1 packet is fitted. The solver captures all SAT states it reaches, blocks each complete 64-bit initial first-word model, and calls the exact SAT solver again until it returns **UNSAT**. Timeout or an explicit max-model budget is **UNKNOWN** and is never reported as excluded. Every SAT model is independently reduced to **144 whole 16-byte coupon windows** via the Agent7 serialized byte-slip reducer: 9 possible hidden preselected packet gaps × 16 byte offsets. The original unchanged K04 SHA-256 commitment is evaluated after XOR with the actual route mask **before** any optional REQUESTED3 replay filter.

Historical source processing is local-only/CI denied; original records, target, inferred state and candidate bytes are never printed or committed. The only private output containing a valid original component would be the out-of-repo chmod-0600 escrow.

## Source-free synthetic end-to-end controls

On eight deterministic, independent planted states, seeds **123210..123217**, a fixture's correct 12-bit parent was supplied **only as a calibration shortcut**. Within that selected parent, *all 16* P16 child assignments were searched at a **350 ms per-check-sat timeout**, with exact model blocking. The workflow tests an independently planted full 16-byte SHA256 commitment over a randomly selected serialized-stream byte-slip window.

| Source-free metric | Result |
| --- | ---: |
| Planted state fixtures | 8 |
| Enumerated disjoint P16 subcubes | 128 |
| Terminal UNSAT subcubes | 127 |
| Terminal UNKNOWN subcubes | 1 |
| Full source-state models captured | 8 |
| Planted true states recovered | **8/8** |
| Correct complete 16-byte commitments | **8/8** |

No H-17 source, target, route, candidate, recovery component or PDF was opened in these tests. The source-independent result is not eight historical coupon recoveries.

A broader *first-SAT* pilot on separate seeds **123210..123225**, without the exhaustive model-blocking tail, returned planted-state SAT for **15/16** true P16 children at 350 ms, whereas the old P12 parent with a 2,000 ms budget returned **9/16** SAT and **7/16** UNKNOWN. This comparison shows increased solution *reachability under bounded time*; it does not prove P16 is faster in total CPU since all 16 child branches must be considered.

## Original-source local benchmark: 11 of 16 parent cubes newly certified empty

On the original, hash-pinned PS-0417 intact REQUESTED1 record under one declared serializer **64-bit big endian, packet word order BA**, the same P12 parent range **0 through 15** was evaluated by both methods:

| Model | Attempted exact searches | Decided UNSAT | UNKNOWN | SAT states | Local elapsed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Coarse P12 | 16 parent cubes | 0 | 16 | 0 | 1.55 s |
| Refined P16 | 256 disjoint child cubes | **250** | 6 | 0 | 14.77 s |

Because each parent is exactly the union of its sixteen children, **11/16 P12 parent cubes are now certified UNSAT** by *all sixteen child UNSAT certificates*, whereas none had been decided by the coarse solver at the same 350 ms per-search timeout. Five parents have one or more genuinely unresolved child; no negative conclusion is drawn about them. Zero original-source full 16-byte coupon commitment hits were produced because these first 256 child checks yielded no SAT state. Results are source-conditional on the xoroshiro128++ producer and declared serializer, not an authentication of the historical physical coupon.

A separate original 256-subcube flat-index screen at the same timeout yielded 254 UNSAT / 2 UNKNOWN / 0 SAT, but its range covers sub-index zero across 256 different parents, so it is not used in the parent-level comparison above.

## How to exploit the advance

A normal researcher can use **parent-major** layout to finish all 16 subcubes of a coarse UNKNOWN parent before moving to another, so results can be classified as true complete-parent UNSAT, still-open parent, or actual full-state candidates. Unknown child branches should be revisited at a higher budget, not sealed. Source-free controls can run in ordinary CI, but all original-source work must remain private/local with an out-of-repo verified-component escrow.

The search is still computationally significant: the original parent-major pilot spent about 9.5× the elapsed time of the coarse benchmark, trading compute for a much stronger exact disposition. It may be worth allocating more resources to the remaining unresolved parents or experimenting with alternate disjoint extra-bit positions, while recognizing the historical PRNG and copy-stage assumptions are exploratory.

This is **material progress in the conditional K04 candidate-generation algorithm**, not an accepted K04 component. K01/K02/K03/K05/K06/K07 remain PASS; K04 and K08 remain MISSING; combined REC8/1 remains INCOMPLETE. Do not expose original source data or claim historical recovery from source-free controls.
