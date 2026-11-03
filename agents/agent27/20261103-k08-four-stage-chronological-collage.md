# Agent27: chronological four-stage K08 caption collage

**3 November 2026, normal mode.** Original K08 is still missing. This is one tested complete-candidate *editorial mechanism*, not an author-attested final phrase and not a proof that K08 is unrecoverable.

## New candidate model

Consider the sequence of Emily's drafts and scene notes in `evidence/crew/noticeboard-and-desk-notes.txt`: N02 (first crew-board draft), N06 (second desk draft), N13 (end-of-night room/window recollection) and N20 (stated desired motifs). Unlike prior N13-base one/two-cut editors and source-pair condensations, this model rebuilds **the whole caption** as four chronological pieces. Each piece is one exact contiguous 2..5-token span from its respective source note, with no modification inside a span. Each of the three boundaries is either one space or the word `and` surrounded by spaces. Normalize as lowercase ASCII with spaces. The source words are taken after the colon in N02/N06 and from the complete one-line N13/N20 notes.

Spans: 42 (N02) × 34 (N06) × 78 (N13) × 110 (N20) = **12,252,240** plain compositions. Seven nonzero boundary masks add **85,765,680**, totaling **98,017,920** complete commitments. No word-bag shuffling, learned synonyms, N13 retained base, arbitrary long prose or variable-length unknown language is in this family.

## Reproducible controls and outcome

- Local original ZIP `h17-archive-dump.zip` extracted read-only. Exact crew-note SHA-256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.
- The implemented HMAC(key = route-sheet desk nonce, normalized sentence, SHA256)[:16], followed by SHA256(slot), matched the independently known N02 exact-caption digest `47e787785ff25082b4b960ad415f1e030ae0edc89c38b2f61c48f9331282ea55`.
- A planted full four-source caption appeared exactly once in each of the plain and joined runs. Expected exact candidate counts asserted. Local optimized OpenSSL/OpenMP source SFT SHA-256: `4e96274e25b72c8ba43be76803e1ed8298b6d3c1e1fe01b2169f448c44f276fe`.
- 12,252,240 base candidates: **0 original K08 commitment matches**.
- 85,765,680 distinct join-mask constructions: **0 original K08 commitment matches**. Four OpenMP threads, 16.23 s on local runtime for the expanded set.
- Neither run reads K04 selected ACK bytes, alters the six known slots, nor changes the original acceptance/verifier/route files.

**Result and limits:** The fully chronological four-fragment collage family fails. This is a distinct source-preserving whole-caption editorial explanation, but its source excerpts are not independently authenticated as actual terminal-envelope words. It does not exclude independent full rewrites, three-stage scenes, other source selection, or a genuinely witnessed final margin. Authentic newly recovered K08 words: **zero**. K04 also remains unresolved, combined REC8 incomplete.

**Next productive pivot:** Investigate an actual *version operator* or a differently grounded scene source that explains why a final envelope caption should have specific literal words. Avoid extending the above by merely multiplying arbitrary connectors, lengths, and synonyms.
