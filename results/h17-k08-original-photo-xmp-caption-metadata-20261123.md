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


## 23 November: native XMP editor layers and genuine IPTC APP13 repair

**Decision:** keep the original-photo intake path available, now with two corrected representations and a passing targeted native-metadata test. This is a source-reader improvement, not an eighth accepted archive component.

The original XMP reader recognized XML *child elements*, but RDF/XML also permits ordinary simple-property values as **attributes on `rdf:Description`**. Added namespaced attribute extraction for the established caption, attribution and date fields, each with an explicit `:attribute` source label. Added `photoshop:TextLayers` extraction of complete `photoshop:LayerText` from each `rdf:li` and its associated `photoshop:LayerName`, accepting element and RDF property-attribute forms. Layers are emitted separately: a named "final" layer is *a source label*, not proof of which version Emily put on the keeper envelope.

A source-reading blocker was also found in the initial IPTC-IIM/Photoshop APP13 implementation:
1. The outer scan for `Photoshop 3.0` did not advance its search offset, causing an infinite loop whenever the marker was found. This explains repeated manually dispatched CI test cancellations.
2. The marker and text-trim literals had accidentally doubled escape backslashes, so the code recognized a literal text `\\x00` instead of the actual zero byte in native Photoshop APP13 data; its synthetic JPEG fixture repeated the same error.
3. Corrected the binary byte escape literals, advanced the scanner after each marker and bounded resource traversal before the next Photoshop section. Test fixtures now construct real JPEG APP13 marker/length bytes, IPTC 0x1c datasets and 8BIM resource blocks; the two-segment test requires exactly one set of captions per section. The source parser never modifies the input.

**Validation:** manual-only, focused `suite=metadata` GitHub Actions run [45104653673](https://github.com/FlareZ123/workplace-v2/actions/runs/45104653673) completed **SUCCESS** at commit `e29db0387e70591d29d0884e21d79cc967f25009`, testing `tests/test_h17_photo_caption_metadata.py`. This is a synthetic **parser and intake control PASS**. The optional image, workbook and profile test groups were intentionally skipped in this targeted run; earlier broad invocations 45103038891 and 45104072786 were canceled before the parser repair, not source negatives.

**Historical evidence boundary:** the supplied 46-file ZIP has no original 2026 photo, XMP sidecar or Photoshop editing document. Consequently there is **no genuine K08 phrase emitted, no original K08 acceptance check, and no change to the six-PASS / two-MISSING REC8/1 status**. To use the new pathway, an independently authorized original photo/catalogue/sidecar must be present, and a contemporaneous envelope-fidelity source must identify Emily's actual final phrase among its drafts and layers. Do not regenerate a historical caption from synthetic fixtures.


**End-to-end follow-up, 03:17 UTC:** added an additional real-byte JPEG APP13 assertion that `iter_text_streams`, the existing exact K08 scanner's input layer, emits the complete `iptc:CaptionAbstract` from a synthetic Photoshop segment. Focused metadata run [45104837306](https://github.com/FlareZ123/workplace-v2/actions/runs/45104837306) completed **SUCCESS** at `ecf0e75ac55aaec71f573b06e44380335e3883b8`. Thus the native JPEG → IPTC property → exact phrase-candidate stream integration is exercised, and still no historical source item or genuine K08 commitment match is implied.
