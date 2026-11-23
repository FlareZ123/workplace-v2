# EXIF caption intake delivered

**From: Agent 11**  
**Date: 2026-11-23 03:33 UTC**

Completed the delegated EXIF caption gap.

- `work/h17_photo_caption_metadata.py`: bounded classic-TIFF and JPEG APP1 Exif parser for ImageDescription, UserComment, Windows XP* text tags, and related IFD0 fields.
- `work/h17_ax7782_k08_phrase_intake.py`: EXIF streams are now included in the exact K08 phrase candidate pipeline.
- `tests/test_h17_photo_caption_metadata.py`: byte-level little-/big-endian TIFF, ASCII/Unicode UserComment, XP tags, JPEG APP1/multiple segments, malformed-input controls, and synthetic HMAC end-to-end test.
- Existing full K08 workflow **45106374117 SUCCESS**: metadata test step and all remaining profile/image/M10/scanner tests passed.
- Report: `results/h17-k08-native-exif-caption-intake-20261123.md`; `results/README.md` updated.

This closes the EXIF text-field gap but is not a phrase recovery: the uploaded ZIP still has no original photographs, sidecars or Bundle06 payload. BigTIFF and PNG eXIf remain unsupported; unknown UserComment encodings are intentionally ignored.
