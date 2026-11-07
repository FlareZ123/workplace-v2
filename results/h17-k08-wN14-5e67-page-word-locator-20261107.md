# WN-14 standby suffix and the Cowper *Sailing Tours* page/word hypothesis

**Status:** strong book-series candidate and unverified locator hypothesis. No K08 phrase has been recovered. The standby value is not a signed WN-14 component.

## Question

Can David's map-bearing book, the L-29/N/S ticket page numbers, and the WN-14 standby suffix identify a particular book and page/word location?

## Source evidence

- `resources/evidence/mail/06.eml` says David's standby WN-14 transcription has group D ending `5E67`, and that it “might help identify the book.” The same message distinguishes the standby transcription from the signed duty register. Do not substitute the standby value for the signed WN-14 source.
- `resources/evidence/mail/09.eml` says the book with a map in the back belongs to David and that a tea receipt has been left in it as a bookmark.
- `resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv` gives L-29/N ticket IDs 094, 081, 106, 099, 112 and L-29/S IDs 130, 151, 121, 135, 142.
- Chapter XX of *The Riddle of the Sands* explicitly names Frank Cowper's *Sailing Tours* among books in the yacht library. This is a direct literary connection to the book clue, not merely a shared maritime theme.
- A 2023 *Practical Boat Owner* article reports that Erskine Childers, author of *The Riddle of the Sands*, admired Cowper's *Sailing Tours* and wrote to Cowper asking to sail with him: https://www.pbo.co.uk/specials/frank-cowper-the-sailor-who-invented-cruising-76055
- **Part I (1892), *The Coasts of Essex and Suffolk*** is listed as 168 pages, red cloth, with maps/charts and a frontispiece map. Its pagination contains all five N ticket pages (81, 94, 99, 106, 112): https://www.pbfa.org/books/sailing-tours-the-yachtsmans-guide-to-the-cruising-waters-of-the-english-coast-part-1-the-coasts-of-essex-and-suffolk
- **Part II (1893), *The Nore to the Scilly Isles*** is listed as 365 pages with 26 coloured charts including a frontispiece. Its pagination contains all five S ticket pages (121, 130, 135, 142, 151): https://www.abebooks.co.uk/first-edition/Sailing-Tours-Yachtmans-Guide-Cruising-Waters/32157744703/bd
- Toovey's catalogue describes a five-volume Cowper set with three colour-map frontispieces and 116 colour maps: https://www.tooveys.com/lots/319115/cowper-frank-sailing-tours-the-yachtsmans-guide-to-the/
- The Online Books Page lists HathiTrust page images for Cowper's 1892 *Sailing Tours*, Part I. I have not retrieved the HathiTrust volume identifier or page images: https://onlinebooks.library.upenn.edu/

## Derivation

Interpret the four hexadecimal digits as two bytes:

- `0x5E` = 94 decimal, a plausible printed page number.
- `0x67` = 103 decimal, a plausible word index on that page.

This gives **page 94, word 103**. ST-094 appears in the L-29/N ticket set, and p.94 is within Cowper Part I's 168-page extent. The full N/S ticket split has a natural two-volume mapping:

| Route | Ticket pages | Cowper volume | Pagination fit |
|---|---|---|---|
| L-29/N | 81, 94, 99, 106, 112 | Part I: Essex and Suffolk | All within 168 pages |
| L-29/S | 121, 130, 135, 142, 151 | Part II: Nore to Scilly | All within 365 pages |

This is a cleaner N/S-to-volume correspondence than the earlier Praeger crosswalk, which placed the ticket pages in two geographical sections of one book. Cowper is also explicitly named in the Riddle of the Sands yacht-library passage, and Childers had a documented personal connection to Cowper.

The simplest first test is **Cowper Part I, printed p.94, word 103**. If that token is meaningful, test word 103 on the remaining N pages in the CSV's original order. Then test the S pages in Part II as a separate sequence and as a control. These are test variants, not established extraction rules.

## Competing candidates

- **Robert Lloyd Praeger, *The Way That I Went* (1947 third edition):** the N pages fall within *The Volcanic North* (starting p.62) and the S pages after the *Silurian Region* boundary at p.118. This remains a plausible alternative, but it is not a yachtsmen's guide and is not named in the Riddle of the Sands yacht-library passage. The N/S split is less directly explained than by Cowper's two volumes. The 1997/1937 pagination has a different section boundary, so edition matters. Google Books record: https://books.google.com/books?id=uT5RAQAAIAAJ
- **W. Eric Wilson, *The Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen* (1934):** a physical-profile analogue (cloth, frontispiece, folding charts) but no evidence ties the title page to the Riddle of the Sands' fictional “Lieut. X--, R.N.” attribution or to Dollmann. It does not explain the N/S page grouping as neatly as Cowper's two-volume series.

## What this does and does not establish

- The page/word split is a hypothesis, not a source-defined convention. MAIL-06 only says the suffix might help identify the book.
- The Cowper series is currently the strongest candidate from the combined literary, physical, and N/S pagination evidence. The actual copy in David's TV room has not been inspected.
- The physical evidence may be one volume or a two-volume set. MAIL-09 uses the singular “book”; this must be resolved by inspection.
- The suffix `5E67` remains a standby transcription and must not replace the signed WN-14 register or the signed desk nonce.
- No page text or word has been recovered. HathiTrust page images are listed, but no volume ID or scan has yet been obtained.

## Highest-value physical test

When the book is located, preserve photographs or scans of:
1. title page, edition statement, and publication details for each volume;
2. complete rear map/chart and its fold/legend;
3. Part I printed p.94, including full page and margins;
4. Part I ticket pages 81, 99, 106, and 112;
5. Part II ticket pages 121, 130, 135, 142, and 151;
6. the tea receipt in place, including date, amount, and any page marking;
7. any frontispiece-map verso, bookplate, previous-owner name, or handwritten marginalia.

Record exactly how word 103 is counted, including treatment of running headers, page numbers, captions, footnotes, and hyphenated words. Verify any resulting phrase only after applying the documented K08 normalization and signed desk nonce.

## Confidence

- Cowper *Sailing Tours* as the book series: **moderate to high candidate**, unconfirmed.
- `5E67 -> page 94 / word 103`: **plausible, low-to-moderate confidence**.
- Exact volume/copy and K08 phrase: **unresolved**.
