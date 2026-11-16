# K08 source-bigram motif-mask-7 walks, lengths 13–14

**Agent 28's reported domain · independently reproduced by Agent 41 · 16 November 2026 · original K08 target: NO_MATCH**

## Question and scope

Agent 28's persistent memory already records a completed all-order search of the 13- and 14-token portions of the established 26-record source-bigram graph. This report preserves that domain and adds an independent, executable reproduction by Agent 41. It is not a new search domain.

The candidate family is every complete directed walk of exactly 13 or 14 tokens in the established graph, in any motif order, containing all three literal motif classes. It remains a conditional lexical model, not an authenticated claim about Emily's author-final process.

## Frozen inputs and construction

The graph reproduces the established source selection: 24 numbered crew notes plus MAIL-11 and MAIL-20, with the same removal of the two prior-envelope quotation strings and signature truncation.

Pinned SHA-256 values:

- Crew notes: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- MAIL-11: `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`
- MAIL-20: `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`
- Route: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- Acceptance: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

Tokenization lowercases ASCII and retains only letters and digits. The deduplicated directed graph contains **331 words and 570 unique bigram edges**. The three motif groups are exactly:

- sea / water
- night / watch / morning
- table / voices / room

An exact-length suffix-feasibility dynamic program prunes only prefixes that cannot reach all three groups in the remaining positions. Every complete candidate is normalized as lowercase tokens joined by single spaces and checked using `SHA256(HMAC-SHA256(desk_nonce_bytes, phrase_UTF8)[0:16])`. Source, route and acceptance pins are checked by the Agent41 C++ runner.

## Validation and result

Agent 28's memory records the same complete candidate counts and zero original matches. Agent 41 independently rebuilt the graph and ran a separate OpenMP C++17/OpenSSL implementation with five threads.

The independently recorded N02 first-draft HMAC16 control reproduced `BF889359B0303F2B2B2FD96AE841210B`.

Agent 41 planted a separate valid graph-walk positive control for each length. The 13-token control produced HMAC16 `B2864706B1F3F9EBDBE840E953E30E5C`; the 14-token control produced `D8500A0542D277B9B049A45313F22858`. Each was recovered exactly once by its corresponding complete search.

| Phrase length | Complete candidates | Original K08 hits | Agent41 synthetic control hits |
|---:|---:|---:|---:|
| 13 | 35,053,300 | 0 | 1 |
| 14 | 191,661,048 | 0 | 1 |
| **Total** | **226,714,348** | **0** | **2** |

Reproducible independent runner: `agents/agent41/k08_source_bigram_mask7_13to14_omp.cpp`. Agent 28's original checked-in runner is `agents/agent28/k08_source_bigram_mask7_13to14_sft.cpp`; as currently committed, its final per-length loop contains a compile-time syntax typo, so the Agent41 runner supplies the validated executable reproduction. Neither run changes the canonical candidate, source, acceptance commitment or verifier.

## Interpretation and next decision

This is a complete negative only for the stated source graph, literal motif vocabulary and exact lengths. Paired with Agent41's 7–12 result and Agent7's 15-token all-order result, all-order mask-7 walks of lengths 7–15 are now closed. The graph remains a conditional phrase-construction model: this does not rule out a different text carrier, authoring/version rule, semantic wording outside the literal motif groups, or a phrase not representable as a source-bigram walk.

Do not repeat this graph/motif/length domain. MAIL-12 points to the small card by the blue mugs; MAIL-14 says photographs and galley captions were kept with Emily's desk notes outside the engineering controlled-copy sleeve; MAIL-20 says the final wording matters. The next K08 step should identify or acquire that photo/caption/profile source, not expand generic graph-walk grids. K04 likewise still requires an independently validated native printer/coupon source. No seventh or eighth component was recovered; combined REC8/1 remains INCOMPLETE.
