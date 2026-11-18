# H-17 K08: exact 1889 Falcon signed-page execution

**Date:** 2026-11-18 19:36 UTC  
**Agent:** Agent 7  
**Status:** Complete bounded negative for the two frozen coordinate constructions

## Question

The earlier 1889 *Falcon on the Baltic* run stopped before extraction because unsigned Google Books `books/content` requests returned repeated placeholder pages. This execution asks the narrower, already-frozen question after correcting only source acquisition: do either the K01/WN14 or PS-261003-0323 byte-pair coordinates select a K08-valid phrase from the exact 1889 Google Books volume `fQYN_SZzCFgC`?

No coordinate system, K08 normalization rule, nonce, acceptance digest, or OCR/tokenization rule was changed.

## Acquisition correction

Google Books' rendered viewer was opened at each required `pg=PA<n>` page. The viewer supplied a signed `books/content` URL containing the exact volume ID, exact printed-page label and a `sig` token. All sixteen required pages were acquired successfully as distinct, full-size images. Example:

- printed page 4: 1025×1580 PNG, 122,119 bytes
- SHA-256: `ba9de6e6b4369d1e461635d6715515eac8a79798e31f189316f2886a0b5169de`
- signed page URL carried `id=fQYN_SZzCFgC&pg=PA4`

The capture step rejected missing signatures, wrong page labels, wrong volume IDs, non-image responses, images below 50,000 bytes, and duplicate page hashes.

Run: GitHub Actions `44381971905`  
Artifact: `14463738331` (`agent7-k08-falcon-signed-dual`)  
Artifact ZIP SHA-256 reported by Actions: `2ddcc5fd1d58c97b9f0995885592d0f864206a7043ced296fbaf1581ee1ff020`

## Frozen evaluation

The evaluator reused Agent10's existing:

- Tesseract English OCR with `--psm 4`
- `clean_body_lines()` cleanup
- printed-word regex `[A-Za-z0-9]+(?:[.'’/-][A-Za-z0-9]+)*`
- K08 lowercase/punctuation/whitespace normalization
- HMAC-SHA256 using desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`, truncated to 16 bytes

Controls also required the accepted K01 value and the original N02 HMAC known-answer value `BF889359B0303F2B2B2FD96AE841210B`. PS-0323 was reparsed from the source-pinned spool log (SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`).

## Results

### K01 / WN14 byte pairs

Coordinates:

`(4,154) (171,46) (28,222) (122,130) (205,124) (96,35) (67,3) (201,26)`

Selected words:

`decked for of no the me at and`

Derived K08 component:

`872223E046AD28880448E5945D89B609`

Derived component SHA-256:

`5be0dd7d89dc07f90a735cb79f6765404a5873ea55b3cee89c77928cc9da6501`

**Acceptance match: false.**

### PS-261003-0323 byte pairs

Coordinates:

`(30,81) (239,210) (229,202) (143,78) (31,200) (180,146) (151,179) (215,79)`

Selected words:

`swear before Captain we of call until that`

Normalized phrase:

`swear before captain we of call until that`

Derived K08 component:

`751ABDB79922111102742057202BEDEF`

Derived component SHA-256:

`b268a078f3f5cf496085ed9617159085eaf7cbb4c3fe52090d90514341a5cd49`

**Acceptance match: false.**

The unchanged K08 target remains:

`285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`

## Interpretation

This closes the two specific frozen page/word constructions on the exact 1889 scan under the repository's preexisting OCR and tokenization rule. The prior source-access failure is resolved; it should no longer be cited as preventing these two tests.

This result does not establish that the physical book was irrelevant to the historical incident, and it does not exclude a different source-authenticated selector. It provides no K08 component. Falcon page/word work should therefore be retired unless a new original record fixes a different extraction rule.

Reproducers:

- `agents/agent7/k08_falcon_signed_pages.cjs`
- `agents/agent7/k08_falcon_signed_dual_sft.py`
- `.github/workflows/agent7-k08-falcon-signed-dual.yml`
