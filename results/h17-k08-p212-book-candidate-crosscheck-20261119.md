# K08 P212 locator: cross-check against known map-back book candidates

**Agent9 | 19 November 2026 | conditional locator synthesis; K08 remains unrecovered**

## Question

Does the source-local AX-7782 decode `P212` identify a specific book/page, and does that page help recover the final Emily envelope caption?

## Stronger source-adjacent alternative: Excel A1 cell P212

The tea-bookmark mirror loop returns specifically to bookmark **#3, Tea-room stock sheets**, whose saved path is `R:/Stores/consumables/mug-stock.xls`. In that context, `P212` is also an exact Excel A1 cell address (column P, row 212), not merely a possible printed page.

The eight K01 byte pairs can be read as candidate worksheet coordinates:

- **First byte = row, second = column:** `EX4, AT171, HN28, DZ122, DT205, AI96, C67, Z201`.
- **Swapped:** `D154, FO46, AB222, DR130, GW124, CR35, BO3, GS26`.

For BIFF8 `.xls`, the 256-column limit is A–IV, so both orientations fit the column limit. The first orientation has rows no greater than 205; the swapped orientation reaches row 222. If the missing workbook's relevant sheet has exactly 212 rows, the first orientation fits and the swapped one does not, with `P212` as a cell in the final row. This is a useful structural discriminator **only if** the workbook's actual dimensions support it.

The K01 source has four named ink groups A–D, each four bytes long; split each group into its two row/column pairs and the address list naturally groups as:

- Group A: `EX4, AT171`
- Group B: `HN28, DZ122`
- Group C: `DT205, AI96`
- Group D: `C67, Z201`

Because the bookmark describes “Tea-room stock sheets” (plural), a further **conditional** test is whether the workbook has four corresponding sheets A–D (or unambiguous A–D group labels). If so, inspect only each group's two listed cells on its matching sheet first; otherwise record the actual sheet names and test the listed addresses without inventing a group-to-sheet permutation. The A–D sheet mapping is a hypothesis, not an authenticated join.

The eight-cell interpretation also has a **pre-registered output check**. The existing note-chain low-bit extraction gives `0x4D` = `M`; in first-bit-as-LSB order, that requires the eight selected cell-value LSBs to be exactly `1,0,1,1,0,0,1,0`. If the workbook is supplied and these addresses are numeric teal-filled cells on a relevant sheet, take only `value & 1` in the listed K01 source order and pack first-bit-as-LSB. A result other than `0x4D`, or no teal/numeric support at those exact cells, weakens this specific cell-bit hypothesis. Do not switch to high bits, reverse order, first-character LSBs, or other nearby encodings after seeing the data. Independently test whether P212 contains text/formula/comment content that, when normalized under the unchanged K08 rule, passes the original HMAC commitment.

This cell reading is directly connected to the mirror-loop destination because it returns to the workbook bookmark. It also gives a bounded future test: preserve the native BIFF workbook and inspect **P212 plus these eight addresses in both orientations**, including hidden sheets/rows/columns, fills, formulas, comments, names, objects and embedded images. The `ATEALBIT` / `ALOWBIT` instructions could be consistent with a teal-style/low-bit carrier. The predicted eight-cell LSB output `0x4D` is falsifiable, but neither the cell mapping nor the style/bit extraction is authenticated.

Important limitations: the K01 route defines ink control groups A–D, not spreadsheet coordinates; no workbook bytes or sheet dimensions are present; and P212 does not establish that the workbook contains Emily's final caption. Treat the A1 reading as a **pre-registered secondary locator hypothesis**, not a phrase or recovered component. The book-page interpretation is independently supported by a strong, but still conditional, ticket-page crosswalk; neither branch currently dominates the other.

## Reproduction of the locator

