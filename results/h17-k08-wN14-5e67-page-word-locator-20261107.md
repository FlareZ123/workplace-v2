# WN-14 standby suffix as a page/word locator

**Status:** unverified but testable cross-source hypothesis. This is a locator lead, not a recovered K08 phrase or a signed WN-14 value.

## Question

Can the standby WN-14 group-D suffix `5E67` identify a page and word in the map-bearing book mentioned by David?

## Source evidence

- `resources/evidence/mail/06.eml` says the standby transcription in David's pocket book has group D ending `5E67`, and that this “might help identify the book.” The same message distinguishes the standby transcription from the signed duty register. The standby value must not replace the signed WN-14 source.
- `resources/evidence/mail/09.eml` says the book with a map in the back belongs to David and that a tea receipt has been left in it as a bookmark.
- `resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv` gives L-29/N ticket IDs 094, 081, 106, 099, 112 and L-29/S IDs 130, 151, 121, 135, 142.
- Google Books identifies the 1947 third edition of Robert Lloyd Praeger's *The Way That I Went* as 416 pages, with **The Volcanic North** beginning at p.62 and **The Silurian Region** at p.118. All five N ticket page numbers fall in the former section; all five S page numbers fall after the latter boundary. <https://books.google.com/books?id=uT5RAQAAIAAJ>
- The NLI catalogue identifies the 1997 reprint as originally published in 1937 and records a 394-page physical description. Its copy is stored offsite. <https://catalogue.nli.ie/Record/vtls000044069>
- A rare-book catalogue describes the 1937 first edition as having a large folding map at the rear, 38 plates, and 394 pages. <https://www.deburcararebooks.com/wp-content/uploads/2021/02/Catalogue-144.pdf>

## Derivation

Interpret the four hexadecimal digits as two bytes:

- `0x5E` = 94 decimal, a plausible printed page number.
- `0x67` = 103 decimal, a plausible word index on that page.

This gives **page 94, word 103**. ST-094 appears in the L-29/N ticket set, and p.94 lies within the 1947 edition's Volcanic North section. The ticket/page alignment is edition-sensitive: in the 1997/1937 pagination, the section boundary is earlier, so p.112 crosses into the next region. The physical edition therefore matters.

A natural first test is to inspect printed p.94, word 103 in David's actual copy. If the token is meaningful, test word 103 on the remaining ticket pages in the CSV's original order, first for N and S separately, then as a combined sequence. The 5 N pages could yield a five-word candidate; the ten ticket pages could yield a ten-word candidate. These are test variants, not established extraction rules.

## What this does and does not establish

- The page/word split is a new interpretation of the standby suffix. It differs from treating `0x5E67` as the single decimal word offset 24,167, which was previously tested against *The Riddle of the Sands* text.
- It does not identify the book. Praeger's book is a strong candidate because of the map and the edition-sensitive N/S page alignment, but the physical copy has not been inspected.
- It does not authorize use of the standby transcription as the signed WN-14 register or HMAC key.
- No page text was available for the 1947 edition, so no word or phrase has been recovered.

## Highest-value physical test

When the book is located, preserve photographs or scans of:
1. the title page, edition statement, and publication details;
2. the complete rear map and its fold/legend;
3. printed p.94, including the full page and margins;
4. the tea receipt in place, including any visible date, amount, or page marking;
5. the other ticket pages: 81, 99, 106, 112, 121, 130, 135, 142, and 151.

Record exactly how word 103 is counted, including treatment of running headers, page numbers, captions, footnotes, and hyphenated words. Verify any resulting phrase only after applying the documented K08 normalization and signed desk nonce.

## Confidence

- `5E67 -> page 94 / word 103`: plausible, low-to-moderate confidence.
- *The Way That I Went* as the physical book: moderate candidate, not confirmed.
- Any K08 phrase or K04 component from this lead: no conclusion yet.
