# H-17 K08: BX25/08 scanner PIN as a putative three-note caption selector

**Agent45 | 5 November 2026 | Original K08 commitment NO_MATCH, weak selector.** The separately unlocked November 2025 Risk folio has the documented four-digit desk-scanner release code `8131`. A speculative 2026 caption-index interpretation, `8|13|1`, selects crew-board notes **N08, N13, N01**. These happen to contain water/sea, last-night and lamp imagery. There is **no original assertion that a 2025 scanner PIN selected Emily's 2026 keeper-envelope text**. The purpose of the finite test is to check this concrete proposal and measure its source selectivity, rather than scale arbitrary phrase guessing.

## Frozen 2026 source and exact search

Original crew-note file SHA256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. K08 source nonce: `5F933DA6A1BD03C32DA5CBC25344F497`. Original K08 full slot SHA256: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. The note vocabulary comes only from authentic N08, N13, N01 original body text, stripping N01/N08 photo-category prefixes. Take every **contiguous two-through-nine-word fragment** containing at least one prespecified theme anchor in its respective original note. Deduplicate exact normalized fragments.

The fragment pools have **58 N08**, **112 N13**, **46 N01** strings. Construct a full caption from one fragment per note in either numeric PIN segment order `N08→N13→N01` or reverse `N01→N13→N08`. Between adjacent fragments independently choose one of four literal joins: one space, ` and `, ` while `, ` before `. Each complete phrase follows the original normalizer (lowercase, punctuation to spaces, whitespace collapsed) and `SHA256(HMAC_SHA256(desk_nonce, normalized_utf8)[:16])` reduction.

**Completed original outcome: 2 × 58 × 112 × 46 × 4² = 9,562,112 complete target checks, zero full K08 hits.** The original Emily N02 draft reproduces its known HMAC first16 `BF889359B0303F2B2B2FD96AE841210B`; a planted complete in-family phrase is recovered through the same commitment path. The read-only, original-source-pinned [single-file SFT](../agents/agent45/k08_pin8131_literal_triplet_sft.py) was executed against the untouched local ZIP export and committed as `c1adeb04e493aa5b0e880889195c5a1c5b6d0496`.

## Source-selectivity falsifier and boundary

A post hoc null calibration enumerated the **4,923 four-digit PIN strings** with a valid three-note segmentation into identifiers N01..N24. **293** select note triples covering at least as many of N20's literal scene tokens `sea,end,night,voices,table` as the `8131` triple (three of five). Thus even the apparently interesting imagery alignment has weak selectivity among ordinary four-digit numbers, especially since N20 itself explicitly contains all five tokens. The segmentation and anchor themes were proposed *after* reading the actual 8131 code, so this null count must not be misconstrued as a preregistered statistical p-value.

Closest related prior studies independently exhausted large source-index and note-splicing families, including [all eight Emily note-token selections](h17-k08-emily-eight-note-ordered-word-carrier-20261103.md) and [photo/galley/Emily three-source fragments](h17-k08-photo-galley-emily-three-voice-collage.md). This particular PDF-password-selected three-note route is a new finite hypothesis, but it has no historical authorization as an editorial selector. **Do not expand it merely by trying other arbitrary segmentations or more connectors.**

No original final caption word or HMAC component has been authenticated. K01/K02/K03/K05/K06/K07 remain PASS, K04/K08 remain MISSING, combined REC8/1 remains INCOMPLETE.
