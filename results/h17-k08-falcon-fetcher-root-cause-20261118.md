# Falcon 1889: unsigned-image fetch failure and signed-viewer evidence audit

**Date:** 2026-11-18  
**Status:** bounded evidence-quality correction; K08 not recovered.

## Question

What did the original page-4 folio failure establish, and what does the later signed-viewer artifact actually support?

## Evidence examined

- Original failed resolver run: [44380167069](https://github.com/FlareZ123/workplace-v2/actions/runs/44380167069), artifact [14463657135](https://github.com/FlareZ123/workplace-v2/actions/runs/44380167069/artifacts/14463657135).
- Signed-viewer dual run: [44381971905](https://github.com/FlareZ123/workplace-v2/actions/runs/44381971905), artifact [14463738331](https://github.com/FlareZ123/workplace-v2/actions/runs/44381971905/artifacts/14463738331).
- Fetch logic: `agents/agent10/k08_falcon_1889_pageword.py`.
- Signed-page capture: `agents/agent7/k08_falcon_signed_pages.cjs`.
- Signed dual extraction: `agents/agent7/k08_falcon_signed_dual_sft.py`.
- Agent 7's companion visual audit: [h17-k08-falcon-signed-folio-artifact-audit-20261118.md](h17-k08-falcon-signed-folio-artifact-audit-20261118.md).

## Finding 1 — the original failure is an image-acquisition failure, not evidence of duplicate genuine folios

The original artifact's folio-4 entry reports `scan_window=[0,16]`, `unique_match_count=0`, and no failed scan indices. Scan indices 1 through 16 all have the same source-image SHA256:

`12557f8948b8bdc6af436e3a8b3adddd45f7f7d2b67c5832e799cdf4686f72bb`

Their recorded margin OCR is likewise identical: empty top, bottom and left zones, and only token `7` in the right zone. Scan index 0 has a different hash and only incidental left/right tokens `6` and `7`. The artifact therefore does **not** show multiple genuine pages bearing printed folio 4; it shows zero qualifying folio-4 matches and repeated identical image content across the remaining scan indices.

The old `fetch_page_image` helper requests unsigned generic `books/content` URLs (zoom 2, `edge=curl`, `source=gbs_api`) and accepts an `image/*` response without checking dimensions, minimum byte size, or duplicate image hashes. The evidence is consistent with a shared fallback/placeholder response from that endpoint. The artifact does not preserve the original image bytes or dimensions, so the precise response type should not be asserted more strongly than “identical repeated image content.”

## Finding 2 — the signed-viewer artifact contains real page images with visible printed folios

The later signed-viewer capture obtains the image URL from the Google Books viewer DOM. Its image URL carries viewer-generated signature parameters (including `sig` and `w=1025`) rather than the unsigned generic request. For page 4, the manifest records 122,119 bytes, dimensions 1025×1572, and image SHA256:

`ba9de6e6b4369d1e461635d6715515eac8a79798e31f189316f2886a0b5169de`

The 16 images in the signed artifact visibly display the requested printed folio:

| Candidate set | Printed folios | Observed folio position |
|---|---|---|
| K01/WN14 | 4, 28, 67, 96, 122, 171, 201, 205 | Top header; left or right |
| PS-0323 | 30, 31, 143, 151, 180, 215, 229, 239 | Top header; left, center or right |

A local OCR diagnostic on the top 16% of each image, split into overlapping left/center/right crops and run with Tesseract PSM 6 and 11 using a digit whitelist, recovered the exact requested folio in at least one top subregion for all 16 images. Folio 215 is centered on a chapter-opening page; folio 229 needs a right-crop/PSM-11 fallback because full-width PSM 6 concatenates adjacent marks as `7229`. Thus there is no universal even/odd corner rule. The defensible layout observation is that the folio is in the top header band, with horizontal position varying.

This agrees with Agent 7's visual audit. It does not, by itself, establish uniqueness against every other scan in the original ±12 window.

## Finding 3 — the two frozen pageword candidates do not recover K08

The signed dual artifact reports `any_acceptance_match=false`. The two candidate constructions are:

| Candidate | Normalized phrase | Derived component | SHA256 of component |
|---|---|---|---|
| K01/WN14 | `decked for of no the me at and` | `872223E046AD28880448E5945D89B609` | `5be0dd7d89dc07f90a735cb79f6765404a5873ea55b3cee89c77928cc9da6501` |
| PS-0323 | `swear before captain we of call until that` | `751ABDB79922111102742057202BEDEF` | `b268a078f3f5cf496085ed9617159085eaf7cbb4c3fe52090d90514341a5cd49` |

Neither matches the original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. These are bounded no-hits for the two frozen pageword constructions, not a recovered phrase. The book itself is still an exploratory locator from MAIL-09, not authenticated as Emily's historical source.

## Corrective implication and limit

A corrected resolver must obtain each image through the viewer-generated signed URL method, validate the requested volume/page identity, reject tiny or repeated image responses, and inspect the top header band. A full-window resolver would still need to fetch every scan in each frozen ±12 window, reject all fetch/OCR failures, and demonstrate exactly one genuine printed-folio match.

**No second full-window run is authorized by this report.** The Critic's frozen rule remains controlling: obtain explicit owner/reviewer agreement (and any required Critic approval) before one corrected resolver pass. Do not change offsets, search other books, or expand phrase generation.

**Conclusion:** the original folio-4 failure was caused by unusable repeated image content from the unsigned fetch path, not a demonstrated duplicate printed folio. The signed-viewer images support the printed-folio labels on the 16 target pages, but neither the K01/WN14 nor PS-0323 word construction passes K08. K08 remains unrecovered.
