# K08 hypothesis: K07 page/word pairs may locate a handwritten book margin

**Status:** bounded, unverified locator hypothesis. No K08 phrase or component recovered.

## Question

Could the eight accepted K07 transfer-checkpoint pairs be page/word locators for the personal book mentioned in MAIL-09, with the relevant K08 wording appearing as a handwritten marginal note rather than as eight printed body words?

## Source basis

- N23 says the wording “in my margin” was not an official slogan and distinguishes that wording from the words finally put on the recovery envelope.
- MAIL-09 describes a book with a map in the back, says it belongs to David rather than the communal shelf, and mentions a tea receipt left as a bookmark.
- K07 is an accepted 16-byte component reduced from eight two-byte transfer checkpoints. A page/word interpretation is a hypothesis about those pairs, not a rule stated by the source.
- The 1889 *Falcon on the Baltic* scan is a candidate for the map-back book, but no supplied source authenticates its identity as David's physical copy.

Together these clues make a physical-book margin a plausible locator target. They do not establish that N23's “my margin” is in that book, that the book is the Falcon, or that any marginal draft is identical to the final envelope inscription.

## Interpretation and decision impact

The page/word experiment should not assume that the eight selected printed body words are themselves the K08 phrase. If the coordinates resolve, the printed word may only anchor the relevant page/location; a handwritten margin could contain an earlier draft, while the recovery envelope retains the final wording. Public-edition body OCR cannot recover a personal annotation that is absent from that copy.

This interpretation explains why a body-word phrase search could be unproductive without implying that K08 is recoverable from the public text. It changes the next decision from further phrase generation to preserving a bounded page/anchor locator and, only if useful, acquiring the corresponding margin in the actual physical copy.

## Bounded check

Keep this inside the already existing K07 page/word experiment:

1. Reuse the existing signed-viewer capture and the same eight predeclared K07 coordinates only.
2. Record requested-page identity, visible printed folio, and anchor resolution separately from OCR, phrase construction, and HMAC.
3. A missing page or unresolved anchor is **INCOMPLETE**, not a no-hit.
4. A resolved public-edition page/anchor is locator evidence only. Do not generate a K08 phrase from an unauthenticated public copy.
5. Do not add books, editions, offsets, tokenizers, coordinate grids, or a new workflow.

This boundary follows the Critic's 2026-11-20 21:58Z direction in `communications/agent50/20261120T215800Z_Critic-margin-locator-boundary.md`.

## Evidence still required

A K08 candidate still requires the complete normalized wording from a source-bearing construction and the unchanged original K08 commitment check. The decisive records remain:

- the actual map-back book or an authorized image of the relevant physical margin, with ownership/custody and page identity;
- the original recovery-envelope face, because it records the final wording rather than an earlier margin draft;
- a source-visible edit/version link connecting any margin or photo-caption wording to Emily's final envelope inscription.

Do not treat a public book scan, a resolved anchor, a thematic match, or the N23 transcription alone as the final phrase. No source bytes, acceptance commitments, candidate values, or verifier were changed by this hypothesis.
