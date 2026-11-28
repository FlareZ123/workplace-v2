# K04 later-first little/AB — fully closed first 496 source-state parents

**Agent 4 · 28 November 2026 · historical-source exact conditional exclusion, no authentic K04 component**

This is the cumulative continuation of [the first 128-parent proof](20261128-first128-p20-exact-closure.md), not a second independent producer or a repeat of its source reads. The declared hypothesis fits the **first two intact words of PS-261003-0417 REQUESTED3 only**, interpreted as little-endian order AB xoroshiro128++ outputs. It neither uses the disputed selected ACK2 copy nor presumes that REQUESTED1 is from the same generator. All original-source work ran locally outside GitHub Actions.

## New cumulative closure

The original pinned printer spool supplies the exact intact 16-byte later packet. Its two-output inverse is solved by partitioning all initial first-generator-word possibilities into **4,096 P12 parent cubes × sixteen P16 children**, fixing a disjoint set of 16 unconstrained state bits purely as a search partition (not guessing historical state information). Every SAT state is checked against the full observed later packet by integer replay, then blocked until terminal UNSAT or UNKNOWN. The first-stage run covered every **7,936** P16 child in parent range **0..495**, with durable private per-child status and full-state receipts.

A timeout is **not** an exclusion. Every one of the **397** P16 UNKNOWN regions in this interval was then split into all **sixteen** disjoint P20 grandchildren, adding state-word bits 8..11. All **6,352 grandchildren** were proved terminal UNSAT after the same independent 350→700ms bounded solve and within-child model blocking. The P20 result therefore completes the proof that the whole initial-state domain of these 496 P12 parents is empty under this exact two-output/serializer/generator model.

| Original source conditional domain | P12 parents | P16 cubes | P16 UNSAT | P16 UNKNOWN | P20 grandchildren terminal UNSAT | P20 UNKNOWN | Full compatible states |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0..127 | 128 | 2,048 | 2,022 | 26 | 416 | 0 | 0 |
| 128..383 | 256 | 4,096 | 3,995 | 101 | 1,616 | 0 | 0 |
| 384..495 | 112 | 1,792 | 1,522 | 270 | 4,320 | 0 | 0 |
| **Total 0..495** | **496** | **7,936** | **7,539** | **397** | **6,352** | **0** | **0** |

All 496 parents are **exactly closed under this model**; the other **3,600 P12 parents** have not been excluded by this result. As zero source-compatible states arise in this interval, there were **zero historical original 16-byte coupon reductions**, not 7,936 or 6,352 attempted commitment matches. Any later SAT state must be checked against the source K04 XOR+SHA256 commitment independently of REQUESTED1. The reusable full-state reducer now covers **all 177 legal contiguous 16-byte coupon starts** among 192 preceding source-hypothetical bytes instead of only the 144 starts nearest the later request.

## Controls, integrity, and limits

- Four independent synthetic P20 exact inversions recovered complete planted 128-bit states.
- A separate source-free exhaustive artificial coupon test recovered **1,152/1,152** planted SHA256 matches under all four packet serializers, with **1,008** byte offsets not on 64-bit boundaries.
- The expanded 177-window reducer independently passed **1,416/1,416** artificial whole-coupon commitment positives, **1,232** off-word-boundary.
- An alternative shared-Z3-context P20 solver was run on **30** already unresolved original P16 children, proving **480/480** grandchildren UNSAT with zero UNKNOWN/compatible states. Under observed local resource contention it was **slower** than the independent grandchildren worker, so it is not the default rescue algorithm. This is a bounded throughput observation, not an independent new historical exclusion.
- The local source reader asserts pinned SHA-256 for only the ordinary spool, routing and acceptance JSON; the prohibited BX25-08 PDF and no native facility or service is touched. Full original state/coupon/commitment values, if ever recovered, are confined to out-of-repository owner-only ledgers and escrow. Only aggregate bounds and dispositions appear here.
- The script chain is [Agent4 P16 source runner](../../agents/agent4/k04_xoropp_reverse_p16_source_local.py), [P20 exact rescue](../../agents/agent4/k04_xoropp_reverse_p20_rescue_local.py), and [177-byte complete coupon replay](../../agents/agent4/k04_xoropp_reverse_p16_replay_local.py). The executed historical code was an independent local implementation with the same exact Boolean circuit, P16/P20 disjoint geometry, whole-packet replay and source mask/acceptance checks. This repository preserves reproducible source-safe methods, not any private historical models.

The only warranted conclusion is **absence of a compatible xoroshiro128++ full state for this one original later-packet presentation in P12 parent range 0..495**. Other parent intervals, byte/word presentations, hidden source stages, producer models and the authentic physical coupon remain open. This does not recover K08 final envelope wording. The authoritative original combined REC8/1 remains **INCOMPLETE**: K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING.

**Next milestone:** continue beyond parent 495, rescues pending P16 UNKNOWNs with exact P20, and combine future disjoint parent intervals until the original state space is closed or a source-compatible state reaches the full commitment gate. Distributed nonoverlapping parent lanes were requested in [Agent4's broadcast](../../communications/broadcast/20261128T1124Z_agent4-littleab-disjoint-P12-lanes.md) to accelerate this without duplicating original-source work.
