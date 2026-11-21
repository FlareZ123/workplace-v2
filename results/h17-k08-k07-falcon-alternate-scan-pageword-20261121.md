# K08: complete the K07/Falcon page-word screen using an alternate 1889 scan

**Date:** 21 November 2026  
**Status:** bounded negative for the four predeclared public-edition interpretations; no K08 recovery.

## Why this was run

Agent50's K07/Falcon page-word workflow, run https://github.com/FlareZ123/workplace-v2/actions/runs/44820093454, ended **PARTIAL**. Its artifact reported all 16 requested printed folios unresolved because the Google Books page-image endpoint returned repeated 300×391 placeholder images. The four candidate views were therefore INCOMPLETE, not HMAC negatives.

The 00:37Z Critic instruction was to preserve that artifact and not widen the family until the exact page-resolution gap was fixed by a source-bearing observation. This test fixes that gap with a separate retained 1889 scan; it does not change the coordinate sets, word-position rule, K08 nonce, normalization, or acceptance commitment.

## Source and folio resolution

Used the Internet Archive scan artifact from https://github.com/FlareZ123/workplace-v2/actions/runs/44415254566, artifact **14479741922** (agent41-k08-falcon-map-control). Its falcononbalticc00knig.pdf identifies Edward Frederick Knight's *The "Falcon" on the Baltic*, W. H. Allen, 1889, from the University of British Columbia Library. The exact PDF used here is 350 pages, 19,125,467 bytes, SHA-256:

0f237b073f5768b77b5badc78836a76e35fc84cd67e5c3542175831b87564d3b

Printed folio to zero-based PDF page-index mapping:

| Printed folio | PDF index | Printed folio | PDF index |
|---:|---:|---:|---:|
| 2 | 15 | 51 | 66 |
| 71 | 86 | 115 | 132 |
| 123 | 140 | 137 | 154 |
| 183 | 200 | 185 | 202 |
| 186 | 203 | 197 | 214 |
| 201 | 220 | 204 | 223 |
| 206 | 225 | 220 | 241 |
| 230 | 251 | 232 | 253 |

Folios 51, 71 and 137 were visually inspected in the scan. The PDF text layer misreads folio 51 as 61; the page image clearly shows 51. It correctly exposes the other folios, including 71 and 137. This is a public 1889 edition candidate, **not an authenticated image of David's physical book** and not proof that this title is the MAIL-09 book.

## Frozen inputs and method

Reconstructed AX-7782 K07 from the accepted transfer receipt and greatest-attempt checkpoint for each sequence 0..7:

- checkpoint preimage: 8947CEDCB9CC73BAB7E87BE63302C5C9
- accepted K07 component: 93495F5E425AB8E592123DABAEB68545
- SHA-256 of that component matches the unchanged K07 commitment.

The two already-declared coordinate views are:

- checkpoint high byte = printed page, low byte = body-word position: (137,71), (206,220), (185,204), (115,186), (183,232), (123,230), (51,2), (197,201)
- checkpoint low byte = printed page, high byte = body-word position: (71,137), (220,206), (204,185), (186,115), (232,183), (230,123), (2,51), (201,197)

For each view, tested both zero-based and one-based word positions. OCR used Tesseract 5.5.0 on 2× page renders with --psm 4; body cleanup and tokenization reuse Agent10's clean_body_lines() and WORD_PATTERN. The independent PDF text layer was also tokenized under the same cleanup. The unchanged K08 normalization/HMAC was applied with the route-sheet desk nonce. The N02 known-answer control returned the expected HMAC16 BF889359B0303F2B2B2FD96AE841210B.

## Results

All four OCR-derived candidates are complete; none matches the K08 commitment 285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747.

| Coordinate view | Word base | Selected words | HMAC16 component | SHA-256(component) |
|---|---:|---|---|---|
| high-page / low-word | 0 | from never our deer fifth justice people distinguished | 8B81BD028AB52178F21473B30903E5A7 | da6bf3cb16cb683061627450ee4dbc4496eb9825e231b78a4cf9c75bbcdcaae0 |
| high-page / low-word | 1 | unmolested was go with the eminence holland be | ADA838B6E6CDBCD42D4EBEE8F64DBAA0 | 9f527326bcd01eb0083c2eb3604e08c985619608c65899eb38e7b9ca207dcccf |
| low-page / high-word | 0 | the which an this which had all the | 020C6EAB532906FB8F2109D581B2CB19 | 1c3b55100d191888cbaec7ad3f7f3fad14f0fc3b71915c26c7853e4cb8b85c0e |
| low-page / high-word | 1 | were opening to time side we on of | 913718DEA9E02A0535E7704A9F4FD71D | ac4822aa424def92356c4cf24890827e19fbf15d696e98bcb48fb6f6a242cbe9 |

The PDF text-layer extraction independently produced four different word strings, also with zero K08 commitment hits:

| Coordinate view | Word base | PDF text-layer words | SHA-256(component) |
|---|---:|---|---|
| high-page / low-word | 0 | the off go well the do people distinguished | c6da97e153c7ee8c326b0cb7232ce2cf5de54fb3b8e70df001225e45d6044204 |
| high-page / low-word | 1 | from far let park through to holland be | 453381549ad2ad2abfdfb76a0f627685fd23de798009f3b13625bdcf1a695daf |
| low-page / high-word | 0 | understood opening to time which had all fiord | 1bee8627911c1695642b9fd04a6f82ffe0342a2bf56b9f000523cac997fd9ece |
| low-page / high-word | 1 | who for obstacle some side we on the | 89c54efeaa364a8097798797780c9d9bafce188e1037213e8723809ff3a6dd6b |

## Public-copy margin inspection

After resolving the folios, rendered all 16 mapped pages and visually reviewed both outer 22% margins in a 4×4 contact sheet. No handwritten marginal words or annotation are visible on any of the 16 selected pages; only ordinary print, gutter shadows, and scan artifacts appear. This closes the N23-style handwritten-margin lead on this particular UBC library scan. It does not speak to David's separate physical copy.

## Disposition

This closes exactly the four predeclared K07 byte-order/index-base page-word views on this public 1889 Falcon scan. It does **not** establish that Falcon was David's physical book, that the N23 margin was in it, or that a different map-back book / physical marginal annotation is excluded. The public scan's selected words are not Emily's final envelope caption.

No K08 value was recovered. candidate.json, acceptance.json, recovery-routing.json, and verify.py remain unchanged. Do not rerun these four Falcon page-word variants or promote the locator to K08 wording.

## Reproduction

- Reproducer: agents/agent12/k08_falcon_alt_scan_pageword.py
- Input: falcononbalticc00knig.pdf from Actions artifact 14479741922; the script verifies its exact SHA-256 before processing.
- Existing incomplete attempt and preserved artifact: run 44820093454 / artifact 14672040841.
