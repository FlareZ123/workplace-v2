# H-17 K04: later-request reverse xoroshiro historical big/AB quarter scan

**Agent 6 · 28 November 2026 · first original-source execution of the later-first route for one declared serializer; K04 remains unrecovered.**

## Decision question

Agent 1's source-free later-first model asks a genuinely different causal question from the active forward REQUESTED1 scans: if the selected physical ACK2 coupon and the later intact REQUESTED3 packet shared an issuer state, while REQUESTED1 may have belonged to an earlier/reset stream, can REQUESTED3 alone determine a complete earlier coupon?

This run executes that model against the original non-PDF source for **big-endian / word order AB** and preserves exact solver disposition per P12 cube. The copied selected ACK2 payload is never read or fitted.

## Frozen model and acceptance order

The existing source-free implementation treats the intact PS-261003-0417 REQUESTED attempt-3 packet as two successive xoroshiro128++ 1.0 output words. The unknown 128-bit state is partitioned by the already-tested 4,096 sparse P12 cubes

`(0,1,2,3,22,23,24,25,45,46,47,48)`.

Within each cube the exact Boolean output-conditioned solver blocks every recovered state until the cube returns terminal **UNSAT** or **UNKNOWN**. For every recovered state, the exact invertible xoroshiro transition is walked backwards and all 18 complete two-word coupon windows immediately preceding the later request are serialized big/AB, reduced through the unchanged K04 route mask, and compared with the unchanged full K04 SHA-256 commitment. REQUESTED1 is only a separate chronology diagnostic and cannot veto a commitment hit.

A source-free planted control recovered the exact unknown 128-bit planted state in its correct P12 cube and then closed that cube to UNSAT after model blocking. The inverse transition and every complete coupon window had already passed Agent 1's independent synthetic controls.

## Original-source result: cubes 0..1023

Local original-source execution used four workers and a **5,000 ms solver budget per cube**. The contiguous first quarter of the P12 namespace produced:

| disposition | count |
| --- | ---: |
| cubes queried | **1,024 / 4,096** |
| exact terminal UNSAT | **414** |
| terminal UNKNOWN | **610** |
| cubes with one or more SAT models | **0** |
| recovered 128-bit models | **0** |
| complete coupon windows generated | **0** |
| original K04 commitment hits | **0** |

The distinction between the last three rows is important. No historical state was recovered in this quarter, so the reducer had no complete coupon to hash. This is **not** a claim that 1,024 generated coupons missed the target. It is an exact exclusion of the declared model in 414 P12 cubes and an unresolved timeout disposition in 610 cubes.

The remaining 3,072 cubes were not part of this checkpoint. The 610 UNKNOWN cubes also remain live and require a larger or different solver budget before they can be excluded.

## What advanced

Before this run, the later-first reverse route had source-free controls but **no historical original-source scan**. This checkpoint converts one quarter of one declared serializer's 4,096-cube domain into a replayable historical disposition map: 414 anchors are now closed exactly, 610 are explicitly marked for retry, and future work can continue at cube 1024 without spending compute on the closed prefix again.

No state word, source-selected packet value, candidate coupon, component, or private escrow value is published here. No PDF was opened. Original evidence, routing, acceptance, verifier and canonical candidate were unchanged.

## Next decision

Continue big/AB from cube 1024 under the same exact model-blocking policy, then revisit only the UNKNOWN subset with a larger budget. Other serializers are separate hypotheses and should retain their own ledgers. A future SAT state must still have every one of its 18 complete backward coupon windows checked against the original K04 commitment before any optional retry-packet diagnostic.

**Archive state after this checkpoint:** K01/K02/K03/K05/K06/K07 remain accepted; K04 and K08 remain unresolved; combined REC8/1 remains incomplete.
