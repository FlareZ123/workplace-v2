# K08: exhaustive five-word product of Emily's original vocabulary

**Agent 2 | 6 November 2026 | Complete original-source 5,904,900,000 candidate experiment | K08 NO_MATCH.**

## Why this candidate class

The original N18 commissioning-envelope label is a genuine five-word Emily inscription: **"Back before the first boat."** N17 standby is a longer eight-word inscription. The prior [short whole-corpus search](h17-k08-short-normalized-source-capsules-20261106.md) covers complete one/two evidence-word candidates and three-word crew-source candidates, and [this author's companion four-word work](h17-k08-emily-fourword-unrestricted-vocabulary-20261106.md) covers all four-word product strings from Emily's own 90 word types. Previous 5..14-word source-bigram walks require documented successive pairs. This experiment removes the bigram constraint for exactly **five words**, retaining an authentic author/label length precedent. Every word must be in the source-derived Emily vocabulary, with no semantic, grammatical, motif or adjacency filter. It thereby includes novel transitions, repeated words, and captions that other source-walk experiments could not construct.

Historical authorship does **not** establish that the final was five words or that Emily reused only her previous note vocabulary. The source does not provide a selected-to-final edit operation. The test is a finite exact candidate family, not a probability of recovering the original.

## Source, reduction and exact search space

Input: unchanged `resources/evidence/crew/noticeboard-and-desk-notes.txt`, SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. Extract all ASCII alphanumeric word types from all eight original Emily note bodies N02,N06,N10,N13,N17,N18,N20,N23; sorted deduplicated 90-word vocabulary, SHA256 of newline-separated list `a323bd487dce87a6023e813c2e9756e9103df4f2f771f3e5c0455e0f1e11e261`. This deliberately includes words from explicitly rejected earlier standby/commissioning labels as possible lexical reuse, without calling those labels the final text.

Enumerate `90^5 = 5,904,900,000` ordered five-word strings with repeats, joining words by one space, which is already the original ASCII normalization. Distinct combinations yield distinct complete normalized captions. For every string, calculate `HMAC_SHA256(nonce, UTF8(caption))[:16]` and SHA256 of that 16byte value against the complete original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. Original 16byte desk nonce: `5F933DA6A1BD03C32DA5CBC25344F497`.

Authentic, independently determined controls: N02 actual known first-draft HMAC16 `BF889359B0303F2B2B2FD96AE841210B` and N18 genuine five-word inscription HMAC16 `A3100AE1ABB9C8D58315D9EBF326978B`; both checked at runtime. Each of ten shards plants a distinct complete five-word candidate generated from the same vocabulary, independently hashes it, and confirms the search recovers its exact whole text **once**. These controls demonstrate that hashing and enumeration can recover a real length-five phrase if its words are in the defined search space.

## Executed original CI and results

Manual-only GitHub Actions [run 42286329615](https://github.com/FlareZ123/workplace-v2/actions/runs/42286329615), all ten matrix jobs **SUCCESS** (6 November 2026 20:12 to 20:17 UTC). Original checkout and compilation succeeded in each. [C++17/OpenSSL SFT](../agents/agent2/k08_emily_fiveword_product_sft.cpp) reproduces the source parsing, SHA pins, exact HMAC-SHA256 reducer, 90 vocabulary and first-word half-open range partitions. [Manual workflow](../.github/workflows/agent2-k08-fiveword-exhaustive-manual.yml) defines exactly ten disjoint ranges, each covering nine of the 90 first words.

| First-word index range | Unique complete phrases | Original K08 hit | Planted full positive |
| --- | ---: | ---: | ---: |
| [0,9) | 590,490,000 | 0 | 1 |
| [9,18) | 590,490,000 | 0 | 1 |
| [18,27) | 590,490,000 | 0 | 1 |
| [27,36) | 590,490,000 | 0 | 1 |
| [36,45) | 590,490,000 | 0 | 1 |
| [45,54) | 590,490,000 | 0 | 1 |
| [54,63) | 590,490,000 | 0 | 1 |
| [63,72) | 590,490,000 | 0 | 1 |
| [72,81) | 590,490,000 | 0 | 1 |
| [81,90) | 590,490,000 | 0 | 1 |
| **TOTAL** | **5,904,900,000** | **0** | **10** |

Actual log line from each successful job (illustrative first-word range 9..18):
```
K08 FIVEWORD source_sha256=13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb vocab_sha256=a323bd487dce87a6023e813c2e9756e9103df4f2f771f3e5c0455e0f1e11e261 shard=9:18 candidates=590490000 original_hits=0 planted_hits=1
```

All ten exact output lines were independently inspected through the dedicated GitHub Actions job-log reader, not inferred solely from CI green status. The code and original source remain unchanged after successful run; original commitment, verifier, and canonical candidate never modified.

## Bounded conclusion and next move

**No five-word final caption composed entirely of these 90 original Emily-note word types satisfies the K08 commitment.** This does not rule out cross-crew words, newly authored words, a six-plus-word inscription, or a literal hidden final-caption witness. It yields no authenticated terminal author-final word and no K08 component. **Do not repeat this entire 5.905-billion domain or expand automatically to 90^6 without a stronger final-version mechanism.** The very different K04 selected physical coupon remains opaque.

Unchanged recovery: K01, K02, K03, K05, K06, K07 PASS; K04 and K08 MISSING; combined REC8/1 INCOMPLETE.
