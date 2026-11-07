# K08 physical-book hypothesis: Praeger page crosswalk

> **Status: competing secondary candidate.** The Wilson *Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen* now has the closer physical-profile match to MAIL-09 and a testable 5E67 → page 94 / word 103 hypothesis. Retain this Praeger report for its North/South page-section crosswalk; do not treat it as the identified book or the leading title without physical confirmation.

**Agent 35 · 7 November 2026**

## Question

Does MAIL-09's David-owned map-back book plausibly correspond to Robert Lloyd Praeger's *The Way That I Went*, and do the L-29 North/South ticket suffixes provide an edition/page discriminator?

## Local source facts

- MAIL-06 (David, 30 September 2026) says his pocket book contains an old WN-14 standby transcription whose group D ends `5E67`.
- MAIL-09 (Jason, 1 October 2026) says a map-back book in the television room belongs to David, and a tea receipt was left in place as its bookmark.
- N20 attributes to Emily a desired line holding the sea, the end of the night, and voices at the table.
- N23 attributes a margin wording to Emily, but does not identify the medium, page, or book.
- MAIL-14 separately locates Emily's desk notes under the WN-14 folder, outside the controlled-copy sleeve. That is the stronger primary K08 literal-source locator; the David-owned book remains a secondary candidate.

The records do not explicitly identify the map-back book as Praeger, or prove that MAIL-06's pocket book and MAIL-09's map-back book are the same object.

## Ticket suffixes from the local reconciliation CSV

The ticket suffixes are:

| Return set | Ticket suffixes |
|---|---|
| L-29/N | 81, 94, 99, 106, 112 |
| L-29/S | 121, 130, 135, 142, 151 |

The CSV's own comments say that R values identify vendor settlement batches and that credit entries retain earlier versions. ST-112 appears twice: R3 POSTED / A3 and R4 HELD / A4. Do **not** interpret R3/R4 as book editions. The duplicate is a settlement-record fact.

## Praeger edition and map evidence

*The Way That I Went: An Irishman in Ireland* by R. Lloyd Praeger is a plausible MAIL-09 book because rare-book records describe a large folding map at the rear.

- [1947 third edition, Methuen, 416 pages](https://books.google.com/books/about/The_Way_that_I_Went.html?id=uT5RAQAAIAAJ): Google Books lists *The Volcanic North* from p.62 and *The Silurian Region* from p.118.
- [1997 reprint, Collins Press, 394 pages](https://books.google.com/books/about/The_Way_that_I_Went.html?id=Fo0iAQAAIAAJ): Google Books lists *The Volcanic North* from p.59 and *The Silurian Region* from p.111.
- [De Búrca Rare Books Catalogue 144, item 243](https://www.deburcararebooks.com/wp-content/uploads/2021/02/Catalogue-144.pdf): describes the 1937 first edition with a large folding map at the rear.
- [IberLibro/Joe Collins Rare Books listing](https://www.iberlibro.com/primera-edicion/Way-Irishman-Ireland-Praeger-Robert-Lloyd/32109818572/bd): describes the 1937 first edition as xiv, 394 pages, with a large folding map at the end.

The accessible description of the 1937 rear map identifies it as an Ireland map of “Sixty Historical Divisions”, with labeled regions and boundaries. It does not describe a 5E67-style alphanumeric grid. The actual 1947 folding map has not been inspected at full resolution, so an edition-specific annotation cannot be ruled out.

## Page crosswalk (derivation, not proof)

For the 1947 third edition:

- Every L-29/N suffix (81, 94, 99, 106, 112) falls within *The Volcanic North*, pp.62–118.
- Every L-29/S suffix (121, 130, 135, 142, 151) falls within *The Silurian Region*, p.118 onward.

For the 1997 reprint, the section boundary is p.111, so p.112 is already in *The Silurian Region*. The North set's ST-112 therefore changes sides under that pagination. This makes the 1947 third edition the strongest **checked** fit for the North/South split.

The 1937 first edition is confirmed as a 394-page book with a rear map, but its section-start page numbers have not been independently recovered here. The 1939 second revised edition's pagination is also unresolved. Accordingly, the 1947 edition is the strongest currently evidenced fit, not a proven unique identification across every edition.

The page-number alignment is unusually specific, but no supplied source says that the ticket suffixes are book page numbers. The physical page and bookmark must validate or falsify that interpretation.

## 5E67: physical identity, not map coordinate

The accessible rear-map description gives no support for `5E67` as a printed map coordinate. Treat it as the physical-object fingerprint in MAIL-06: if the recovered map-back book or a loose insert contains the old WN-14 standby transcription ending `5E67`, that would provide a source-backed join between David's pocket book and MAIL-09's map-back book. Do not treat it as a K08 component, word offset, map coordinate, or book-cipher rule without further evidence.

## Required physical check

Retrieve David's map-back book and the tea receipt **together and in situ**. Record:

1. Exact title, edition, publisher, year, pagination, binding, and rear folding map.
2. Whether the receipt actually marks page 112; preserve its original position.
3. Page 112, adjacent pages, all marginalia, and both sides of the receipt.
4. Whether the book or any loose insert contains the WN-14 standby transcription ending `5E67`.
5. Custody/movement history sufficient to establish whether the item is David's MAIL-06 pocket book and MAIL-09 map-back book.
6. Any page-level or map-level marks that independently link the ticket suffixes to the book.

Retrieve Emily's original desk notes under the WN-14 folder separately; MAIL-14 is the stronger direct locator for N23's margin wording. Do not merge the two physical carriers until provenance establishes the link.

## Status and confidence

- **Strong derived pattern:** the five North and five South ticket suffixes partition exactly across the 1947 third edition's two named sections.
- **Strong candidate:** Praeger's 1947 third edition is the best currently evidenced map-back-book candidate.
- **Unresolved:** whether David's physical book is that title/edition, whether the receipt marks p.112, whether `5E67` is present in the same object, and whether Emily wrote the K08 margin there.
- **No K08 words recovered.** The exact phrase still requires the original marked page, receipt, or Emily's desk-note originals.


## 5E67 structured page/word hypothesis (Agent15)

A separate, low-confidence interpretation splits the two bytes of the MAIL-06 standby suffix:

- `0x5E` = **94**, candidate printed page.
- `0x67` = **103**, candidate word index on that page.

This is distinct from interpreting `0x5E67` as one raw word offset (24,167), which produced generic text in the unrelated Riddle candidate. The structured split is strengthened by the existence of L-29/N ticket ST-094 and by p.94 falling within the 1947 Praeger edition's *Volcanic North* section. No supplied source defines this byte-splitting convention, and no authorized scan of p.94 has been inspected. Treat it as a testable locator hypothesis, not a decoded word or K08 component.

If the physical book proves to be the 1947 Praeger edition, inspect printed p.94 and count word 103 using a documented convention, while preserving the page, adjacent pages and receipt position. If the book is another title or edition, do not transfer this locator without evidence. Also check for the WN-14 standby transcription ending `5E67` as an identity join between MAIL-06 and MAIL-09.
