# H-17 K04: exact XORWOW same-job four-word gap inversion

**Agent 3, 5 November 2026 | Original-source necessary-condition exclusion, zero physical K04 bits recovered.** This is a distinct target-facing producer model. It uses no candidate-byte guesses, acceptance hash during model fitting, or compromised selected ACK2 payload. The actual printer firmware and capture-stage generation order remain unauthenticated.


## 5 November extension: arbitrary 32-bit Weyl increment, fully excluded

**Stronger source-only bound:** the canonical `362437` increment is no longer assumed. Treat **both** the initial Weyl term `d0` and the per-output additive increment `step` as independent unknown 32-bit integers, with every one of their `2^64` possible assignments permitted. Keep the identical five-word XORWOW GF(2) recurrence, 4-output per same-job attempt, original 18:01/18:03 sources, and eight serializer layouts. This is a genuinely broader producer class, including canonical XORWOW as a strict subset.

Crucial exact observation: for any known output `Y_t`, the native word `V_t = Y_t − d0 − t*step mod 2^32` has its low `b+1` bits determined *entirely* by the low `b+1` bits of **both** parameters. Therefore the 96 source-only GF(2) parity equations admit **four-way 2-adic lifting** of every surviving parameter-pair prefix, with all independent parity checks of maximum involved bit `b` enforced at stage `b`. This inductively covers every 64-bit parameter pair without an infeasible naive search. The 160-register-bit rank and exact missing 128-bit projection remain unchanged. No partial SHA or target payload data enter the inference.

All eight historical layouts have **zero surviving parameter pairs** before or at bit16 of the two 32-bit parameters. Exact first-pruning histories and reproducible code are in [the unrestricted-Weyl source-pinned SFT](../agents/agent3/k04_xorwow_any_weyl_sft.py), which uses the same [five-word basis derivation](../agents/agent3/k04_xorwow_gap_weyl_sft.py). Eight layouts × two genuinely simulated 12-word XORWOW emitters, with increments `362437` and `0xA5A5BEEF`, independently recover the **unique true pair** and **entire 16-byte withheld selected coupon** from the other eight source outputs: **16/16 synthetic positives**. Original eight layouts: **0/8 compatible emitters**, no candidate reaches the K04 commitment.

The source still does not attest XORWOW, constant additive-step behavior, fixed four-output spacing, or the REQUESTED-to-ACK producer equivalence. This extension excludes that finite **full 32+32-bit Weyl-parameter class** under precisely those assumptions, while leaving different source generators, gap patterns and missing physical media open. The six genuine accepted REC8 slots remain unchanged.

## Source-bound proposed producer and missing coupon

The original print reconstruction contains three consecutive **same-job** RECOVER records for logical ESC-N's `PS-261003-0417`:

| UTC | Attempt/status | Actual copied payload |
|---|---|---|
| 3 October 18:01 | 1, REQUESTED | `CD3E4F216ADB2FB180DA2AA90B33F7A4` |
| 3 October 18:02 | **2, ACK (selected physical coupon missing)** | Disputed unauthenticated export `A9A9DC5731A5E2AE879C47215C2559D5` |
| 3 October 18:03 | 3, REQUESTED | `44D53DFC29D7943A95D89371DA58EC64` |

Hypothesis: a *canonical five-register XORWOW* issuer emitted four successive native uint32 words for each attempt, with the 18:02 ACK2 occupying four **missing** outputs between the two intact original requested-frame packets. The native recurrence uses `t=x XOR (x>>2)`, `v'=(v XOR (v<<4)) XOR (t XOR (t<<1))`, rotate five 32-bit registers, and emitted `v' + d` modulo 2^32, with Weyl `d += 362437` each output. Initial five register values and initial 32-bit Weyl term are unknown; the independent selected copied ACK2 is **excluded from deriving either**.

This differs from previously tested fourword xorshift128(+), 128bit modular-ring affine retry, and cross-source finite-field affine interpolations. Here the complete missing 128-bit packet is reconstructible from two original intact **same-job** fourword records if the exact issuer is consistent. There is no historical claim that XORWOW was the actual printer algorithm.

Test eight complete plausible serializations of each 4-word packet: within-word big/little endian, original/reversed fourword order, ordinary/per-byte-reversed bit orientation, all held constant across the two intact packets and selected reconstructed frame.

## Complete exact elimination without a 2^32 brute search

Each XORWOW five-register transition is *linear over GF(2)* before the Weyl addition. Symbolically propagate each of 160 initial state basis bits through twelve output stages. The eight preserved 32-bit outputs at stages `0,1,2,3,8,9,10,11` yield **256 GF(2) equations of rank160**, hence exactly **96 independent necessary parity checks**, plus a unique linear reconstruction expression for every bit of the four withheld native outputs at stages4..7. These equations are independent of the original selected copied packet.

For each trial Weyl initial word `d0`, convert the observed outputs to the native XOR-linear outputs by subtracting `d0 + stage*362437 (mod 2^32)`. Each parity equation mentioning output bits at most `b` depends only on `d0`'s low `b+1` bits. Therefore lift surviving `d0` bit prefixes from low bit0 through bit31, **testing every possible next bit** against exactly the newly applicable parity equations. This 2-adic lifting is exhaustive over all 2^32 possible initial Weyl terms, with no omitted high-bit effects.

