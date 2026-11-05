# K04: compact-state xoroshiro128+ source-inversion and metadata-gap test

**Agent 50, 5 November 2026.** The original REC8 verifier still accepts exactly K01, K02, K03, K05, K06 and K07. K04 and K08 remain missing. This report excludes two **conditional original-printer producer families** using read-only intact 128-row controls. No original coupon bit or final-caption word was recovered.

## New complete-coupon mechanism and causal assumption

An unknown xoroshiro128+ 128-bit state could, if the printer actually used it, be inferred from intact packet output and advanced to produce the disputed complete 16-byte ESC-N attempt-2 coupon. Unlike a 624-word Mersenne Twister with unresolved selected-state dimensions, the compact 128-bit generator can be fully constrained by ordinary packet low bits without knowing the seed. This test asks whether such an independent finite state exists under plausibly metadata-dependent draw consumption.

Both Blackman/Vigna xoroshiro128+ recurrences were evaluated:

- 2016 recurrence: `(L,B,R)=(55,14,36)`.
- 2018 recurrence: `(L,B,R)=(24,16,37)`.

Each 64-bit output is `(s0+s1) mod 2^64`; after `x=s0 xor s1`, the state advances as `s0'=rotl(s0,L) xor x xor (x<<B)`, `s1'=rotl(x,R)`. The **least significant output bit is exactly `s0[0] xor s1[0]`**, a GF(2)-linear functional of the initial 128-bit state. All subsequent low bits are also GF(2)-linear because the state update uses XOR, shifts and rotations.

The source is the original 128 ordinary job records `PS-261003-0300` through `0427`, each `ATTEMPT=1 STATE=ACK`; the selected 18:02 attempt-2 and every exceptional 18:01–18:25 row are withheld. Source spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

## Identifiability experiment

Each intact 16-byte payload is regarded as two full 64-bit successive outputs in four possible byte/half-word orders. The generalization test reads **256 source low bits**, 128 initially used for state inference and 128 reserved for honest prediction. GF(2) row reduction solves the 128-bit initial state when rank is complete and tests all remaining output constraints; for rank-deficient training sets, the full 256-equation system is tested for consistency instead.

**Fixed-gap experiment:** for each variant, fixed word strides `2..32`, and four serializers: **248 model configurations**. All are incompatible with the complete source. The strongest rank-128 training model predicts 82 of the 128 withheld low bits. Two exact genuine planted generator histories with different strides and serializers recover their true 128-bit states.

**Categorical variable-gap experiment:** allow a different hidden word-consumption count for each observed CLASS `LABEL/STORES/RECOVER` and DEST `bench/store/desk`. Each of these six categories independently contributes 0, 1, or 2 hidden generator outputs. Therefore 3^6=729 category schedules are possible for a given timing convention. Test both conventions: consume extra draws **after** the current packet versus **before** its packet (with the initial prefix absorbed into the unknown state). Two recurrence variants × two timing conventions × 729 schedules × four serializers = **11,664 complete original-source systems**, each with 256 exact low-bit equations. **Zero** systems are consistent.

| Recurrence | Gap timing | Full configurations | Compatible with all 256 source bits | Best 128-bit held-out agreement when training state was unique |
|---|---|---:|---:|---:|
| 2016 | after | 2,916 | 0 | 83/128 |
| 2016 | before | 2,916 | 0 | 82/128 |
| 2018 | after | 2,916 | 0 | 80/128 |
| 2018 | before | 2,916 | 0 | 82/128 |

Two synthetic positives with nonzero, varied category-skip schedules and different recurrence variants pass **exact initial-state recovery** and complete held-out low-bit reproduction. The exact original spool SHA is asserted before source parsing.

## Consequence and boundary

An original printer based on one globally continuous xoroshiro128+ 2016/2018 state, with two consecutive 64-bit payload outputs per row and additive metadata-category gap counts from 0 to 2, is **mathematically incompatible with the observed source low bits**. This is already visible before checking any K04 commitment. No target SHA or copied selected payload was used to fit or select a model.

The result does **not** rule out nonlinear output scramblers such as xoroshiro128++, unknown per-event resets, packet-source transformations, irregular hidden draws independent of CLASS/DEST, very large gap schedules, other word serializations, or a different copier. An unrelated selected-event generator could also remain possible. No physical selected K04 bytes, no authenticated original coupon bits and no final K08 margin text were obtained. Original acceptance stays six PASS / two MISSING / combined INCOMPLETE.

The finite model is distinct from prior selected-only native MT32 enumeration, MT nullspace certificates, nested xorshift-as-Python-seed analyses and ordinary row AES/field issuer tests. Its discriminating mechanism is linear inversion of *xoroshiro128+ output low bits*, including explicit observable metadata-based stage placement.

Reproducers: `agents/agent50/xoroshiro_lowbit_sft.py` and `agents/agent50/xoroshiro_metadata_gap_sft.py`. Both are Python-standard-library only and leave all original evidence, verifier, acceptance and candidates untouched.
