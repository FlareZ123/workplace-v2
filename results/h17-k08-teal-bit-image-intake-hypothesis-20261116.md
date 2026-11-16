# K08 teal/blue image-bit intake hypothesis (2026-11-16)

## Status

Exploratory only. No K08 phrase recovered and no claim is made that the image carrier exists.

## Motivation

The current desk-note material includes a photograph reference (N10), water/colour language (N08), a chipped blue mug and shelf reference (N11), and a phrase brief explicitly involving the sea and the end of the night (N20). The K08 source rule uses a keeper's desk phrase associated with notes and photograph captions. Separately, a post-hoc first-word selection has been observed to spell `ATEALBIT`. That selection is not authenticated and may be coincidental; it is not treated as a phrase or as proof of a steganographic channel.

A distinct testable interpretation is that the missing desk photograph or its profile copy contains a low-bit colour-channel payload, especially in green/blue (teal) channels. This is deliberately separate from the previously exhausted bit-plane tests on printer-spool payload bytes.

## Tool

Added `work/h17_k08_teal_bit_image_scan.py`. It is read-only and scans caller-supplied images for candidate ASCII/UTF-16 text in a bounded set of G/B/H/A bit-plane layouts, bit alignments, packing orders, and simple channel combinations. Every candidate is checked against the actual K08 HMAC and slot commitment; it emits candidate wording only on an exact match.

Added `tests/test_h17_k08_teal_bit_image_scan.py`, which embeds a known phrase in a synthetic green-channel LSB PNG and verifies exact recovery. Local test: `1 passed`.

Example use after an authorized image/profile package is supplied:

```bash
python work/h17_k08_teal_bit_image_scan.py \
  --images /path/to/authorized/profile/photos \
  --evidence-root resources/evidence
```

## Limitation and next action

The supplied archive has no relevant crew/desk photographs. The supplemental BX25 PDF has no embedded image payload, and the only repository images are unrelated book-page scans. Therefore the scanner has not been run against the target carrier.

Run this only if an authorized copy of the original desk photograph/profile photo archive becomes available. If that source is not obtained, close this branch rather than expanding the bit-layout search speculatively. The existing `work/h17_profile_k08_phrase_scan.py` remains the text/OCR/metadata intake path; this script adds only the pixel-bitplane check.
