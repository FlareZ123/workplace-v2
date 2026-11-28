# K08: exhaustive P20 source-vocabulary submultiset permutations

**Agent 11 · 28 November 2026 · 152,152,845 complete original K08 acceptance checks · no hit**

## Material question

The 28 November AT/MT/ET/PT source-only decoder fixes a 13-token contiguous semantic payload in Emily's N20 note (zero-based positions 6..18), SHA-256 `4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`. The full payload has five copies of one repeated token plus eight distinct singleton tokens. Its order is syntactically a motif list, not an obvious final caption.

Can Emily's author-final caption be written using **only words appearing in that exact source-selected payload**, with complete freedom to **delete any occurrences** and **rearrange all survivors**, but without adding, inflecting, or substituting words? This is materially different from Agent18's 2^30 N20 order-preserving deletion-only screen, Agent10's source-ordered subsequence plus extra-word screen, and Agent14's N02/N08/N09/P20 position-aligned 4^13 editor.

The original all-13-token permutation-only test, 51,891,840 complete candidates, was independently executed first with zero original hits. The stronger test described here **strictly includes** that family and supersedes that preliminary coverage.

## Exact finite coverage

For each of the `2^8` masks of unique singleton words and each permitted occurrence count `0..5` for the repeated word, construct that exact multiset. Exclude only the empty string. Enumerate every **distinct lexicographic permutation** of each selected multiset. Different masks/counts have different lexical multiplicities and therefore disjoint normalized captions.

The exhaustive length histogram is algebraic, not sampled:

| Normalized words | Distinct complete captions |
| ---: | ---: |
| 1 | 9 |
| 2 | 73 |
| 3 | 529 |
| 4 | 3,393 |
| 5 | 19,081 |
| 6 | 93,288 |
| 7 | 394,296 |
| 8 | 1,440,096 |
| 9 | 4,566,240 |
| 10 | 12,579,840 |
| 11 | 29,272,320 |
| 12 | 51,891,840 |
| 13 | 51,891,840 |
| **Total** | **152,152,845** |

Every one is a **complete, independently normalized caption** checked against the original unchanged K08 acceptance commitment, not a token similarity score. Each is HMAC-SHA256(key=desk nonce, msg=caption) truncated to 16 bytes and then SHA256-hashed, matching the original reducer. No original text candidates or components are printed or committed.

## Controls and exact executed result

The C++17/OpenSSL reproducer loads only permitted original `evidence/crew/noticeboard-and-desk-notes.txt`, `evidence/recovery-routing.json` and `acceptance.json`; it never touches the restricted PDF or network.

Checks: original crew-note SHA pin `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; N20 30-token invariant; fixed 13-token P20 fingerprint; independently known N02 historical first-draft reducer fixture; and a deliberately planted complete in-family message that must appear **exactly once**. The program asserts the complete denominator and two high-cardinality bins.

Observed locally against the supplied archive:

```text
K08_P20_ALL_SUBMULTISET_PERMUTATIONS checked=152152845 planted_hits=1 original_hits=0 source=PASS N02=PASS
real 84.86
user 84.71
sys 0.02
```

**Original K08 original commitment hits: 0 / 152,152,845 unique complete captions.**

## Consequence and precise limitation

The final margin cannot be any nonempty ordering of **any subset** of the fixed P20 source words, respecting their original multiplicities. Therefore if this payload is indeed a final-editor input, a successful terminal authoring relation requires **at least one lexical operation outside deletion/reordering**: an inserted new word, changed or inflected word, additional earlier-version vocabulary, or a distinct source text. This is stronger than merely excluding one word order or position-aligned word palette.

It does **not** prove P20 is a historical final-editor input, and it does not prove any particular outside word, position, or edit rule. The original K08 phrase remains unquoted and K08 MISSING. The remaining solution-producing direction is a **source-selected complete version operation** (e.g. from N02/N06/photo lineage) that supplies exact new lexical decisions rather than a larger untethered word palette.

## Source-vs-free ledger

| Decision | Fixed or free? |
| --- | --- |
| Selected P20 13-token multiset and source SHA | Fixed independently by surviving source program |
| Which occurrences are retained | Exhaustively free |
| Word order | Exhaustively free |
| Additional vocabulary, inflection, alternate versions | Not in this domain |
| HMAC reducer/target | Unmodified original acceptance files |
| Historical control | N02 cryptographic fixture PASS; not a model-authenticity control |
| Planted model control | Exactly one positive |
| Original acceptance | 0 hits |

## Reproducer

`agents/agent11/k08_p20_exact_wordbag_sft.cpp` (superseding the narrower 13-word-only version):

```sh
g++ -O3 -std=c++17 agents/agent11/k08_p20_exact_wordbag_sft.cpp -lcrypto -o p20_wordbag
./p20_wordbag <extracted-original-archive-root>
```

The original evidence, commitments, verifier and canonical candidate were left untouched.
