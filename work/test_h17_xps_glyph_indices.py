#!/usr/bin/env python3
"""Tests for h17_xps_glyph_indices.py."""
from __future__ import annotations

import io
import sys
import unittest
import uuid
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_xps_glyph_indices as extractor

try:
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont
except ImportError:
    FontBuilder = None
    TTGlyphPen = None
    TTFont = None


def make_test_font(text: str, include_cmap: bool = True) -> bytes:
    chars = sorted(set(text))
    names = [".notdef", "space"] + [f"uni{ord(c):04X}" for c in chars if c != " "]
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder(names)
    cmap = {32: "space"}
    for char in chars:
        if char != " ":
            cmap[ord(char)] = f"uni{ord(char):04X}"
    builder.setupCharacterMap(cmap)
    glyf = {}
    for name in names:
        glyf[name] = TTGlyphPen(None).glyph()
    builder.setupGlyf(glyf)
    builder.setupHorizontalMetrics({name: (500, 0) for name in names})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable({
        "familyName": "H17 Test",
        "styleName": "Regular",
        "uniqueFontIdentifier": "H17 Test Font 1",
        "fullName": "H17 Test",
        "psName": "H17Test",
    })
    builder.setupOS2()
    builder.setupPost()
    builder.setupMaxp()
    output = io.BytesIO()
    builder.save(output)
    font_data = output.getvalue()
    if not include_cmap:
        font = TTFont(io.BytesIO(font_data))
        del font["cmap"]
        stripped = io.BytesIO()
        font.save(stripped)
        font.close()
        font_data = stripped.getvalue()
    return font_data


def make_xps(
    text: str,
    relative_uri: bool = False,
    cluster: bool = False,
    page_name: str = "1.fpage",
    include_cmap: bool = True,
    split_at: int | None = None,
    reverse_runs: bool = False,
) -> bytes:
    font_bytes = make_test_font(text, include_cmap=include_cmap)
    font_guid = str(uuid.uuid4())
    font_part = f"Resources/Fonts/{font_guid}.odttf"
    key = uuid.UUID(font_guid).bytes_le[::-1]
    obfuscated = bytearray(font_bytes)
    for i in range(32):
        obfuscated[i] ^= key[i % 16]

    font = TTFont(io.BytesIO(font_bytes))
    if include_cmap:
        cmap = font.getBestCmap()
        gids = [font.getGlyphID(cmap[ord(ch)]) for ch in text]
    else:
        gids = [font.getGlyphID("space" if ch == " " else f"uni{ord(ch):04X}") for ch in text]
    font.close()

    if cluster:
        glyph_runs = [(f"(2:1){gids[0]}", 10.0)]
    elif split_at is not None:
        glyph_runs = [
            (";".join(str(g) for g in gids[:split_at]), 10.0),
            (";".join(str(g) for g in gids[split_at:]), 100.0),
        ]
        if reverse_runs:
            glyph_runs.reverse()
    else:
        glyph_runs = [(";".join(str(g) for g in gids), 10.0)]

    page_part = f"Documents/1/Pages/{page_name}"
    if relative_uri:
        font_uri = f"../../../{font_part}"
    else:
        font_uri = f"/{font_part}"

    glyph_xml = "".join(
        f'<Glyphs FontUri="{font_uri}" FontRenderingEmSize="12" OriginX="{x}" OriginY="20" Indices="{indices}" />'
        for indices, x in glyph_runs
    )
    page = (
        '<FixedPage xmlns="http://schemas.microsoft.com/xps/2005/06" Width="816" Height="1056">'
        f'{glyph_xml}'
        '</FixedPage>'
    ).encode("utf-8")
    content_types = (
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        f'<Override PartName="/{page_part}" ContentType="application/vnd.ms-package.xps-fixedpage+xml" />'
        '</Types>'
    ).encode("utf-8")

    package = io.BytesIO()
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr(font_part, bytes(obfuscated))
        zf.writestr(page_part, page)
    return package.getvalue()


