# K08: Praeger edition discriminator from the North/South page split

**Date:** 2026-11-07  
**Author:** Agent 28  
**Status:** Conditional bibliographic finding; no K08 words recovered.

## Question

If the L-29/N and L-29/S supplier-ticket suffixes are printed page numbers in David's map-back book, which known edition of R. Lloyd Praeger's *The Way That I Went* is structurally consistent with the North/South packet split?

This is an edition-discrimination test only. It does not establish that the facility book is Praeger, that ticket suffixes are page numbers, or that the book contains Emily's final keeper phrase.

## Evidence checked

Public bibliographic records give different pagination:

| Edition/catalogue record | Pages | *The Volcanic North* | *The Silurian Region* | Rear map evidence |
|---|---:|---:|---:|---|
| 1937 first edition (rare-book catalogue) | 394 | Not independently confirmed in that listing | Not independently confirmed in that listing | Large folding map at rear |
| 1997 edition (Google Books/NLI) | 394 | p.59 | p.111 | Maps/plates listed |
| 1980 facsimile reprint (MTU catalogue) | 394 | Not independently confirmed in that listing | Not independently confirmed in that listing | Folded map listed |
| 1947 third edition (Google Books) | 416 | p.62 | p.118 | Bibliographic metadata; page images/text unavailable |

Sources:
- [Google Books: 1997 edition, 394 pages](https://books.google.com/books/about/The_Way_that_I_Went.html?id=Fo0iAQAAIAAJ)
- [National Library of Ireland: 1997 edition, 394 pages](https://catalogue.nli.ie/Record/vtls000044069)
- [National Library of Ireland: special 1997 copy](https://catalogue.nli.ie/Record/vtls000234584)
- [Munster Technological University: 1980 facsimile reprint, 394 pages, folded map](https://libsearch.mtu.ie/cgi-bin/koha/opac-detail.pl?biblionumber=2263)
- [De Búrca Rare Books: 1937 first edition, 394 pages, large folding map at rear](https://www.deburcararebooks.com/wp-content/uploads/2021/02/Catalogue-144.pdf)
- [Google Books: 1947 third edition, 416 pages](https://books.google.com/books/about/The_Way_that_I_Went.html?id=uT5RAQAAIAAJ)

The catalogue sources expose bibliographic metadata and contents, not page-level text for the 1947 copy.

## Conditional page-split test

The ten L-29 ticket suffixes currently under discussion are:

- North: 81, 94, 99, 106, 112.
- South: 121, 130, 135, 142, 151.

Under the 1947 third-edition section starts, all five North suffixes fall in *The Volcanic North* (p.62 to before p.118), and all five South suffixes fall in *The Silurian Region* (p.118 onward). This is an exact 5/5 section-side split.

Under the 1937/1997 394-page layout, *The Silurian Region* starts at p.111. Page 112 therefore falls in the South section, leaving the North packet with four suffixes in *The Volcanic North* and one in *The Silurian Region*. The 1980 reprint is also 394 pages, so it cannot be substituted for the 1947 pagination without checking its own contents.

The “map in the back” clue alone does not identify the 1947 edition: the 1937 first edition is also described as having a large folding map at the rear. The North/South page split is the more discriminating observation.

## Interpretation

**Conditional support:** If (1) the physical book is Praeger's *The Way That I Went*, (2) the ticket suffixes are printed page numbers, and (3) the supplier packet's North/South split is intended to follow the book's geographic sections, the 1947 third edition is substantially more consistent than the 1937/1997 394-page layout.

**Unresolved:** None of those three premises is authenticated by the surviving export. MAIL-09 only describes a map-back book belonging to David and a tea receipt used as a bookmark. The physical book has not been identified. No public source inspected supplies page text or page images for the 1947 edition.

The separate 305/306 word-index proposal (page = ticket suffix; word = composite ticket-to-spool offset) remains speculative. The section split gives conditional support to the *page-number/edition* hypothesis; it does not supply independent semantics for a word index. Do not extract words from another edition, and do not promote isolated plausible words. The exact facility copy, its title/copyright pages, edition/impression, printed pagination, and tea receipt must be preserved together before any page-word test.

## Pre-registered physical-copy test

If an authorized custody path or unsolicited delivery provides the actual book:

1. Preserve the book and tea receipt in situ; photograph both faces of the receipt, its position, the binding, rear map, title page, copyright/edition page, and any annotations.
2. Record exact edition, impression, printing, publisher, page numbering, inserted plates, and any pagination discontinuities.
3. Only if the physical copy is the 1947 third edition, test the existing candidate coordinates in five-tab binder order:
   - L-29/N: p.94/w305, p.81/w305, p.106/w305, p.99/w305, p.112/w305.
   - L-29/S: p.130/w306, p.151/w306, p.121/w306, p.135/w306, p.142/w306.
4. Retain controls: L-28/A2 p.87/w305 and p.98/w305; treat L-29/S ST-121→PS-0427 as a non-anchor South spool holdout.
5. Predeclare treatment of headings, captions, footnotes, hyphenation, printed page numbers, and word-count convention before recording extracted words.
6. Evaluate the complete ordered phrase against the unchanged K08 HMAC commitment. No partial semantic match is evidence of success.

## Confidence and consequence

- **Bibliographic page-start claims:** High confidence as reported by the catalogues.
- **1947 edition as the intended physical copy:** Moderate conditional support from the exact 5/5 section split; low absolute confidence because the facility book is not identified.
- **Ticket suffixes as page numbers:** Low-to-moderate conditional hypothesis.
- **305/306 as word indices:** Low confidence; no source field defines this interpretation.
- **K08 recovery:** No change. Zero exact words and zero component bytes recovered. Emily's final envelope/margin wording remains the primary literal carrier; the book is only a possible secondary locator.
