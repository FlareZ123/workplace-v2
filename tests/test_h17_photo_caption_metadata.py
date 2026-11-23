import hashlib
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "work"
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

from work.h17_ax7782_k08_phrase_intake import iter_text_streams
from work.h17_photo_caption_metadata import iter_exif_caption_units, iter_iptc_caption_units, iter_xmp_caption_units
import work.h17_ax7782_k08_phrase_intake as phrase_intake
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
        datasets.append(b"\x1c\x02" + bytes([dataset]) +
                        len(value).to_bytes(2, "big") + value)
    iptc = b"".join(datasets)
    resource = (b"8BIM" + b"\x04\x04" + b"\x00\x00" +
                len(iptc).to_bytes(4, "big") + iptc +
                (b"\x00" if len(iptc) & 1 else b""))
    payload = b"Photoshop 3.0\x00" + resource
    return (b"\xff\xd8\xff\xed" + (len(payload) + 2).to_bytes(2, "big") +
            payload + b"\xff\xd9")


def _tiff_exif_fixture(endian="<", ifd0_fields=(), user_comment=None):
    """Build a minimal classic TIFF with optional ExifIFD UserComment."""
    type_sizes = {1: 1, 2: 1, 7: 1}
    ifd0_offset = 8
    entry_count = len(ifd0_fields) + (1 if user_comment is not None else 0)
    ifd0_table_end = ifd0_offset + 2 + 12 * entry_count + 4
    data_blob = bytearray()
    entries = []

    def entry(tag, field_type, raw):
        count = len(raw)
        size = count * type_sizes[field_type]
        if size <= 4:
            value_field = raw.ljust(4, b"\x00")
        else:
            value_offset = ifd0_table_end + len(data_blob)
            value_field = struct.pack(endian + "I", value_offset)
            data_blob.extend(raw)
        return struct.pack(endian + "HHI", tag, field_type, count) + value_field

    for tag, field_type, raw in ifd0_fields:
        entries.append(entry(tag, field_type, raw))

    exif_block = b""
    if user_comment is not None:
        exif_ifd_offset = ifd0_table_end + len(data_blob)
        exif_table_end = exif_ifd_offset + 2 + 12 + 4
        if len(user_comment) <= 4:
            value_field = user_comment.ljust(4, b"\x00")
            user_comment_data = b""
        else:
            value_field = struct.pack(endian + "I", exif_table_end)
            user_comment_data = user_comment
        user_comment_entry = (
            struct.pack(endian + "HHI", 0x9286, 7, len(user_comment)) + value_field
        )
        exif_block = (
            struct.pack(endian + "H", 1) + user_comment_entry
            + struct.pack(endian + "I", 0) + user_comment_data
        )
        entries.append(
            struct.pack(endian + "HHI", 0x8769, 4, 1)
            + struct.pack(endian + "I", exif_ifd_offset)
        )

    header = (b"II*\x00" if endian == "<" else b"MM\x00*") + struct.pack(endian + "I", ifd0_offset)
    ifd0 = struct.pack(endian + "H", entry_count) + b"".join(entries) + struct.pack(endian + "I", 0)
    return header + ifd0 + data_blob + exif_block


