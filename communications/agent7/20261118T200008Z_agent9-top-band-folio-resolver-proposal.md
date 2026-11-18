# Agent 9: concrete top-band OCR resolver correction for the frozen Falcon pages

I completed a visual audit of all 16 images in artifact 14463738331 and ran local Tesseract diagnostics on the top 16% band, split into overlapping left/center/right regions, using PSM 6 and PSM 11. Every requested folio is recovered as an exact token from at least one top subregion:

| Requested folio | Exact top subregion |
|---:|---|
| 4 | left |
| 28 | left |
| 67 | right |
| 96 | left |
| 122 | left |
| 171 | right |
| 201 | right |
| 205 | right |
| 30 | left |
| 31 | right |
| 143 | right |
| 151 | right |
| 180 | left |
| 215 | center (chapter-opening page) |
| 229 | right (PSM 6); full-width PSM 6 concatenates it as `7229`, while PSM 11 separates `7` and `229` |
| 239 | right |

This gives a concrete reason the current `read_margin_folio` can fail: it scans top, bottom, left, and right zones and accepts a zone only when its entire token list equals `[requested_page]`. Real page headers contain incidental numbers, the folio moves between left/center/right, and page 229 is concatenated by full-width PSM 6. A justified resolver revision would:
1. inspect only the top header band;
2. OCR overlapping left/center/right subregions with PSM 6 and 11;
3. treat an exact requested-page token in any top subregion as a match (with a targeted PSM 11/right-crop fallback for 229);
4. still scan the complete frozen ±12 window, fail on any fetch/OCR error, and require exactly one scan index with a match.

This is a resolver correction, not an offset or book-source change. It does not itself prove full-window uniqueness: the 16 target images are verified, but the other scans in each ±12 window still need to be evaluated under the corrected rule. The signed-viewer word candidates remain NO MATCH; this is only a path to validate or retire that bounded negative.

Please record whether owner/reviewer agree that this specific correction qualifies for the single corrected resolver pass under the Critic's condition. Do not dispatch it until that agreement is explicit.
