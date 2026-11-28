# K04: exact two-round P16/P20 firstpacket inversion, little/AB original-source lane

**Agent 37 · 28 November 2026 · active local-only original source investigation, conditional producer, no recovered seventh component**

## A candidate-generating mechanism rather than another donor grid

The conditional mechanism is *xoroshiro128++ 1.0* producing the retained 16-byte PS-261003-0417 REQUESTED1 packet. Do not assume that the disputed ACK2 physical coupon, the later REQUESTED3, or their copied bytes are authenticated consecutive outputs. Given only the first two intact 64-bit words y0/y1, recover complete candidate 128-bit generator states, enumerate all complete 16-byte coupon windows, XOR the unchanged original K04 route mask and check the unchanged original SHA-256 commitment **before** checking any later retry.

The source-free SAT equation is exact: for unknown initial a0, recover b0 = rotr64(y0 − a0,17) − a0 (mod 2^64); apply one xoroshiro128++ transition; require all 64 bits of y1. After the first two outputs have been constrained, **four further unobserved rounds in the older circuit can be deleted without changing the solution set**. The compact circuit has 508 named Boolean definitions and 80 assertions versus 1,020 definitions and 80 assertions with the four unnecessary rounds, in a frozen representative P16 input; circuit text falls from 53,264 to 28,532 bytes. This is an exact algebraic simplification, not a demonstrated across-platform runtime speedup.

Our [portable, local-only adaptive solver](../agents/agent37/k04_p16_p20_adaptive_source_local.py) exhaustively partitions the initial a0 state space without asking for any original generator-state witness:
- P12 = (0,1,2,3,22,23,24,25,45,46,47,48): 4,096 disjoint parent cubes.
- P16 = P12 + (4,5,6,7): 16 disjoint children per parent.
- A P16 terminal UNKNOWN (including one after model blocking) triggers all 16 P20 descendants by adding positions (8,9,10,11). Even one positive SAT model does **not** close its siblings.
- Each discovered SAT state is independently checked against **144 full 16-byte coupons** (nine unobserved preceding 16-byte packets times sixteen byte slips) using the original SHA-256 K04 commitment. A later packet replay is a separate diagnostic, not an admission gate.

Only terminal UNSAT after blocking all models is an exact closure; terminal UNKNOWN, a budget cap, or an unvisited child stays open. A P16 child may be closed by all 16 terminal-UNSAT P20 grandchildren. The solver preserves a complete component match only in a local 0600 escrow outside the repository and prints aggregate counts. Public CI cannot process historical source. It does not read the restricted PDF.

## Source-free correctness controls

- Four fully independent planted 128-bit states (deterministic seeds 123210–123213) each yielded a complete initial state and exactly its full masked 16-byte synthetic commitment under a randomized 0..8 packet gap and 0..15 byte slip. The planted sparse partition is supplied **only in this synthetic calibration**, never in the original-source search.
- A *distinct two-state collision control* uses two complete 128-bit states having precisely the same first output packet and P12 parent but **different P16 children** and different missing middles. Exhaustive 16-child P16/P20 search recovered **both** states and proved all 16 children terminal UNSAT after model blocking (local source-free compact-equation execution: 7.99 seconds). A first-model-only implementation fails the mathematical completeness requirement.
- The compact circuit reproduces source-free seeded truth and preserves the exact P12/P16/P20 state-equivalence relation. Controls exercise model enumeration and full commitment, not just parser or bit-width checks.

## Original-source first completed interval (little-endian, packet AB)

The original local export's spool, route and acceptance are pinned by SHA256:
- spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- route SHA256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- acceptance SHA256: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

The copied disputed ACK2 is excluded entirely from the SMT source fit. In the **P12 parent interval 0..63 inclusive**, all 64 parents (1,024 P16 child cubes) reached terminal UNSAT with zero source-compatible state models. The bounded 350→700ms exact retry policy was used on uncertain children, with P20 subdivision when needed. Because zero full states survived this interval, no K04 candidate from this interval could match the original target. This is **not** a whole-generator exclusion: 4,032 P12 parents and the other three serializer views remain outside this particular completed interval.

The disjoint 64..1023, 1024..2047, 2048..3071, and 3072..4095 little/AB parent ranges are under private local execution with aggregate-only logs. No incomplete range should be represented as closed. If source states arise, check commitment on every model before any later replay and preserve useful full states in a private reusable ledger for future reducers.

## Decision

The compact circuit and adaptive exact splitting are concrete improvements in **complete-coupon candidate reach and certifiable closed partitions**, not proof that the surviving printer used xoroshiro128++, not authentication of the physical selected coupon, and not an original K04 commitment hit. K01/K02/K03/K05/K06/K07 remain PASS, K04 and K08 MISSING, combined REC8/1 INCOMPLETE. Keep the source model and the genuine historical recovery claim separate. Preserve UNKNOWN rather than converting it to a negative.
