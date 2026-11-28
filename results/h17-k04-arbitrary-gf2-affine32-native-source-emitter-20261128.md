# K04: native-word arbitrary GF(2)-affine issuer, exact full-class reconstruction gate

**Agent 39 | 28 November 2026 | new whole-coupon producer class, original-source falsification | no component recovered.**

## Why this target reaches a different architecture

A printer issuing 16-byte opaque coupons may maintain a native 32-bit register updated at each generated word, rather than a 128-bit packet RNG, a keyed hash or a copied-source mosaic. Unlike named xorshift/PRBS/LCG generator guesses, test the **entire class of all 32-bit binary affine next-word transformations**:

```text
x[n+1] = M*x[n] XOR c
M: any 32x32 matrix over GF(2)
c: any 32-bit fixed vector
```

Thus no particular shift constants, seed, feedback polynomial or scrambler parameters are preselected. All 1,056 binary matrix/constant bits are determined by sufficiently many **intact original input→next-word transitions**. The broad affine class includes every fixed xorshift32 and linear/affine LFSR whose 32-bit output is its actual state, but excludes nonlinear output scramblers, modular-addition carries, hidden internal states and per-packet resets. No source proves that this is the historical printer implementation.

Freeze two non-overlapping physical stream topologies:

1. **Serial interleaving:** one category-specific 32-bit map emits the four words of each 16-byte packet consecutively. The map is trained on the intact ordinary printer packets under the globally ordered sequence, original CLASS group, DEST group, or ordered CLASS×DEST group. Repeat once with the original four native words reversed inside each packet. These are **8** model assignments.
2. **Parallel word lanes:** four independent 32-bit maps, one per aligned native word lane of successive packets, keyed by the global, CLASS or DEST printer routing cohort. These are **3** model assignments; reversing whole packet words only permutes lane names, so it adds no new model.

Within-word byte/bit reversals also merely conjugate the class of **arbitrary** GF(2)-affine 32-bit matrices, and so are already covered exactly without duplicate runs. Total **11** genuinely distinct topology/routing assignments.

The copied `PS-261003-0417` attempt-2 ACK payload is **excluded from all training, fitting, predictions and candidate generation**.

## Rank and heldout mathematical gate

Write each source-native input word as 33-bit vector `v=(1||x)`. Its output is a GF(2)-linear function `F(v)=M*x XOR c`. Construct an **online GF(2) basis** from intact original word transitions, preserving the earliest 33 independent input→output pairs. Once the basis reaches rank 33, there is one exact affine map consistent with those independent samples, with **no remaining coefficient choices**. Every later dependent source input yields a **predicted full 32-bit output**; if the corresponding intact source output disagrees, the entire proposed class is impossible for that category. No SAT timeout or seed sampling is involved.

For the model's 18:02 physical coupon, after learning the same source category's map(s) from ordinary printer rows, take the intact 18:01 `RECOVER/bench` REQUESTED1 packet as the selected predecessor. Serial models emit the next **four** native words by four consecutive map applications; parallel models update each native word lane once. Reassemble sixteen complete physical-coupon bytes, XOR the original K04 route mask, and compare SHA256 of the complete 16-byte component to the unchanged K04 commitment. The intact 18:01 full packet (from the last ordinary category packet) and the 18:03 full REQUESTED3 packet (from the hypothetical coupon) provide separate whole-object source holdouts. No source-failing model is accepted just because it can emit a candidate.

A seeded synthetic test generates arbitrary full-rank affine 32-bit maps, unobserved starts and 200-step streams, learns the map by its own earlier source words, and predicts every remaining withheld native word exactly. **12/12 independent synthetic source-fit controls PASS**. No historical candidate bytes are part of those controls.

## Executed original-source results

Original source: `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Original 128 ordinary jobs were retained; selected 18:02 copied payload was not read. The exact selected-job/time/class/destination/source mask and original target commitment are asserted before candidate checks.

| Source/topology model | Configurations | Full **independent 16-byte** original packet holdouts | Whole-packet matches | Complete original K04 checks | K04 matches |
| --- | ---: | ---: | ---: | ---: | ---: |
| Serial, global | 2 | 238 | 0 | 2 | 0 |
| Serial, CLASS | 2 | 202 | 0 | 2 | 0 |
| Serial, DEST | 2 | 198 | 0 | 2 | 0 |
| Serial, CLASS×DEST | 2 | 88 | 0 | 2 | 0 |
| Parallel word lanes, global | 1 | 93 | 0 | 1 | 0 |
| Parallel word lanes, CLASS | 1 | 16 | 0 | **0 (ambiguous selected lane)** | — |
| Parallel word lanes, DEST | 1 | 20 | 0 | 1 | 0 |
| **Total** | **11** | **855** | **0** | **10** | **0** |

Every model has original-source affine contradictions, from 104 through 478 dependent original word-transition disagreements per model. This is stronger than just a missing target hash; its asserted generator rule fails to replay the *unquestioned* printer history. The ten models that determine complete selected physical coupons also fail both same-job REQUESTED1/REQUESTED3 full-packet controls and all ten original K04 target commitments.

The **parallel CLASS** model is treated differently: despite its intact source contradictions, at least one selected 32-bit lane still lies outside the fitted 33-vector source span, so it does **not** determine a unique 16-byte coupon. No arbitrary coefficient completion or guessed K04 value is substituted; the actual target checks are ten, not eleven.

## Scope and decision

This source-constrained class is far broader than a named 32-bit PRNG seed sweep and has a strict independent original-data consistency test. It differs from Agent39's same-day **GF(2^128) second-order category** reconstruction and **xoshiro128** packet-state multiplexing, and from previous **GF(256)** byte-symbol Berlekamp–Massey work. Those engines have different state dimensions, coefficient rings, output transforms and prediction rules. All point away from the notion of an uninterrupted low-order ordinary-printer state generator, not to any authenticated physical-coupon value.

**Excludes:** the exact serial/parallel 32-bit affine source-continuity publisher classes under stated original routing chronology and complete native word observations. **Does not exclude:** hidden-state output scramblers, per-job reseeding, unrecorded skips, nonlinear generators, missing native print queue stages, or the physical coupon itself. The 18:02 ACK's copied bytes remain unauthenticated, and the accepted K04 preimage is not inferred from any failed model.

**Status:** K01/K02/K03/K05/K06/K07 still individually PASS; K04 and K08 MISSING; full REC8/1 INCOMPLETE. No official source/acceptance/verifier/candidate changed, and no original-sourced candidate words or state parameters are published.

Reproduction: [Agent39 original-source/synthetic exact affine 32-bit publisher](../agents/agent39/k04_affine32_native_issuer_sft.py). Run locally with the original authorized archive root; the runner reports only rank-derived source mismatch counts, complete original holdout dispositions, synthetic positive controls and original commitment hit flags.
