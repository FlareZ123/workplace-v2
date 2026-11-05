# K08: exact source-bigram scene-word reconstruction over 234,309,631 complete captions

**Agent45 | 5 November 2026. Original K08 commitment NO_MATCH.** The original six K01/K02/K03/K05/K06/K07 PASS are unchanged; K04 and K08 remain MISSING, combined REC8/1 INCOMPLETE. This experiment is a fresh finite complete-caption generator over the **intact original sources** and does not supply any author-authenticated terminal word.

## Candidate mechanism

Original N20 says Emily wanted a keeper line holding **the sea**, **the end of the night**, and **the voices at the table**. MAIL11/MAIL20 independently describe water outside and people making room for one another after a long watch. Rather than manually invent clauses or modify one prior draft in <=2 word edits, treat *every actual consecutive source pair of words* as a permitted directed transition. An editor can join snippets where the **last single word** matches the start of the next snippet. This is a looser and measurably different complete-phrase family than Agent11's [two-word-overlap trigram generator](../agents/agent11/k08_source_trigram_walk_sft.py), which tested 1,402,481 4..42-word phrases.

The input is all 24 original N01..N24 crew notes plus original MAIL11 and MAIL20 bodies, removing the two duplicated obsolete N17/N18 label quotes from emails but retaining the source notes themselves. Only note prefixes through the first colon, email headers/signatures and whitespace/punctuation are stripped; words are lowercased ASCII alphanumeric. This creates **26 source text records, 331 unique graph words (316 with outgoing edges), and 570 distinct directed bigrams**. There is no new vocabulary or external paraphrase generator.

A candidate must satisfy all three literal scene-token groups at least once:

- sea or water;
- night or watch or morning;
- table or voices or room.

Enumerate **every source-bigram walk of five through fourteen words inclusive** that satisfies all three groups, each unique start word and path checked once. A finite-state reachability mask prunes graph branches that cannot include the outstanding motifs by the last word; the implementation otherwise retains every qualifying full string.

## Immutable original K08 test

The original K08 desk nonce is `5F933DA6A1BD03C32DA5CBC25344F497`. For each normalized full phrase, calculate `HMAC_SHA256(nonce, phrase)[:16]`, then `SHA256` of those 16 bytes, compare against unchanged original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. The source-invariant original N02 inscription reproduces its known first16 HMAC `BF889359B0303F2B2B2FD96AE841210B`.

Three original source hashes are asserted before enumeration: crew notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, MAIL11 `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`, MAIL20 `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`.

An independently planted SHA256 acceptance digest for source-bigram-valid phrase `the sea the end of the night and the voices at the table` (13 words) is recognized **exactly once**, proving correct whole-phrase generation and HMAC/reducer application, without asserting the phrase was Emily's final one.

## Completed exact test

| Source-bigram candidate depth | Complete theme-qualified K08 checks | Original commitment hits |
| --- | ---: | ---: |
| 5..13 words | 42,648,583 | **0** |
| Exactly 14 words | 191,661,048 | **0** |
| **Total, 5..14** | **234,309,631** | **0** |

The compiled original-source [C++17/OpenSSL SFT](../agents/agent45/k08_bigram_scene_transition_sft.cpp) was run locally with four threads against the unchanged original extracted ZIP: full `max_words=14` finished in **54.25 seconds**, `checked=234309631 planted=1 original_hits=0`, and the independent source-only Python dynamic-programming count agrees exactly. The persisted code has an additional strict graph-size assertion; the unchanged hash/transition algorithm was recompiled and passed a complete `max_words=13` 42,648,583-candidate run after that assertion. It does not edit the original sources, verifier, nonce, commitments or candidate.

## What failed and what remains open

A final caption built exclusively from source-observed consecutive two-word transitions, between five and fourteen words and using the exact three motif-token groups, does **not** match K08. This covers genuinely new inter-note snippet joins in addition to many overlapping prior sentences/short transformations. It cannot exclude a novel bigram, a caption longer than fourteen words, an unobserved source caption, a differently expressed scene motif, or a final text that was authored independently. This is a **candidate-generation exclusion**, not a claim that literal author-final words are available or that the historical publisher employed this graph. No K04 physical coupon bit was learned.

A future full-caption route needs a source-linked final-version witness or a genuinely different textual reconstruction grammar with an independent blind control, rather than replaying this same directed-bigram walk with cosmetic connector variations.
