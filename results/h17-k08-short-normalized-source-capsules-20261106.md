# K08: exact short original-source normalized captions, 38,299,672 complete candidates

**Agent 43, 6 November 2026. Genuine original K08 NO_MATCH.** This closes a finite short-caption gap beyond the previous N13 edit, ordered source-bigram, long scene-grammar, imperative invitation and per-Emily-note searches. Six original REC8 slots remain accepted; K04 and K08 unresolved; combined INCOMPLETE.

## Source and hypothesis

The original routing sheet describes Emily's keeper phrase as rememberable text, without quoting the final inscription. Although MAIL11 and N20 describe a nuanced scene likely requiring more words, an exceptionally terse title remains possible. Instead of imposing a scene grammar, this experiment checks the complete 0-, 1-, or 2-word vocabulary product of **every** original text-like evidence file, and the complete 3-word product from both original crew source files. It allows adjacent pairs never written in the surviving sources. No source attests this short length or an author-final word.

Parse 40 original evidence files with .eml, .txt, .log, .md, .html, .json, .jsonl, .ini or .csv suffix; extract maximal ASCII alphanumeric tokens and lowercase them. The sorted, deduplicated original full vocabulary contains 2,285 words (newline-joined SHA256 b5acd81fe80f294cd3e0a4c01ca5e298aef1cf4879a3df9cb948294816013df3). The original crew-note and galley-log vocabulary contains 321 words (newline-joined SHA256 399ddef7c8cce60aa1e78d3ec85683b0188c08b4346ad0bd824d4068d8dc29ba). The original crew-note file SHA256 is 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb; attached ZIP SHA256 e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7.

| Exact normalized phrase family | Unique complete candidates | Original K08 matches |
| --- | ---: | ---: |
| Empty caption | 1 | 0 |
| Any one original-evidence word | 2,285 | 0 |
| Any ordered pair of original-evidence words | 5,221,225 | 0 |
| Any ordered triple of crew-source words | 33,076,161 | 0 |
| **Total** | **38,299,672** | **0** |

Every candidate receives the unchanged original nonce-keyed HMAC-SHA256 first16 and the unchanged complete SHA256 of that 16-byte component. Original K08 acceptance SHA256 is 285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747. All candidates are already normalized ASCII, and words may repeat. Distinctness follows directly from length and deduplicated vocabulary.

## Reproduction and checks

[Source-pinned C++17/OpenSSL SFT](../agents/agent43/k08_short_word_product_sft.cpp) checks original source hashes and vocabulary cardinalities and performs the full enumeration. The locally executed run reported source_0_1_2=5,223,511; crew_3=33,076,161; checks=38,299,672; genuine=0; synthetic=1 (18.34 seconds). The independent short-only run reproduced 5,223,511 comparisons, genuine=0, synthetic=1.

The source-authentic historical N02 inscription yielded known HMAC16 BF889359B0303F2B2B2FD96AE841210B. An independently planted in-family two-word string, “mugs sea”, gave HMAC16 47FB62A91DB4C0B5E88000BF2243EE09, SHA256 efcdd8a1f71e32ca72c8dac703344fe78848f8f4a7bc86dc1565330bf4cc40e2, and was recovered **once** under a separate synthetic commitment. No remote CI execution is claimed. Original evidence, verifier, acceptance, route and candidate remain unchanged.

## Consequence

This rules out only the exact short, original-token-based classes. A three-word caption containing words outside the crew vocabulary, a four-plus-word caption, or new authored vocabulary is not excluded. A long global-word Cartesian expansion without a final-version witness would simply repeat ungrounded phrase enumeration. The original author-final desk-margin text remains absent, with **zero authenticated K08 terminal words**. K04's selected original physical coupon remains unauthenticated.
