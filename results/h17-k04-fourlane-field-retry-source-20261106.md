# K04: lane-permuted four-GF(2^32) affine retry source issuer

**Agent 21 | 6 Nov 2026 | original K04 NO_MATCH, no physical coupon authenticated.** New full-coupon producer hypothesis with an independent original printer-record holdout. Original printer log, six accepted components, routing, commitment and checker unchanged.

## Source-visible control, exact hypothesis

Original printer source `evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The repeated original job IDs allow two genuine before/after observations:

- **0417:** 16:45 LABEL ACK1 value `A=E1E60D5F6B6DD2225FA6D5A2A63AD932`; 18:01 RECOVER REQUESTED1 `B=CD3E4F216ADB2FB180DA2AA90B33F7A4`. The 18:02 selected physical ACK2 is **excluded** from model derivation, along with its suspect copied buffer; 18:03 RECOVER REQUESTED3 `C=44D53DFC29D7943A95D89371DA58EC64` is an independent heldout complete packet.
- **0420:** 17:00 STORES ACK1 `U=31C9714DD36DB2677BB9006670A9DFFD`; 18:25 RECOVER ACK2 `V=432475F72A62DB39F3D5693E2C937FA4`.

Could a printer's retry/copy mechanism apply an **independent affine transform to each of four native 32-bit lanes**, with a fixed four-lane input permutation, producing its next packet?

For each output word lane j and source input lane `p(j)`, define `T(x)[j] = a_j * x[p(j)] + b_j` in the characteristic-two field GF(2^32). Solve `T(A)=B` and `T(U)=V` exactly by field division, then produce the complete unknown physical coupon **`X=T(B)`** and predict independent full source holdout **`C=T(X)`**. No selected ACK2 copied bits or original commitment are used to solve any coefficients. This is different from a **single GF(2^128)** affine map, from a **Z/(2^128)** modular-ring map with carries between words, or from a shared 32-bit added copier counter: it uses four separate nonlinear 32-bit multiplicative states and an explicit lane permutation.

The original archive does not attest that the two jobs or CLASS/ACK versus REQUESTED source stages share this producer. This is an exploratory *complete source-calibrated issuer*, not a firmware identification.

## Exact finite original-source computation

Three verified irreducible binary 32-degree field polynomials are `0x10000008D`, `0x1000000AF`, `0x1000000C5`. For each, try both per-word byte endian views, bit reversal within each word on/off, and all 24 fixed lane permutations. `3 × 2 × 2 × 24 = 288` exact full-coupon producer assignments.

All source input differences are nonzero, so unique field-affine lane coefficients exist in each assignment. **Every** model fits the two complete source calibration pairs exactly. Each predicts a complete physical coupon `X`, reduces it with unchanged mask `8556C8CB6140A7F9A5123AC7571BEE1C` by XOR, and hashes the resulting 16byte K04 component against original complete SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Executed locally against the user's intact 46-file original ZIP:

| Original-source / target criterion | Observed |
| --- | ---: |
| Fully calibrated 16-byte issuer assignments | **288 / 288** |
| Whole independent source holdout packets `T(T(B))=C` | **0 / 288** |
| Exact independently heldout 32bit lane agreements (all assignments) | **0 / 1,152** |
| Original complete K04 commitment matches | **0 / 288** |
| Independently seeded source issuer + full synthetic target recovered | **288 / 288** |

The genuinely generated controls use nonzero affine lane slopes and independent input packets under each of 288 exact field/serializer/permutation settings. The code first reconstructs all four coefficients from two complete synthetic source pairs, predicts the hidden synthetic whole packet and its subsequent source holdout, and compares the entire masked synthetic coupon SHA. All 288 pass, so the test is genuinely target-reaching when the hypothesized producer supplies the data. It is not calibrated using original K04 target prefixes.

[Reproducible source-pinned standard-library Python SFT](../agents/agent21/k04_fourlane_field_retry_sft.py) models the original unique 0417 ACK2 without reading its payload into emitter inference. Each assigned calibration and holdout object is source-backed, not a generated control standing in for evidence.

## Decision and next direction

The lane-permuted per-32-bit affine retry model is **rejected by actual independent source packets** before relying on the K04 SHA, and its own complete coupon candidates fail acceptance. The result is not proof that no printer emitted a correlated retry packet: CLASS changes, REQUESTED-vs-ACK stages, random generator phase and physical-copy damage could invalidate this simplifying shared transition. It recovers no original coupon bits.

Do not enlarge this family by arbitrary word-specific nonlinear parameters without another original control pair. The material need remains a genuinely identifiable source-stage generator, a physical-to-copied-ACK calibration that survives the 0420 and 0417 controls, or an independent original coupon. All six previously accepted REC8 values remain PASS; K04 and K08 missing, combined INCOMPLETE.
