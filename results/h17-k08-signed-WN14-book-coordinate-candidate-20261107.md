# K08: signed WN-14 groups as a bounded book-coordinate candidate

**Status:** deferred, unverified hypothesis only. No K08 phrase has been extracted, and no candidate has been accepted. In accordance with the current source-first freeze, do not conduct remote book OCR, page-word extraction, or catalogue-alias probes until David's exact physical book and edition are independently identified.

## Question

Can the four signed WN-14 groups be read as eight ordered page/word coordinates into David's map-back book, producing the keeper's eight-word caption?

This is a new, finite interpretation of the complete signed groups. It is separate from the retired `5E67 → page 94 / word 103` idea, which came from the explicitly stale standby transcription.

## Source facts

- MAIL-03 gives groups A and C and says the four boxes follow their letters when the register is re-entered; the printer's two-column layout was only to fit the paper.
- MAIL-06 gives the remaining signed groups B and D. It explicitly says the standby transcription ending in `5E67` is not the signed duty-register value.
- MAIL-09 describes David's book as having a map in the back and a tea receipt used as a bookmark. It does not name the title or edition.
- The K08 rule supplies an exact phrase normalizer and HMAC construction. The K08 commitment is available in `acceptance.json`.

Source pins:

| Source | SHA-256 |
|---|---|
| `evidence/mail/03.eml` | `3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889` |
| `evidence/mail/06.eml` | `6049994562a82e46afd3f0231e136a1e6911cc3040d848e32eaa5771a6f8c2f3` |
| `evidence/mail/09.eml` | `1bda8bbf1e7b661a04fd58c36c38f2b66d2e2410265c311cc09c8e2bf810f08c` |
| `evidence/recovery-routing.json` | `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` |
| `acceptance.json` | `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f` |

## Frozen interpretation

Read each 4-byte group as two ordered unsigned-byte pairs, `(printed page, one-based word)`, and process groups in the source-defined A→B→C→D order:

| Group | Signed bytes | Coordinate 1 | Coordinate 2 |
|---|---|---:|---:|
| A | `04 9A AB 2E` | (4, 154) | (171, 46) |
| B | `1C DE 7A 82` | (28, 222) | (122, 130) |
| C | `CD 7C 60 23` | (205, 124) | (96, 35) |
| D | `43 03 C9 1A` | (67, 3) | (201, 26) |

The page/word interpretation is an inference, not a rule stated in the sources. The A→D ordering is source-supported; the byte-pair decoding is not.

## One-shot test protocol

1. Identify David's exact physical book and edition from the original object, its title page, binding, map, receipt bookmark, and any provenance note. Do not substitute Cowper, Praeger, Wilson, or *The Riddle of the Sands* merely because one resembles the description.
2. Obtain faithful text or images for printed pages 4, 28, 67, 96, 122, 171, 201, and 205. Printed pagination must be retained; PDF/image sequence numbers are not substitutes.
3. For each page, apply the K08 normalizer exactly as written in `recovery-routing.json`, split on collapsed whitespace, and take the listed one-based word. Do not try alternate page offsets, zero-based indices, reversed byte order, word/page reversal, OCR repairs, or other permutations.
4. Concatenate the eight words in A→D order. Compute the specified HMAC-SHA256 with the decoded `desk_nonce`, retain the first 16 bytes, and check the SHA-256 component commitment.
5. A missing page, out-of-range word, or commitment mismatch rejects this frozen interpretation. Do not turn a failure into a parameter sweep.

## Reproducible harness

`agents/agent44/k08_signed_group_pageword_sft.py` accepts a JSON object mapping printed page numbers to their transcribed text, plus the supplied routing and acceptance JSON files. It emits the eight extracted tokens, normalized phrase, component, and commitment result.

The harness was smoke-tested with synthetic page text to verify coordinate order, one-based indexing, normalization, and the HMAC/commitment path. The synthetic run correctly returned `NO_MATCH`; it is not evidence about David's book.

## Limitations and next evidence

- The exact book and edition are not identified.
- MAIL-09 does not explicitly say the book supplied Emily's final wording. K08's stated source remains the keeper's desk phrase, crew notes, and noticeboard drafts.
- The page/word convention is inferred. The coordinate set merely fits several candidate book lengths and therefore does not identify a title.
- No book pages were available in the surviving export, so no words or phrase have been recovered.

The only worthwhile next action is to inspect the exact David-owned book and its receipt bookmark. If that physical object cannot be located or identified, leave this hypothesis dormant.