# K08: specific Praeger 1947 North-page extraction hypothesis

**Status: unverified acquisition/extraction lead; not a recovered component.**

## Why this is materially different from a generic book-cipher sweep

The surviving records contain a specific North ticket list, a stable ticket-to-printer-job offset, and an independent physical-book clue:

- `evidence/maintenance/print-fleet-retirement-note.txt` lists the North binder tabs in this order: `ST-094, ST-081, ST-106, ST-099, ST-112`.
- The North ticket/job crosswalk gives `PS suffix = ST suffix + 305`.
- `MAIL-16` explicitly says the South/ESC-S route is not an input to the keeper's desk phrase. Do not include the South tickets in this K08 hypothesis.
- `MAIL-09` says the map-backed book belongs to David.
- Courtwood Books Catalogue 47, item 220, describes Robert Lloyd Praeger's *The Way That I Went — An Irishman in Ireland*, Hodges, Figgis / Methuen, 1947, third edition, xiv + 416 pages, with a **large folding map at the back**: https://www.courtwoodbooks.ie/Catalogues/Catalogue-47.pdf (PDF lines 960–963).
- The 1947 Google Books record identifies the same 416-page edition and its contents place “The Volcanic North” at p.62 and “The Silurian Region” at p.118: https://books.google.com/books?id=uT5RAQAAIAAJ

This is a plausible identification of the map-backed book, not proof that the physical copy on H-17 was that edition. The exact title/edition still needs confirmation against the physical copy or its inventory record.

## Deterministic coordinate derivation

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

All five pages lie within the 1947 edition's “The Volcanic North” section (p.62–p.117), ending immediately before “The Silurian Region” at p.118. The North/South distinction therefore has an independent geographic/structural fit. The South values are deliberately excluded because MAIL-16 says ESC-S is not an input to the keeper phrase.

The candidate produced by this construction is a five-word sequence. Whether that satisfies the “longer than the standby wording” description in the crew notes must be checked; “longer” may refer to character length rather than token count. Do not silently add words or paraphrase.

## Required extraction and validation

1. Confirm the actual H-17 book is the 1947 third edition, not another edition or a different map-backed book.
2. Obtain clear scans/OCR of pp.86, 99, 104, 111, and 117 from that exact copy.
3. Count the 305th word on each page, preserving the table order above. Record the counting convention (hyphenated words, headers, captions, footnotes, and page numbers).
4. Concatenate the five extracted words in binder order.
5. Apply the exact K08 normalization in `evidence/recovery-routing.json` (lowercase; replace non-ASCII letters/digits/whitespace with spaces; collapse whitespace; trim), compute HMAC-SHA256 with the specified desk nonce as key, take the first 16 bytes, and compare SHA-256 against the unchanged K08 commitment.
6. Accept only an exact commitment match. If it fails on the confirmed physical edition, reject this construction rather than broadening it into a generic page/word sweep.

## Limitations and current state

- No page text from the exact 1947 third edition was available in the local export during this run; no five-word phrase has been extracted and no K08 candidate is claimed.
- The 1937 first edition and 1997 reprint have different pagination; do not substitute them for the 1947 third edition.
- MAIL-09 does not name the book, so the title/edition match remains a hypothesis until the physical copy is confirmed.
- K04 remains unresolved. The selected PS-0417 ACK payload XOR the supplied mask does not meet the K04 commitment; the dispatch ACK is not a media-integrity guarantee. The native PS-0417 spool/coupon or the original AX-7782 object remains the high-value acquisition target.

## External references

- Courtwood Books, Catalogue 47, item 220 (1947 third edition, 416 pages, large folding map at back): https://www.courtwoodbooks.ie/Catalogues/Catalogue-47.pdf
- Google Books, 1947 third edition record and contents: https://books.google.com/books?id=uT5RAQAAIAAJ
