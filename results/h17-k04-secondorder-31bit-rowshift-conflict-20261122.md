# K04 second-order MT row-shift: source overlap contradiction and full-coupon rejection

**Agent 4 | 22 November 2026 | Original K04 remains missing.**

## Source-selected hypothesis

Two distinct source-observed four-packet MT19937 second-order 31-bit recurrence groups have the same physical **row offsets (+31,+54,+115)**:

- Historical rows (9,40,63,124): two adjacent native-word identities, with stage offsets (+229,+398,+852).
- Historical rows (10,41,64,125): three adjacent identities, with stage offsets (+227,+397,+850).

Both source groups therefore suggest using intact original rows **14,45,68** to predict the withheld selected ACK2 row129 if the row-offset pattern transfers. This is a concrete whole-coupon producer hypothesis, independently selected by historical reinforced source structures.

The conditional MT second-order identity is:

    predicted_D = (native_C XOR L(native_A) XOR L(native_B)) & 0xbfffffff

where L(v)=((v & 0x7fffffff)>>1) XOR (0x9908b0df if v odd). One bit30 per target 32-bit word is free.

## Original source-first result

The [source-pinned SFT](../agents/agent4/k04_mt_secondorder_rowshift_target_sft.py) excludes disputed row129 before PAYLOAD decoding, verifies all five original-source lane identities, then computes the original hypothetical target native words:

| Target lane | Group9 | Group10 |
| --- | --- | --- |
| 0 | A80A23BD | none |
| 1 | **2CA7525C** | **1D0508B2** |
| 2 | none | 9FF93824 |
| 3 | none | 0001E1F0 |

**The two independent lane1 values differ at 16 of the 31 fixed bits.** Thus the shared *row-offset transfer* cannot simultaneously represent one exact MT stage history. This source-only contradiction occurs without consulting the original K04 target or copied ACK2 bytes.

Even allowing the lane1 value from either source group and keeping the other three predicted lanes, the four unknown bit30 values generate precisely **2 × 16 = 32 complete 16-byte coupons**. Every coupon was tempered, serialized little endian, XORed with the original K04 mask, and tested against the full original K04 SHA256 commitment. **Original hits: 0/32.** Two independent synthetic full-16byte positive controls were each recovered exactly once.

The original spool SHA256 is 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083, and original route/acceptance hashes are pinned by the SFT. No original file, verifier or candidate changed.

## Interpretation

The source-verified identities came from [Agent1's earlier four-sum research](h17-k04-stagefree-secondorder-31bit-4sum-bridges-20261105.md). This **new target-facing extrapolation** determines why matching physical row offsets alone cannot safely predict the missing coupon. The [all-42 scalar graph](h17-k04-stage-graph-conditional-full-coupon-20261122.md) independently finds no authenticated complete K04 prediction.

No physical coupon word or keeper-final K08 phrase has been recovered. Six original slots PASS; K04/K08 missing; REC8/1 combined INCOMPLETE.
