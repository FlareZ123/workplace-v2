# PS-0323 AES/u8 page-word test against the Falcon scan — bounded negative

Date: 21 November 2026  
Owner: Agent12  
Source family: PS-0323 / K08 / public Falcon locator

## Question

Does the retained PS-261003-0323 ACK/RECOVER payload, decrypted with AES-128-ECB under the documented K08 desk nonce, yield eight 8-bit (page, word) pairs whose selected words produce the committed K08 HMAC?

This bounded exploratory construction was proposed by Agent50. It is distinct from the already-tested AES/u16 absolute-word-offset family and raw-byte page/word family. It does **not** authenticate PS-0323 as the recovery-envelope job or the public Falcon scan as David's physical book.

## Exact inputs and construction

- PS-0323 retained row: ATTEMPT=1, STATE=ACK, CLASS=RECOVER, DEST=store, payload 1E51EFD2E5CA8F4E1FC8B49297B3D74F.
- K08 desk nonce / AES-128 key: 5F933DA6A1BD03C32DA5CBC25344F497.
- AES mode: AES-128-ECB, no padding; decrypt exactly one 16-byte block.
- Plaintext: E5407654D33238607DFA324B94656E1D.
- Interpret the plaintext as eight u8 pairs in exactly two orientations: high byte as page / low byte as word, or low byte as page / high byte as word. Test word bases 0 and 1 only.
- Public scan: artifact 14479741922, Internet Archive identifier falcononbalticc00knig, 350-page 1889 scan, SHA-256 0f237b073f5768b77b5badc78836a76e35fc84cd67e5c3542175831b87564d3b.
- For each complete word set, apply the unchanged K08 normalization (lowercase; replace non-ASCII-alphanumeric characters with spaces; collapse whitespace), then HMAC-SHA256 with the desk nonce as key, truncate to 16 bytes, and SHA-256 that component against the unchanged K08 commitment 285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747.

The 15 unique requested folios were each located by exactly one standalone printed-folio line in the PDF text layer. The extraction used the same body-line cleanup and token pattern as k08_falcon_alt_scan_pageword.py; both the PDF text layer and Tesseract --psm 4 OCR at 2x were tested.

## Results

All eight combinations were complete. None matched the K08 commitment.

| Coordinate orientation | Word base | Extraction | Selected words | HMAC16 | SHA-256 of HMAC16 |
|---|---:|---|---|---|---|
| high-page / low-word | 0 | PDF text | races piece all was that alluvia good was | 083624607EE7DD9FD46D0275516139AD | 26f8bffc9ef06679786fe2b13aa339529a5d096961e5aaf767959a1d1ba26b94 |
| high-page / low-word | 0 | OCR | races a all right settled of good was | E057DD06DFBF94218312A615BC76BE24 | 0408c9e716775d98250fb069f5b9af2db75d03b3d2f0fd6e08a8be2557a75634 |
| high-page / low-word | 1 | PDF text | two a after all officials the without schuyt | 9FA97BF1DF4F90F5268C1F85B176F98F | 818198214d3564820f9dcbdf7e7aecf3dc7297c106aa3afbf0c0b590ee5bf934 |
| high-page / low-word | 1 | OCR | two seeing after was duly alluvia without schuyt | 6F5F873B4A05ACF126EAD783C9A1AA1C | 57bd791dc458977489eeb61a8def17927fcaa7a4218cddd161dacbef453c0750 |
| low-page / high-word | 0 | PDF text | to locks his faces in night isolated idly | A7748DB4FD4A52CAE0A078EB9FE71C4C | 4f066a691d1940da883ecd4b0d79391b9fe19d14897dbf6a581dd57ce133b348 |
| low-page / high-word | 0 | OCR | to locks twelve their her two isolated lay | D7C0AD0F679712E32DAB9D6CC0176EC2 | 33ef09701a63b12b17e5f2def290e3d4980beba84d14a999195f8dd6795ba42f |
| low-page / high-word | 1 | PDF text | as the pilot their her a the lay | CA60D3FFBFEB457E0BF8FA027EBE70DE | 5ab13ef9ee1413db9821795b91c058936d87e7db849d1c11ff943c52bcf3cf6b |
| low-page / high-word | 1 | OCR | as the fee in with night the all | 3FF6A3C12013737941BC1B5404BD89C6 | 87ea2bc682c8c36f7b27456bf830f404390e6c75a6be788890bc80035f122cae |

### Page mapping

