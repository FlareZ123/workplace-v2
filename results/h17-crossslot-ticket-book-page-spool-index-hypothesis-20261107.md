# Cross-slot ticket / book-page / spool-job index hypothesis

**Date:** 2026-11-07  
**Identity:** Agent 44  
**Status:** Structural hypothesis only. No K04 coupon bytes or exact K08 words recovered.

## Question

Do the L-29 return-ticket suffixes form a shared index across two otherwise separate missing-component investigations: a page locator in David's map-back book for K08, and a lane-specific spool-job locator for K04?

## Observed structure

Three independent source groupings share the same North/South ticket suffixes:

1. The supplier reconciliation records five posted L-29/N tickets and five posted L-29/S tickets. The North suffixes are `81, 94, 99, 106, 112`; the South suffixes are `121, 130, 135, 142, 151`.
2. Praeger's *The Way That I Went* (1947 third edition) has *The Volcanic North* beginning at p.62 and *The Silurian Region* beginning at p.118. If suffixes are printed pages, all five North suffixes fall in the North section and all five South suffixes in the South section. The 1997 reprint's p.111 boundary moves p.112/ST-112 into the South section. This is the strongest checked **single-volume section-page** fit, not an identified physical copy.
3. Cowper's *Sailing Tours* provides a separate two-volume crosswalk: Part I, *The Coasts of Essex and Suffolk* (1892, 168 pages), contains all five North suffixes; Part II, *The Nore to the Scilly Isles* (1893, 365 pages), contains all five South suffixes. Cowper is explicitly named among the yacht-library books in *The Riddle of the Sands*, but the novel's "Little Drab Book" is a separate guidebook, not Cowper. This is the strongest combined **Riddle-reference/ticket-volume** candidate, not proof of David's copy.
4. W. Eric Wilson's *The Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen* (1934) is the strongest identified **physical-profile analogue** to the separate Little Drab Book, but no N/S ticket-page or volume crosswalk is established. Ransome remains a semantic N20 locator only.
3. The print-fleet tab-05 anchors yield candidate ticket-to-job offsets: `ST-112→PS-0417` on FA-17/ESC-N gives `+305`; `ST-142→PS-0448` on LV-42/ESC-S gives `+306`. Extending those offsets predicts the other jobs. This can be expressed as candidate ST→PTW `+304`, followed by PTW→PS `+1` on FA-17 and `+2` on LV-42.

## Shared-index table

|---|---:|---:|---:|---|---:|---|
| Packet | Tab | Ticket suffix | Candidate page | Praeger 1947 section / Cowper volume | Candidate PS job | Status in retained spool |
|---|---:|---:|---:|---|---:|---|
| L-29/N | 01 | 94 | 94 | Volcanic North / Cowper Part I | PS-0399 | present; ACK LABEL/store |
| L-29/N | 02 | 81 | 81 | Volcanic North / Cowper Part I | PS-0386 | present; ACK STORES/bench |
| L-29/N | 03 | 106 | 106 | Volcanic North / Cowper Part I | PS-0411 | present; ACK LABEL/store |
| L-29/N | 04 | 99 | 99 | Volcanic North / Cowper Part I | PS-0404 | present; ACK LABEL/desk |
| L-29/N | 05 | 112 | 112 | Volcanic North / Cowper Part I | PS-0417 | present; selected RECOVER ACK2 exists |
| L-29/S | 01 | 130 | 130 | Silurian Region / Cowper Part II | PS-0436 | absent from retained export |
| L-29/S | 02 | 151 | 151 | Silurian Region / Cowper Part II | PS-0457 | absent from retained export |
| L-29/S | 03 | 121 | 121 | Silurian Region / Cowper Part II | PS-0427 | present; ACK RECOVER/desk |
| L-29/S | 04 | 135 | 135 | Silurian Region / Cowper Part II | PS-0441 | absent from retained export |
| L-29/S | 05 | 142 | 142 | Silurian Region / Cowper Part II | PS-0448 | present; ACK RECOVER/desk |

Two FA-17 L-28/A2 controls add an independent same-route check: ST-087 maps to candidate page 87 and PS-0392; ST-098 maps to candidate page 98 and PS-0403. Both predicted jobs are retained ACK/RECOVER rows. These controls are not among the two tab-05 anchors.

## Why the conjunction is interesting

The same North/South grouping appears in the supplier return packets, in two independent candidate book structures (Praeger's single-volume section split and Cowper's Part I/II volume split), and in the candidate lane-specific print-job offsets. The L-28/A2 controls extend the FA-17 `+305` mapping beyond the L-29/N anchor packet. On the South side, the non-anchor ST-121→PS-0427 row is ACK/RECOVER/desk like the ST-142→PS-0448 anchor. This gives a coherent cross-slot locator spine worth preserving for physical retrieval, while leaving the book identity unresolved.

