# K08: Alfred Noyes / Mermaid Tavern quotation lead

**Status:** new thematic lead; exact-quotation hypothesis falsified; no K08 candidate recovered.

## Why this lead was opened

The company name in the supplied records is Noyes Energy Group. That name could be incidental, but it also provides a specific author-name pointer to Alfred Noyes. Two poems in his collected works have unusually close thematic overlap with the keeper-caption brief:

- *Forty Singing Seamen* (Collected Poems, Vol. I): a crew crossing the sea, singing, arriving at twilight, and sharing a dinner.
- The “Tales of the Mermaid Tavern” scene (Collected Poems, Vol. II): midnight, a shared cup, new songs and voices, friends saying good-night, a head bowed across a table, and old companions' voices gathering in the room.

The latter is particularly close to MAIL-11 / N20's description of a line holding the sea, the end of the night, and voices at a table. This is a **hypothesis about a possible literary source**, not evidence that Emily's caption was taken from Noyes. The MAIL-09 book-with-map clue has not been linked to a Noyes volume.

## Test

Used the exact K08 normalization and commitment procedure from the supplied routing/acceptance data:

1. lowercase;
2. replace punctuation/non-alphanumeric characters with spaces;
3. collapse whitespace;
4. compute HMAC-SHA256 using the supplied K08 desk nonce;
5. compare the first 16 bytes against the K08 component commitment.

Enumerated every contiguous normalized word span of lengths 1–30 in:

| Source text | Normalized words | Candidate spans tested | Match |
|---|---:|---:|---|
| *Forty Singing Seamen* (Vol. I) | 989 | 29,235 | None |
| “Tales of the Mermaid Tavern” midnight/table/old-friends scene (Vol. II) | 597 | 17,475 | None |

The test used the complete relevant poem text for the first item and the full identified scene excerpt for the second. Neither produces the committed K08 value as an unchanged contiguous quotation.

## Interpretation

- A verbatim contiguous quote from either tested passage is ruled out under the supplied normalizer.
- The thematic match is strong enough to preserve as a lead, but not enough to promote a paraphrase, splice, or generated phrase.
- No source-grounded editing/selection operator has yet been identified. In particular, the Noyes name alone does not establish that the missing physical book was by Noyes.
- This does not recover K08 and does not alter the acceptance commitment.

## Reproduction sources

- Alfred Noyes, *Collected Poems*, Vol. I, Project Gutenberg: https://www.gutenberg.org/files/30501/30501-h/30501-h.htm (the “Forty Singing Seamen” text).
- Alfred Noyes, *Collected Poems*, Vol. II, Project Gutenberg: https://www.gutenberg.org/cache/epub/30599/pg30599-images.html (the relevant “Tales of the Mermaid Tavern” scene, around pp. 431–433).

## Next useful test

An independent K08 reviewer should determine whether there is an authenticated edition/selection clue connecting Emily's final margin caption to this material, and require a complete independent caption/label control for any proposed transformation. Do not broaden into another unconstrained phrase-generation sweep.
