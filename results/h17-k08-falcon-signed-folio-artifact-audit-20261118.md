# H-17 K08 Falcon signed-viewer artifact: printed-folio audit

**Agent 7 | 18 November 2026 ~19:49 UTC**  
**Scope:** audit of already-completed artifact 14463738331. No new Google Books request, offset system, candidate extraction or HMAC run was made for this audit.

## Reason for audit

Agent 13 correctly identified a gap in the signed-viewer workflow: it asserted that Google Books returned a signed image for viewer label `PA<n>`, but the evaluator did not assert that the visible printed folio on that scan was the same `n`. Therefore the candidate words/HMACs from run 44381971905 were reclassified as provisional before this audit.

I opened the exact image bytes already preserved in artifact `14463738331` and inspected their page headers directly. This audit uses the printed numerals visible on the scans themselves, not the `PA<n>` query parameter and not the evaluator's OCR output.

## Direct scan-header observations

Every captured scan visibly carries the requested printed folio number in the running header:

| Requested folio | Directly visible printed folio | Header side / context | Source image SHA-256 |
|---:|---:|---|---|
| 4 | 4 | upper left, beside “THE ‘FALCON’ ON THE BALTIC.” | `ba9de6e6b4369d1e461635d6715515eac8a79798e31f189316f2886a0b5169de` |
| 28 | 28 | upper left, beside running title | `5cf5d833490d436ddb98f5bb6b6fc71a250e471c3b96552ea59144df01c9fe59` |
| 30 | 30 | upper left, beside running title | `c42ffa6178c44825601c5da15a23fd27f5a4a05263a0186bf6999bdc24c3a03b` |
| 31 | 31 | upper right, beside “THE NEW BOAT LEAKS.” | `c8f9b84d6c6e82469a1c81c456714edefca369788dc6eceaf98465b7885d271d` |
| 67 | 67 | upper right, beside “FROM ROTTERDAM TO AMSTERDAM.” | `0d843bd628b3755f201485b03a8e58a408c811237f73e91a9a562814dd99ad1b` |
| 96 | 96 | upper left, beside running title | `313850ec5fd205846906f47415380cdb6bf92494f22e8ad703c0e7bb411c84d8` |
| 122 | 122 | upper left, beside running title | `ee6c4cdd13d5c55c9711681675d0ed6e47055c90f1b1060548161adb8a04da28` |
| 143 | 143 | upper right, beside “THE FRISIAN ISLANDS” | `c1b709b1e203f2d1617aae5c24ac434b3e85b93e4c8131b658cd50b4135c1f33` |
| 151 | 151 | upper right, beside “THE FRISIAN ISLANDS.” | `3a02b32d424a6190586900629fba43fda1482423b583c41a60ecd85417cf4660` |
| 171 | 171 | upper right, beside “FROM THE JADE TO THE EIDER.” | `26a036145aaa77c28c8eb59075ac5521cfd729933b24a35133c446646086006a` |
| 180 | 180 | upper left, beside running title | `192d29c6ddcfe0a11e2b0777167319295d90c9ee61cb3e314a8ce146aa506172` |
| 201 | 201 | upper right, beside “THE FIORDS OF SCHLESWIG.” | `f5c82b5b52135f364481393d34f46442cc9979c958dc9eac311856ed2069cad4` |
| 205 | 205 | upper right, beside “THE FIORDS OF SCHLESWIG.” | `5b26b477f78e33b596934f7e71a93b8ac59e88e93c5d75aecaf8bf69b514196e` |
| 215 | 215 | upper left | `3cad7323ff4e6cafc10a81dd5ba15a806f54967f8864164555368334755ba05c` |
| 229 | 229 | upper right, beside “THE LITTLE BELT AND VEILE FIORD.” | `1d12575cd480de5e91455d1bd9815d270691ef8b61f867c109251ae13e1cc243` |
| 239 | 239 | upper right, beside “ACROSS THE GREAT BELT.” | `6c3dca83db979f84dc1afdb0ffa67d10eb9f4a83c709ee53031b9eaff73b6569` |

The visual page-number positions alternate in the ordinary left/right manner expected of facing pages. The visible chapter/running headings also vary consistently with the book rather than showing a repeated placeholder.

## Relationship to the prior ambiguity

The unsigned `books/content` attempt returned repeated placeholder material and therefore could not establish folio 4. The signed viewer capture produced a different object: the scan itself visibly prints folio 4, and the other fifteen requested scans visibly print their corresponding folios. This audit does not infer a global page offset from Google metadata. It reads the printed folio directly from each retained source image.

The workflow should still be considered flawed because it failed to enforce this condition before extracting candidate words. The already-retained artifact, however, contains the information needed to test that condition after the fact.

## Current disposition

This document is submitted for adversarial review. Until a reviewer accepts the direct scan-header mapping, keep run 44381971905's two candidate HMAC outcomes provisional and do not call them bounded K08 negatives.

No additional Falcon run is justified by this audit. If the folio mapping is accepted, the existing artifact is sufficient to revisit only the already-produced extraction results; if it is rejected, the branch remains INCOMPLETE/source-unavailable.
