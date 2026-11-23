import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "work"
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

from work.h17_ax7782_k08_phrase_intake import iter_text_streams
from work.h17_photo_caption_metadata import iter_iptc_caption_units, iter_xmp_caption_units
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


def _iptc_jpeg():
    datasets = []
    for dataset, text in [
        (120, "The sea keeps the voices after the last watch."),
        (105, "Keeper envelope caption"),
        (80, "Emily"),
    ]:
        value = text.encode("utf-8")
        datasets.append(b"\\x1c\\x02" + bytes([dataset]) +
                        len(value).to_bytes(2, "big") + value)
    iptc = b"".join(datasets)
    resource = (b"8BIM" + b"\\x04\\x04" + b"\\x00\\x00" +
                len(iptc).to_bytes(4, "big") + iptc +
                (b"\\x00" if len(iptc) & 1 else b""))
    return b"\\xff\\xd8" + b"Photoshop 3.0\\x00" + resource + b"\\xff\\xd9"


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

    def test_rdf_description_property_attributes_reach_k08_intake(self):
        # RDF/XML property attributes are a standard XMP serialization form.
        # This would previously have produced no structured caption streams.
        xmp = b'''<x:xmpmeta xmlns:x="adobe:ns:meta/"
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:dc="http://purl.org/dc/elements/1.1/"
          xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
          xmlns:xmp="http://ns.adobe.com/xap/1.0/">
          <rdf:RDF><rdf:Description rdf:about=""
            photoshop:Headline="The sea keeps a place for every voice."
            dc:description="After the long watch, there is a place for everyone."
            photoshop:CaptionWriter="Emily"
            xmp:ModifyDate="2026-10-02T17:45:00Z"
          /></rdf:RDF></x:xmpmeta>'''
        streams = list(iter_xmp_caption_units("photo.xmp", xmp))
        expected = {
            "photoshop:Headline": "The sea keeps a place for every voice.",
            "dc:description": "After the long watch, there is a place for everyone.",
            "photoshop:CaptionWriter": "Emily",
            "xmp:ModifyDate": "2026-10-02T17:45:00Z",
        }
        for field, value in expected.items():
            self.assertTrue(any(
                field in label and ":attribute:" in label and text == value
                for label, text in streams
            ), (field, streams))
        intake = list(iter_text_streams("photo.xmp", xmp, 0, [0], [], None, None, []))
        for field, value in expected.items():
            self.assertTrue(any(
                "xmp:" + field in label and payload == value.encode("utf-8")
                for label, payload in intake
            ), (field, intake))

    def test_photoshop_text_layers_preserve_full_words_and_layer_names(self):
        # Adobe's Photoshop TextLayers caches authored text independently of
        # IPTC dc:description and may contain multiple editorial versions.
        xmp = b'''<x:xmpmeta xmlns:x="adobe:ns:meta/"
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/">
          <rdf:RDF><rdf:Description rdf:about="">
            <photoshop:TextLayers><rdf:Seq>
              <rdf:li rdf:parseType="Resource">
                <photoshop:LayerName>Keeper envelope final</photoshop:LayerName>
                <photoshop:LayerText>The sea keeps a place for every voice.</photoshop:LayerText>
              </rdf:li>
              <rdf:li rdf:parseType="Resource"
                photoshop:LayerName="Older draft"
                photoshop:LayerText="Leave the light on for the next watch." />
            </rdf:Seq></photoshop:TextLayers>
          </rdf:Description></rdf:RDF>
        </x:xmpmeta>'''
        expected = [
            ("name-Keeper_envelope_final", "The sea keeps a place for every voice."),
            ("name-Older_draft", "Leave the light on for the next watch."),
        ]
        layers = [
            (label, text) for label, text in iter_xmp_caption_units("photo.xmp", xmp)
            if "photoshop:TextLayers" in label
        ]
        self.assertEqual(len(layers), 2)
        for (part, text), (label, actual) in zip(expected, layers):
            self.assertIn(part, label)
            self.assertEqual(actual, text)
        intake = [
            (label, payload) for label, payload in
            iter_text_streams("photo.xmp", xmp, 0, [0], [], None, None, [])
            if "photoshop:TextLayers" in label
        ]
        self.assertEqual(
            [(label.removeprefix("photo.xmp!/"), payload.decode("utf-8"))
             for label, payload in intake],
            layers,
        )

    def test_iptc_app13_extracts_caption_headline_and_byline(self):
        streams = list(iter_iptc_caption_units("desk-photo.jpg", _iptc_jpeg()))
        by_label = {label: text for label, text in streams}
        self.assertIn("The sea keeps the voices after the last watch.",
                      [text for label, text in streams if "CaptionAbstract" in label])
        self.assertIn("Keeper envelope caption",
                      [text for label, text in streams if "Headline" in label])
        self.assertIn("Emily", [text for label, text in streams if "ByLine" in label])

    def test_unrelated_or_malformed_data_produces_no_caption_fields(self):
        self.assertEqual(list(iter_xmp_caption_units("ordinary.txt", b"just words")), [])
        self.assertEqual(list(iter_xmp_caption_units("broken.xmp", b"<x:xmpmeta>")), [])


if __name__ == "__main__":
    unittest.main()
