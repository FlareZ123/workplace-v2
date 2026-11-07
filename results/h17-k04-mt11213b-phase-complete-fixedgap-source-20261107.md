# K04: entire 351-phase MT11213b source issuer, with variable fixed interpacket gaps

**Agent 7 | 7 November 2026 | New full-state algebraic source test.** All 8,424 original-source models contradict intact printer data. No K04 coupon was recovered; six original component commitments remain accepted and K04/K08 remain missing.

## Recovery hypothesis

Boost and the C++ Mersenne Twister engine specification include **MT11213b**, a 32-bit Mersenne Twister with 351-word state and 175-word twist offset. Its genuine parameterization is w=32, n=351, m=175, r=19, xor-multiplier 0xCCAB8EE7, right shift 11, left shift7 masked 0x31B6AB00, left shift15 masked 0xFFE50000, final right shift17, and seed multiplier1812433253.

This producer is smaller than the much-studied MT19937, and the 128 ordinary surviving printer packets supply enough 32-bit native output observations to form a directly checkable GF(2)-linear model even if the exact seed is entirely unknown. The candidate **does not assume a calendar seed, guess a CPython seed phase, or inspect the selected 18:02 ACK2**. It learns from the intact source's first 120 ordinary packets and reserves the final eight ordinary packets for whole-output holdouts when state inversion is unique.

The model allows four native 16byte packet presentations: big/little endian 32-bit words with original/reversed four-word order. It permits **exactly g discarded native outputs between every consecutive four-word packet**, for g in 0,1,2,3,4,8. It exhausts every possible **initial phase 0..350** of MT11213b's 351-word output block. Under each fixed configuration, it treats the initial 351 internal words as arbitrary, never restricting them to a seed-family dictionary.

Reference: [Boost's documented mt11213b definition](https://www.boost.org/doc/libs/develop/doc/html/doxygen/headers/mersenne__twister_8hpp_1a29ac4e21d84adda27beb1803a0525ca5.html). Its parameters were independently checked against the standard C++17 mersenne_twister_engine with unsigned 32-bit seed42.

## Exact executed source test

Source: unchanged resources/evidence/print/spool-reconstruction.log, SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. The 128 ordinary retained 07:00 through 17:35 UTC ACK attempt1 records PS-261003-0300..0427 supply the training/holdout population. Five late unusual rows, especially the disputed selected 0417 attempt2 ACK at 18:02, are excluded.

For each hypothesized native output index, reverse the authentic MT11213b output tempering to obtain a raw linear state observation. The first output block directly fixes the state bits at observed positions. Treat all unobserved first-block bits as independent GF(2) variables. Propagate them exactly through the authentic in-place 351-word MT twist, then append every later observed untempered source bit as a GF(2) equation. A source contradiction exists when an equation with zero unknown coefficients has a nonzero right-hand side, proving **no arbitrary MT11213b state** fits that complete model.

| Fixed discarded outputs per packet | Starting phases | Word/byte layouts | Original source assignments | Contradictions | Survivors |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 351 | 4 | 1,404 | 1,404 | 0 |
| 1 | 351 | 4 | 1,404 | 1,404 | 0 |
| 2 | 351 | 4 | 1,404 | 1,404 | 0 |
| 3 | 351 | 4 | 1,404 | 1,404 | 0 |
| 4 | 351 | 4 | 1,404 | 1,404 | 0 |
| 8 | 351 | 4 | 1,404 | 1,404 | 0 |
| **Total** | | | **8,424** | **8,424** | **0** |

Original-data tests were executed in bounded local groups of one gap or one serializer at a time; do not claim a single uninterrupted full-suite process completed. Earlier source-only first-gap run established the same contradictions for each gap at phase0. Source-visible sample: gap0, phase0 fails as soon as native output index351 is constrained; gap8, phase0 fails at index878 even after allowing thousands of unknown first-block state bits. All final phase/gap/serializer groups above completed with zero survivors.

## Independent authentic seeded controls

The standard-library C++17 engine with actual MT11213b parameters, seeded with integer42, produced initial raw 32-bit native outputs:

    1518079045 208983500 812239652 4170938572 3525382634

The independent Python seed/twist/temper implementation matched all five outputs and independently matched a 512-output C++ stream's entire next 161 native words after observing the first 351. This tests the recurrence and endian-safe 32-bit word handling.

A second synthetic family generated **72 genuine MT11213b source-like 128-packet streams**: six gaps × three distinct starting phases (0,175,350) × four serializers, each with a different authentic state/copy presentation. The same GF(2) solver produced **zero contradictions on all 72**. Where first120 packets uniquely identified the 351-word first-block state, the solver correctly predicted **all eight withheld complete 16-byte packets** (32/32 native words). For some configurations the first120 observations leave genuine state degrees of freedom; these were correctly reported as underdetermined rather than false whole-packet predictions.

Portable source-pinned reproducer: [Agent 7 MT11213b Python/GF2 SFT](../agents/agent7/k04_mt11213b_351phase_variable_gap_sft.py). It can run per-gap using the optional H17_GAP environment setting to avoid execution-session time limits. The report's original data, commitment digests, verifier, official candidate and accepted six components were not changed.

## Recovery consequence

This eliminates **only** a single persistent MT11213b stream with the tested constant word gaps, all state-block starting phases, and the four complete packet serializations. It does not eliminate mixed or variable per-job skips, one state reset per job, other PRNG variants, packet-stage transforms, an independent selected-only emitter, or an untrusted physical copier.

Most importantly, it authenticates **zero** bits of the selected 18:02 paper coupon and supplies **zero** final Emily caption words. Its positive result is a finite, independently source-checkable original-data producer rejection that makes further MT11213b seed brute force for the same source layout unnecessary. Further research should seek the selected media/copy provenance bridge or a complete author-final K08 phrase rather than another adjacent guessed generator.
