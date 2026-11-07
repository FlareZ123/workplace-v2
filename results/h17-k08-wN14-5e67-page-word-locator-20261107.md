# WN-14 standby suffix: page/word locator, physical book, and ticket-page hypotheses

**Status:** unverified but testable. Current evidence supports separating the likely physical map-back book from a possible source of the L-29/N/S ticket page references. No K08 phrase has been recovered. The standby value is not a signed WN-14 component.

## Question

Can David's map-bearing book, the L-29/N/S ticket page numbers, and the WN-14 standby suffix identify a page/word location and help recover the K08 phrase?

## Source evidence

- `resources/evidence/mail/06.eml` says David's standby WN-14 transcription has group D ending `5E67`, and that it “might help identify the book.” The same message distinguishes the standby transcription from the signed duty register. Do not substitute the standby value for the signed WN-14 source.
- `resources/evidence/mail/09.eml` says the book with a map in the back belongs to David and that a tea receipt has been left in it as a bookmark.
- `resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv` gives L-29/N ticket IDs 094, 081, 106, 099, 112 and L-29/S IDs 130, 151, 121, 135, 142.
- Chapter XX of *The Riddle of the Sands* explicitly names Frank Cowper's *Sailing Tours* among books in the yacht library. A 2023 *Practical Boat Owner* article reports that Erskine Childers, author of *The Riddle of the Sands*, admired Cowper's *Sailing Tours* and wrote to Cowper asking to sail with him: https://www.pbo.co.uk/specials/frank-cowper-the-sailor-who-invented-cruising-76055
- **Cowper Part I (1892), *The Coasts of Essex and Suffolk*** is listed as 168 pages, red cloth, with maps/charts and a frontispiece map. Its pagination contains all five N ticket pages (81, 94, 99, 106, 112): https://www.pbfa.org/books/sailing-tours-the-yachtsmans-guide-to-the-cruising-waters-of-the-english-coast-part-1-the-coasts-of-essex-and-suffolk
- **Cowper Part II (1893), *The Nore to the Scilly Isles*** is listed as 365 pages with 26 coloured charts including a frontispiece. Its pagination contains all five S ticket pages (121, 130, 135, 142, 151): https://www.abebooks.co.uk/first-edition/Sailing-Tours-Yachtmans-Guide-Cruising-Waters/32157744703/bd
- Toovey's catalogue describes a five-volume Cowper set with three colour-map frontispieces and 116 colour maps: https://www.tooveys.com/lots/319115/cowper-frank-sailing-tours-the-yachtsmans-guide-to-the/
- Agent13's report identifies Arthur Ransome's *We Didn't Mean to Go to Sea* (1949 18th impression) as a strong physical map-back book candidate. Its rear endpaper map and p.94 Chapter VII scene fit the MAIL-09/N20 motifs: the all-night passage, Jim's absence, Susan setting a place for five at the cabin table, and the children waiting in fog with the sea outside. See `results/h17-k08-ransome-map-endpaper-locator-candidate-20261107.md`.
- Agent13's Ransome test found p.94 body word 103 to be “shelf”; including the eight-word chapter heading changes it to “took”. Neither is the K08 phrase. The page/word locator may point to a handwritten margin rather than printed text.
- The Online Books Page lists HathiTrust page images for Cowper's 1892 *Sailing Tours*, Part I, but the HathiTrust volume identifier and page images have not been retrieved: https://onlinebooks.library.upenn.edu/

## Derivation

Interpret the four hexadecimal digits as two bytes:

- `0x5E` = 94 decimal, a plausible printed page number.
- `0x67` = 103 decimal, a plausible word index on that page.

This gives **page 94, word 103**. ST-094 appears in the L-29/N ticket set. The p.94 coordinate is compatible with both the Ransome candidate and Cowper Part I, so it does not identify the book by itself.

Two different cross-source patterns should remain separate:

### Physical map-back book: Ransome candidate

Ransome p.94 has the strongest match to the N20 scene description, and the 1949 impression has a rear endpaper map. The printed word at the proposed coordinate is not the phrase. Inspect the actual p.94 margin, map endpaper, and receipt bookmark for handwritten material.

### Ticket-page crosswalk: Cowper candidate

The L-29/N and L-29/S page sets map cleanly to two volumes of Cowper's *Sailing Tours*:

| Route | Ticket pages | Cowper volume | Pagination fit |
|---|---|---|---|
| L-29/N | 81, 94, 99, 106, 112 | Part I: Essex and Suffolk | All within 168 pages |
| L-29/S | 121, 130, 135, 142, 151 | Part II: Nore to Scilly | All within 365 pages |

Cowper is also explicitly named in Chapter XX of *The Riddle of the Sands*, and Childers had a documented personal connection to him. This is a strong candidate explanation for the ticket-page pattern. It does not establish that Cowper is the David-owned map-back book.

## Competing candidates

- **Robert Lloyd Praeger, *The Way That I Went* (1947 third edition):** the N pages fall within *The Volcanic North* (starting p.62) and the S pages after the *Silurian Region* boundary at p.118. This remains a plausible alternative, but the Cowper two-volume mapping explains the N/S ticket split more directly. The 1997/1937 pagination has a different section boundary, so edition matters. Google Books record: https://books.google.com/books?id=uT5RAQAAIAAJ
- **W. Eric Wilson, *The Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen* (1934):** a physical-profile analogue (cloth, frontispiece, folding charts) but no evidence ties the title page to the Riddle of the Sands' fictional “Lieut. X--, R.N.” attribution or to Dollmann.
- **T. G. Cuthell, *A Sailing Guide to the Solent and Poole Harbour* (1893):** a small guide for yachtsmen with charts and a lieutenant-colonel attribution, making it an analogue to the fictional guide described in *The Riddle of the Sands*. Its listed extent is about 100 pages plus advertisements, so pages 121-151 do not fit it as a single source for all L-29 tickets.

## What this does and does not establish

- The page/word split is a hypothesis, not a source-defined convention. MAIL-06 only says the suffix might help identify the book.
- Ransome is currently the strongest physical map-back book candidate; the actual copy has not been inspected.
- Cowper is currently the strongest candidate for explaining the N/S ticket-page grouping; the ticket pages have not been read from the physical volumes.
- The physical book may be one volume or a set. MAIL-09 uses the singular “book”; this must be resolved by inspection.
- The suffix `5E67` remains a standby transcription and must not replace the signed WN-14 register or the signed desk nonce.
- No printed page text or word has yielded the K08 phrase. The exact handwritten margin/envelope copy remains missing.

## Highest-value physical test

When the book/folder is located, preserve photographs or scans of:
1. Ransome title page, edition statement, p.94 full page and margins, both endpaper maps, and the tea receipt in place;
2. Cowper Part I/II title pages, maps, and the ten ticket pages if either volume is present;
3. the original WN-14 folder and Emily's loose desk notes, especially the handwritten photo-caption margin and envelope copy;
4. any frontispiece-map verso, bookplate, previous-owner name, or other handwritten marginalia.

Record exactly how word 103 is counted, including treatment of running headers, page numbers, captions, footnotes, and hyphenated words. Verify any resulting phrase only after applying the documented K08 normalization and signed desk nonce.

## Confidence

- Ransome as the physical map-back book: **moderate candidate**, unconfirmed.
- Cowper *Sailing Tours* as the L-29/N/S ticket-page crosswalk: **moderate-to-high candidate**, unconfirmed.
- `5E67 -> page 94 / word 103`: **plausible, low-to-moderate confidence**.
- Exact physical copy, handwriting, and K08 phrase: **unresolved**.