The independent reducer review is preserved in [Agent9's message to Agent22](../communications/agent22/20261119T015000Z_agent9-p212-adversarial-review.md). Under the plausible “lower attempt on even chunk sequence, higher attempt on odd sequence” reading of `LOW IF EVEN`, followed by the established first-bit-as-LSB low-bit packing, AX-7782 yields bytes `50 D4` = `P212`. The same fixed rule on AX-7778, AX-7781 and AX-7783 yields `694A`, `C28A` and `CF59`; none is a page-like P locator. The attempt-selection reading is reasonable but not uniquely forced, and eight per-chunk selection masks produce the same low-bit output because several attempt pairs share LSBs. Preserve P212 as conditional source-derived locator evidence, not as a recovered phrase.

## Independent page-index support: the L-29/N and L-29/S ticket suffixes

The page interpretation is not merely a generic “many books have p.212” guess. The existing [Praeger ticket-page report](h17-k08-mail09-mapbook-praeger-ticket-pages-20261107.md) shows that, **if** the ten L-29 ticket suffixes are printed page numbers, the 1947 third edition of Praeger's *The Way That I Went* gives an exact regional split: North suffixes 81, 94, 99, 106 and 112 all fall in *The Volcanic North* (p.62–117), while South suffixes 121, 130, 135, 142 and 151 all fall in *The Silurian Region* (p.118 onward). The 1997 reprint's p.111 boundary moves ST-112 to the South section, producing a 4/6 split. Praeger is also independently described by rare-book catalogues as a rear-map volume.

The existing [Cowper two-volume candidate report](h17-k08-signed-WN14-book-coordinate-candidate-20261107.md) supplies a second substantial page-index structure: the five L-29/N ticket suffixes (81,94,99,106,112) fit Cowper *Sailing Tours*, Part I (168 pages), while the five L-29/S suffixes (121,130,135,142,151) fit Part II (365 pages). The 1893 Part II therefore contains printed p.212. The same report notes that Childers's *Riddle of the Sands* names Cowper's *Sailing Tours* among Davies's library books, and a PBFA Part I listing records a previous-owner name on the reverse of its frontispiece map. The signed-WN14 page/word test against Cowper Part II did **not** recover K08 (selected words `a / should / At / away / a / Why / the / We`, NO_MATCH), but that does not rule out Cowper as the physical receipt/bookmark carrier.

This makes the book-page branch genuinely plural: **Cowper's two-volume set is the strongest multi-source physical-book candidate** in the existing synthesis, while **Praeger 1947 is the strongest single-volume N/S section-boundary candidate** if ticket suffixes are printed pages. Neither is authenticated. if the ticket suffixes really are page locators and if the physical copy is that edition. It does not authenticate either premise: the CSV does not say ticket suffixes are pages, MAIL-09 does not name Praeger, and the 1937/1939 editions' section boundaries remain unverified. The 1947 pagination must not be transferred to another edition.

Accordingly, retain two parallel P212 readings:

1. **Workbook A1:** P212 is a cell in the exact `mug-stock.xls` destination of the bookmark mirror loop; the eight K01 pairs may be cell addresses, with a falsifiable `0x4D` LSB check.
2. **Book page:** P212 is a printed page in David's map-back book; Praeger 1947 has the strongest N/S ticket-page structure, while Ransome has the strongest N20 thematic fit and Falcon has a directly captured p.212 page image.

They may be alternatives or complementary locators. Do not collapse them into a single object or select one without the native workbook or physical book/receipt.

## Candidate page cross-check

| Candidate | What P212 would mean | Page/context evidence | Assessment |
|---|---|---|---|
| **Arthur Ransome, *We Didn't Mean to Go to Sea* (1949 impression)** | Printed page 212 | The edition's contents place Chapter XVI, **“Dawn at Sea,”** at p.208 and Chapter XVII at p.222, so p.212 lies inside the dawn-after-watch chapter. The existing [Ransome locator report](h17-k08-ransome-map-endpaper-locator-candidate-20261107.md) describes the chapter's all-night passage, cabin gathering, tableware/cocoa and sea changing at dawn. | **Strongest thematic fit** to N20's “sea / end of the night / voices at the table” brief, but the exact physical copy and page-212 text/receipt are not identified. The earlier bounded phrase search over 11,100 spans from the dawn-at-sea excerpt had no K08 hit. |
| **Erskine Childers, *The Riddle of the Sands* (1903)** | Printed page 212 | Google Books' 1903 contents place Chapter XX, **“The Little Drab Book,”** at p.201 and Chapter XXI at p.213; p.212 is therefore the last page of the chapter. Chapter XX describes a cabin table, books, cups/cocoa, the late hour, and a separate old guide for yachtsmen with a map-related clue. The 1903 text also lists Knight's *Falcon in the Baltic* among Davies's library. | A strong **literary locator** for the book/map/table clues, but Chapter XX's “Little Drab Book” is a *separate estuary guide*, not automatically the physical H-17 book. Do not conflate the novel with the guide it describes. |
| **R. M. Ballantyne / W. H. Knight, *The Falcon on the Baltic* (1889)** | Printed page 212 | Agent7's signed-viewer full-window artifact contains an authenticated Google Books image for `PA212` (volume `fQYN_SZzCFgC`; artifact 14486034855, run 44433317701). The visible page describes an old sea-captain and a Baltic Hotel public room with local gossips, pipes and beer. The 1889 item has a rear GENERAL MAP. | A plausible map-back candidate and partial sea/voices/social-room fit, but weaker than Ransome for the late-watch/dawn/table wording. A bounded OCR/HMAC search over p.212 and adjacent pp.211–213 found no exact K08 hit (OCR-dependent negative only). |
| **R. Lloyd Praeger, *The Way That I Went*** | Printed page 212 | Agent22's [P212 locator report](h17-k08-ax7782-p212-locator-20261119.md) establishes that p.212 is an interior text page in the 1937/1939 and 1947 candidates, within “The Land of Naked Limestone.” | Valid page number, but page context does not independently explain N20's sea/night/table brief. The page could still locate a receipt; no title identification follows. |
| **Cowper, *Sailing Tours*, Part II (1893)** | Printed page 212 is in range (the volume is listed as 365 pages). | The existing signed-WN14 page/word test against Cowper Part II captured all eight coordinate pages and selected `a / should / At / away / a / Why / the / We`; its K08 HMAC commitment check was **NO_MATCH**. The two-volume Cowper ticket crosswalk maps L-29/N pages to Part I and L-29/S pages to Part II, conditionally. | P212 is physically possible in Part II, but the printed-word extraction did not recover K08. The receipt/margin could still be at p.212; the physical set/copy is unverified. |
| **Cowper, *Sailing Tours*, Part I (1892)** | Printed page 212 | The [Little Drab Book / Cowper distinction report](h17-k08-little-drab-book-messum-cuthill-20261107.md) gives Part I as a 168-page volume with charts. | **Cannot be the printed-p.212 object** if P212 means a printed folio. Cowper remains a separate map-back candidate, but P212 would have to refer to another object or a non-folio index. |
| **Messum (1903) / Cuthill (1893) estuary guides** | Printed page 212 | The same bibliographic report gives Messum as 24 numbered pages plus unpaginated chart/tide-table leaves, and Cuthill as 100 pages plus advertisements. | These are analogues for the separate guide described in Riddle Chapter XX; neither supports printed p.212. |

## What the cross-check establishes

1. P212 is a useful **dual-use locator**. The Excel A1 reading is directly connected to the bookmark fixed point returning to `mug-stock.xls`; the printed-page reading has an independent conditional N/S ticket crosswalk that makes Praeger 1947 the strongest page-index candidate. Neither interpretation selects a unique object without source bytes. Several long map-bearing books have a page 212, while some otherwise plausible small guidebooks and Cowper Part I do not.
2. Ransome is the strongest **semantic** candidate because p.212 lies inside “Dawn at Sea.” Falcon has an actual p.212 scan and rear map, but its p.212 scene is a hotel/public-room episode rather than the late-watch/dawn cabin scene.
3. Riddle is an important **literary key** to the separate estuary guide and the table/cocoa/book setting. Its p.212 is in “The Little Drab Book,” but this does not prove the David-owned physical book is Riddle.
4. The printed pages tested do not supply the exact committed phrase. The Falcon OCR test checked 42,778 contiguous spans on p.212 and 362,526 spans across pp.211–213; no match. The prior Ransome test checked 11,100 spans from its dawn-at-sea excerpt; no match. These are bounded text negatives, not evidence against a handwritten receipt, margin, or caption.

## Next discriminating evidence

If an independently authorized workbook is supplied, first preserve its native bytes and sheet dimensions, then inspect P212's value/formula/comment and the eight K01 cell addresses in both orientations. If the exact cells are numeric and teal-filled, test only their value LSBs in source order for the pre-registered `0x4D` output before any broad extraction. If an independently authorized physical book is supplied, identify its title/edition and preserve the tea receipt **in situ**; only then check whether printed p.212 is relevant. The physical receipt/book, the mug-shelf card, the native `mug-stock.xls` workbook and Emily's author-final envelope/margin remain distinct possible carriers; do not merge them without a source join.

**Status:** P212 preserved as conditional locator evidence. No book title is authenticated, no K08 phrase was generated, and no K08 commitment hit was obtained.
