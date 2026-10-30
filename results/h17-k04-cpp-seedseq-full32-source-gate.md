# K04: exact one-word C++ `std::seed_seq` full-32-bit producer exclusion (conditional p955)

**Agent 4, 30 October 2026, ~04:54 UTC.** This is a complete computational exclusion of one explicitly scoped possible printer producer/initialization, **not** the recovery of any historical coupon byte or a claim that this was the physical producer. The original acceptance hashes, K04 mask, selected 18:02 ACK row and K08 were **never read by the experiment**.

## Source-derived hypothesis and prior art

The unmodified original printer spool has SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Under the previously published common-MT19937, *retrospectively selected p955* row-start chronology, V1 Agent22's GF(2) inverse using **only the 128 ordinary source printer rows** gives source rank **15,014**, with **190 completely fixed** pre-first-twist initialized-state words. In particular:

```text
S[3] = 873F7515
S[4] = ADD0D034
```

The original selected `PS-261003-0417` 18:02 ACK row and **all five exceptional late rows** are excluded from the observation equations used to fix these state words. The p955 chronology was earlier chosen using some late records, so it is **not a blind, independently established historical epoch**.

The hypothesized producer is a standard C++ `std::mt19937` whose initialized register is produced by `std::seed_seq{one_unsigned_32bit_word}`; its standard `generate(624)` outputs must equal the two fixed words if this is the historical model. The `std::seed_seq` algorithm is specified in [cppreference's generation rule](https://en.cppreference.com/cpp/numeric/random/seed_seq/generate).

**Closest predecessor:** V1 Agent3 exhausted **65,536** 16-bit-valued single-word inputs with zero `S[3]` hits; V1 Agents2/3 attempted full 32-bit symbolic bit-vector models and obtained **UNKNOWN** after bounded Z3 timeouts. The present experiment is the *completed full-domain computation* of that previously unsolved input range, not a new independent source observation.

## Exact reproducible computation

[Agent4's AVX2 single-file reproducer](../agents/agent4/k04_cpp_seedseq32_avx2_sft.cpp) implements the standard two-pass `seed_seq` recurrence with eight 32-bit lanes. It executes all 624 steps of the first pass and through k=946 of the second pass, the last step capable of changing either `S[3]` or `S[4]`. It first compares seven distinct seeds (`0`, `1`, `0x8131`, `0x12345678`, `0xDEADBEEF`, `0xFFFFFFFF`, `123456789`) against **native `std::seed_seq.generate`** on the same compiler/runtime, checking both words for each. All seven pass.

Four disjoint exhaustive searches each cover `2^30` inputs at starts `0`, `1073741824`, `2147483648` and `3221225472` respectively, total **4,294,967,296 / 2^32 unsigned seeds** without overlap or omission. Shard runtimes were 707.139, 707.540, 706.716 and 706.185 seconds on four concurrent local CPU workers. All four completed successfully with seven native-positive controls each; the one `0x8131` complete synthetic pair fell in shard zero as expected.

| Seed range start | Inputs | S[3] matches | Both-word matches |
| ---: | ---: | ---: | ---: |
| 0 | 1,073,741,824 | 0 | 0 |
| 1,073,741,824 | 1,073,741,824 | 0 | 0 |
| 2,147,483,648 | 1,073,741,824 | 2 | 0 |
| 3,221,225,472 | 1,073,741,824 | 0 | 0 |
| **Total** | **4,294,967,296** | **2** | **0** |

The only two first-word matches were independently tested again with **native C++ standard-library generation**, reproducing their `S[3]=873F7515` and disproving `S[4]=ADD0D034`:

| Single-word seed | Native S[3] | Native S[4] | Source-required S[4] |
| --- | --- | --- | --- |
| `8B63FE5E` | `873F7515` | `B6A7EC44` | `ADD0D034` |
| `A48B1F40` | `873F7515` | `21CA9F65` | `ADD0D034` |

This is an exact **zero-pair** exclusion for all unsigned **single-word, full-32-bit** `std::seed_seq` initializers under the specified p955 source-state reconstruction. It also subsumes V1 Agent3's prior 16-bit subset and closes the precise 32-bit timeout question.

## What the result cannot conclude

The source model does **not** establish that the historical printer used C++ `std::seed_seq`, that its initial MT output epoch is the retrospective p955 placement, or that it shared a physical producer with all printed rows and the selected ESC-N cassette. Multiword `seed_seq`, other MT initializers, earlier cycles, different row geometry, corrupted source copies and independent producer streams remain outside the test. No cryptographic acceptance value was queried, and the two `S[3]` coincidences are **not** plausible recovered coupon candidates because their source-required second word fails.

**Target-information impact:** K04 exact authenticated selected bits **0/128**, K08 quoted exact final words **0**. Existing K01/K02/K03/K05/K06/K07 still PASS; combined REC8 remains INCOMPLETE. Do not enlarge this into adjacent speculative producer families without a new source-authenticated engine/epoch relation or an independently indexed target-ancestor donor.
