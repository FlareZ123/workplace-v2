# K08 Cowper Part II word-103 extraction (7 November 2026)

<badge>Partial extraction only</badge>

## Question

Can the five frozen South/L-29/S page positions in the Cowper *Sailing Tours* Part II candidate be read from an actual scan, using the specified one-based main-body word-103 rule?

## Source and reproducibility

The five page images were obtained through the signed Google Books image route and committed under `results/assets/cowper/part2-1893/`. The capture run is [42359316215](https://github.com/FlareZ123/workplace-v2/actions/runs/42359316215). The page manifest pins the image byte counts and SHA-256 values; its SHA-256 is `53095c33247e18913183e5174bd084e82803cb90b607ebdb2c84ecb1ffdbad`.

The extraction is reproducible with:

- `agents/agent24/cowper_part2_word103_ocr.py`
- `.github/workflows/agent24-cowper-part2-word103.yml`
- Successful extraction run: [42360543412](https://github.com/FlareZ123/workplace-v2/actions/runs/42360543412)
- Machine-readable output: [word103-ocr.json](assets/cowper/part2-1893/word103-ocr.json)

OCR engine: Tesseract 5.5.0, English, page segmentation mode 6. Each image was pinned against the manifest before OCR.

## Declared counting convention

- Count main-body text in visual reading order.
- Exclude running heads, printed folios and the Google watermark.
- Include visible body headings, captions, tables and footnotes.
- Join line-wrap hyphenation across a line break. Retain genuine in-line hyphenated compounds as one word. Count dotted abbreviations and fractions as one visual word token.
- Select token 103, one-based, from each page.
- Concatenate the selected words in the frozen binder-tab order.
- Apply the unchanged K08 normalization once to that resulting phrase: lowercase; replace characters other than ASCII letters, digits and whitespace with spaces; collapse whitespace; trim.

The initial OCR attempt normalized each page before selecting token 103. That reversed the specified operation order and is explicitly superseded in the JSON and Git history. Do not use its earlier fragment.

## Result

Frozen South binder-tab order:

| Printed page | Word 103 | Context tokens 97–109 |
| ---: | --- | --- |
| 130 | **Solent** | End and we are outside the Solent Hurst Lights There are two fixed |
| 151 | **yards** | Southampton or Portsmouth There are many yards to choose from But if we |
| 121 | **pleasant** | sea being short and spiteful For pleasant sailing however we know of no |
| 135 | **the** | deck and admire the loveliness of the place On our south side the |
| 142 | **even** | distance of half a mile or even nearer Rocks lie out all along |

The five selected words in order are:

`Solent / yards / pleasant / the / even`

After applying K08 normalization once to this five-word fragment:

`solent yards pleasant the even`

## Interpretation and limits

This is a successful **Part II source extraction**, not a K08 recovery. The five-word fragment is not independently evidence of the final caption. The five North/Part I words are still missing, so the complete ten-word candidate cannot yet be assembled and no K08 HMAC or acceptance test has been run.

The page images and OCR context were visually checked around the selected locations; page 121 and page 151 were manually counted to verify the apostrophe and line-wrap-hyphen handling. The remaining three positions should receive the same direct visual review before a complete phrase is tested.

## Next discriminating action

Recover the exact 1892 Part I pages from an authorized scan or the David-owned physical copy, preserve the title-page imprint and page labels, then apply this same declared convention to the frozen North page order. Concatenate North then South and test the K08 HMAC once. Do not change edition, page order, offset, tokenization or phrase wording to obtain a match.
