# K04: completed xoshiro128+ two-request inverse, whole-coupon acceptance screen

**Agent 8 | 22 November 2026 | Original K04 commitment: zero matches in 786,384 whole-coupon assignments.** The historical six accepted REC8/1 components are unchanged; K04 and K08 are missing and combined acceptance remains incomplete.

## A distinct complete-coupon construction

Test the conditional hypothesis that an ESC-N printer job emitted each complete 16-byte payload as **four consecutive native 32-bit outputs** of the published Blackman/Vigna [xoshiro128+ 1.0](https://prng.di.unimi.it/xoshiro128plus.c) generator, with a 128-bit unknown internal state. xoshiro128+ outputs `(s0+s3) mod 2^32` and updates the state by xoshiro's four-register XOR/rotate transition. Its output function is **not the same** as xoshiro128** or xoroshiro128++ tested in earlier work.

No original H-17 evidence identifies xoshiro128+ as the real spool producer or asserts that the requests and ACK attempts share one generator state. Treat this as one explicit source-to-whole-coupon model, not an authenticated source reconstruction.

The surviving *unacknowledged* ESC-N requests give independent possible state anchors:
- PS-261003-0417 attempt **1**, 18:01 UTC, REQUESTED: `CD3E4F216ADB2FB180DA2AA90B33F7A4`.
- Same job attempt **3**, 18:03 UTC, REQUESTED: `44D53DFC29D7943A95D89371DA58EC64`.

Withhold the disputed **attempt 2**, 18:02 UTC, ACK, copied payload from every source inversion. The original source is the 133-row spool reconstruction, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Four fixed 32-bit serializer views per anchor cover both uniform word-byte orders and normal/reversed fourword order.

An exact 128-bit Z3 bitvector formula fits four complete output equalities and the actual xoshiro state update. Enumerate **every** initial-state model, blocking all four 32-bit registers after each model and retaining the termination status. Source-defined REQUESTED1 solutions advance in chronological order; REQUESTED3 solutions run the exact **inverse** state transition to recover earlier fourword packets. Under each reconstructed source state, generate complete fourword coupons at 65,532 positions: `4..65535` inclusively in the anchor-relative enumerated stream. Reassemble original 16-byte physical coupon bytes under the fixed serializer, XOR the original K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`, and SHA-256-test the **entire resulting 16-byte component** against the unchanged original K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Also attempt to predict the **whole opposite REQUESTED packet** as a separate independent source-heldout, rather than comparing just one 32-bit lane.

## Exact completed results

| Independent source anchor | Source-time direction | Serializer | Full 128-bit source-state preimages | End of enumeration | Complete K04 assignments | Original commitment / opposite REQUESTED whole-packet matches |
| --- | --- | --- | ---: | --- | ---: | --- |
| REQUESTED1 | Forward | Little-endian, normal fourword order | 1 | UNSAT | 65,532 | 0 / 0 |
| REQUESTED1 | Forward | Little-endian, reversed fourword order | 0 | UNSAT | 0 | 0 / 0 |
| REQUESTED1 | Forward | Big-endian, normal fourword order | 1 | UNSAT | 65,532 | 0 / 0 |
| REQUESTED1 | Forward | Big-endian, reversed fourword order | 0 | UNSAT | 0 | 0 / 0 |
| REQUESTED3 | Backward | Little-endian, normal fourword order | 2 | UNSAT | 131,064 | 0 / 0 |
| REQUESTED3 | Backward | Little-endian, reversed fourword order | 3 | UNSAT | 196,596 | 0 / 0 |
| REQUESTED3 | Backward | Big-endian, normal fourword order | 1 | UNSAT | 65,532 | 0 / 0 |
| REQUESTED3 | Backward | Big-endian, reversed fourword order | 4 | UNSAT | 262,128 | 0 / 0 |
| **Total** | | **8 fixed views** | **12 full-state preimages** | **8 UNSAT termination certificates** | **786,384** | **0 / 0** |

The 786,384 figure counts complete **assignments**, not globally deduplicated candidate byte strings. Every one was checked with the original 256-bit slot hash; there are zero accepted components in this bounded model. The opposite-request holdout was never produced in any tested source trajectory within the declared source window.

The first run with a 12-second Z3 timeout had one UNKNOWN view (REQUESTED3/little/normal). An independent focused longer original-source run resolved it in **30.753 seconds** to **exactly two** state preimages and then UNSAT; those two states produced 131,064 full-coupon candidates and zero target/holdout matches. A complete second original-source run with a calibrated **45-second per-solve timeout** reproduced all eight views, returned UNSAT after each complete state enumeration and independently confirmed 786,384 complete K04 comparisons, zero commitment hits and zero whole opposite-request matches.

## Positive and negative controls

- **10,000** deterministic genuine 128-bit xoshiro-state transition/inverse tests pass; each backward output round-trips exactly to the true earlier state.
- One planted genuine complete four-output packet recovers the planted 128-bit source state. Importantly the same four-output vector has **a second valid full-state preimage**. Both were independently enumerated and enumeration then terminated UNSAT, proving why taking just one plausible SMT model is insufficient.
- Four original-source views have 0 or 1 valid source states; the combined model count and full search are finite, with no solver timeout or preimage cap in the completed run.
- The selected 18:02 copied ACK2 payload does **not** enter state fitting, so a corrupted ACK cannot manufacture a source preimage.

The portable read-only [reproducer](../agents/agent8/k04_xoshiro128plus_twoanchor_sft.py) uses the Z3 shared-library C API and original `resources/` or the supplied ZIP as input, pins the spool SHA, performs synthetic controls, enumerates every source preimage and checks original K04 SHA-256. No file in the recovery evidence, canonical candidate, route sheet, acceptance commitments or original verifier was modified. Earlier attempts with different generator scramblers, fixed geometries and physical copy mappings are separate experiments, not additional coverage claimed here.

## Decision

The original K04 is **not** in the 786,384 coupon assignments reachable from these eight fully inverted xoshiro128+ source anchors within their 65,532 tested positions. The opposite unacknowledged request is also not reproduced, weakening the same-stream chronology. The bounded result does **not** exclude more than 65,532 intervening packets, arbitrary fourword permutations, separately reseeded attempts, corrupted REQUESTED fragments, another writer or source-native original physical media. It authenticates **zero** new physical selected K04 bits and contributes no K08 final caption wording.

Do not rerun the same eight state views or inflate the negative assignments into proof of a historical generator. A materially different source-to-full-coupon producer or genuine selected ESC-N physical original remains necessary. **Official REC8/1: six individual PASS; K04/K08 MISSING; combined INCOMPLETE.**


## 22 November follow-up: two original sibling configuration fields as independent complete anchors

To test a genuinely different source relationship beyond the unacknowledged printer REQUESTED fragments, the original route's \`K04.masked_component\` and \`K08.desk_nonce\` were independently inverted as hypothetical four-output xoshiro128+ objects. They are immutable commissioning routing fields, not reconstructed printer payloads.

Use the same four 32-bit serializer views and exhaust every Z3 state model to UNSAT. For each, advance 65,532 complete packet windows in both temporal directions, compare full packets against the other original configuration field, and SHA256-check every complete coupon after the **unchanged** K04 XOR mask. No K04 printed ACK is used as an input, and no supposed common commissioning producer is asserted without a full source-heldout prediction.

| Original 16-byte anchor | Valid complete internal state models across four views | Complete K04 candidate assignments | Other configuration field reproduced | Original K04 SHA256 hits |
| --- | ---: | ---: | ---: | ---: |
| K04 masked_component | 5 | 655,320 | 0 | 0 |
| K08 desk_nonce | 0 | 0 | 0 | 0 |
| **Total** | **5** | **655,320** | **0** | **0** |

All eight original-source solver views terminated **UNSAT** after their exact state enumerations, with no UNKNOWN status. The five states are two little-endian/reversed and three big-endian/normal from the mask. Their 655,320 assignments include both forward and reverse 65,532-position continuations for each complete mask state. This is an independent, bounded source-field screen and does **not** extend the two REQUESTED-anchor total of 786,384 to a single mutually source-authenticated coupon family. No underlying historical evidence associates the K04 mask and K08 nonce with xoshiro128+; absence of a cross-field prediction is evidence against only this exact model.

## Same-generator ordinary-printer full-source discriminator

A separate **source-only** necessary test asks if the 128 intact ordinary PS-0300..PS-0427 printer ACK packets are four consecutive native xoshiro128+ 32-bit outputs from a **single shared 128-bit state**, with a fixed 0..16 hidden-word gap after every packet. The low bit of each output \`s0 + s3 (mod 2^32)\` is exactly \`s0[0] XOR s3[0]\`. The whole internal transition is GF(2)-linear, so all low bits are exact 128-variable equations, permitting source-only elimination without a nonlinear solver or K04 acceptance feedback. Test both 32-bit endian choices and both whole-word orders, 4 × 17 = **68 complete source configurations**.

- **0/68** original fixed-gap models are consistent with all 512 original fullword low-bit observations.
- The first contradiction occurs by zero-based ordinary packet row **33** in every configuration. The initial 128 rows are selected from the source by their original consecutive job identifiers and ACK status, never by output values.
- Two independently generated genuine 128-packet xoshiro128+ positive fixtures with gaps 3 and 9, contrasting serializers, reconstruct exactly and have **no** source contradictions.

The read-only portable [low-bit producer SFT](../agents/agent8/k04_xoshiro128plus_sourcewide_lowbit_sft.py) checks the pinned original spool SHA, synthetic generator/serializer controls and all 68 historical models. It is disjoint from the selected REQUESTED exact-state inversion: a printer may reset per incident, use variable gaps, copy imperfectly or produce a different type of payload, so this source-wide failure does not negate the exact 786,384 selected-event hashes.

**Combined decision for the xoshiro128+ family:** no original K04 commitment hit, no authentic cross-field witness, no ordinary-source uniform-gap fit, and no new K08 caption. The original six PASS slots are unchanged. Avoid another sweep of the identical serializer and uniform-gap models.
