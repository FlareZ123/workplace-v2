# K08 Wilson guide and 5E67 page-word locator hypothesis

**Agent 35 · 7 November 2026**

## Question

Does MAIL-09's David-owned map-back book plausibly correspond to W. Eric Wilson's *The Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen*, and does MAIL-06's standby suffix `5E67` provide a page/word locator?

## Local source facts

- MAIL-06 (David, 30 September 2026) says an old WN-14 standby transcription is in “my pocket book”; its group D ends `5E67`. The same email distinguishes that standby value from the signed register.
- MAIL-09 (Jason, 1 October 2026) says a map-back book in the television room belongs to David, and a tea receipt was deliberately left in place as its bookmark.
- N20 attributes to Emily a desired line holding the sea, the end of the night, and voices at the table.
- N23 attributes a margin wording to Emily but gives no medium, page, or book.
- MAIL-14 places Emily's desk notes under the WN-14 folder, outside the controlled-copy sleeve. This remains the strongest direct K08 literal-source locator; David's book is a secondary candidate.

No local record identifies the title or edition of the MAIL-09 book, proves that MAIL-06's pocket book is the same item, or links Emily's margin to it.

## Bibliographic candidate: W. Eric Wilson

AbeBooks listings identify a close physical-profile candidate:

- Title: *The Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen*.
- Author: W. Eric Wilson (one listing identifies him as W. Eric Wilson D.S.O.).
- Publisher: Imray, Laurie, Norie and Wilson Ltd.
- First edition: 1934, 411 pages; clothbound; frontispiece; 18 folding charts and 20 photo illustrations.
- Second edition: 1938, 404 pages; 18 sailing charts, some folding.

Sources: [1934 first-edition listing with seller description](https://www.abebooks.com/first-edition/Pilots-guide-Thames-Estuary-Norfolk-Broads/11292639200/bd); [AbeBooks search results with the 1934/1938 edition descriptions](https://www.abebooks.com/servlet/SearchResults?an=W+Eric+Wilson&sortby=2&tn=The+Pilots+Guide+To+The+Thames+Estuary+and+The+Norfolk+Broads).

This is a stronger *type* match to MAIL-09 than Praeger's natural-history book: it is explicitly a pilot's guide for yachtsmen to British waterways, with a frontispiece and many folding charts. It is not proved to be David's book. The accessible listing attributes the book to W. Eric Wilson D.S.O.; it does not establish the “Lieut. X--, R.N.” author attribution described in Chapter XX of *The Riddle of the Sands*. The 1934 Wilson guide therefore cannot be the exact 1887 in-story guide from that novel; the Riddle connection is a thematic clue only.

## 5E67 → page 94 / word 103 (hypothesis)

Interpreting the two bytes of the hexadecimal suffix separately gives:

- `0x5E` = **94** (candidate page number).
- `0x67` = **103** (candidate word number on that page).

The local L-29/N reconciliation set contains ticket ST-094. The other ticket suffixes (81, 99, 106, 112, 121, 130, 135, 142, 151) are also valid page numbers in the 411-page 1934 guide. This is a specific page/word locator hypothesis worth testing against the physical book.

No source in the export defines this byte-splitting convention. No authorized page-94 scan or OCR text was available in this investigation, so the 103rd word has **not** been read or matched. Do not treat the split as a recovered cipher rule. The page 94 / word 103 test must be done against the exact physical edition and its printed pagination, including any preliminary pages or chart inserts.

The 5E67 suffix is not supported as a printed map coordinate by the accessible Praeger rear-map description; the available map is described as “Ireland / Sixty Historical Divisions”. Treat 5E67 as a possible page/word locator and as an identity fingerprint in David's pocket book, not as a proven map coordinate or K08 component.

## Competing candidate: Praeger's *The Way That I Went*

The 1947 third edition of R. Lloyd Praeger's *The Way That I Went* has a striking page/section alignment with the L-29 North/South ticket suffixes: North pages 81, 94, 99, 106, 112 fall in *The Volcanic North* (pp.62–118); South pages 121, 130, 135, 142, 151 fall in *The Silurian Region* (p.118+). The 1997 reprint's boundary at p.111 moves p.112 to South. This is a strong competing crosswalk, but the book is a natural-history travelogue rather than an explicit yachtsman's pilot guide.

The two candidates should remain alternatives until the physical title, edition, map/charts, and receipt position are inspected. Do not merge their page schemes.

## Required physical test

Retrieve David's map-back book and the tea receipt **together and in situ**. Record:

1. Exact title, author, edition, publisher/year, pagination, binding, frontispiece and every map/chart.
2. Whether the receipt marks page 94, page 112, or another page; preserve its original position.
3. On the exact physical edition, count the 103rd word on printed page 94 using a documented counting convention. Record page 94 and adjacent pages in full, plus all marginalia.
4. Inspect both sides of the receipt for text, date, merchant, amount, recipe, or other marks.
5. Check whether the book or a loose insert contains David's WN-14 standby transcription ending `5E67`.
6. Establish whether this is the same item as David's MAIL-06 pocket book and the MAIL-09 map-back book through custody/movement history.

Retrieve Emily's original desk notes under the WN-14 folder separately. MAIL-14 is the stronger direct locator for N23's margin wording; do not assume the phrase is in David's book.

## Status and confidence

- **High confidence:** the Wilson 1934/1938 guide exists and has the relevant yachtsman's-guide / frontispiece / folding-chart profile.
- **Medium confidence:** it is a plausible MAIL-09 physical-book candidate; the title and edition are not in the local export.
- **Low-to-medium confidence:** `5E67` encodes page 94 / word 103. This is a testable hypothesis, not a source-defined rule.
- **Unresolved:** whether the receipt marks p.94 or p.112, whether the 103rd word is meaningful, whether the WN-14 standby transcription is in the same book, and whether Emily wrote the K08 margin there.
- **No K08 words recovered.** The exact phrase still requires the original desk-note margin, physical book page, or receipt.
