# K04: alternate route-mask object selection from all preserved original carriers

**Agent41 | 3 November 2026 | Original K04: zero matches in 67,470 complete candidates, including 67,468 new reduced values.** Existing six independently accepted REC8 components stay PASS; K04 and K08 remain unresolved; combined archive key INCOMPLETE.

## Distinct target-bearing question

The source-selected ESC-N / PS-261003-0417 / RECOVER / attempt2 ACK retained printer copy is `A9A9DC5731A5E2AE879C47215C2559D5` (P0), and the separate route-sheet transcribed mask is `8556C8CB6140A7F9A5123AC7571BEE1C` (M0). The original reduction is `K04 = physical_coupon XOR original_mask`, and the unchanged SHA256 slot commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The predecessor [all-file verbatim carrier audit](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-all-file-carrier-bound.md) searched historical bytes/hex as **replacement physical coupons**, holding **M0** fixed. Agent30/Agent12 explored serializer operations of M0 or both operands. This new test asks the orthogonal object-selection question: could **P0 be the authentic coupon** while the original **mask** was miscopied, with an exact 16-byte replacement mask present somewhere else in the original export? For each historical carrier X, test `SHA256(P0 XOR X)` against the original K04 target. A copied-original-mask hypothesis is speculative because the original source contains no alternate attested mask, and MAIL16 warns P0 lacks independent physical-byte integrity. This is an exact bounded test, not a claim of historical mask corruption.

## Frozen exhaustive source extraction and real result

Read the original 46 regular members of the supplied H17 ZIP, SHA256 **e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7**. Cross-check original printer spool SHA256 **7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083** and exact P0 source inclusion. Extract every contiguous **16 raw bytes** from all member bodies and every **32-nibble window** of maximal ASCII hex runs (both nibble phases). Dedupe the resulting masks before hashing.

| Measurement | Exact count |
|---|---:|
| Original regular ZIP members | 46 |
| Sliding raw16 assignments | 117,583 |
| Sliding hex32 assignments | 892 |
| Distinct original 16-byte carrier values | **67,470** |
| Distinct final component values C=P0 XOR carrier | **67,470** |
| Prior v1 fixed-mask carrier-component set C=carrier XOR M0 | 67,470 |
| **Actual component-set intersection** | **2** |
| **New final K04 candidates outside that prior carrier class** | **67,468** |
| Full SHA256 authentic K04 matches | **0** |
| Independent planted alternative-mask positive | **1** |

The pairwise overlap is computed over final **C** bytes, not descriptions of the physical stage. Two obvious identities are present in the original source carrier set: both P0 and M0 appear verbatim, producing the existing `P0 XOR M0` component and the all-zero candidate across the two stage views. All remaining 67,468 complete source-mask substitutions genuinely extend the *named earlier source-carrier stage*. No claim is made that they are globally new relative to every numerical PRNG or fault model previously tested.

The planted control chooses an original maintenance-file 16-byte window as a hypothetical correct alternative mask, hashes `P0 XOR planted_mask` to a separate in-memory synthetic commitment, and recovers exactly one unique matching carrier. The authentic commitment, route source, source ZIP, canonical candidate and verifier were never modified.

## Reproducibility, limit, and next action

[Source-pinned portable standard-library SFT](../agents/agent41/k04_original_mask_carriers_sft.py) can run on the original ZIP as an explicit argument or on the repository `resources/` copies, excluding the two locally produced non-original members. An independently executed equivalent local script on the original supplied ZIP returned all counts above. The code compares final-byte candidate sets according to the [K04 XOR equivalence critique](../communications/broadcast/20261103T1429Z_Critic_k04-xor-normal-form-target-search.md).

This excludes replacement masks carried **verbatim as any contiguous raw16/hex32 source window** while treating the selected copied P0 as genuine. It does not exclude encoded/decoded mask source (which would be a separate stage), an unrecorded mask, arbitrary copy corruption, or alternative full-coupon producers. There is no original proof that P0 is physically authentic. **Zero authentic K04 bits** and **zero final K08 words** were recovered. Further work should seek a historically indexed physical coupon/original mask witness rather than repeat the fixed-carrier extraction under a different filename.
