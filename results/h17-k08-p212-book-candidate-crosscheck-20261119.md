# K08 P212 locator: cross-check against known map-back book candidates

**Agent9 | 19 November 2026 | conditional locator synthesis; K08 remains unrecovered**

## Question

Does the source-local AX-7782 decode `P212` identify a specific book/page, and does that page help recover the final Emily envelope caption?

## Reproduction of the locator

The independent reducer review is preserved in [Agent9's message to Agent22](../communications/agent22/20261119T015000Z_agent9-p212-adversarial-review.md). Under the plausible “lower attempt on even chunk sequence, higher attempt on odd sequence” reading of `LOW IF EVEN`, followed by the established first-bit-as-LSB low-bit packing, AX-7782 yields bytes `50 D4` = `P212`. The same fixed rule on AX-7778, AX-7781 and AX-7783 yields `694A`, `C28A` and `CF59`; none is a page-like P locator. The attempt-selection reading is reasonable but not uniquely forced, and eight per-chunk selection masks produce the same low-bit output because several attempt pairs share LSBs. Preserve P212 as conditional source-derived locator evidence, not as a recovered phrase.

## Candidate page cross-check

| Candidate | What P212 would mean | Page/context evidence | Assessment |
|---|---|---|---|
| **Arthur Ransome, *We Didn't Mean to Go to Sea* (1949 impression)** | Printed page 212 | The edition's contents place Chapter XVI, **“Dawn at Sea,”** at p.208 and Chapter XVII at p.222, so p.212 lies inside the dawn-after-watch chapter. The existing [Ransome locator report](h17-k08-ransome-map-endpaper-locator-candidate-20261107.md) describes the chapter's all-night passage, cabin gathering, tableware/cocoa and sea changing at dawn. | **Strongest thematic fit** to N20's “sea / end of the night / voices at the table” brief, but the exact physical copy and page-212 text/receipt are not identified. The earlier bounded phrase search over 11,100 spans from the dawn-at-sea excerpt had no K08 hit. |
| **Erskine Childers, *The Riddle of the Sands* (1903)** | Printed page 212 | Google Books' 1903 contents place Chapter XX, **“The Little Drab Book,”** at p.201 and Chapter XXI at p.213; p.212 is therefore the last page of the chapter. Chapter XX describes a cabin table, books, cups/cocoa, the late hour, and a separate old guide for yachtsmen with a map-related clue. The 1903 text also lists Knight's *Falcon in the Baltic* among Davies's library. | A strong **literary locator** for the book/map/table clues, but Chapter XX's “Little Drab Book” is a *separate estuary guide*, not automatically the physical H-17 book. Do not conflate the novel with the guide it describes. |
| **R. M. Ballantyne / W. H. Knight, *The Falcon on the Baltic* (1889)** | Printed page 212 | Agent7's signed-viewer full-window artifact contains an authenticated Google Books image for `PA212` (volume `fQYN_SZzCFgC`; artifact 14486034855, run 44433317701). The visible page describes an old sea-captain and a Baltic Hotel public room with local gossips, pipes and beer. The 1889 item has a rear GENERAL MAP. | A plausible map-back candidate and partial sea/voices/social-room fit, but weaker than Ransome for the late-watch/dawn/table wording. A bounded OCR/HMAC search over p.212 and adjacent pp.211–213 found no exact K08 hit (OCR-dependent negative only). |
| **R. Lloyd Praeger, *The Way That I Went*** | Printed page 212 | Agent22's [P212 locator report](h17-k08-ax7782-p212-locator-20261119.md) establishes that p.212 is an interior text page in the 1937/1939 and 1947 candidates, within “The Land of Naked Limestone.” | Valid page number, but page context does not independently explain N20's sea/night/table brief. The page could still locate a receipt; no title identification follows. |
| **Cowper, *Sailing Tours*, Part I (1892)** | Printed page 212 | The [Little Drab Book / Cowper distinction report](h17-k08-little-drab-book-messum-cuthill-20261107.md) gives Part I as a 168-page volume with charts. | **Cannot be the printed-p.212 object** if P212 means a printed folio. Cowper remains a separate map-back candidate, but P212 would have to refer to another object or a non-folio index. |
| **Messum (1903) / Cuthill (1893) estuary guides** | Printed page 212 | The same bibliographic report gives Messum as 24 numbered pages plus unpaginated chart/tide-table leaves, and Cuthill as 100 pages plus advertisements. | These are analogues for the separate guide described in Riddle Chapter XX; neither supports printed p.212. |

## What the cross-check establishes

1. P212 is a useful **page-location lead**, but it does not select a unique title or edition. Several long map-bearing books have a page 212, while some otherwise plausible small guidebooks and Cowper Part I do not.
2. Ransome is the strongest **semantic** candidate because p.212 lies inside “Dawn at Sea.” Falcon has an actual p.212 scan and rear map, but its p.212 scene is a hotel/public-room episode rather than the late-watch/dawn cabin scene.
3. Riddle is an important **literary key** to the separate estuary guide and the table/cocoa/book setting. Its p.212 is in “The Little Drab Book,” but this does not prove the David-owned physical book is Riddle.
4. The printed pages tested do not supply the exact committed phrase. The Falcon OCR test checked 42,778 contiguous spans on p.212 and 362,526 spans across pp.211–213; no match. The prior Ransome test checked 11,100 spans from its dawn-at-sea excerpt; no match. These are bounded text negatives, not evidence against a handwritten receipt, margin, or caption.

## Next discriminating evidence

If an independently authorized original is supplied, first identify the David-owned title and edition from its cover/title page and rear map, then preserve the tea receipt **in situ** and record its printed page position. Check p.212 and the adjacent margin/receipt before moving anything. The physical receipt/book, the mug-shelf card, the native `mug-stock.xls` workbook and Emily's author-final envelope/margin remain distinct possible carriers; do not merge them without a source join.

**Status:** P212 preserved as conditional locator evidence. No book title is authenticated, no K08 phrase was generated, and no K08 commitment hit was obtained.
