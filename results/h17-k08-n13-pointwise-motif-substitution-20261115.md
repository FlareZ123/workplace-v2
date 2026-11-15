# K08 pointwise motif-replacement model on Emily's retained drafts

**Agent 14 · 15 November 2026 · bounded original-source negative.**

## Question

Could the final keeper-envelope wording be a lightly edited version of one of Emily's three retained text bases—N02 (first crew-board draft), N06 (second desk draft), or N13 (desk-scene recollection)—with one to three individual words replaced by literal content words from her N20 intent brief and MAIL-11?

This is a pointwise edit model: every original base word not selected for replacement is retained, in its original position and order. No words are inserted or deleted. The replacement lexicon is frozen at 12 source-literal content words: sea, voices, table, people, room, water, outside, watch, long, each, other, line. Each occurs in N20 or MAIL-11; the lexicon is deliberately narrower than the full crew vocabulary.

## Exact test

For each of the three bases, enumerate every choice of one, two, or three distinct word positions. Replace each selected position with one lexicon word, excluding a no-op replacement when the replacement equals the original token. Preserve every other word and the complete source order. Normalize using the official K08 rule: lowercase ASCII alphanumeric words, punctuation to spaces, collapse to single spaces. For each complete phrase, compute HMAC-SHA256 with the original 16-byte K08 nonce, retain the first 16 HMAC bytes, SHA256 those 16 bytes, and compare the full 32-byte digest to the unchanged K08 slot commitment.

Inputs are source-pinned in the reproducer:
- noticeboard-and-desk-notes.txt: 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb
- mail/11.eml: f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29
- acceptance.json: 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f

The original N02 first-draft HMAC16 control reproduced exactly. A planted full-caption positive made by replacing the first three N13 words with sea voices table was found by the same three-position enumerator.

## Result

**No original K08 hit.**

| Base | Original words | Assignments checked |
|---|---:|---:|
| N02 | 13 | 486,431 |
| N06 | 11 | 293,172 |
| N13 | 22 | 2,694,648 |
| **Total** | | **3,474,251** |

The original K08 commitment matched zero candidates. The synthetic positive was found after 15 checks in its dedicated enumerator run. The six previously accepted components remain unchanged; K04 and K08 remain unresolved and combined REC8/1 remains incomplete.

## Interpretation and limits

This closes only the specified 1–3 pointwise replacement family over the 12-word N20/MAIL-11 lexicon and the N02/N06/N13 source bases. It does not exclude multiword replacement, insertion/deletion, reordering, a different base caption, newly authored words, or the actual final margin. The source does not establish that Emily used this exact edit operation; this is a falsifiable exploratory construction, not an authenticated history of authorship.

Reproducer: agents/agent14/k08_n13_pointwise_motif_substitution_sft.cpp. No source, candidate, acceptance commitment, or official verifier was modified.
