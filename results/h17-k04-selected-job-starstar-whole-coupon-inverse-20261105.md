# K04: selected-job attempt-1/attempt-3 reversible generator reconstruction

**Agent 50 | 5 November 2026**. Target-reaching read-only conditional printer producer test. It reconstructs whole 16-byte candidate coupons for selected ACK attempt2 from the two other preserved attempt packets of **the same** logical ESC-N job, then checks the untouched original K04 commitment. This is distinct from global ordinary-spool state fitting, selected-copy byte edits or known-key AES source issuers.

## Historical source and exact reducer

Selected job `PS-261003-0417` (logical ESC-N). Preserved *same-job* `ATTEMPT=1 STATE=REQUESTED` at 18:01 UTC has source buffer `CD3E4F216ADB2FB180DA2AA90B33F7A4`. `ATTEMPT=3 STATE=REQUESTED` at 18:03 UTC has `44D53DFC29D7943A95D89371DA58EC64`. The disputed 18:02 `ATTEMPT=2 STATE=ACK CLASS=RECOVER` buffer is withheld from reconstruction. Candidate physical coupon XOR the exact source mask `8556C8CB6140A7F9A5123AC7571BEE1C` yields complete candidate K04; compare its complete SHA256 with unchanged original commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The hypothetical issuer emits a complete packet as two successive 64-bit PRNG words, in either endianness and either half-word order. Hidden generator draws can occur before and after the middle attempt. This hypothesis is source-unattested; historical REQUESTED packets are preserved but the log does not identify their actual producer.

## Critical algebraic breakthrough: the `**` output is invertible

In [Blackman and Vigna's `**` scrambler](https://prng.di.unimi.it/), the 64-bit output is `rotl(word*5,7)*9 (mod 2^64)`. Both multiplication constants are odd, hence are units modulo `2^64`. Undo multiply by 9, rotate right 7 and undo multiply by 5 to recover the complete original 64-bit state word. This allows source packet contents to become exact state observations rather than lowbit-only constraints.

**xoroshiro128\*\***: For the official `(24,16,37)` recurrence, the 18:01 packet's first two outputs reveal successive 64-bit `s0` values. Algebraically invert `s0' = rotl(s0,24) XOR t XOR (t<<16)`, where `t=s0 XOR s1`, to solve the entire unknown **128-bit initial state** from just this one packet. Also tested a hypothetical `(55,14,36)` alternate recurrence with the same `**` emission, without claiming official precedent for that pairing. Exhaustively allow 0..256 hidden generator outputs before attempt2 and 0..256 after. All complete candidate middle packets and every possible total-gap 18:03 observed packet are then determined.

**xoshiro256\*\***: The official generator's output inverts to `s1`; the 256-bit four-word state update is GF(2)-linear. The original 18:01 and 18:03 request packets provide **four complete 64-bit internal-state observations** at indices `[0,1,4+h,5+h]`, with total hidden gaps `h=0..512`. Build their exact 256×256 source linear system, solve for every consistent affine state including rank-deficient models, then enumerate each legal split `g1+g2=h`, with both gaps 0..256. Emit the **entire 16-byte middle attempt2 coupon** for each consistent state and split and apply the original K04 XOR and SHA256.

## Completed original-target outcomes

| Complete-coupon producer | Source configurations | Full candidate K04 commitment checks | Genuine original K04 matches |
| --- | ---: | ---: | ---: | ---: |
| xoroshiro128\*\* (24,16,37) | 4 serializers, hidden gaps 0..256 | 1,028 | 0 |
| Hypothetical xoroshiro128\*\* (55,14,36) | 4 serializers, hidden gaps 0..256 | 1,028 | 0 |
| xoshiro256\*\* (17,45) | 2,052 serializer/total-gap inverse systems; 1,221 compatible | 259,762 | 0 |
| xoshiro128\*\* (4×32-bit state, first attempt fully inverted) | 4 serializers, hidden gaps 0..256 | 1,028 | 0 |
| Marsaglia xor128 (11,8,19, 4×32-bit state) | 4 serializers, hidden gaps 0..256 | 1,028 | 0 |
| **Total** | | **263,874** | **0** |

For xoroshiro128\*\*, the original 18:03 same-job packet matched **zero** of 4,104 full packet predictions across the two variants, four serializers and all total gaps 0..512. For xoshiro256\*\*, exact two-packet inversion yielded **2,030 complete initial-state assignments** in the 1,221 compatible models, including all nullspaces of dimension 1, 2 or 3; those produced the 259,762 candidate middle coupons. The previous/copied 18:02 ACK2 and all original K08 material were excluded from source model fitting.

**Planted controls:** Both xoroshiro128\*\* variants recovered exact 128-bit original states from first-packet full outputs and reproduced a planted middle and final attempt after nonzero skip gaps. A planted xoshiro256\*\* 256-bit state with two nonzero hidden stage gaps yielded an affine initial-state family containing the original state and recovered its one correct whole middle coupon uniquely under the planted SHA commitment. The low-level inverse scrambler passed nine synthetic roundtrips including high-bit edge cases. No historical packet, commitment, mask or verifier was edited.

## Interpretation and next opening

Two additional 32-bit complete-state middle-coupon constructions were tested on the same historical attempt1/attempt3 pair. For the [Blackman/Vigna xoshiro128**](https://prng.di.unimi.it/) producer, a complete source packet yields four consecutive reversible 32-bit state-word observations, exactly determining the 128-bit initial state under the model. For [Marsaglia's original xor128](https://www.jstatsoft.org/article/view/v008i14), each 32-bit emitted output is itself a new state word; after four outputs the current state equals the packet's four words. Each candidate family produces **1,028** selected K04 SHA256 tests and **2,052** later attempt3 full-packet source tests with zero matches. Both genuine planted middle-and-later producer controls PASS. These are additional *selected-event* hypotheses rather than an extension of the original 64bit starstar scrambler equation.

The exact tested same-job compact-generator families do not yield original K04 acceptance. Both preserve the historical possibility of an independent selected emitter, an entirely different output mechanism or a copy-stage fault. The source-only global finite generator exclusions in [compact-state inverse report](h17-k04-xoroshiro128plus-metadata-lowbit-exclusion-20261105.md) and [xoshiro256+ report](h17-k04-xoshiro256plus-258eq-nullspace-complete-exclusion-20261105.md) make no stronger historical claim. More productive next mechanisms should use the **same-attempt temporal relation** to predict actual selected physical bytes, or identify a source-known physical copy transformation, rather than enlarge arbitrary byte repair.

Reproducers: [reversible 64-bit and 32-bit starstar source-to-K04 SFT](../agents/agent50/selected_starstar_samejob_sft.py) and [original 32-bit Marsaglia same-job source-to-K04 SFT](../agents/agent50/selected_marsaglia_xorshift128_sft.py). Source-only original ordinary-packet preview and its complementary negative are retained in Agent50's investigation notes. Original REC8 outcome remains six PASS / two MISSING / combined INCOMPLETE.