The source-specific parity-equation frontier is exactly 0 constraints at bits0..3, 3 new equations at each bit4..29, 6 at bit30 and 12 at bit31. Original prefix survival:

| Endian / reversed word order / bit-reversed bytes | Survivors for d0 low bits, from bit0 until extinction |
|---|---|
| little / no / no | 2, 4, 8, 16, 4, 2, **0** at bit6 |
| little / no / yes | 2, 4, 8, 16, 2, **0** at bit5 |
| little / yes / no | 2, 4, 8, 16, **0** at bit4 |
| little / yes / yes | 2, 4, 8, 16, 3, **0** at bit5 |
| big / no / no | 2, 4, 8, 16, 3, **0** at bit5 |
| big / no / yes | 2, 4, 8, 16, 3, 1, **0** at bit6 |
| big / yes / no | 2, 4, 8, 16, **0** at bit4 |
| big / yes / yes | 2, 4, 8, 16, 3, **0** at bit5 |

**None of the eight layouts has even one original-source-compatible full XORWOW state.** As a separate computational check, a compiled C implementation enumerated **8 × 2^32 = 34,359,738,368 complete initial Weyl assignments**, across multiple local shard executions. Every layout reported zero source-compatible assignments. This computational check confirms the algebraic prefix result; it is a source-only rejection before checking the K04 SHA256.

## Positive controls, reproduction and boundaries

Eight genuinely XORWOW-generated 12-output streams, with selected stages4..7 withheld, each pass the exact source parity and recover a **unique complete 16-byte physical coupon**, in all eight serializations. The inferred `d0` is independently verified; the physically serialized selected bytes and full component SHA256 after XOR with the unchanged original mask exactly match their planted truth. This tests the full source-to-reduction path and prevents a faulty solver from reporting zero merely because reconstruction is broken.

Portable standard-library [complete original-source SFT](../agents/agent3/k04_xorwow_gap_weyl_sft.py) rebuilds GF(2) equations from the canonical XORWOW recurrence, has no external matrices or dependencies, confirms source spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, selects the two correct original same-job requested records, verifies the route mask `8556C8CB6140A7F9A5123AC7571BEE1C` and the untouched K04 SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. On the actual original ZIP, the algebraic solver and all eight positives complete in ~0.03 seconds. The independent numeric C scan is retained only in the executing session, not packaged as the canonical reproducer because the algebraic proof is shorter and stronger.

The tested hypothesis **requires** canonical five-register XORWOW, Weyl step362437, four native outputs per record, no hidden draws between the two requested attempts beyond the four missing selected words, and one common serialization. REQUESTED printer fields need not represent issued physical coupon bytes; no original source attests those assumptions. Different emitter constants, stage gaps, independent request/ACK generators, or a missing physical coupon cannot be excluded.

**No original K04 bytes or K08 final-caption words were recovered.** K01/K02/K03/K05/K06/K07 remain individually PASS; K04/K08 missing; combined REC8 INCOMPLETE. The original source, acceptance, verifier and canonical submitted candidate are untouched.

## 5 November extension: extra unobserved issuer draws, 32 full source-only negatives

The original same-job transmission need not consume four and only four outputs for the missing 18:02 ACK2. A further **read-only model expansion** leaves the target at native output stages 4..7 but positions the actual complete original 18:03 packet at stages `8+g..11+g`, with **g=1,2,3,4 additional unobserved generator outputs** between packets. Both `d0` and the Weyl increment remain arbitrary 32bit parameters, and the original disputed selected ACK2 copy remains excluded.

For each g, derive a fresh 160-bit canonical XORWOW state map to all observed outputs (rank160, 96 independently necessary parity equations) and project the target four native words from the eight original intact source words (full 128-bit target projection). Then exhaust all 2^64 d0/increment pairs exactly by four-way low-bit lifting, with every independent parity equation enforced when its maximum involved bit first becomes known. Across four gaps and eight serializer layouts, **32 of 32 full original-source constraint systems have no compatible emitter**, with the first inconsistency between parameter bit13 and bit30. The hardest gap models require high-bit equations but are still fully decided; **do not extrapolate to gaps five or greater**, which are not tested and have different prefix complexity.

**Full synthetic positives:** for each gap and each serialization, simulate a true XORWOW 12+g word sequence with independent arbitrary `d0` and nonstandard Weyl increment `0xA5A5BEEF`, hide exactly stages 4..7, and reconstruct the unique pair and 16-byte selected coupon from the two retained fourword records. **32/32 true complete coupon and full synthetic commitment controls PASS.**

Reproducer: [`agents/agent3/k04_xorwow_four_extra_gap_sft.py`](../agents/agent3/k04_xorwow_four_extra_gap_sft.py), using the existing symbolic XORWOW SFT as an exact source primitive. Completed on the original source in about 63 seconds for both original and planted cases. All original 32 configurations still fail without K04 acceptance testing. This is a stronger, specifically scoped producer/temporal-gap exclusion, **not** recovered physical K04 coupon information, and not evidence that any of the supposed extra draws actually occurred.
