# H-17 K08: Praeger book and ticket-page locator

**Status:** strong physical-source locator; not a recovered phrase or verified K08 component.

## Finding

The book described in `resources/evidence/mail/09.eml` — David's personal book with a map at the back and a tea-receipt bookmark — is strongly identified as Robert Lloyd Praeger's *The Way That I Went: An Irishman in Ireland*, third edition, Methuen, 1947.

The public catalogue evidence is unusually specific:

- Google Books record `uT5RAQAAIAAJ` identifies the 1947 third edition as 416 pages and gives the contents boundary: **The Volcanic North, p. 62**; **The Silurian Region, p. 118**.
- A rare-book catalogue describes the same 1947 third edition as 416 pages with a **folding map at the rear**.
- The National Library of Ireland catalogue entry is for a 1997 reprint (394 pages). Its pagination is not interchangeable with the 1947 edition and should not be used for this page locator.

References:
- Google Books, 1947 third edition: https://books.google.com/books?id=uT5RAQAAIAAJ
- Arden Books catalogue, 1947 third edition / folding map: https://www.ardenbooks.co.uk/catalogs/Cat.112.pdf
- NLI catalogue, 1997 reprint: https://catalogue.nli.ie/Record/vtls000044069/HoldingsILS

## Local crosswalk

The supplied `supplier-reconciliation-L29.csv` contains two five-ticket sets:

| Route | Ticket suffixes | Book section |
|---|---|---|
| L-29/N | 081, 094, 099, 106, 112 | All fall within p. 62–117, *The Volcanic North* |
| L-29/S | 121, 130, 135, 142, 151 | All fall at/after p. 118, *The Silurian Region* |

This is a complete ten-ticket control for the proposed suffix-to-page mapping: every supplied North ticket lands in the book's North section and every supplied South ticket lands in its South section. The match is stronger than a generic “book with a map” identification, although the local documents do not explicitly state that ticket suffixes are page numbers.

Two unresolved North alternatives, **ST-113** and **ST-117**, have appeared in the crosswalk investigation but are not present in the supplied reconciliation CSV. If they are genuine missing ticket references, they point to pages immediately before the p. 118 section boundary. Treat these as inspection candidates, not verified ticket records.

## Why this matters to K08

The local correspondence and desk notes say that:
- the map-back book belongs to David and had a tea receipt left in it as a bookmark (`mail/09.eml`);
- Emily's keeper phrase was a personal caption, not an official slogan (`mail/11.eml`);
- the final wording was put in the margin and then on the envelope (`mail/20.eml`, note N23 in `crew/noticeboard-and-desk-notes.txt`).

The strongest next physical inspection is therefore **David's actual 1947 third-edition copy**, especially pages **113 and 117**, including the full margins, the facing pages, and the tea-receipt bookmark. A generic reprint or clean library copy may establish printed text but cannot recover Emily's handwriting or the bookmark's position.

## Possible K04 connection

The same page crosswalk is relevant to the North cassette route L-29/N and the unresolved ST-113/ST-117 references. It may help locate the missing North physical coupon or its associated service record. It does **not** establish that the coupon is in the book, nor does it replace the selected printer job's missing independent integrity evidence.

## Limits and next action

- This finding identifies a likely physical carrier and a narrow page range; it does not reveal the exact phrase.
- No K08 HMAC candidate has been validated from this finding.
- No K04 component has been recovered from it.
- Preserve the 1947 pagination: the NLI's 1997 reprint is a different pagination.
- Obtain a scan/photo of David's copy at pp. 113 and 117, including margins and the bookmark/receipt, or the original physical copy. Test any transcribed phrase against the existing K08 commitment before accepting it.
