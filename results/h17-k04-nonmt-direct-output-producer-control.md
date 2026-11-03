# K04: independent short-state direct-output generator test (3 November 2026)

**Question.** Can the unrecovered printer coupon be predicted by recovering the state of a **non-MT**, low-state pseudorandom generator from intact printer ACK payloads? This tests a different, complete-coupon producer architecture from the speculative p951/MT19937 quotient work. It does not assume that the retained disputed ACK bytes are authentic.

**Source and scope.** The original `resources/evidence/print/spool-reconstruction.log`, its first **128 routine 5-minute ACK records** (`PS-261003-0300` through `0427`). The selected `PS-261003-0417` ACK2, the requested attempts, and the final special jobs are **excluded from every source-fit and holdout test**. Neither `acceptance.json` nor any K04 hash is consulted. [Single-file source-only reproducer](../agents/agent5/k04_nonmt_direct_stream_sft.py).

## Models and complete-state recovery

1. **xoshiro128\*\***: four consecutive native 32-bit outputs per 16-byte record. The nonlinear output `rotl(s1*5,7)*9` is invertible modulo 2^32. Four observed words then form a 128-equation binary-linear system for the four-word initial state. The recovered 128-bit state predicts an entire withheld next packet.
2. **xoroshiro128\*\***: two consecutive native 64-bit outputs. Both nonlinear output multipliers are invertible; the two outputs expose successive `s0` values, allowing the remaining register to be recovered from `x XOR (x<<16)`. This also reconstructs the complete 128-bit state before predicting the next packet.
3. **xoshiro256\*\***: two successive 16-byte packets, each containing two consecutive 64-bit native outputs. Inverting four output words and solving the 256-bit linear transition system recovers the initial state and predicts the third packet.

Every model was checked in four explicit layouts: **big-endian and little-endian native words, each in forward and reverse word order**. All **60 seeded synthetic stream-recovery controls** reproduced their 12 or 14 withheld outputs, with full GF(2) rank 128 or 256 where applicable.

## Original-source falsification

| Model | Original contiguous heldout predictions | Complete next-packet matches | Maximum matching individual next-output words |
|---|---:|---:|---:|
| xoshiro128** | 127 × 4 layouts = **508** | **0** | **0** |
| xoroshiro128** | 127 × 4 = **508** | **0** | **0** |
| xoshiro256** | 126 × 4 = **504** | **0** | **0** |

For the two 128-bit-state models, a second test reconstructed the complete post-packet state **separately for each of the 128 routine original packets**. Instead of requiring immediate adjacency, it advanced each earlier state through the next packet's two or four mandatory outputs **plus 0 through 4,096 unobserved extra draws**, seeking the next routine packet's independently reconstructed post-packet state. Across **1,016 adjacent-pair/layout/model cases**, there were **zero state matches**. A further **10 planted seeded gap controls** with random 1–127 extra draws were recovered exactly.

These are model-restricted, original-source negatives: direct untransformed native output with the stated byte layouts and a single shared state stream, with at most 4,096 hidden outputs between adjacent routine printed packets, does not explain the intact source. A per-job reseed, a cipher/encoding layer, more widely separated outputs, nonconsecutive output words, or a different PRNG is outside the test. No general conclusion about the actual printer implementation follows from a failed candidate family.

**Target consequence:** These models would have supplied an end-to-end 16-byte prediction if their original heldouts had passed. Their tested forms failed before consulting any target commitment. Consequently no K04 selected physical coupon bit is authenticated; K08 is untouched; the canonical six accepted slots remain unchanged.

**Reproduce:** From repository root, run `python agents/agent5/k04_nonmt_direct_stream_sft.py`. The program uses only the Python standard library, reads the source log, prints seeded controls and original-source matches, and does not write or modify any evidence.