| Printed folio | PDF index (zero-based) |
|---:|---:|
| 29 | 44 |
| 50 | 65 |
| 56 | 71 |
| 64 | 79 |
| 75 | 90 |
| 84 | 99 |
| 96 | 111 |
| 101 | 118 |
| 110 | 127 |
| 118 | 135 |
| 125 | 142 |
| 148 | 165 |
| 211 | 232 |
| 229 | 250 |
| 250 | 275 |

### Control

The N02 known-answer control normalized to "a good watch leaves the room ready for the next pair of hands" and produced HMAC16 BF889359B0303F2B2B2FD96AE841210B, matching the pinned control. Its HMAC16 SHA-256 is 47e787785ff25082b4b960ad415f1e030ae0edc89c38b2f61c48f9331282ea55, not the K08 target.

## N20/PS-0320 earlier-version control

Agent50 supplied the earlier-version PS-0320 control. Its retained row is ATTEMPT=1, STATE=ACK, CLASS=RECOVER, DEST=bench, payload 9B9D8D85D48AF325FF55556CE0AE7BF3. AES-128-ECB under the same K08 desk nonce decrypts it to 9266952F91A151BA399876EB5A0E83E2. The same two byte orientations and word bases 0/1 were applied, using both PDF text-layer and Tesseract OCR tokens.

The high-page/low-word orientation is incomplete in all four extraction/base combinations: its fourth pair requests word 186 on printed folio 81, where the body token counts are 154 (PDF text) and 155 (OCR). No offset or selector adjustment was attempted. The low-page/high-word orientation is complete in all four combinations and none matches K08:

| Word base | Extraction | Selected words | HMAC16 | SHA-256 of HMAC16 |
|---:|---|---|---|---|
| 0 | PDF text | mouth of to is entrance green Baltic of | EF559FAF75D8751635FEDF7E74A1EB52 | ee294d2788697e1133828b4388fd345f2a06a3ea83e6fe00ce972d701befbe6e |
| 0 | OCR | mouth myself travel always entrance green described of | 116D4BD7C462997A7AB61212FEF11BF1 | 430bdc00111be5ff4edc401e33cd93466b3d8e0bf972bb4d05f35a9e848752fc |
| 1 | PDF text | its ashamed yacht There the dark the side | 0C377CF365E5BEF1559DA2779A182D2F | f07ee484684cd5869021f276011b6c3f96f5cba09cdf9f583a3f57aaddcfd687 |
| 1 | OCR | its of to is the dark and side | EDBB26BCEF49421B540DEDE65FA9D51E | adb99daf7ad2bbbd3af951ffccd0f3b8c4a06e6dbd89c6c42f4958ff8fe53cc0 |

The N20 folio map is: 14→27, 47→62, 57→12, 81→96, 90→105, 102→119, 118→135, 131→148, 145→162, 146→163, 149→166, 152→169, 161→178, 186→203, 226→247, 235→256 (PDF indices zero-based). Folios 14, 81 and 161 were visually resolved from the page images because the text layer produced ambiguous hits or OCR read “161” as “IGl”; the remaining folios had unique standalone text-layer hits.

This is an earlier-version negative control, not a candidate search to expand. The control script is agents/agent12/k08_ps0320_aes_u8_pageword_control.py. It produced four complete and four incomplete combinations, with zero K08 commitment matches.

## Reproduction

Run:

    python agents/agent12/k08_ps0323_aes_u8_pageword_falcon.py --pdf /path/to/falcononbalticc00knig.pdf --output /tmp/ps0323-aes-u8-pageword.json

For a local copy of the extracted archive, add --root /path/to/extracted-Bundle06. The script pins the PS-0323 row, desk nonce, PDF SHA-256, K08 commitment and N02 control. It checks that every requested printed folio has exactly one standalone text-layer hit and preserves selected-word contexts for all eight outputs. Dependencies: cryptography, PyMuPDF, Pillow, pytesseract and Tesseract.

## Interpretation and boundary

This closes only the four predeclared AES/u8 page-word views against this particular public scan, using both text-layer and OCR token streams. It does not test workbook cells, another book/edition, alternate AES modes, other coordinate grammars, or other source objects. Do not widen the family.

The result does not authenticate the PS-0323-to-envelope join or the public scan as David's physical copy. No K08 component was recovered or promoted. The original recovery-envelope face, N23 margin/underleaf, source-linked photo-caption archive, or authenticated native PS-0323 document/render remains necessary for source authentication and exact final wording.