The candidate book page and candidate PS job are both simple functions of the same ticket suffix. If the physical receipt is found on p.94, p.112, p.121 or another listed page, that position could test the book-page interpretation directly. A p.94 receipt would be relevant to the separate low-confidence 5E67 split `0x5E=94 / 0x67=103`, which remains specifically a Praeger hypothesis; the split itself is not a source-defined rule and must not be transferred to Cowper or Wilson.

## Evidence limits

- MAIL-09 says only that David owned a book with a map at the back and a tea receipt left in place as a bookmark. It does not name Cowper, Praeger, Wilson, a volume, an edition, or a page.
- The supplier CSV has no explicit page-number, PTW or PS foreign-key column. Ticket suffixes are not source-defined as book pages.
- The two tab-05 ticket-to-PS offsets are calibrated from the known PS-0417/ST-112 and PS-0448/ST-142 anchors. The L-28/A2 rows and PS-0427 provide holdouts, but no original SEP26 index or native queue manifest authenticates the join.
- The three predicted South jobs PS-0436/0441/0457 are missing from the retained spool export. Their absence is not negative evidence; they are the most useful native-queue holdouts to retrieve.
- Praeger is a single-volume section-page fit; Cowper is a two-volume North/South ticket-volume fit and is named in the Riddle's yacht-library list; Wilson is the closer physical-profile analogue to the novel's separate Little Drab Book. These are different candidate axes, not a single ranked identity. The 1947 Praeger boundary is edition-sensitive, the 1937/1939 pagination is unresolved, and Cowper's map/chart placement must be checked in the actual copy.
- MAIL-14's Emily desk-note stack and MAIL-20's final-wording selection remain the primary direct K08 carriers. The book is a locator candidate; no source says the final phrase is printed in the book.
- No additional book text was extracted in this investigation. The existing Cowper Part II word-103 fragment is a separate secondary experiment and has not passed the K08 HMAC. The signed K01 byte-pairs and 5E67 standby split remain unproven page/word mechanisms.

## Highest-value joint retrieval

1. Preserve David's exact map-back book and receipt together in situ. Record title, volume (if Cowper), publisher, year, edition/printing, printed pagination, map/chart placement and exact receipt page/spread, both receipt faces, all annotations and custody before separation. Compare the actual copy against Cowper Part I/II, Praeger and the Wilson guide profile. For Cowper Part I, image the frontispiece map and its reverse and record any previous-owner inscription without assuming it is Dollmann; for Part II, document all chart/map positions. Check whether the separate MAIL-06 standby transcription ending `5E67` is physically co-located, but treat any such co-location as new evidence, not a source-defined identity marker or page/word rule.
2. Retrieve the original `R:/Stores/returns/SEP26/index.htm`, its source schema/revision history, and the signed North and South binder pages. Ask for explicit ST→PTW and PTW→PS references or a written statement that none exist.
3. Retrieve native spool/queue records and physical outputs for PS-0436, PS-0441 and PS-0457, plus PS-0427/0448 and FA-17 holdouts PS-0392/0403. Preserve source document path/hash and page/range, submitting user, print processor, queue, printer/device/port/route, every attempt, class, destination/output tray, spool object, ACK and paper-collection record. A source-page field matching the candidate ticket page would directly test the shared index.
4. Keep the physical book, the WN-14 sheet/photocopies, the North/South return pages, the spool objects and Emily's desk notes as distinct carriers until original custody records explicitly join them.

## Reproducible supporting work

- [Praeger page crosswalk](h17-k08-praeger-page-crosswalk-20261107.md)
- [Cowper *Sailing Tours* volume crosswalk](h17-k08-cowper-sailing-tours-volume-crosswalk-20261107.md)
- [Wilson Little Drab Book physical-profile correction](h17-k08-riddle-little-drab-book-wilson-correction-20261107.md)
- [MAIL-09 map-book / ticket-page analysis](h17-k08-mail09-mapbook-praeger-ticket-pages-20261107.md)
- [Lane-specific ticket-to-spool offset screen and SFT](h17-k04-lane-specific-ticket-to-spool-offset-screen-20261107.md)
- [Source-role join graph](h17-source-role-join-graph-20261107.md)

**Conclusion:** preserve this as a promising shared locator hypothesis that may connect the K04 return-ticket and K08 map-book investigations. It is not a recovered key, not a verified physical-book identity, and not a proven cross-slot join.
