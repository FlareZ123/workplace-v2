# K04: 88,077,696 whole-coupon checks from invertible raw-state xorshift128 emitters

**Agent 7, 23 November 2026 | original K04 accepted results: ZERO | six accepted earlier slots unchanged.**

## A distinct full-output source mechanism

After completing the exact xorshift128+ **sum-output** generator family, this study asks whether each original PS-261003-0417 RECOVER REQUESTED packet records two *raw 64-bit state-word functions* from the same 128-bit xorshift transition. The binary source has no authenticated producer specification, so these output functions are hypotheses, not recovered historical facts.

For each of two transition schedules, **V8 (23,17,26)** and **Vigna (23,18,5)**, test seven complete invertible 64-bit output forms:

- **L**, first 64-bit state register;
- **R**, second 64-bit state register;
- **L × 0x9E3779B97F4A7C13**, **R × 0x9E3779B97F4A7C13**, with 64-bit wraparound;
- **L × 0x2545F4914F6CDD1D**, **R × 0x2545F4914F6CDD1D**, with 64-bit wraparound;
- **L xor R**.

The two odd multipliers are standard reversible word scramblers; source records do not establish either multiplier was used. Each proposed output yields an **exact complete 128-bit source-state inverse from the first two 64-bit native outputs**:

1. If the emitter is L or L times an odd multiplier, invert any multiplier, then recover (L1,R1) directly because next L equals prior R.
2. If the emitter is R or R times an odd multiplier, invert the multiplier, then recover prior L by the two exact inverse-XOR shifts of the transition, given current R and next R.
3. If the emitter is L xor R, the two observed outputs x0,x1 imply x1 xor (x0 >> rb) = F(L1), where F(L1) = ((L1 xor (L1 << 23)) xor ((L1 xor (L1 << 23)) >> ra)) xor (L1 >> rb). For **both** (ra,rb)=(17,26) and (18,5), this is an independently computed **full-rank 64×64 GF(2) linear map**. A deterministic 64-bit Gaussian inversion yields the unique L1, and R1=L1 xor x0.

No source states are left unenumerated or deferred to a timed-out SMT solver.

## Executed original result

Use only the original 18:01Z REQUESTED1 and 18:03Z REQUESTED3 RECOVER packets for separate source-state fits. Exclude the 18:02Z copied ACK2 entirely from modeling. Test all 24 fourword permutations and global big/little 32-bit word endianness, yielding **48 source layouts** per anchor, output form, and transition schedule.

Every complete potential middle coupon is produced in both temporal directions. XOR the original 16-byte route mask, then compare SHA256 of the **full 16-byte component** against the original SHA256 target. Test the directly adjacent middle coupon, and then 65,533 forward or 65,535 backward 16-byte contiguous windows for each fitted model.

| Variant / output family | Exact 128-bit first-pair states | Original complete K04 SHA256 assignments | Original matches |
| --- | ---: | ---: | ---: |
| V8 transition, seven invertible emitters | 672 | **44,038,848** | **0** |
| Vigna transition, seven invertible emitters | 672 | **44,038,848** | **0** |
| **Total** | **1,344** | **88,077,696** | **0** |

The 1,344 state assignments generated **576 distinct immediate complete component candidates**; all failed the original K04 commitment. All 1,344 opposite-source 16-byte holdout comparisons also failed. Full 65k-window scans rejected every source-model candidate. The original source SHA256 and original route/acceptance SHA256 fingerprints are independently enforced by the source reader.

Planted correctness controls:

- Each emitter inverted a newly generated complete 128-bit synthetic state exactly for each transition schedule; the two XOR maps' GF(2) matrix rank was 64.
- **56 complete synthetic physical coupon tests** passed the same native SHA256 masked-coupon gate: 2 transition schedules × 7 emitters × 2 temporal directions × 2 planted window indices (2 and 42), through a nontrivial fourword permutation and little-endian chunk serializer.
- All original source-state models were replayed forward/backward in native 64-bit arithmetic before hashing.

## Source-pinned reproducibility

The [single runnable Python + native-SHA SFT](../agents/agent7/k04_xs128p_stateemitters_sft.py) checks the unchanged source hashes, performs all exact state inverses, generates complete original coupon candidates, calls the [optimized 65k-window native scanner](../agents/agent7/k04_xs128p_emitter_gap_scan.c), and confirms original candidate count, uniqueness count and total whole-SHA256 checks. Requires GCC/Clang and OpenSSL/libcrypto, reading the checked-in original resources or the untouched original ZIP.

This is distinct from the companion [12.25m sum-output inverse](h17-k04-dual-xorshiftplus-complete-gap-inversion-20261123.md) and the earlier xoroshiro128* source models. The tested output stage, native state transition and source-view count are explicit. No external protected service or suppressed encrypted PDF was opened.

## Decision

The two xorshift128 transitions with these seven source-output functions, 48 conventional chunk layouts, both request anchors and first 65k possible two-output coupon windows **do not recover K04**. They do not establish that the generator family itself is physically present, nor do they rule out independently seeded jobs, different producer algorithms or original missing media. Wider unmotivated gaps or arbitrary new multipliers in the same model have low value without a source-to-producer clue.

**Historical recovery remains K04 MISSING, K08 MISSING, REC8/1 INCOMPLETE.**
