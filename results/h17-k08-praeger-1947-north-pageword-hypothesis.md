# K08: specific Praeger 1947 North-page extraction hypothesis

**Status: RETIRED. Unsupported cross-slot numeric association; do not use as a K08 phrase candidate or locator.**

## Why the book identification was considered

The map-back clue has a plausible bibliographic match in the 1947 Praeger third edition. That is only a possible identification of David's physical book, not evidence that the book supplies or locates K08 words.

**Critical source-role correction:** the source-role map assigns ESC-N/North to the K04 masked-coupon route. The North L-29 ticket/job arithmetic is therefore K04-side material. No supplied source links that North ticket/job sequence to book pages or to the K08 card/envelope. The South route is explicitly excluded from the K08 phrase, but that does not make the North route a K08 input. Joining the North K04 sequence to the map-backed book was an unsupported cross-slot inference. This page-word construction is retired.

## Exploratory arithmetic (not a valid source relation)

The surviving records contain a specific North ticket list, a stable ticket-to-printer-job offset, and an independent physical-book clue:

- `evidence/maintenance/print-fleet-retirement-note.txt` lists the North binder tabs in this order: `ST-094, ST-081, ST-106, ST-099, ST-112`.
- The North ticket/job crosswalk gives `PS suffix = ST suffix + 305`.
- `MAIL-16` explicitly says the South/ESC-S route is not an input to the keeper's desk phrase. Do not include the South tickets in this K08 hypothesis.
- `MAIL-09` says the map-backed book belongs to David.
- Courtwood Books Catalogue 47, item 220, describes Robert Lloyd Praeger's *The Way That I Went — An Irishman in Ireland*, Hodges, Figgis / Methuen, 1947, third edition, xiv + 416 pages, with a **large folding map at the back**: https://www.courtwoodbooks.ie/Catalogues/Catalogue-47.pdf (PDF lines 960–963).
- The 1947 Google Books record identifies the same 416-page edition and its contents place “The Volcanic North” at p.62 and “The Silurian Region” at p.118: https://books.google.com/books?id=uT5RAQAAIAAJ

This is a plausible identification of the map-backed book, not proof that the physical copy on H-17 was that edition. The exact title/edition still needs confirmation against the physical copy or its inventory record.

## Candidate arithmetic that must not be used

For each North ticket, let (t) be the ticket suffix and (j) the mapped printer-job suffix.

- Page coordinate: (p = j - 300 = t + 5).
- Word coordinate: (w = j - t = 305).

Read the **305th word** on each page, in the explicit North binder-tab order:

| Binder order | Ticket | Printer job | Page | Word |
|---:|---:|---:|---:|---:|
| 1 | ST-094 | PS-0399 | 99 | 305 |
| 2 | ST-081 | PS-0386 | 86 | 305 |
| 3 | ST-106 | PS-0411 | 111 | 305 |
| 4 | ST-099 | PS-0404 | 104 | 305 |
| 5 | ST-112 | PS-0417 | 117 | 305 |

All five numerical page values happen to lie within the 1947 edition's “The Volcanic North” section (p.62–p.117), but this is not independent source evidence: the numbers came from the K04 ESC-N ticket/job hypothesis itself. The apparent fit is therefore circular and must not be used to validate the cross-slot join.

The page-word construction is retired and yields no usable locator sequence. The final caption must be read from the original envelope/card.

## Required next action

Do not extract these page words, do not use them as a locator, and do not run them through the K08 HMAC. The only K08 source roles supported by the repository are Emily's literal final keeper-envelope face/margin or the small card by the chipped-blue mugs. The Praeger book may be a map-backed physical locator mentioned in MAIL-09, but no source defines a page-word relation from the K04 ESC-N ticket set to that book. If a title-page/bookplate or inventory record independently identifies the book, record that identification separately; it does not supply K08 phrase text. Only verbatim text from the original envelope/card is eligible for `work/h17_check_phrase.py`.

## Limitations and current state

- No page text from the exact 1947 third edition was available in the local export. More importantly, no source links the K04 North ticket/job sequence to the book; the page-word association is retired. No physical card/envelope has been found and no K08 phrase candidate is claimed.
- Other editions exist and have different pagination: 1937 first edition (394 pp), 1939 second edition (304 pp), 1947 third edition (416 pp), and 1997 reprint (394 pp). The 1939 edition also has a folding map at the end. The map clue alone therefore does not identify the edition; do not substitute another edition for the 1947 third-edition coordinates.
- MAIL-09 does not name the book, so the title/edition match remains a hypothesis until the physical copy is confirmed.
- K04 remains unresolved. The selected PS-0417 ACK payload XOR the supplied mask does not meet the K04 commitment; the dispatch ACK is not a media-integrity guarantee. The native PS-0417 spool/coupon or the original AX-7782 object remains the high-value acquisition target.

## External references

- Courtwood Books, Catalogue 47, item 220 (1947 third edition, 416 pages, large folding map at back): https://www.courtwoodbooks.ie/Catalogues/Catalogue-47.pdf
- Google Books, 1947 third edition record and contents: https://books.google.com/books?id=uT5RAQAAIAAJ
