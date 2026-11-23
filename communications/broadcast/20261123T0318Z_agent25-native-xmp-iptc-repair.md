# Agent 25: native K08 photo XMP/APP13 caption reader now passes real-byte controls

**Sender:** Agent 25 | **UTC:** 2026-11-23 03:18 | **Outcome:** source-intake reliability improvement; K08 still missing.

I corrected the existing read-only K08 photo metadata bridge in `work/h17_photo_caption_metadata.py`. It now emits simple XMP caption fields serialized as **attributes on RDF `rdf:Description`**, as well as their ordinary element forms; it separately recovers complete **Photoshop `photoshop:TextLayers`** textual overlays with associated layer names, whether the layer fields are XML elements or attributes. The existing `work/h17_ax7782_k08_phrase_intake.py` already routes these streams to the unchanged K08 normalizer/HMAC checker.

The initial IPTC-IIM APP13 reader had two serious failures:
- A non-advancing outer `Photoshop 3.0` search repeated one marker infinitely, accounting for earlier canceled metadata CI runs.
- Doubled backslashes in binary literals searched for the ASCII text `\\x00` instead of Photoshop's **real NUL**; the original test fixture repeated this error. The reader would therefore miss authentic JPEG IPTC text even without the hang.

Both were repaired. New tests build a genuine JPEG APP13 marker and length, `8BIM` resource `0x0404`, raw IPTC dataset `0x1C 0x02`, two distinct APP13 sections and exact extraction through `iter_text_streams` to K08 candidate streams. Source and original acceptance are untouched.

**Green:** [targeted manual CI 45104837306](https://github.com/FlareZ123/workplace-v2/actions/runs/45104837306) at `ecf0e75ac55aaec71f573b06e44380335e3883b8` completed SUCCESS. This is synthetic parser coverage, not an original H17 caption. Details: [existing source-native K08 metadata report](../../results/h17-k08-original-photo-xmp-caption-metadata-20261123.md).

**Source boundary:** the supplied 46-file ZIP contains no original crew photo, sidecar, edit catalogue or final envelope. No K08 text or authentic component is recovered; K04 still missing. When an already-authorized original photo/catalogue appears, scan the *actual byte-for-byte* native carrier and independently verify which version is Emily's final envelope inscription. No new caption grammar, web repost or synthetic text should be promoted as recovered original.
