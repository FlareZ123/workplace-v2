# K08: 13- and 14-word three-motif source-bigram completion (16 November 2026)

**Agent 28. Historical K08 acceptance: NO_MATCH across 226,714,348 complete original-target comparisons.**

## Boundary

This is the disjoint, previously unchecked 13/14-token portion of the same conditional 26-record directed-bigram model as Agent 41's 7–12-token motif-mask-7 SFT and Agent 7's 15-token motif-mask-7 SFT. It is an exploratory *complete phrase generator*, without evidence that Emily's actual final envelope wording was assembled as graph walks. Repeating adjacent graph lengths is not an independent author-final version mechanism.

The inputs are exactly 24 N01–N24 crew-note bodies plus MAIL-11 and MAIL-20 message bodies, with N17/N18 older envelope-label quotations removed from the email copies. ASCII alphanumeric lowercase tokenization and deduplicated within-record consecutive directed edges yield **26 records, 331 tokens, 570 edges**. A valid path is 13 or 14 words and contains at least one word from each literal motif set: {sea,water}, {night,watch,morning}, {table,voices,room}. Cross-document transitions may occur only where an identical word joins source-derived edges. Every path generates its entire normalized phrase, joined by one space.

Source SHA-256: notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; MAIL-11 `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`; MAIL-20 `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`. The route and acceptance hashes are also pinned in the reproducible source. Each candidate uses the original desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`: `SHA256(HMAC-SHA256(nonce, normalized_phrase)[:16])` compared with the complete unmodified K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

## Exact result

| Length | Independent Python dynamic-programming count | Executed complete checks | Original hits | In-domain planted positives |
| ---: | ---: | ---: | ---: | ---: |
| 13 | 35,053,300 | 35,053,300 | 0 | 1 |
| 14 | 191,661,048 | 191,661,048 | 0 | 1 |
| **Total** | **226,714,348** | **226,714,348** | **0** | **2** |

The original-source graph/count check reproduced the previously published lengths 7–12 exactly, including 554 at length 7 and 6,314,210 at length 12. The two independent Python-planted positive HMAC16 values are `16AD5A969D4AF0D40835DDC08C77C872` (length 13) and `35B505F202DB944E922AC95FEBA5E3BB` (length 14), each found once. The N02 complete-note HMAC reference is `BF889359B0303F2B2B2FD96AE841210B`. The local C++17/OpenSSL/OpenMP pass executed every 13/14 complete candidate and matched both independently computed counts and planted values. It did not modify any original evidence, source routing, commitments, verifier or canonical candidate.

The portable checked-in [reference SFT](../agents/agent28/k08_source_bigram_mask7_13to14_sft.cpp) implements the same source parser, exact-length DP pruning, original-target HMAC/hash and two planted controls, adapted from the published Agent 41 runner. Build with C++17 and OpenSSL, run with the unmodified extracted `evidence/` directory. This reference is single-threaded; the local four-thread implementation returned the results in the table.

## Research decision

The complete conditional graph domain for **all-three-literal-motif walks at lengths 7–15** is now covered when combined with the [7–12 result](h17-k08-source-bigram-mask7-7to12-20261116.md) and [15-word result](h17-k08-source-bigram-long-anchor-20261116.md). This is a domain closure, *not* an inference that the source graph is the true authoring process. Do not open 16+ generic graph length sweeps without a new dated editing/selection mechanism. The original terminal inscription remains unquoted; K08 has no accepted component and K04 remains unresolved. Official REC8/1 acceptance remains six individual PASS and combined INCOMPLETE.
