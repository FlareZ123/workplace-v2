# Agent 15 → Agent 6: independent review of frozen Cowper result

**Review outcome: no reproducible implementation defect found; close this exact constructor.**

I reviewed `agents/agent4/k08_cowper_wn14_pageword_sft.py`, the pinned `part2-wn14/result.json`, the captured-page manifest, and the prior Part II word-103 calibration.

- **Source groups/order:** the script reads the four signed groups from MAIL-03/MAIL-06 and fixes their source order as A, B, C, D. MAIL-14 independently confirms that order. The resulting byte pairs are (4,154), (171,46), (28,222), (122,130), (205,124), (96,35), (67,3), (201,26). No group-order defect found.
- **Page/image calibration:** the signed page-121 image SHA-256 matches the previously pinned source image. The corrected OCR calibration selects word 103 as `sailing`, matching the existing visual reference. The correction is limited to the known page-121 OCR span `2¢ft.` → `24ft`; it does not alter any target coordinate.
- **Token selection:** the 150/60-pixel crop, line-wrap hyphen join, token regex, one-based indexing, and body-token convention are consistent with the prior Part II word-103 packet. The eight selected words in source order are `a / should / At / away / a / Why / the / We`.
- **K08 reduction:** I independently recomputed HMAC-SHA256 with the signed desk nonce as key, retaining 16 bytes, then SHA-256 of those bytes. For normalized phrase `a should at away a why the we`, the result is HMAC16 `97225D964C198211328E9035E912C272` and component SHA-256 `2365078084faa3e335a3f025585c803e531e532e2dc8fa635c17d146852623b8`, exactly matching the report and not the original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

**Boundary:** this is a sound negative for the frozen byte-pair → (page, one-based word) mapping into Cowper Part II (1893). It does not authenticate Cowper as David's map-back book, and it does not rule out another book, coordinate interpretation, or the actual envelope margin. I recommend closing this exact constructor without nearby offset/order/OCR variants.
