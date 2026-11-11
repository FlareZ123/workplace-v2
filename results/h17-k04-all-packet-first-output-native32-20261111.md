# K04: exhaustive native uint32 MT19937 first-output starts within retained printer packets

**Agent 40, 11 November 2026. Original K04 unresolved; original K08 unresolved.** This is a completed, source-gated, 32-bit seeded-producer exclusion. It produces no new accepted component.

## Distinct complete-candidate mechanism

A possible alternative to the assumed long-lived p951 printer stream is a native C++ `std::mt19937(uint32_seed)` producer started or restarted **inside any retained original printer packet**. If two consecutive native outputs match genuine adjacent original words, the seed is a reconstructible full generator and further source chronology could be checked to produce a complete missing ESC-N coupon.

Prior work covered the spool's row-zero first output and fifteen source-fixed negative-stage origins ([Agent 1](h17-k04-native-mt-single-seed-complete-exclusion.md), [Agent 3](h17-k04-native-pre-spool-seed-15origin-full32.md)). This trial has **no assumed native stage-start vector**. It takes every one of the 132 other printer packets at three possible starts, word lanes 0, 1, 2, with both 32-bit word byte orientations. Every start has a following original 32-bit word for an independently testable full consecutive pair. There are exactly **132 × 3 × 2 = 792** such source-anchored starts.

The disputed 18:02 ESC-N ACK2 payload (row129) is never decoded or used as a possible start, training example, comparison, or generator seed. Its job/attempt/status selector is the only field consulted. Original source SHA256 pin:

`resources/evidence/print/spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

## Executed full 32-bit seed search

For every integer seed in **[0, 4,294,967,296)**, a vectorized AVX2 implementation computes the exact first `std::mt19937` output, comparing it to a 792-source-word hash index with a non-excluding high/low-half prefilter. Every firstword collision is verified independently against the original **second** consecutive retained word with the C++ standard-library `std::mt19937` seeded generator. Lanes 0/1 also permit a third-word comparison. Checks are performed in both within-word endiannesses.

| Exact original-source measure | Result |
|---|---:|
| Original intact packets available | 132 |
| Distinct word-position/orientation starts | 792 |
| Exhaustive uint32 seeds | 4,294,967,296 |
| Prefilter survivors | 615,324 |
| Original firstword coincidences | 784 |
| **Original consecutive secondword matches** | **0** |
| Original consecutive threeword matches | 0 |

The full local original-source run finished successfully in **102.38 seconds** using four OpenMP threads; no shards are missing. Six real independent native-seeded first-output controls, including seed 5489 and 0xFFFFFFFF, passed. Additionally **36/36 planted packet layouts** (six seeds × three allowed firstword lanes × two byte orientations) reproduced their true first and second output words, and a third where applicable. The exact committed SFT also passed a local 100,000-seed smoke execution.

## Recovery consequence

**No 32-bit native MT19937 seed, emitted starting at any of these 792 original source packet positions, reproduces two consecutive genuine words.** Therefore this particular within-packet reset/initialization route cannot supply a candidate for selected K04. It does not exclude a seed origin at an unprinted stage, before the first printer record, after the third word, an independently reseeded selected-only event, a non-native MT initializer, or another producer/copy corruption mechanism. No historical company document actually identifies native MT19937 as the printer generator.

**Prior-art qualification:** [Agent16's earlier scalar-seed-register any-phase source falsifier](h17-k04-scalar-seed-register-any-phase-source-falsifier.md) already rejects all source-testable initialization phases **when the retrospective p951 MT stage vector is assumed**. The current scan's contribution is its **stage-index-free, direct original two-consecutive-output gate** covering the physical packet lanes without reliance on that p951 index vector, and its exhaustive all-uint32 check. It does not supersede the earlier conditional contradiction, recover a coupon, or justify repeating native seeded-origin searches.\n\nThis source-only test never queries the K04 acceptance target or route mask because it has **no surviving seed capable of predicting a full selected coupon**. Original `candidate.json`, `resources/`, `acceptance.json` and `verify.py` were untouched. Six components remain independently PASS; K04 and K08 are missing; combined REC8/1 stays INCOMPLETE.

**Reproducer:** [Agent40 single-file C++17 SFT](../agents/agent40/k04_native_all_packet_starts_sft.cpp). Run from repository root with a C++17 compiler supporting AVX2/OpenMP and OpenSSL: compile with `-O3 -std=c++17 -mavx2 -fopenmp -lcrypto`, then provide positional arguments `resources/evidence/print/spool-reconstruction.log 0 4294967296`. Exit status is zero when no multiword originals match; all counters are printed. The published source is identical to the locally executed final full test.
