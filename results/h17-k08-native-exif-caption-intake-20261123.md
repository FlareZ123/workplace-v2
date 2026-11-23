# Native EXIF caption intake for K08

**Agent 11 | 23 November 2026 | Source-intake improvement; no K08 phrase recovered.**

## Gap addressed

The existing original-photo reader already extracted XMP and Photoshop IPTC-IIM caption fields, but did not read native TIFF/EXIF text fields. A photograph can carry authored wording in EXIF even when XMP and IPTC are absent.

## Implementation

Added `iter_exif_caption_units` to `work/h17_photo_caption_metadata.py` and wired it into `iter_text_streams` in `work/h17_ax7782_k08_phrase_intake.py`.

Supported carriers and fields:

- Classic TIFF files and JPEG APP1 segments containing `Exif\0\0`.
- IFD0 text fields: `DocumentName`, `ImageDescription`, `PageName`, `Artist`, `Copyright`.
- Windows XP text fields: `XPTitle`, `XPComment`, `XPAuthor`, `XPKeywords`, `XPSubject`.
- ExifIFD `UserComment` with the standard ASCII, UNICODE and JIS designators; Unicode byte order follows the TIFF header unless a BOM is present.

The parser is read-only and bounded: it validates classic-TIFF headers, IFD table bounds, entry counts, value offsets and text sizes; follows only the IFD0 ExifIFD pointer; stops JPEG marker parsing at SOS/EOI; and fails closed on unknown UserComment encodings. Labels preserve carrier segment, field, IFD, tag ID and decoding. No OCR or free-form binary string scraping was added.

## Validation

The existing K08 profile/intake workflow was run against this commit:

- [Full K08 metadata/profile intake run 45106374117](https://github.com/FlareZ123/workplace-v2/actions/runs/45106374117) — **SUCCESS**.
- The `test_h17_photo_caption_metadata.py` step passed, including new byte-level controls for little- and big-endian TIFF, ImageDescription, XP* fields, ASCII and Unicode UserComment, JPEG APP1 extraction, multiple APP1 segments, malformed offsets, truncated JPEG and unknown UserComment encodings.
- The end-to-end control sends a synthetic JPEG EXIF ImageDescription through `iter_text_streams`, normalizes it under the original K08 rule, and verifies the synthetic HMAC commitment hit. The full workflow also passed the existing profile/thumbnail, teal-bit image, M10 workbook selector and scanner self-tests.

These are synthetic fixture controls, not an original-photo hit. The supplied 46-member ZIP contains no original photographs or sidecars, so the new path does not recover Emily's final phrase and does not alter the K08 candidate or acceptance commitment.

## Limits

- Classic TIFF/EXIF and JPEG APP1 are covered; BigTIFF and PNG eXIf chunks are not.
- Unknown UserComment encodings are deliberately ignored rather than guessed.
- No original photo, sidecar, workbook, envelope or profile-refresh package was present to test against.
- This closes a parser-coverage gap only; it does not establish authorship or final-version status for any future caption field.

## Reproduction

Run the existing workflow with `suite=full`:

`.github/workflows/agent25-k08-profile-thumbcache-manual.yml`

Tests: `tests/test_h17_photo_caption_metadata.py`.
