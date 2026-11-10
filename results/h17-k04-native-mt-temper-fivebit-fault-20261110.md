# H-17 K04: exhaustive native MT19937 five-bit pre-temper fault

**Agent 3 | 10 November 2026 | Original K04: zero accepted.**

## New conditional copy-recovery mechanism

The selected spool event is ESC-N, PS-261003-0417, RECOVER ACK attempt 2 at 18:02 UTC on 3 October. Its copied packet is A9A9DC5731A5E2AE879C47215C2559D5. The archived ACK does not prove independent copied-buffer integrity. Earlier exhaustive output-bit Hamming distances 0..8 from this packet rejected all candidates ([prior eight-bit shell](h17-k04-exact-eightbit-shell-completed-20261109.md)). A fault in the **four native untempered MT19937 generator words** can produce many output-bit changes through the standard linear temper transform while changing few internal bits.

This speculative internal copy/producer-fault model differs from direct bit or byte errors in the recorded packet. **No original record authenticates MT19937 as the printer's actual producer or proves a native fault occurred.**

Original unchanged source spool SHA256:
7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083

Original route XOR mask:
8556C8CB6140A7F9A5123AC7571BEE1C

Original K04 component SHA256 commitment:
930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0

Interpret the copied 16 bytes as four little-endian tempered 32-bit native outputs. For a native bit at word w and bit b, its 16-byte output error is the standard MT19937 temper function applied to (1<<b), serialized in little-endian at w. Temper stages are x ^= x>>11, x ^= (x<<7)&0x9d2c5680, x ^= (x<<15)&0xefc60000, x ^= x>>18. Since temper is GF(2)-linear, independently toggling up to five of the 128 native bits produces a complete 16-byte possible physical coupon by XORing their five full output deltas with the selected copy. The source-derived original mask is XORed afterward, then all 256 original SHA bits are compared.

Candidate output XOR deltas of Hamming weight at most eight are **counted as prior coverage and not redundantly hashed**. Every other candidate is hashed against the unchanged original K04 commitment.

## Exhaustive original result

The five-native-bit domain has C(128,5)=264,566,400 distinct subsets. The local original-source run completed all 32 disjoint shards, partitioned by the first two native-bit positions. Each shard checked the pinned untouched spool, original event, route mask and K04 target. Exact final aggregates:

| Original five-bit domain | Result |
| --- | ---: |
| Complete native fault assignments | **264,566,400** |
| Previously exhausted output-Hamming<=8 candidates | **941,188** |
| **Additional original full SHA256 checks** | **263,625,212** |
| K04 authentic original accepted matches | **0** |
| Synthetic independently planted whole-component hits | **1** |

The planted native subset uses indices 0, 17, 34, 67, 126 (zero-based across four little-endian native words). It yields a complete masked component with output Hamming distance 23, beyond all previously checked direct output shells. Its independently computed synthetic full SHA256 commitment is detected exactly **once**, within shard16/32. A separate compact implementation reproduced all four counters in shards 0,16,31 from the completed original run. No original evidence, mask, acceptance, verifier, or canonical candidate was modified.

The preceding local exact lower-weight run also completed, with full original K04 checks:

| Native fault weight | Newly checked, output HD>8 | Already-covered output HD<=8 | Genuine hits |
| ---: | ---: | ---: | ---: |
| 1 | 4 | 124 | 0 |
| 2 | 4,962 | 3,166 | 0 |
| 3 | 308,736 | 32,640 | 0 |
| 4 | 10,460,874 | 207,126 | 0 |
| 5 | 263,625,212 | 941,188 | 0 |
| **All 1..5** | **274,399,788** | **1,184,244** | **0** |

The previous output-HD<=8 result is accepted as already exhausted separately; therefore every pre-temper native fault of one through five bits has been covered or reduced to that earlier output fault family.

## Reproducer

[Portable original-source C++20/OpenSSL SFT](../agents/agent3/k04_native_temper_fivebit_sft.cpp) checks the original spool SHA256, selected row129 identity and buffer, mask, target commitment, and a five-bit synthetic planted full-coupon commitment. Compile using a C++20 compiler and OpenSSL libcrypto; run with the original spool-log path, plus integer shard ID 0..31 and shard count 32. Sum the four printed fields NEW_CHECKS, OLD_SHELL_SKIPS, ORIGINAL_HITS, PLANTED_HITS across all shards. A spool path without shard arguments runs the full five-bit domain in one process. The standalone code uses standard C++20, OpenSSL SHA256 and no GitHub workflow.

## Meaning and next attack

The original commitment rejects every complete coupon created by changing up to five bits of the four hypothesized original MT19937 native words underlying this selected copy. This **does not** establish that the historical printer ran native MT19937, or that the actual paper coupon differed by such an upstream fault. Upstream state-register errors whose effects cross multiple generated words and independent selected-stage copy mechanisms remain distinct models. An independent author-final K08 transcription or editor/selection rule remains necessary for that slot.

**No selected physical K04 bits and no exact K08 final words were recovered. Six other original REC8/1 slots PASS; K04/K08 MISSING; combined INCOMPLETE.**
