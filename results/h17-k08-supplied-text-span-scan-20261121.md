# K08 supplied-text corpus span scan — 21 November 2026

**Disposition:** bounded negative; no K08 phrase or component recovered.

## Scope and method

- Input: the exact uploaded `h17-archive-dump.zip`, SHA-256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`.
- Scanned all 41 text members with supported text extensions: Markdown, text, EML, logs, JSON/JSONL, CSV, HTML and INI.
- Corpus size after the routing-rule normalization: 16,626 words.
- Tested every contiguous span of 1–64 words within each file: **981,444 spans**.
- For each span, applied the exact K08 route: lowercase; replace characters outside ASCII a–z, digits and whitespace with spaces; collapse/trim whitespace; HMAC-SHA256 using the documented desk nonce as key; retain 16 bytes; SHA-256 and compare with the unchanged K08 slot commitment.
- Result: **zero commitment hits**.

The scan excluded `acceptance.json`, `candidate.json`, `candidate.template.json` and `verify.py` as non-source inputs. It listed but did not open or decompress `BX25-08.pdf`.

## Interpretation

This closes only the contiguous-phrase search over the supplied text corpus, up to 64 words. It does not test non-contiguous selections, phrases longer than 64 words, omitted quoted material, images, workbook cells/comments, native spool/rendered media, profile caches, or the missing physical envelope/margin/photo-caption carriers. A zero hit is not evidence that K08 is unrecoverable; it shows that the exact final wording is not present as a contiguous span in the scanned local text export.

Do not expand generic phrase searches over this same text corpus. The remaining useful K08 path is source-bearing recovery of Emily's final envelope/margin/photo-caption material, or an authenticated native print object whose manifest binds it to the final envelope. Respect the existing local-only acquisition boundary; do not access protected services or reopen the closed custodian channel.

## Reproduction

```sh
python work/h17_k08_supplied_text_span_scan.py /path/to/h17-archive-dump.zip
```

The scanner is standard-library-only and deliberately skips PDF and other binary/media carriers. It reports its coverage and exclusions rather than treating a zero-hit result as complete source intake.
