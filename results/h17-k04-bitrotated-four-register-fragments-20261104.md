# K04: complete four-fragment independent bit-rotation/reflection coupon reconstruction

**Agent 11 | 4 November 2026 | original-source complete candidate experiment.** No new accepted component. Six previously recovered slots still PASS, K04/K08 unresolved and combined REC8/1 INCOMPLETE.

## Distinct physical-copy proposal

MAIL16 warns the archived spool payload for `PS-261003-0417` at 18:02Z, RECOVER ACK attempt2, lacks an independent physical-media checksum. The remaining 16-byte retained reconstruction `A9A9DC5731A5E2AE879C47215C2559D5` has four 32-bit words. A possible copier or serial-decoder error could preserve each **32-bit register's entire bit pattern**, but independently shift its bit origin or reverse its bit order, then assemble the words in a different order. Such a model can change all sixteen source bytes without introducing unconstrained replacement words. The original export **does not attest** bit reversal or rotation, so this is a conditional full-coupon search.

Prior Agent25 four-fragment reconstruction tested offset **byte-window copies** from four buffers, including byte reversal; v1 Agent9's global bit slip tested one missing **full-stream edge**; Agent19's full-byte lane repair tested four independently changed bytes. The present proposed four **32-bit circular bit rotations**, independently MSB-first or LSB-first within each source word, are different operations. Those prior tests may overlap individual generated candidates but do not exhaust this specific set.

## Frozen source and enumeration

Original `evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` is asserted before any candidate is tested. Select exactly the one historical ACK RECOVER attempt2 job0417 row and assert its copied payload. For each of the four source words independently, choose bit orientation original or full 32-bit reflection, and a circular left-rotation count 0..31. Choose one of 24 word permutations, assembling the complete 16-byte candidate. Each of the four original 32-bit words has exactly 64 distinct possible variants, and **all 256 word variants across four source words are pairwise distinct** (separate source-only check). Therefore all `24×64^4 = 402,653,184` 16-byte coupon assemblies are distinct. For every coupon test both interpretations: the historical XOR against unchanged original mask `8556C8CB6140A7F9A5123AC7571BEE1C`, and a direct whole-component hypothesis; compare full SHA256 against unchanged original K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The exact source-byte-based C++17/OpenSSL SFT uses six lexicographically contiguous permutation shards `[0,4),[4,8),[8,12),[12,16),[16,20),[20,24)`, each processing `4×64^4` complete distinct coupon assemblies, with both original K04 stages. A planted full-coupon positive uses permutation `[2,0,3,1]`, independent rotations `[3,11,17,29]` and bit reflections on the second and fourth words. Its SHA256 of XOR-masked complete coupon is calculated in memory and validated through the **same enumeration loop**.

## Completed original results

| Permutation shard | Full original SHA256 comparisons | Original K04 PASS | Planted control |
| --- | ---: | ---: | ---: |
| [0,4) | 134,217,728 | 0 | 0 (out of range) |
| [4,8) | 134,217,728 | 0 | 0 |
| [8,12) | 134,217,728 | 0 | 0 |
| [12,16) | 134,217,728 | 0 | **1 PASS** |
| [16,20) | 134,217,728 | 0 | 0 |
| [20,24) | 134,217,728 | 0 | 0 |
| **All 24 permutations** | **805,306,368** | **0** | **1 PASS** |

All six executable shards returned exit code 0 against the original user-supplied spool bytes. Measured local wall times 19.27, 19.56, 22.50, 18.14, 20.95, 17.50 seconds, with eight OpenMP threads in a Linux compute environment. Independently the narrower no-reflection subset was completed: 24×32^4 coupon assemblies / **50,331,648** original stage comparisons, zero original hits, one own planted positive. It is included in the full search and must **not** be added to the original unique-coverage count.

[Single-file source-pinned C++ SFT](../agents/agent11/k04_word_bitrotate_reflect_sft.cpp) requires C++17/OpenSSL with optional OpenMP and a read-only original spool pathname, then start/end permutation indices; its output includes actual hit and planted counts.

## Evidence limit

This test rejects only original K04 candidates whose physical coupon can be reconstructed by these exact independently oriented/bit-rotated copies of all four 32-bit words of the disputed spool buffer, optionally with a whole-word reordering, under either stated reduction stage. There is **no independent proof** that the printer actually corrupted 32-bit registers this way. Unknown physical coupon bytes, unrecorded source words, noncircular shifts, error masking across word boundaries, and other producer/copier stages remain possible. No historical K04 bit is authenticated and no K08 final wording is learned.