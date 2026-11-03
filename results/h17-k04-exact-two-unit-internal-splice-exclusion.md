# H-17 K04: two removed, two inserted copied-payload units, exact target gate

**Agent50 | 3 November 2026 | Source-anchored, target-facing corruption model, no accepted K04.**

## Distinct source and fault hypothesis

The original `ESC-N / PS-261003-0417 / 18:02 UTC / RECOVER / ACK attempt 2` copy reports a 16-byte buffer `A9A9DC5731A5E2AE879C47215C2559D5`. Original MAIL16 acknowledges that dispatch ACK does **not** independently validate copied spool payload bytes. The original unchanged route mask is `8556C8CB6140A7F9A5123AC7571BEE1C`, and original K04 commitment is SHA256 of the masked 16-byte component `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The closest source-target predecessor is [workplace-v1's one-unit internal splice](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-internal-splices.md): one arbitrary deleted/inserted bit, nibble or byte, with no authentic match. The previously completed [three-byte arbitrary substitution](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-three-byte-bound.md) and [all contiguous four-byte substitutions](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-unaligned-fourbyte-bound.md) likewise cannot exhaust two separated deletions **and** two arbitrary insertions, where the intact middle fragment slides.

**New conditional fault model:** during spool buffer reassembly, exactly two same-size units from the recorded 128-bit buffer are omitted, and exactly two unconstrained replacement units are inserted anywhere to restore its 128-bit width. Test units of **1 bit, 4 bits, or 8 bits** in byte-major, most-significant-first physical buffer order. There is no direct original evidence that two such operations occurred. This test deliberately holds the selected ACK's original bytes as the starting copy, without presuming the recorded media is correct.

For each granularity `g`, partition the 128-bit source into `N=128/g` units. Enumerate **every unordered pair** of original deletion positions, then **every unordered pair** of insertion positions in the shortened sequence as rebuilt to full N units, then **every** value pair in `0..2^g-1`. Reassemble the 128-bit candidate, XOR the unchanged original mask, and compare SHA256 of the 16-byte component against the original full digest. All source data and official verifier remain untouched.

## Exhaustive original target results

| Unit size | Units N | Original deletion pairs | Replacement position pairs | Values per pair | Complete assignment checks | K04 SHA hits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 bit | 128 | 8,128 | 8,128 | 4 | **264,257,536** | **0** |
| 4 bits | 32 | 496 | 496 | 256 | **62,980,096** | **0** |
| 8 bits | 16 | 120 | 120 | 65,536 | **943,718,400** | **0** |
| **All three** | | | | | **1,270,956,032** | **0** |

These are **assignments tested**; duplicated restored coupons can occur under different edit scripts and are deliberately not claimed as distinct candidates.

Exact shard coverage:
- Bit: 4 contiguous deletion-pair ranges beginning at 0, 2032, 4064, 6096, each 2,032 pairs and **66,064,384** checks, all zero.
- Nibble: 4 ranges beginning at 0, 124, 248, 372, each 124 pairs and **15,745,024** checks, all zero.
- Byte: 4 ranges beginning at 0, 30, 60, 90, each 30 pairs and **235,929,600** checks, all zero.

Four shard `COMPLETE` summaries were obtained for each of the three geometries. Every summary reports `accepted=0`. Enumeration cardinality follows `C(N,2)^2 * 2^(2g)`, and the disjoint shard boundaries exactly cover all deletion pairs.

## Reproducibility and independent positives

The [single C++17 OpenSSL SHA256 source](../agents/agent50/k04_two_unit_copy_sft.cpp) implements all three identical unit-level enumerators and supports disjoint `start_delete_pair, count_pairs` shards. It includes the exact unchanged copied ACK2, route mask and target digest as compile-time constants. `g++ -O3 -std=c++17 ... -lcrypto` was used for the exhaustive original test, with 12 completed original-target shards.

A completely separate Python encoder generated deliberately edited coupons by removing original units0 and1, inserting maximum-value units at positions4 and10, then XORing the known mask and independently hashing the result. Supplying those *synthetic* full commitments to the **same fixed search** recovered the planted complete component for all three granularities:
- 1bit: planted restored coupon `AB69DC5731A5E2AE879C47215C2559D5` and component `2E3F149C50E54557228E7DE60B3EB7C9`, found twice under equivalent edit assignments.
- 4bit: coupon `A9DCF5731AF5E2AE879C47215C2559D5` and component `2C8A3DB87BB54557228E7DE60B3EB7C9`, one match.
- 8bit: coupon `DC5731A5FFE2AE879C47FF215C2559D5` and component `5901F96E9EA2097E3955C5E60B3EB7C9`, one match.

Each full original-target shard and each planted control returned successfully. Original spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Original copied ACK and commitment are not altered.

## Scope and next recovery direction

This eliminates **exactly two lost plus two inserted units** in the unverified copied ACK under the specified three unit geometries. It does not exclude three-or-more edits, different copied event or producer, external old or new coupon, arbitrary interleaving, source transcription faults, or loss/repair of the routing mask. Although a successful SHA match would have provided a complete target K04 component, zero original hits were observed. Future work should seek historically meaningful copier/reprint signatures or original target-bearing source rather than repeat this exact finite family.

No independently authenticated selected K04 bit has been recovered; the original final K08 author-version caption is also unknown. **Six original component PASS, K04/K08 missing, combined REC8 INCOMPLETE.**
