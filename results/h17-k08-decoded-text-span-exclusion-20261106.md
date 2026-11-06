# K08 decoded-text span exclusion

**Date:** 6 November 2026  
**Investigator:** Agent 49  
**Question:** Could the missing K08 phrase be present in the surviving export in a common encoded textual form that the raw UTF-8 span scan would miss?

## Method

The uploaded archive contained 46 file entries. Forty-four entries decoded as UTF-8. The scan constructed unique normalized text variants using:

- raw UTF-8 text;
- HTML entity decoding;
- URL percent decoding, including HTML-then-URL decoding;
- JSON parsing and reserialization for JSON files;
- printable UTF-8 recovered from Base64 and hexadecimal candidate strings.

For each normalized text variant, every contiguous span of 1–32 words was tested through the original K08 candidate-component and SHA-256 acceptance path. No nonce or target digest is reproduced here.

A notebook execution against the uploaded ZIP produced:

| Measure | Result |
|---|---:|
| File entries | 46 |
| UTF-8-decodable files | 44 |
| Unique normalized text variants | 47 |
| Printable Base64 payloads recovered | 0 |
| Printable hexadecimal payloads recovered | 0 |
| Contiguous spans tested | 539,424 |
| Original K08 commitment matches | **0** |

The earlier raw-text-only scan tested 503,520 contiguous spans and also found zero matches.

## Finding

The exact K08 phrase does not appear as a contiguous 1–32-word span in the uploaded export after the common text-decoding layers above. There were no printable Base64 or hexadecimal payloads to expand into another text layer.

This strengthens the exclusion of direct textual reuse. It does not rule out arbitrary encrypted or binary print payloads, images, a physical photograph/caption, an omitted version record, the missing R-drive incident index, or a phrase assembled through non-contiguous edits.

## Reproduction

The scanner is preserved at [`agents/agent49/k08_decoded_span_scan.py`](../agents/agent49/k08_decoded_span_scan.py). It can scan the repository's extracted evidence tree by default, or an archive supplied with `--archive`.

The R-drive index reference `R:/Records/INDEX/IR-261003-H17.txt` is already documented as missing in [`h17-missing-evidence-request.md`](h17-missing-evidence-request.md); this result does not repeat that request.

## Consequence

Do not spend further compute on raw/HTML/URL/JSON/Base64/hex contiguous-span scans of this export. If the sentence-free positive controls also fail, prioritize the selected-version or physical-source witness over another generative search.
