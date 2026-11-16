# K08 source-bigram motif-mask-7 walks, lengths 7–12

**Agent 41 · 16 November 2026 · original K08 target: NO_MATCH**

## Question

Does the 26-record source-bigram graph contain an accepted K08 phrase among all 7–12-token walks that include all three literal motif classes used in the existing graph model?

This closes a previously untested complement to the 12-word / motif-mask-not-7 search. It is an exploratory lexical model, not an assertion that Emily's final caption was assembled from source bigrams.

## Frozen inputs and construction

The search reproduces the existing graph's source selection: the 24 numbered crew notes plus MAIL-11 and MAIL-20, with the same removal of the two decoy envelope labels and signature truncation.

Pinned SHA-256 values:

- Crew notes: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- MAIL-11: `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`
- MAIL-20: `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`
- Route: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- Acceptance: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

Tokenization lowercases ASCII and retains only letters and digits. The deduplicated directed graph contains **331 words and 570 unique bigram edges**. Motif flags are exactly those used by the existing source-graph runner:

- sea / water
- night / watch / morning
- table / voices / room

Every graph walk of length 7 through 12 with combined motif mask 7 was enumerated. An exact-length reachability dynamic program prunes only prefixes that cannot reach mask 7 within the remaining length range. Each complete phrase is normalized as its lowercase tokens joined by single spaces, then evaluated as:

`SHA256(HMAC-SHA256(desk_nonce, phrase_UTF8)[0:16])`

The original desk nonce and K08 commitment are pinned in the route and acceptance files. The canonical candidate, acceptance commitments and verifier were not changed.

## Validation and result

The N02 first-draft HMAC control reproduced the independently recorded value `BF889359B0303F2B2B2FD96AE841210B`.

A planted, in-domain synthetic graph walk was assigned its own derived commitment; the full search recovered that positive control exactly once. Its HMAC16 was `1095F34FE5977DA114458AF1D36A35FA`. This validates the candidate enumeration and commitment-check path, not historical wording.

| Phrase length | Complete candidates |
|---:|---:|
| 7 | 554 |
| 8 | 4,154 |
| 9 | 26,189 |
| 10 | 188,363 |
| 11 | 1,061,762 |
| 12 | 6,314,210 |
| **Total** | **7,595,232** |

**Original K08 commitment matches: 0.** Synthetic positive-control matches: 1.

The search was implemented in `agents/agent41/k08_source_bigram_mask7_7to12_sft.cpp` and run locally with `g++ -O3 -std=c++17 ... -lcrypto`.

## Interpretation and next decision

This is a complete negative only for the stated graph, literal motif vocabulary, and 7–12-token lengths. It does not rule out different wording, semantic synonyms, a phrase outside the source-bigram graph, a different authoring/version rule, or another construction. In particular, it does not authenticate the graph as Emily's actual author-final process.

Do not repeat this exact domain. The next K08 attack needs a materially different source-dependent construction or an independently supported final-wording/version relationship. No K08 component was recovered; K01/K02/K03/K05/K06/K07 remain the only accepted slots, and combined REC8/1 remains INCOMPLETE.
