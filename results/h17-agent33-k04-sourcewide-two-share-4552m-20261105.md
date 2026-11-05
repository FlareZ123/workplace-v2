# K04: full original 67,470-source-window, two-share XOR candidate search

**Agent 33 | 5 November 2026 | Original K04 NO_MATCH.** The source documents do not attest a two-share XOR encoding. This is an exploratory complete-source producer hypothesis, distinct from earlier pair arithmetic over only 532 curated 16-byte source fields. Neither original coupon bytes nor a seventh accepted component were recovered.

## Exact original source and enumeration

Pinned original 46-member uploaded ZIP SHA256: e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7. All 46 original regular files were included. Crew notes source SHA256: 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb; original printer spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. From every file, extract all 16-byte raw windows (117,583 occurrences) and every sliding 32-character decoded ASCII hex window (892 occurrences). Deduplicate and sort: **67,470 complete 16-byte source values**, SHA256 of concatenated sorted values e75d45a2b9e95ed99ce911dc9c4d19ff04cd3bbd2d5fd7ef54e08d2c8f948ab5.

Every unordered pair A,B with repetition was checked as full (a) direct 16-byte K04 value A XOR B, and (b) source-derived coupon A XOR B XOR unchanged routing mask 8556C8CB6140A7F9A5123AC7571BEE1C. Hash the entire 16-byte result via SHA256 against untouched original K04 commitment 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0. No selected physical ACK2 bytes were assumed correct, though that copied fragment is retained as one untrusted source window. No historical archive files or checker modified.

## Actual complete computation

- Distinct original candidate-source pairs: **2,276,134,185**.
- Original full SHA256 K04 component assignments: **4,552,268,370**.
- Original commitment hits: **0**.
- Planted positive hits: **1**, using two original indexed windows (100 and 57480) and the actual K04 mask, with its own planted full SHA256 commitment.
- Actual local program output: `CARRIERS=67470 PAIRS=2276134185 COMPONENT_CHECKS=4552268370 EXPECTED=4552268370 ORIGINAL_HITS=0 PLANT_HITS=1 SECONDS=953.908`.
- GCC 14.2.0, OpenSSL 3.5.5, 12 configured OpenMP threads (about four CPU cores). Original local executed C source SHA256 60a4c101486fc24b08db9f480f0e7b66e9f189f19f200e1e80293309f5c36e3a.

Reproducer: [Python whole-original 16-byte window extractor](../agents/agent33/k04_sourcewide_two_share_sft.py), [C exhaustive SHA256 pair tester](../agents/agent33/k04_sourcewide_two_share_sft.c), and [opt-in manual Actions workflow](../.github/workflows/agent33-k04-sourcewide-twoshare-manual.yml). The original local run and committed source use the same source-window SHA, target, mask, pair traversal and SHA256 stages; only the local carrier-file versus portable stdin transport differs. The observed synthetic positive checks complete enumeration and reduction within the modeled family.

## Interpretation and remaining work

**Conditional exact exclusion:** a full original coupon/component formed as XOR of any two 16-byte windows present in the **decompressed 46-file archive** (optionally with the official routing mask) does not verify. This is not a cross-source recovery witness; no historical two-share law was supplied. This experiment excludes neither a lost original physical coupon nor a different source representation (ZIP container bytes, noncontiguous fragments, independent original records, other producer laws). Absent a genuine historical bridge, adding third and fourth arbitrary operands would be a low-value combinatorial search.

The original six slots K01/K02/K03/K05/K06/K07 remain PASS; K04 and K08 missing; combined REC8/1 INCOMPLETE. No author-final K08 wording was recovered.
