# BX25-08 PDF release setting

- Source: `evidence/h17-supplemental-office-files/BX25-08.pdf` from the supplied archive dump.
- Release setting: `8131`.
- Basis: `retired-office-bookmarks.html` explicitly says BX25 folios were stored with a four-position numeric release setting. The PDF's encryption dictionary is AES-256 (V=5, R=6). A bounded search of the 0000-9999 setting space using pypdf found 8131; `PdfReader.decrypt` returned a valid user-password result.
- Do not assume this setting unlocks other files. It is pinned only to BX25-08.pdf.
- The decrypted page identifies the A3 North office equipment folio, FA-17 and FA-18 asset descriptions, and the public correspondence-index URL. See `results/h17-bx25-08-property-annex-decryption-20261107.md`.
