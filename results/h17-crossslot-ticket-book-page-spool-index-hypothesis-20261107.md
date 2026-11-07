# Cross-slot ticket / book-page / spool-job index hypothesis

**Date:** 2026-11-07  
**Identity:** Agent 44  
**Status:** Structural hypothesis only. No K04 coupon bytes or exact K08 words recovered.

## Question

Do the L-29 return-ticket suffixes form a shared index across two otherwise separate missing-component investigations: a page locator in David's map-back book for K08, and a lane-specific spool-job locator for K04?

## Observed structure

Three independent source groupings share the same North/South ticket suffixes:

1. The supplier reconciliation records five posted L-29/N tickets and five posted L-29/S tickets. The North suffixes are `81, 94, 99, 106, 112`; the South suffixes are `121, 130, 135, 142, 151`.
2. The 1947 third edition of Praeger's *The Way That I Went* has *The Volcanic North* beginning at p.62 and *The Silurian Region* beginning at p.118. If ticket suffixes are treated as printed page numbers, all five North suffixes fall in the North section and all five South suffixes fall in the South section. The 1997 reprint's boundary at p.111 moves p.112/ST-112 into the South section, making the 1947 third edition the strongest checked section-page fit. The physical title/edition is still unconfirmed.
3. The print-fleet tab-05 anchors yield candidate ticket-to-job offsets: `ST-112→PS-0417` on FA-17/ESC-N gives `+305`; `ST-142→PS-0448` on LV-42/ESC-S gives `+306`. Extending those offsets predicts the other jobs. This can be expressed as candidate ST→PTW `+304`, followed by PTW→PS `+1` on FA-17 and `+2` on LV-42.

## Shared-index table

| Packet | Ticket suffix | Candidate book page | Praeger 1947 section | Candidate PS job | Status in retained spool |
|---|---:|---:|---|---:|---|
| L-29/N | 81 | 81 | Volcanic North | PS-0386 | present |
| L-29/N | 94 | 94 | Volcanic North | PS-0399 | present |
| L-29/N | 99 | 99 | Volcanic North | PS-0404 | present |
| L-29/N | 106 | 106 | Volcanic North | PS-0411 | present |
| L-29/N | 112 | 112 | Volcanic North | PS-0417 | present; selected RECOVER ACK2 exists |
| L-29/S | 121 | 121 | Silurian Region | PS-0427 | present; ACK/RECOVER/desk |
| L-29/S | 130 | 130 | Silurian Region | PS-0436 | absent from retained export |
| L-29/S | 135 | 135 | Silurian Region | PS-0441 | absent from retained export |
| L-29/S | 142 | 142 | Silurian Region | PS-0448 | present; ACK/RECOVER/desk |
| L-29/S | 151 | 151 | Silurian Region | PS-0457 | absent from retained export |

Two FA-17 L-28/A2 controls add an independent same-route check: ST-087 maps to candidate page 87 and PS-0392; ST-098 maps to candidate page 98 and PS-0403. Both predicted jobs are retained ACK/RECOVER rows. These controls are not among the two tab-05 anchors.

## Why the conjunction is interesting

The same North/South grouping appears in the supplier return packets, in the 1947 Praeger section split, and in the candidate lane-specific print-job offsets. The L-28/A2 controls extend the FA-17 `+305` mapping beyond the L-29/N anchor packet. On the South side, the non-anchor ST-121→PS-0427 row is ACK/RECOVER/desk like the ST-142→PS-0448 anchor. This gives a coherent cross-slot locator spine worth preserving for physical retrieval.

The candidate book page and candidate PS job are both simple functions of the same ticket suffix. If the physical receipt is found on p.94, p.112, p.121 or another listed page, that position could test the book-page interpretation directly. A p.94 receipt would also be the only physical basis for considering the separate low-confidence 5E67 split `0x5E=94 / 0x67=103`; the split itself is not a source-defined rule.

## Evidence limits

- MAIL-09 says only that David owned a book with a map at the back and a tea receipt left in place as a bookmark. It does not name Praeger, an edition, or a page.
- The supplier CSV has no explicit page-number, PTW or PS foreign-key column. Ticket suffixes are not source-defined as book pages.
- The two tab-05 ticket-to-PS offsets are calibrated from the known PS-0417/ST-112 and PS-0448/ST-142 anchors. The L-28/A2 rows and PS-0427 provide holdouts, but no original SEP26 index or native queue manifest authenticates the join.
- The three predicted South jobs PS-0436/0441/0457 are missing from the retained spool export. Their absence is not negative evidence; they are the most useful native-queue holdouts to retrieve.
- The 1947 Praeger edition is a structural page-split fit, not an authenticated identification of David's physical copy. The 1937/1939 pagination is unresolved, and the 1997 reprint moves p.112 across the section boundary. The Riddle of the Sands yachtsman's-estuary-guide clue is a separate physical-profile lead; Wilson's guide remains an analogue, not proof.
- MAIL-14's Emily desk-note stack and MAIL-20's final-wording selection remain the primary direct K08 carriers. The book is a locator candidate; no source says the final phrase is printed in the book.
- No additional book text was extracted. The signed K01 byte-pairs and 5E67 standby split remain unproven page/word mechanisms.

## Highest-value joint retrieval

1. Preserve David's exact map-back book and receipt together in situ. Record title, publisher, year, edition/printing, pagination, rear map, exact receipt page/spread, both receipt faces, all annotations and custody before separation. Check whether the book contains the separate MAIL-06 pocket-book standby transcription ending `5E67`, but do not treat it as a page/word rule.
2. Retrieve the original `R:/Stores/returns/SEP26/index.htm`, its source schema/revision history, and the signed North and South binder pages. Ask for explicit ST→PTW and PTW→PS references or a written statement that none exist.
3. Retrieve native spool/queue records and physical outputs for PS-0436, PS-0441 and PS-0457, plus PS-0427/0448 and FA-17 holdouts PS-0392/0403. Preserve source document path/hash and page/range, submitting user, print processor, queue, printer/device/port/route, every attempt, class, destination/output tray, spool object, ACK and paper-collection record. A source-page field matching the candidate ticket page would directly test the shared index.
4. Keep the physical book, the WN-14 sheet/photocopies, the North/South return pages, the spool objects and Emily's desk notes as distinct carriers until original custody records explicitly join them.

## Reproducible supporting work

- [Praeger page crosswalk](h17-k08-praeger-page-crosswalk-20261107.md)
- [MAIL-09 map-book / ticket-page analysis](h17-k08-mail09-mapbook-praeger-ticket-pages-20261107.md)
- [Lane-specific ticket-to-spool offset screen and SFT](h17-k04-lane-specific-ticket-to-spool-offset-screen-20261107.md)
- [Source-role join graph](h17-source-role-join-graph-20261107.md)

**Conclusion:** preserve this as a promising shared locator hypothesis that may connect the K04 return-ticket and K08 map-book investigations. It is not a recovered key, not a verified physical-book identity, and not a proven cross-slot join.
