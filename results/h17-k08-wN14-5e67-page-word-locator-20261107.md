# WN-14 standby suffix: Cowper map-verso fingerprint and page/word locator

**Status:** strongest current book candidate, still unverified. No K08 phrase has been recovered. The standby value is not a signed WN-14 component.

## Question

Can David's map-bearing book, the L-29/N/S ticket page numbers, and the WN-14 standby suffix identify a page/word location and help recover the K08 phrase?

## Source evidence

- `resources/evidence/mail/06.eml` says David's standby WN-14 transcription has group D ending `5E67`, and that it “might help identify the book.” The same message distinguishes the standby transcription from the signed duty register. Do not substitute the standby value for the signed WN-14 source.
- `resources/evidence/mail/09.eml` says the book with a map in the back belongs to David and that a tea receipt has been left in it as a bookmark.
- `resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv` gives L-29/N ticket IDs 094, 081, 106, 099, 112 and L-29/S IDs 130, 151, 121, 135, 142.
- Chapter XX of *The Riddle of the Sands* explicitly names Frank Cowper's *Sailing Tours* among books in the yacht library. A 2023 *Practical Boat Owner* article reports that Erskine Childers, author of *The Riddle of the Sands*, admired Cowper's *Sailing Tours* and wrote to Cowper asking to sail with him: https://www.pbo.co.uk/specials/frank-cowper-the-sailor-who-invented-cruising-76055
- **Cowper Part I (1892), *The Coasts of Essex and Suffolk*** is listed as 168 pages, red cloth, with maps/charts and a frontispiece map. Crucially, the PBFA description records a **previous owner's name on the reverse of the frontispiece map**. This is a sharp physical parallel to the Riddle clue about an owner's name on the back of the map: https://www.pbfa.org/books/sailing-tours-the-yachtsmans-guide-to-the-cruising-waters-of-the-english-coast-part-1-the-coasts-of-essex-and-suffolk
- **Cowper Part II (1893), *The Nore to the Scilly Isles*** is listed as 365 pages with 26 coloured charts including a frontispiece: https://www.abebooks.co.uk/first-edition/Sailing-Tours-Yachtmans-Guide-Cruising-Waters/32157744703/bd
- Toovey's catalogue describes a five-volume Cowper set with three colour-map frontispieces and 116 colour maps: https://www.tooveys.com/lots/319115/cowper-frank-sailing-tours-the-yachtsmans-guide-to-the/
- The Online Books Page lists HathiTrust page images for Cowper's 1892 *Sailing Tours*, Part I, but the HathiTrust volume identifier and page images have not been retrieved: https://onlinebooks.library.upenn.edu/
- Agent13's report identifies Arthur Ransome's *We Didn't Mean to Go to Sea* (1949 18th impression) as a thematic alternative: its rear endpaper map and p.94 Chapter VII scene fit the N20 motifs (all-night passage, place for five at the cabin table, children waiting in fog with the sea outside). See `results/h17-k08-ransome-map-endpaper-locator-candidate-20261107.md`.
- On the Ransome 1949 impression, p.94 body word 103 is “shelf”; including the eight-word chapter heading changes it to “took”. Neither is the K08 phrase. This is a thematic/page-94 analogue, not the strongest physical fingerprint.

## Derivation

Interpret the four hexadecimal digits as two bytes:

- `0x5E` = 94 decimal, a plausible printed page number.
- `0x67` = 103 decimal, a plausible word index on that page.

This gives **page 94, word 103**. ST-094 appears in the L-29/N ticket set. The p.94 coordinate fits Cowper Part I's 168-page extent.

Cowper also gives a natural two-volume mapping for the N/S ticket pages:

| Route | Ticket pages | Cowper volume | Pagination fit |
|---|---|---|---|
| L-29/N | 81, 94, 99, 106, 112 | Part I: Essex and Suffolk | All within 168 pages |
| L-29/S | 121, 130, 135, 142, 151 | Part II: Nore to Scilly | All within 365 pages |

The map-reverse owner inscription in the Part I listing adds a distinctive physical match. Taken together, the direct Riddle reference, Childers-Cowper connection, N/S-to-volume mapping, p.94/word103 locator, and map-verso owner-name detail make Cowper the strongest current candidate for David's map-bearing book. The actual copy and the name on its map have not been inspected.

## Competing candidates

- **Arthur Ransome, *We Didn't Mean to Go to Sea* (1949 18th impression):** strong N20 thematic and p.94 scene analogue, with a rear endpaper map. Printed word 103 does not yield the phrase; no equivalent owner-name-on-map-reverse or N/S two-volume page crosswalk has been established. Keep as a secondary physical candidate until the actual book is seen.
- **Robert Lloyd Praeger, *The Way That I Went* (1947 third edition):** N pages fall within *The Volcanic North* (starting p.62) and S pages after the *Silurian Region* boundary at p.118. Plausible but less direct than Cowper's two-volume mapping. Google Books record: https://books.google.com/books?id=uT5RAQAAIAAJ
- **W. Eric Wilson, *The Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen* (1934):** a physical-profile analogue (cloth, frontispiece, folding charts), with no confirmed map-verso owner inscription or ticket-page mapping.
- **T. G. Cuthell, *A Sailing Guide to the Solent and Poole Harbour* (1893):** a small guide for yachtsmen with charts and a lieutenant-colonel attribution, making it an analogue to the fictional guide described in *The Riddle of the Sands*. Its listed extent is about 100 pages plus advertisements, so pages 121-151 do not fit it as a single source for all L-29 tickets.

## What this does and does not establish

- The page/word split is a hypothesis, not a source-defined convention. MAIL-06 only says the suffix might help identify the book.
- Cowper *Sailing Tours* is the strongest current candidate for the map-bearing book and for explaining the L-29/N/S ticket pages. The physical copy has not been inspected.
- The PBFA listing describes a previous owner's name on the reverse of a frontispiece map. It does not identify that name as Dollmann or prove that the listing's copy is David's copy.
- The physical evidence may be one volume or a set. MAIL-09 uses the singular “book”; this must be resolved by inspection.
- The suffix `5E67` remains a standby transcription and must not replace the signed WN-14 register or the signed desk nonce.
- No printed page text or word has yielded the K08 phrase. The exact handwritten margin/envelope copy remains missing.

## Highest-value physical test

When the book/folder is located, preserve photographs or scans of:
1. Cowper Part I and Part II title pages, edition statements, maps, and the **reverse of the Part I frontispiece map**, including the previous-owner inscription;
2. Part I printed p.94, including full page and margins, then Part I ticket pages 81, 99, 106, and 112;
3. Part II ticket pages 121, 130, 135, 142, and 151;
4. the tea receipt in place, including date, amount, and any page marking;
5. the original WN-14 folder and Emily's loose desk notes, especially the handwritten photo-caption margin and envelope copy;
6. Ransome's p.94 and rear endpaper map only if Cowper is absent or the physical copy contradicts this candidate.

Record exactly how word 103 is counted, including treatment of running headers, page numbers, captions, footnotes, and hyphenated words. Verify any resulting phrase only after applying the documented K08 normalization and signed desk nonce.

## Confidence

- Cowper *Sailing Tours* as the map-bearing book and L-29/N/S ticket-page crosswalk: **moderate-to-high candidate**, unconfirmed.
- The map-reverse previous-owner inscription as a match to the Riddle clue: **strong physical parallel**, actual name unknown.
- `5E67 -> page 94 / word 103`: **plausible, low-to-moderate confidence**.
- Exact physical copy, handwritten phrase, and K08 component: **unresolved**.
