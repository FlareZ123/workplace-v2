# Agent 9 — K08 LOW BIT full specificity review (2026-11-19)

I have completed the requested source-preserving specificity review and published:

- results/h17-k08-lowbit-full-specificity-review-20261119.md
- results/h17-k08-note-order-null-20261119.json
- agents/agent9/k08_note_order_null.py
- agents/agent9/k08_source_map_sensitivity.py

Key corrections and results:

1. The N10→N11 Emily +1 edit remains the unique valid +1 row edit producing ATEALBIT and the fixed ALOWBIT splice. But the generic contiguous 1+3+3 splice search has **2/288** ALOWBIT constructions because ATEALBIT has A at both positions 0 and 3. Agent35's upstream joint null (3/10,878,433,280) does not correct for this extra splice-position search.
2. The baseline K01/K02/K05/K06/K07 source map appears in **2/16** byte/packed-byte/hex/character-order conventions.
3. Selector 7 occurs in 24/120 lower/LSB component orders, 60/120 upper/LSB, 6/120 upper/MSB, and 0/120 lower/MSB. Literal YEA is 1/120 in lower/LSB.
4. Source-valid AX-7782 mask 255 still reproduces accepted K07 and 53D5. Selector 11 appears under 64/256 AX-7782 masks and 72/256 AX-7781 dry-run masks; only one AX-7782 mask is source-valid. Alternate renderings of the same official bytes yield selectors 13, 14, 3, or 13.
5. The bookmark control has two MAIL13 mappings; only reverse position 3 is the Tea-room stock sheets bookmark. Reverse ordinal remains inferred.
6. Across 1,054 email/routing three-word windows, two map N20 to “end of the”: MAIL11 “long watch with” and K08 rule “late watch rather”. Fixed positions 12/10/11 yield “the end of” only at N20. N13 also contains those words in ordinary prose, so do not claim phrase occurrence is unique.
7. The K08/source field is the only one of eight slot-source fields / 26 routing strings to reduce to VLOWL→12. The note HMAC graph has the unique N19/SANTE path 19→13→9→12→11; N23 “words” and N20 “wanted” are the only LOW19 tokens.
8. A new 200,000-trial within-author body-to-note-ID shuffle produced **0 full-chain hits** (rule-of-three 95% upper bound 1.5e-5 under that conditional shuffle only). This preserves authorship and all body texts, changing only which same-author body occupies each note ID. It is not a global p-value.

The existing 7,372,800-combination downstream factorial remains conditional: joint endpoint 1/4,800; source-valid mask only 1/307,200; exact 53D5 1/38,400. Do not multiply upstream, downstream, and note-order rates into a global probability.

Decision unchanged: LOW BIT is a source-local locator hypothesis, not a recovered K08 phrase. K04/K08 remain missing; no candidate or acceptance commitment was changed. Do not add another locator chain or rotate to another phrase without a new source witness. Next useful evidence is an independently authorized local copy of N23's final margin/envelope or associated native caption/profile/workbook material. The custodian reply channel remains closed.
