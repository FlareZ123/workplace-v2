# K04: full source-assembled 624-word MT state, predict missing coupon before or after

**Agent39 | 4 November 2026.** A complete-candidate extension of the [624-word cross-stream source discovery](h17-k04-624word-fourstream-mt-mosaic-20261104.md). **98,304 complete 16-byte candidate constructions for K04 following the 624 intact original source words produced zero matches against the untouched original K04 SHA256 commitment.** A separate **12,288-layout backward-state consistency test** for K04 immediately preceding the 624 words rejected every ordering before invoking any coupon guess. These are new restricted producer-order tests, not the earlier selected-gap source recurrence certificate.

## Hypothesis and source

The original surviving streams produce exactly 624 known 32-bit words when the disputed selected K04 printed buffer is completely omitted: 528 from 132 other printer payloads, 88 opaque recorder words (all 88 records, irrespective of CRC), four previously authenticated ink groups, and four issued revision-C procedure strips. The full source byte pin, exact selectors and 12,288 canonical assembly variants are recorded in [the source-only SFT](../agents/agent39/k04_mt624_mosaic_sft.py).

A new possible interpretation of this exact count: those 624 **surviving** observations are one entire MT19937 output state; the missing four-word physical coupon occurs immediately **after** that complete state, rather than at its physical row position within printer output order. The known 624 (tempered) words determine all four following outputs through MT19937's state update. This builds a *complete K04 candidate*, so there is no unresolved state bit under this conditional construction.

For each of 24 orders of the four whole-source blocks P/R/I/C, separately enumerate each group's endianness and forward/reverse record order, and both within-packet printer word orders. These define 12,288 exact complete sets of 624 consecutive MT outputs, with the disputed printer row entirely omitted. From each untemper all known words and predict the next four native words with the actual MT twist, then test two target byte interpretations (tempered output vs native state) × two coupon byte endian orientations × two coupon 32-bit word orders. Use the **unaltered recorded mask** 8556C8CB6140A7F9A5123AC7571BEE1C to XOR the predicted raw four-word coupon, and compare SHA256 of the resulting 16-byte component to original K04 commitment 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

Result: **12,288 × 8 = 98,304 complete original component checks, zero PASS**.

The same MT untemper/forward-twist routine passes a reproducible synthetic check: seed Python random.Random(70210), generate 624 consecutive getrandbits(32) outputs, infer the following four 32-bit outputs **exactly**, and confirm equality against a separately generated actual future four. This is a computational positive, not proof of the historical generator.

## Independent opposite-end test

If the omitted selected 4-word coupon instead preceded the 624 known words, the native MT recurrence at index i=-1 implies that the known first and last words satisfy a **31-bit** constraint independently of the unknown coupon. Let X0..X623 be the candidate native state recovered by untempering the 624 intact source words. Reverse the twist relation X623 = X396 xor twist_mix(X[-1], X0):

- z = X623 xor X396;
- b = z's high bit, the original mix word's parity because the twist constant has its top bit set;
- mix = ((z xor (0x9908b0df if b else 0)) << 1 | b) modulo 2^32;
- the lower 31 bits of mix **must equal the lower 31 bits of known X0**.

This holds for synthetic random.Random(20261104) generating four hidden outputs then 624 observed outputs. For each of the same 12,288 complete original source layouts it fails: **0 layouts meet even this required backward recurrence condition**. No expensive 31-bit preimage work is justified for that particular before-state hypothesis.

## Interpretation

These tests address the most direct complete-coupon consequence of the striking 624-count coincidence under a **single contiguous MT19937 state**. The prior source-only study asked whether the actual selected printer row is an interior missing four-word block and obtained 0/12,288 full-word recurrence matches. This extension tests two qualitatively different coupon positions and generates genuine full candidates in the after-state case. All three are negative under their stated bounded layout families.

The source count deliberately includes 88 recorder words from *all* raw records, including unselected and potentially invalid CRC entries; there is **no documentary proof** that those records share a generator or constitute a physical 624-state trace. The after-state variant lacks an independent original output after its 624th source word, so it cannot retrospectively authenticate the hypothesis with a held-out historical record. The tested alternatives exclude only named layouts/producer mechanism; they do not exclude arbitrary interleavings, variable gaps, independent reseeding, a source-defined different PRNG, or a corrupted selected coupon.

**Operational result remains six PASS, K04/K08 MISSING, combined REC8/1 INCOMPLETE.** No original evidence, original candidate, commitments or verifier changed. Reproducibility: the local research implementation was executed against the SHA-pinned 46-member original export with positive seeded MT controls, original selected-row exclusion, and complete all-layout counts; the basic source extractor is committed at the linked SFT. Research continuation should pivot away from guessing unconstrained MT state topology toward a **source-backed original selected stage or K08 author-final inscription**.