class GlyphIndexExtractionTests(unittest.TestCase):
    def test_parse_indices_preserves_cluster_metadata(self):
        parsed = extractor.parse_indices("(2:3)94;76;88;(2:1)162")
        self.assertEqual(parsed[0]["glyph_id"], 94)
        self.assertEqual(parsed[0]["cluster_code_units"], 2)
        self.assertEqual(parsed[0]["cluster_glyph_count"], 3)
        self.assertEqual(parsed[1]["glyph_id"], 76)

    def test_empty_cluster_defaults_to_one_to_one(self):
        parsed = extractor.parse_indices("()12")
        self.assertEqual(parsed[0]["cluster_code_units"], 1)
        self.assertEqual(parsed[0]["cluster_glyph_count"], 1)

    def test_glyph_metrics_do_not_change_glyph_ids(self):
        parsed = extractor.parse_indices("12,500,0,0;13,-10,1.5,0")
        self.assertEqual([item["glyph_id"] for item in parsed], [12, 13])

    def test_odttf_guid_key_byte_order_vector(self):
        guid = "00112233-4455-6677-8899-aabbccddeeff"
        part = f"Resources/Fonts/{guid}.odttf"
        expected_key = bytes.fromhex("FFEEDDCCBBAA99886677445500112233")
        self.assertEqual(uuid.UUID(guid).bytes_le[::-1], expected_key)
        original = bytes(range(64))
        obfuscated = bytearray(original)
        for i in range(32):
            obfuscated[i] ^= expected_key[i % 16]
        self.assertEqual(extractor.deobfuscate_odttf(bytes(obfuscated), part), original)

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_extracts_glyph_indices_from_obfuscated_font(self):
        phrase = "the sea is quiet"
        result = extractor.extract_xps_glyph_indices(make_xps(phrase))
        self.assertEqual(result["status"], "decoded")
        self.assertEqual(result["text"], phrase)
        self.assertEqual(result["runs"][0]["unresolved"], [])

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_glyph_name_fallback_when_cmap_is_missing(self):
        phrase = "named glyphs"
        result = extractor.extract_xps_glyph_indices(make_xps(phrase, include_cmap=False))
        self.assertEqual(result["text"], phrase)

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_scanner_compatible_stream_adapter(self):
        phrase = "the sea is quiet"
        streams = extractor.extract_xps_glyph_streams(
            make_xps(phrase, split_at=7, reverse_runs=True)
        )
        self.assertTrue(any(label.endswith("spatial-joined") and data.decode("utf-8") == phrase
                            for label, data in streams))

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_glyph_runs_join_and_spatial_order(self):
        phrase = "the sea is quiet"
        result = extractor.extract_xps_glyph_indices(make_xps(phrase, split_at=7, reverse_runs=True))
        joined = next(s["text"] for s in result["streams"] if s["label"] == "joined")
        spatial = next(s["text"] for s in result["streams"] if s["label"] == "spatial-joined")
        self.assertNotEqual(joined, phrase)
        self.assertEqual(spatial, phrase)

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_opc_declared_fixed_page_with_non_fpage_extension(self):
        phrase = "declared page"
        result = extractor.extract_xps_glyph_indices(make_xps(phrase, page_name="1.bin"))
        self.assertEqual(result["text"], phrase)

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_relative_font_uri_resolves(self):
        phrase = "quiet sea"
        result = extractor.extract_xps_glyph_indices(make_xps(phrase, relative_uri=True))
        self.assertEqual(result["text"], phrase)

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_non_one_to_one_cluster_is_not_guessed(self):
        result = extractor.extract_xps_glyph_indices(make_xps("a", cluster=True))
        self.assertEqual(result["runs"][0]["text"], "")
        self.assertIn("cluster requires UnicodeString", result["runs"][0]["unresolved"][0]["reason"])

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_unicode_string_is_left_to_existing_extractor(self):
        package = io.BytesIO()
        page = (
            '<FixedPage xmlns="http://schemas.microsoft.com/xps/2005/06">'
            '<Glyphs UnicodeString="already mapped" Indices="1;2" FontUri="/missing.odttf" />'
            '</FixedPage>'
        ).encode()
        content_types = (
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Override PartName="/Documents/1/Pages/1.fpage" ContentType="application/vnd.ms-package.xps-fixedpage+xml" />'
            '</Types>'
        ).encode()
        with zipfile.ZipFile(package, "w") as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("Documents/1/Pages/1.fpage", page)
        result = extractor.extract_xps_glyph_indices(package.getvalue())
        self.assertEqual(result["status"], "no-glyph-index-only-runs")
        self.assertEqual(result["runs"], [])


if __name__ == "__main__":
    unittest.main()
