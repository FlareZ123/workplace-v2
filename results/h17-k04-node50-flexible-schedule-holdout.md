# H-17 node50 source-to-printer bridge: 4,230 alternative writer schedules

**Agent18, 3 November 2026. Conditional source-model test; no recovered K04 or K08.**

## Discovery objective

Prior studies found CRC-valid node50 recorder CONTROL values at MT19937 indices relative to 132 intact printer packets under the unproven p951 shared-generator hypothesis. Short local chains fit CPython-like metadata samplers, while the previously proposed homogeneous field order fails across additional original records. This investigation tests whether different emitter representations or stage order can connect independently source-matched node50 CONTROL sites seq45=-540 and seq70=-339, without reading disputed printer ACK2 or any K04/K08 commitment.

This advances beyond Agent23's single five-field stage/epoch, Agent28's selected local chains, and Agent25's seq9..13 stage path, by testing a frozen emitter schema throughout 25 original consecutive record transitions. Arbitrary separately fitted variable schedules are not in scope.

## Source and conservative model

[Read-only single-file reproducer](../agents/agent18/k04_recorder_alt_stage_sft.py) imports Agent2's existing p951 printer closure and validates original CRCs and recorder SHA256. Original spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Original recorder SHA256: 5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba.

Some source-native MT words are fully fixed, some fix only low31 native bits (two possible temperings), and many are entirely unknown. The sampler comparator rejects only when every possible known original output contradicts the recorded field or a necessary rejection. Unknown output words remain freely compatible. Therefore a negative under these permissive constraints is valid within the specified producer model; a seeming feasible path need not be globally realizable under all MT recurrence relations.

The frozen schematic contains one 32-bit CONTROL, AUX, timestamp, EVENT and LATCH per record, with strictly increasing native indices. Epoch offsets of 0 or 2 seconds relative to 21:09 UTC are permitted. Rejection samplers allow 1..12 draws per original field.

## Two distinct model portfolios

1. **1,350 fixed-order producer variants:** Preserve timestamp/event/latch/control/aux field order. Test AUX as rejection, top13 modulo or uint32 scaling; timestamp as rejection, opaque one/two draws, uint32 scaling or two-word CPython 53-bit scaling; EVENT as rejection, modulo or scaling; LATCH as rejection, getbits2 or scaling; either timestamp epoch; and 0 or 1 extra hidden draw before one of the four fields.
2. **2,880 alternative field orders:** All 120 permutations of five fields, timestamps as rejection or opaque 1/2 draws, LATCH as rejection or getbits2, plus 0..3 hidden draws per transition boundary. The same producer schema is required across all rows.

The second portfolio independently tries seq9=-793 through source-matched seq12=-775 and seq13=-769: **586/2,880** models admit both anchors under conservatively free unobserved state words. The first portfolio includes a genuine seeded Python rejection-sampler control of 24 record transitions, all passing.

## Original results

| Model portfolio | Complete emitter schemas | Connect seq45=-540 to seq70=-339 | Longest source-consistent prefix |
|---|---:|---:|---|
| Fixed field order, alternative field samplers | 1,350 | **0** | fails on or before seq66 |
| Alternative field orders, selected field samplers | 2,880 | **0** | fails on or before seq68 |
| **Total** | **4,230** | **0** | |

Counts are schemes, not original slot hashes or fully determined K04 coupons. The historical printer producer and shared recorder origin are still **unattested**. No K04 selected physical coupon bit or Emily's exact K08 wording was obtained. Original six individually PASS, combined still INCOMPLETE.

## Next discriminating mechanism

A generator-stage switch at an **originally identified** record batch boundary, separately sourced time draws or different per-record writer roles could explain the failed stationary sequences. Such a proposed switch must predict a withheld original CONTROL at an independently source-indexed position, and must eventually reach the selected K04 native state. Simply increasing latent draws or fitting a new schedule to each row would reintroduce unconstrained complexity without target information.

Original evidence, route sheet, official verifier, acceptance and canonical candidate were not modified.


## Extended bounded value-dependent hidden-stage rules, 3 November ~07:51 UTC

A later read-only [source-only value-gap SFT](../agents/agent18/k04_recorder_value_gap_sft.py) tests an alternative mechanism to the constant 0..3 omitted-draw budget above: the writer consumes a **row-value-dependent** number of extra native words at each record boundary. Model rules include previous/next original EVENT, LATCH, AUX, TIMESTAMP low two bits, sequence low two bits, previous/next EVENT grouped by tens, and AUX grouped by thousands, giving **14 explicit functions** including no extra draw. Combine 120 output-field permutations, three time-source representations (CPython range400, one opaque draw, two opaque draws), two LATCH serializers, two EVENT rejection bounds (39 and 40), and the 14 functions: **20,160 fixed value-dependent architectures**.

The genuine seeded CPython sampler positive passes. Independently observed seq9=-793, seq12=-775, seq13=-769 form a model-selection control: **996/20,160** architectures pass this early trio under the original intact printer's conservative known/unknown word masks. Freeze those 996 architectures before the independent late heldout chain seq45=-540, seq61=-417, seq63=-397, seq64=-390, seq70=-339. **Zero** reaches seq70, and none reaches past seq60. The existing [exact GF(2) one-bit LATCH57 falsifier](h17-k04-node50-latch57-symbolic-contradiction.md) separately guards against false positives from the permissive mask model.

Together with the earlier 8,460 frozen/constant-gap variants (two EVENT bounds), this documents **28,620 source-defined emitter-schedule alternatives**, all failing the stipulated full late original sequence. These are hypothetical architectures, not mutually exclusive real historical producer possibilities or recovery hashes. An original stage-consumption rule conditioned on a different recorded field or an independent genuine donor remains unexcluded. No selected printer coupon bit or K08 final word was inferred.
