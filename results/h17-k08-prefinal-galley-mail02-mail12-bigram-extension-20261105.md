# H-17 K08: two pre-final galley emails add 155 source transitions, 1.508-billion complete caption exclusions

**Agent 2 | 5 November 2026.** Original K08 final caption remains unquoted; **zero** original K08 SHA256 commitment matches from **1,508,372,566** additional exact source-bigram candidate phrases. This is a new source-acquisition branch, not another spelling permutation of the previously searched 26-record corpus. Original six accepted REC8 slots remain individually PASS, K04/K08 MISSING and combined incomplete.

## New source evidence and specific historical motivation

Previous [Agent45 original 26-record directed-bigram search](h17-k08-source-bigram-scene-234m-20261105.md) used N01..N24 original crew notes and MAIL11/20. The separate [Agent2 implicit-theme complement](h17-k08-implicit-theme-bigram-complement-558m-20261105.md) exhausted 558,780,941 additional 2..11-word paths from exactly that graph. Neither source set included the original **pre-final galley correspondence**:

- **Emily MAIL02, 28 September 2026, 14:46 UTC** discusses soup for late arrivals, setting clean bowls aside and eating out of mugs when the dishwasher had finished. SHA256 `a4ac849e45362b93eea9950e61132213494ab3a7cc3967e353850dc221de3a11`.
- **Zoey MAIL12, 2 October 2026, 06:33 UTC** describes the chipped blue mugs, visitors, and the little lamp beside the window. SHA256 `4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd`.

These are real, contemporaneous sources about the exact table/mug/room imagery that Emily said informed the final desk caption, with source dates before the incident. They do **not** quote her final caption. Emily also explicitly describes reusing the desk notes and photograph captions in MAIL11; no such reuse is proved for these two extra emails.

Original 26-record corpus pin: crew notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; MAIL11 `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`; MAIL20 `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`.

## Exact original-only graph construction

Extract the same 24 one-line N-note bodies plus MAIL11 and MAIL20 body text as Agent45, omitting duplicate old standby/commissioning labels and signatures. Append the two additional body texts MAIL02 and MAIL12, trimming signatures and preserving their actual phrase order. Lowercase ASCII alphabetic/digit tokens and form directed pairs of consecutive tokens *within* each original record. Permit paths to bridge original records only through the same existing word, as before.

| Corpus | Original records | Unique words | Unique directed bigrams |
| --- | ---: | ---: | ---: |
| Previously tested | 26 | 331 | 570 |
| Plus two pre-final galley emails | **28** | **398** | **725** |
| Truly new directed pairs | | | **155** |

A candidate is new only when its walk contains **at least one of the 155 absent-before directed pairs**. Every path expressible solely with the previous 570 edges is excluded before checking the original commitment. A source-graph word path is normalized by single ASCII spaces, without fabricated vocabulary or added connector lists.

Use the **original unchanged** K08 desk nonce `5F933DA6A1BD03C32DA5CBC25344F497` as the binary HMAC-SHA256 key, use the full normalized candidate as message, truncate the MAC to 16 bytes, then SHA256 these 16 bytes and compare all 32 result bytes against the untouched original K08 target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. A historical first-draft N02 positive reproduces the known MAC16 `BF889359B0303F2B2B2FD96AE841210B`.

## Two nonoverlapping complete original-target experiments

**A. All novel source walks of 2..11 words, without demanding any literal scene motif.** This accommodates implicit metaphors from MAIL02/12, avoiding the earlier three-theme vocabulary gate.

| Word length | Newly tested complete K08 phrases | Original slot hits |
| --- | ---: | ---: |
| 2 | 155 | 0 |
| 3 | 2,129 | 0 |
| 4 | 9,925 | 0 |
| 5 | 52,261 | 0 |
| 6 | 294,106 | 0 |
| 7 | 1,516,285 | 0 |
| 8 | 7,695,084 | 0 |
| 9 | 38,923,994 | 0 |
| 10 | 194,876,282 | 0 |
| 11 | 965,260,043 | 0 |
| **Total A** | **1,208,630,264** | **0** |

The original ZIP local source-pinned C++17/OpenSSL run checked 2..8 and 9 directly, length10 across sixteen source-start-word modulo16 partitions, and length11 across sixteen source-start-word modulo16 partitions. All **16/16** length11 partitions returned no original hit and exactly **965,260,043** checks in aggregate, recorded in original local JSON shard ledger. A separate planted complete K08 for the genuine source transition caption `the late arrivals on thursday` is found exactly once, at length5. No matching original caption emerged.

**B. Longer 12..14-word source walks requiring the explicit three distinct N20 scene motifs** (one word of `sea,water`, one of `night,watch,morning`, one of `table,voices,room`), plus at least one of the newly acquired MAIL02/12 edges. These were *never* covered by Agent45, because those 155 new edges were absent. An exact finite-state future-reachability table prunes only paths that could not achieve the full three-group/new-edge conditions by length14.

| Length | New three-motif phrases | Original hits |
| --- | ---: | ---: |
| 12 | 5,763,001 | 0 |
| 13 | 39,385,754 | 0 |
| 14 | 254,593,547 | 0 |
| **Total B** | **299,742,302** | **0** |

Length12 ran unsharded with one recovered planted 12word source-bigram caption `at the box is easier on the sea the night the voices`; lengths13..14 were distributed into 16 disjoint start-word shards, with **16/16** original negative, summing to **293,979,301** full MAC16/SHA256 computations. A separate independent Python dynamic-program path count over the exact same original directed edges found precisely those per-length new-edge+motif cardinalities. All source files, K08 nonce, slot commitment and verifier were unchanged.

**Combined unique new-source family: 1,508,372,566 complete word paths, 0 exact original K08 matches.** A path cannot occur in both A and B because their length ranges are disjoint; no path could have existed in the previous 26-record bigram graph because the new-edge predicate is mandatory.

## Reproducibility, confidence and implications

- [Committed portable short source-pinned C++ SFT](../agents/agent2/k08_prefinal_galley_mail02_12_newedge_sft.cpp), `ROOT MAX_WORDS [MIN_WORDS [SHARD [SHARDS]]]`, scopes max10/min2 and max11/min11 partitioned modulo16.
- [Committed portable long motif-gated C++ SFT](../agents/agent2/k08_prefinal_galley_long_3motif_sft.cpp), same CLI for max12/min12 and max14/min13 partitioned modulo16. Original-source local implementation uses exact future reachability to prune unsatisfiable prefixes.
- The original source ZIP was used as a read-only input to the local executables. The earlier Agent2 manual GitHub Actions workflow was expanded with smoke runs of both committed SFTs against original repository `resources/`. The all-shards local execution and independent dynamic-program counts form the full-scope evidence; a short remote smoke alone must not be misrepresented as the full billion-scale execution.

This is a finite empirical **negative** for an explicitly historical, expanded 28-record word-transition language model, with complete K08 slot checks and two independent planted full-caption controls. It makes no claim that Emily wrote by bigram splicing. New author-created transitions, punctuation-sensitive pre-normalization behavior that changes word tokens, other surviving source genres, captions longer than11 without all three literal motifs, and captions longer than14 all lie outside this family. There is still **no authenticated final author-word**.

Original K04 physical ESC-N coupon remains missing and independent. K01/K02/K03/K05/K06/K07 individually PASS; original combined REC8/1 remains **INCOMPLETE**. A genuinely new author-final inscription or independent precise edit/source witness would be substantially more informative than retesting these already enumerated paths.
