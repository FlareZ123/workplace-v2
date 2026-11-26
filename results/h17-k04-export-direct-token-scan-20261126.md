# K04 supplied-export direct 16-byte representation scan

## Question

Does the supplied local export already contain a complete 16-byte K04 component or payload in a directly represented binary/text form, even though the selected PS-0417 ACK2 row does not satisfy the commitment?

## Method

For every non-PDF member of the supplied archive, scan every raw 16-byte window and each standalone 16-byte representation recognized by the exact-token scanner in [h17_k04_binary_window_intake.py](../work/h17_k04_binary_window_intake.py). For each decoded 16-byte block B, test both:

- `SHA256(B) == K04 commitment` (direct component);
- `SHA256(B XOR route_mask) == K04 commitment` (source payload under the published route rule).

Recognized textual encodings were ASCII 32-hex, UTF-16LE/BE 32-hex, grouped hex byte pairs, strict Base64, RFC UUID, Windows GUID byte order, Base32, and Base64URL. Raw byte windows were scanned at stride 1. No heuristic transformations or candidate generation were used.

The quarantined PDF member was excluded by filename **without reading it**. No PDF text, image, embedded file, or derivative was accessed.

## Scope and result

<badge color="success">No direct or masked hits</badge>

- Archive members: 46 total; 45 non-PDF members scanned.
- Bytes scanned: 112,866.
- Member types scanned: 20 EML, 7 TXT, 4 LOG, 3 JSONL, 3 JSON, 2 Markdown, 2 HTML, 1 Python, 1 INI, 1 CSV, and 1 RAW.
- PDF members skipped without reading: 1.
- Direct-component commitment hits: 0.
- Payload-XOR-route-mask commitment hits: 0.

The scan did not emit or persist candidate bytes, the route mask, or any derived component.

## Interpretation and limits

This closes only direct 16-byte representations and the listed standard encodings within the 45 non-PDF members of this supplied export. It does not inspect or exclude absent native SPL/SHD spool files, OLE/CFB workbooks, XPS/EMF/PCL streams, image sources, the original physical coupon, the missing monthly consumables return, or any other source object not present in the archive. It does not alter the K04 route rule or acceptance state.

The full native intake tool remains the appropriate path if an authorized original source object is later supplied. The current export itself contains no directly represented K04 component or masked payload under the tested encodings.
