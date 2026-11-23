# K08 original-photo XMP/IPTC caption metadata intake (2026-11-23)

## Source basis

MAIL-11 says Emily used desk notes and photograph captions to work out the final keeper-envelope wording. MAIL-20 says several captions/drafts existed and only her final choice counts. The existing source request/issue also identifies original incident-period desk/crew photographs, photo catalogues, caption sidecars and IPTC/XMP/EXIF description fields as a distinct source class.

## Change

Added `work/h17_photo_caption_metadata.py` and integrated it into `work/h17_ax7782_k08_phrase_intake.py`. It extracts structured fields from XMP sidecars and embedded XMP packets in original image bytes, preserving field and language labels:
- `dc:description`, `dc:title`, `dc:creator`, `dc:subject`;
- Photoshop `Headline`, `CaptionWriter`, `Instructions`, `Credit`;
- XMP `Label`, `CreateDate`, `ModifyDate`;
- TIFF `DateTime`, EXIF `DateTimeOriginal`, and IPTC Core `Location`.

It also parses IPTC-IIM text datasets in Photoshop APP13 resources: Caption/Abstract, Headline, By-line, ObjectName, Keywords, DateCreated, TimeCreated, City, CountryName and CopyrightNotice. This is not OCR or a broad wordlist. It reads source-authored metadata fields and emits separately labelled text streams so the unchanged K08 HMAC scanner can test exact complete phrases.

## Validation

`tests/test_h17_photo_caption_metadata.py` covers XMP sidecar fields, language alternatives, embedded XMP inside image bytes, integration into the K08 intake, and malformed/unrelated data. The targeted K08 workflow is running the full regression suite plus workbook-selector and profile-scanner controls; record its result after completion.

## Limits

The supplied 46-file ZIP contains no original incident-period photographs or XMP sidecars. No K08 phrase or real metadata hit was recovered. This reader does not yet parse application-specific photo-project edit histories. A hit in a caption field remains a draft unless independently linked to Emily's final H-17 incident-envelope wording.

The next useful source is an already-authorized original photo/catalogue/sidecar set with preserved paths, hashes and timestamps. Do not substitute public reposts, resized thumbnails, or unrelated modern captions.

## Confidence

- **High:** the structured XMP field parser is covered by synthetic sidecar and embedded-packet controls.
- **None:** no real source photo or K08 phrase recovered in this run.
