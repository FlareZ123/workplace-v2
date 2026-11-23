import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "work"
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

from work.h17_ax7782_k08_phrase_intake import iter_text_streams
from work.h17_photo_caption_metadata import iter_xmp_caption_units
if str(WORK_DIR) in sys.path:
    sys.path.remove(str(WORK_DIR))


XMP = b"""<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
 xmlns:xmp="http://ns.adobe.com/xap/1.0/">
 <rdf:RDF><rdf:Description>
  <dc:description><rdf:Alt>
   <rdf:li xml:lang="x-default">The sea keeps a place for every voice.</rdf:li>
   <rdf:li xml:lang="en-US">The sea keeps a place for every voice.</rdf:li>
  </rdf:Alt></dc:description>
  <dc:title><rdf:Alt><rdf:li xml:lang="x-default">Night watch photograph</rdf:li></rdf:Alt></dc:title>
  <dc:creator><rdf:Seq><rdf:li>Emily</rdf:li></rdf:Seq></dc:creator>
  <photoshop:Headline>Keeper envelope caption draft</photoshop:Headline>
  <xmp:CreateDate>2026-10-02T17:45:00Z</xmp:CreateDate>
 </rdf:Description></rdf:RDF>
</x:xmpmeta>"""


class PhotoCaptionMetadataTests(unittest.TestCase):
    def test_sidecar_extracts_caption_fields_and_language_labels(self):
        streams = list(iter_xmp_caption_units("desk-photo.xmp", XMP))
        by_label = {label: text for label, text in streams}
        descriptions = [text for label, text in streams if "dc:description" in label]
        self.assertEqual(len(descriptions), 2)
        self.assertTrue(all(text == "The sea keeps a place for every voice."
                            for text in descriptions))
        self.assertTrue(any("lang-x-default" in label for label in by_label))
        self.assertTrue(any("lang-en-US" in label for label in by_label))
        self.assertIn("Emily", [text for label, text in streams if "dc:creator" in label])
        self.assertIn("Keeper envelope caption draft",
                      [text for label, text in streams if "photoshop:Headline" in label])

    def test_embedded_xmp_packet_is_extracted_from_image_bytes(self):
        image_bytes = b"JPEG-PREFIX\xff\xd8" + XMP + b"JPEG-SUFFIX\xff\xd9"
        streams = list(iter_xmp_caption_units("desk-photo.jpg", image_bytes))
        self.assertTrue(any("dc:description" in label for label, _ in streams))

    def test_k08_intake_emits_structured_xmp_source_streams(self):
        streams = list(iter_text_streams("desk-photo.xmp", XMP, 0, [0], [], None, None, []))
        self.assertTrue(any("xmp:dc:description" in label and
                            text.decode("utf-8") == "The sea keeps a place for every voice."
                            for label, text in streams))

    def test_unrelated_or_malformed_data_produces_no_caption_fields(self):
        self.assertEqual(list(iter_xmp_caption_units("ordinary.txt", b"just words")), [])
        self.assertEqual(list(iter_xmp_caption_units("broken.xmp", b"<x:xmpmeta>")), [])


if __name__ == "__main__":
    unittest.main()
