# K08: Robert Bridges corpus literal-span exclusion

**Date:** 2026-11-12  
**Scope:** source-motivated K08 candidate construction; exact contiguous text spans only  
**Outcome:** no K08 commitment hit in the three tested Bridges corpora.

## Why this candidate family was tested

The existing physical-book hypothesis identifies Robert Lloyd Praeger's *The Way That I Went* as a candidate for the "map in back" clue. That title is associated with Robert Bridges' poem "Fortunatus Nimium". Separately, Emily's N20 draft asks for a line holding the sea, the end of the night, and voices at the table. These two source clues justify testing Bridges' poetry as a bounded literal source family. This is not a claim that the final envelope caption is a Bridges quotation.

## Construction and acceptance test

For each text, scanning began at the Gutenberg START marker and stopped before the END marker (the preamble and trailing footer were excluded; the marker and title/metadata lines after START remain in the scan slice). The scan slice was normalized using the K08 rule: lowercase; replace every character outside ASCII letters, digits, and whitespace with a space; collapse whitespace; trim. Every contiguous word span in the stated length range was tested as UTF-8:

`mac = HMAC-SHA256(desk_nonce, normalized_span)[:16]`

A hit requires `SHA256(mac) == acceptance.slot_sha256.K08`.

The implementation's SHA-256 was checked against the standard `SHA256("abc")` vector and HMAC-SHA256 against RFC 4231 test case 1 before scanning.

## Corpus coverage and result

| Corpus | Normalized body words | Span lengths | Candidates tested | Commitment hits |
|---|---:|---:|---:|---:|
| Robert Bridges, *Poetical Works*, vol. 1 (Gutenberg 54789) | 42,504 | 1–24 | 1,019,820 | 0 |
| Robert Bridges, *Poetical Works*, vol. 2 (Gutenberg 55178) | 26,654 | 1–20 | 532,890 | 0 |
| Robert Bridges, *October and Other Poems with Occasional Verses on the War* (Gutenberg 55031) | 7,952 | 1–24 | 190,572 | 0 |
| **Total** | | | **1,743,282** | **0** |

The tested material includes the title-source poem "Fortunatus Nimium" and the sea poem "The Sea Keeps Not the Sabbath Day", as well as the relevant poems in both collected-works volumes. No exact contiguous normalized span in these corpora produces the K08 commitment.

Sources:
- [Gutenberg 54789 — *Poetical Works of Robert Bridges*, vol. 1](https://www.gutenberg.org/ebooks/54789)
- [Gutenberg 55178 — *Poetical Works of Robert Bridges*, vol. 2](https://www.gutenberg.org/ebooks/55178)
- [Gutenberg 55031 — *October and Other Poems with Occasional Verses on the War*](https://www.gutenberg.org/ebooks/55031)

## Interpretation and boundary

This closes only the **literal contiguous-span** hypothesis for these three public-domain corpora and the stated length ranges. It does not exclude an original caption, a paraphrase, a phrase assembled from non-contiguous material, a text from another author/work, or wording on the missing envelope/desk-note carrier. It does not solve K08 and must not be reported as a recovered phrase.

Do not repeat this Bridges-corpus sweep. The next useful K08 action requires a materially different, source-authenticated construction or the original final-caption carrier. The Praeger physical-book/page-coordinate hypothesis is separate and remains unvalidated; this result does not establish that book as the phrase source.
