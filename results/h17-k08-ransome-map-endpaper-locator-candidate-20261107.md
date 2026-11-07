# K08: Arthur Ransome map-back book as a new locator candidate

**Agent 13 | 7 November 2026.** New competing book-location hypothesis; K08 is not recovered.

## Candidate

Arthur Ransome, *We Didn't Mean to Go to Sea* (first published 1937). An academic study of the novel's fictional map describes a doubled endpaper map, at the front and back of the book, with the English and Dutch coasts framing the Channel voyage. The map title describes the Goblin's outward and return journeys; its annotations include meeting a stranger in the dark and rescuing a kitten. The article also quotes the chart being spread on the cabin table. This gives a concrete candidate for MAIL-09's David-owned book with a map at the back and a thematic match for MAIL-11/N20's sea, late-night and table motifs.

Sources:
- H. J. (Lancaster University repository), “Paratext or Imagetext? Interpreting the Fictional Map”: https://eprints.lancs.ac.uk/id/eprint/75836/1/REVISEDFINALParatextorImagetext.pdf
- Faded Page text and contents for the 1949 18th impression (first publication 1937): https://www.fadedpage.com/books/20180428/html.php

The Faded Page contents place chapters at pp.79, 94, 109, 124, 136, 148, 161, 197, 208 and 257, among others. The story includes chapters on keeping awake, dawn at sea and grown-up voices below. The book's endpaper map and narrative are a stronger nautical locator candidate than an unqualified guess from theme alone.

## Bounded K08 tests

Using the exact route-sheet desk nonce, normalization, HMAC-SHA256/first-16-byte rule and the original K08 SHA256 commitment, the following printed candidates were checked:
- both map annotations quoted by the article;
- the map title;
- the map's tide annotation;
- the quoted cabin-table passage;
- the quoted map/chart passage;
- the book title.

All failed the complete K08 commitment. A further 2,151 contiguous normalized word spans from those quoted passages also produced zero hits. This rejects these printed excerpts as the exact final phrase. It does not test handwritten marginalia, unquoted passages, or Emily's separate photo-caption stack.

## Ticket-page observation: hypothesis only

The L29/N ticket numbers in binder-tab order are 94, 81, 106, 99, 112; L29/S are 130, 151, 121, 135, 142. These are valid page numbers in the 1949 impression and fall in the book's early sea-voyage chapters. Pages 81 and 121 are also listed illustration pages. This is an interesting cross-reference, but it is **not evidence that service-ticket IDs are book-page selectors**. Do not build a book cipher or infer words from those numbers without independent evidence that the physical receipt/book uses this mapping. The split is not a clean north/south chapter boundary.

## Limits and next discriminator

Nothing in the local export proves David owned this title, that the physical copy is the relevant map-back book, or that the tea receipt marks a specific page. The physical book, its receipt bookmark and Emily's handwritten margin remain absent. The K08 phrase is not recovered. Do not reopen the closed custodian channel. If an already-authorized source delivery or custody path yields the book, inspect the actual back endpaper, bookmark position, and any handwriting around the receipt-marked page; compare against Praeger and the other guidebook candidates before promoting this identification.

## Additional narrative check

The accessible 1949 impression text gives a closer thematic match than the map alone: one chapter describes a skipper exhausted after an all-night passage; a later night crossing leaves one child at the tiller while another sleeps; at dawn the crew gather in the lighted cabin with cocoa, bread and tableware as the sea changes from black to grey. A separate early scene explicitly has the skipper making room for Susan in the crowded cabin. These are strong locator-level parallels to MAIL-11/N20's long watch, water outside, end of night, and people making room for one another.

I tested the exact “made room for Susan” variants and **11,100** contiguous normalized word spans from the dawn-at-sea excerpt against the original K08 commitment. No hit. This further supports treating the book as a likely *inspiration/location clue*, not the literal source of the final phrase. The physical marginalia and separate photograph captions remain essential.

## Map/5E67 discriminator

The academic map analysis describes a pictorial Channel-route endpaper, with outward and return tracks, safe harbours, and narrative annotations. It does not describe a coordinate grid or a navigational grid reference. Thus the map-back clue fits Ransome well, while interpreting standby suffix `5E67` as a literal coordinate on this map currently lacks support. The actual physical endpaper should be inspected before ruling out any handwritten or publisher-added markings.

## 5E67 → page94/word103 hypothesis

A new cross-agent lead interprets the standby group-D suffix `5E67` as two hexadecimal bytes: `0x5E=94`, `0x67=103`. This may mean page94, word103 in the map-back book. The North binder's first tab is ticket `ST-094`, independently matching decimal page94.

In the 1949 impression of Ransome's book, p.94 begins Chapter VII, **“He's Been an Awful Long Time …”** (the actual “Dawn at Sea” chapter is p.208). Chapter VII opens with Jim's dinghy disappearing, Susan preparing a place for five at the cabin table, and the children waiting in fog after Jim's all-night passage. It includes the table, eggs, mugs, tea, and water/sea outside. This is a particularly close thematic match to MAIL-11/N20's long-watch, table, water and making-room description.

The first page's body word103 is `shelf`; if the eight-word chapter heading is counted, word103 is `took`. Neither is the final phrase. Therefore `5E67` may be a locator to handwritten marginalia on p.94 rather than a direct printed-word answer. The ST-094/page94 convergence is suggestive but does not establish a book cipher or identify the physical copy. The actual page layout, receipt bookmark and handwriting remain unverified.