def _jpeg_app1_exif(tiff):
    payload = b"Exif\x00\x00" + tiff
    return b"\xff\xe1" + (len(payload) + 2).to_bytes(2, "big") + payload



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
        native_streams = list(iter_text_streams(
            "desk-photo.jpg", _iptc_jpeg(), 0, [0], [], False, None, []
        ))
        self.assertTrue(any(
            "/iptc:CaptionAbstract:" in label
            and payload.decode("utf-8") == "The sea keeps the voices after the last watch."
            for label, payload in native_streams
        ))

    def test_two_real_jpeg_app13_segments_are_read_once_each(self):
        jpeg = _iptc_jpeg()
        app13 = jpeg[2:-2]
        combined = b"\xff\xd8" + app13 + app13 + b"\xff\xd9"
        self.assertIn(b"Photoshop 3.0\x00", combined)
        streams = list(iter_iptc_caption_units("two-segment.jpg", combined))
        self.assertEqual(len(streams), 6)
        captions = [text for label, text in streams if "CaptionAbstract" in label]
        self.assertEqual(
            captions, ["The sea keeps the voices after the last watch."] * 2
        )

    def test_unrelated_or_malformed_data_produces_no_caption_fields(self):
        self.assertEqual(list(iter_xmp_caption_units("ordinary.txt", b"just words")), [])
        self.assertEqual(list(iter_xmp_caption_units("broken.xmp", b"<x:xmpmeta>")), [])


    def test_tiff_extracts_image_description_windows_xp_and_unicode_usercomment(self):
        tiff = _tiff_exif_fixture(
            "<",
            [
                (0x010E, 2, b"The sea keeps a place for every voice.\x00"),
                (0x9C9B, 1, "Night watch photograph".encode("utf-16le") + b"\x00\x00"),
                (0x9C9C, 1, "A place for one more".encode("utf-16le") + b"\x00\x00"),
                (0x9C9D, 1, "Emily".encode("utf-16le") + b"\x00\x00"),
                (0x9C9E, 1, "sea;watch;table".encode("utf-16le") + b"\x00\x00"),
                (0x9C9F, 1, "After the long watch".encode("utf-16le") + b"\x00\x00"),
            ],
            b"UNICODE\x00" + "the water outside".encode("utf-16le") + b"\x00\x00",
        )
        streams = list(iter_exif_caption_units("desk-photo.tif", tiff))
        values = {label.split(":")[2]: text for label, text in streams}
        self.assertEqual(values["ImageDescription"], "The sea keeps a place for every voice.")
        self.assertEqual(values["XPTitle"], "Night watch photograph")
        self.assertEqual(values["XPComment"], "A place for one more")
        self.assertEqual(values["XPAuthor"], "Emily")
        self.assertEqual(values["XPKeywords"], "sea;watch;table")
        self.assertEqual(values["XPSubject"], "After the long watch")
        self.assertEqual(values["UserComment"], "the water outside")
        self.assertTrue(any("ifd0:tag-0x010E:encoding-ascii" in label for label, _ in streams))
        self.assertTrue(any("exif-ifd:tag-0x9286:encoding-utf-16le" in label for label, _ in streams))

    def test_big_endian_tiff_decodes_unicode_usercomment_in_tiff_byte_order(self):
        tiff = _tiff_exif_fixture(
            ">",
            [(0x010E, 2, b"Late watch at first light\x00")],
            b"UNICODE\x00" + "the sea is quiet".encode("utf-16be") + b"\x00\x00",
        )
        streams = list(iter_exif_caption_units("desk-photo-big-endian.tif", tiff))
        self.assertIn(("exif:tiff:ImageDescription:ifd0:tag-0x010E:encoding-ascii",
                       "Late watch at first light"), streams)
        self.assertIn(("exif:tiff:UserComment:exif-ifd:tag-0x9286:encoding-utf-16be",
                       "the sea is quiet"), streams)

    def test_usercomment_ascii_designator_is_decoded(self):
        tiff = _tiff_exif_fixture(
            "<", [], b"ASCII\x00\x00\x00" + b"the last watch\x00"
        )
        streams = list(iter_exif_caption_units("desk-photo.tif", tiff))
        self.assertIn(("exif:tiff:UserComment:exif-ifd:tag-0x9286:encoding-ascii",
                       "the last watch"), streams)

    def test_jpeg_app1_exif_caption_reaches_k08_phrase_stream_and_hmac(self):
        phrase = "The sea keeps a place for every voice."
        nonce = bytes(range(16))
        target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()
        tiff = _tiff_exif_fixture(
            "<", [(0x010E, 2, phrase.encode("ascii") + b"\x00")]
        )
        jpeg = b"\xff\xd8" + _jpeg_app1_exif(tiff) + b"\xff\xd9"
        native_streams = list(iter_text_streams(
            "desk-photo.jpg", jpeg, 0, [0], [], False, None, []
        ))
        self.assertTrue(any(
            "exif:jpeg-app1-0:ImageDescription" in label
            and payload.decode("utf-8") == phrase
            for label, payload in native_streams
        ))
        hits = []
        for source, payload in native_streams:
            for label, text in phrase_intake.decode_text_variants(payload, source):
                phrase_intake.scan_phrase_spans(
                    text, nonce, target, source + " [" + label + "]", 16, hits
                )
        self.assertTrue(any(hit["normalized_phrase"] == phrase.lower() for hit in hits))

    def test_multiple_jpeg_exif_app1_segments_keep_distinct_source_labels(self):
        first = _tiff_exif_fixture("<", [(0x010E, 2, b"First caption\x00")])
        second = _tiff_exif_fixture("<", [(0x010E, 2, b"Second caption\x00")])
        jpeg = b"\xff\xd8" + _jpeg_app1_exif(first) + _jpeg_app1_exif(second) + b"\xff\xd9"
        streams = list(iter_exif_caption_units("two-exif-segments.jpg", jpeg))
        self.assertIn(("exif:jpeg-app1-0:ImageDescription:ifd0:tag-0x010E:encoding-ascii",
                       "First caption"), streams)
        self.assertIn(("exif:jpeg-app1-1:ImageDescription:ifd0:tag-0x010E:encoding-ascii",
                       "Second caption"), streams)

    def test_malformed_tiff_offsets_truncated_jpeg_and_unknown_usercomment_fail_closed(self):
        bad_tiff = b"II*\x00" + struct.pack("<I", 0xFFFFFFFF)
        truncated_jpeg = b"\xff\xd8\xff\xe1\x00\x20Exif\x00\x00"
        unknown_comment = _tiff_exif_fixture("<", [], b"UNKNOWN!!" + b"binary")
        self.assertEqual(list(iter_exif_caption_units("bad.tif", bad_tiff)), [])
        self.assertEqual(list(iter_exif_caption_units("bad.jpg", truncated_jpeg)), [])
        self.assertEqual(list(iter_exif_caption_units("unknown.tif", unknown_comment)), [])
        self.assertEqual(list(iter_exif_caption_units("ordinary.bin", b"not an image")), [])



if __name__ == "__main__":
    unittest.main()
