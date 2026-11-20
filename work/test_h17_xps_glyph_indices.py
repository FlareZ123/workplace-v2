#!/usr/bin/env python3
"""Tests for h17_xps_glyph_indices.py."""
from __future__ import annotations

import io
import sys
import unittest
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_xps_glyph_indices as extractor
import h17_ax7782_k08_phrase_intake as phrase_intake

try:
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont
except ImportError:
    FontBuilder = None
    TTGlyphPen = None
    TTFont = None


def make_test_font(text: str, include_cmap: bool = True, ambiguous_cmap: bool = False) -> bytes:
    chars = sorted(set(text))
    names = [".notdef", "space"] + [f"uni{ord(c):04X}" for c in chars if c != " "]
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder(names)
    cmap = {32: "space"}
    for char in chars:
        if char != " ":
            cmap[ord(char)] = f"uni{ord(char):04X}"
    if ambiguous_cmap and "a" in text and "b" in text:
        cmap[ord("b")] = cmap[ord("a")]
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
    ambiguous_cmap: bool = False,
    namespace: str = "http://schemas.microsoft.com/xps/2005/06",
    unknown_glyph: bool = False,
    transform: bool = False,
    nonfinite_coordinates: bool = False,
) -> bytes:
    font_bytes = make_test_font(text, include_cmap=include_cmap, ambiguous_cmap=ambiguous_cmap)
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
    if unknown_glyph:
        gids = gids[:2] + [max(gids, default=0) + 1000] + gids[2:]

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

    def coord(value):
        return "NaN" if nonfinite_coordinates else str(value)

    glyph_xml = "".join(
        f'<Glyphs FontUri="{font_uri}" FontRenderingEmSize="12" OriginX="{coord(x)}" OriginY="20" Indices="{indices}" />'
        for indices, x in glyph_runs
    )
    if transform:
        glyph_xml = f'<Canvas RenderTransform="1,0,0,1,10,0">{glyph_xml}</Canvas>'
    page = (
        f'<FixedPage xmlns="{namespace}" Width="816" Height="1056">'
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
    def test_ambiguous_cmap_is_not_guessed(self):
        result = extractor.extract_xps_glyph_indices(make_xps("ab", ambiguous_cmap=True))
        self.assertEqual(result["runs"][0]["text"], "")
        self.assertTrue(any("ambiguous cmap" in item["reason"]
                            for item in result["runs"][0]["unresolved"]))

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


    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_accepts_openxps_fixedpage_namespace(self):
        result = extractor.extract_xps_glyph_indices(
            make_xps("open xps", namespace="http://schemas.openxps.org/oxps/v1.0")
        )
        self.assertEqual(result["status"], "decoded")
        self.assertEqual(result["text"], "open xps")

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_rejects_foreign_fixedpage_namespace(self):
        result = extractor.extract_xps_glyph_indices(
            make_xps("not xps", namespace="urn:foreign:fake-xps")
        )
        self.assertEqual(result["status"], "no-glyph-index-only-runs")
        self.assertEqual(result["runs"], [])
        self.assertEqual(result["streams"], [])

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_partial_glyph_run_is_diagnostic_only(self):
        result = extractor.extract_xps_glyph_indices(make_xps("the sea is quiet", unknown_glyph=True))
        self.assertEqual(result["runs"][0]["status"], "partial")
        self.assertTrue(result["runs"][0]["text"])  # diagnostic text is retained
        self.assertEqual(result["streams"], [])
        self.assertEqual(result["text"], "")
        self.assertFalse(result["coverage"]["complete"])

    def test_zero_cluster_counts_are_rejected(self):
        parsed = extractor.parse_indices("(0:1)12;(1:0)13")
        self.assertTrue(all("error" in item for item in parsed))
        self.assertTrue(all("positive" in item["error"] for item in parsed))

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_nonfinite_coordinates_disable_spatial_order(self):
        result = extractor.extract_xps_glyph_indices(
            make_xps("the sea is quiet", split_at=7, reverse_runs=True, nonfinite_coordinates=True)
        )
        labels = [stream["label"] for stream in result["streams"]]
        self.assertNotIn("spatial-joined", labels)
        self.assertNotIn("spatial-spaced", labels)

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_transformed_page_disables_spatial_order(self):
        result = extractor.extract_xps_glyph_indices(
            make_xps("the sea is quiet", split_at=7, reverse_runs=True, transform=True)
        )
        labels = [stream["label"] for stream in result["streams"]]
        self.assertNotIn("spatial-joined", labels)
        self.assertNotIn("spatial-spaced", labels)

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_malformed_indices_are_isolated_per_run(self):
        with patch.object(extractor, "MAX_GLYPHS_PER_RUN", 6):
            result = extractor.extract_xps_glyph_indices(
                make_xps("the sea is quiet", split_at=4)
            )
        self.assertEqual([run["status"] for run in result["runs"]], ["decoded", "malformed-indices"])
        self.assertEqual(result["streams"], [])
        self.assertFalse(result["coverage"]["complete"])

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_total_xml_budget_exhaustion_is_explicit(self):
        with patch.object(extractor, "MAX_TOTAL_XML_BYTES", 1):
            result = extractor.extract_xps_glyph_indices(make_xps("budget"))
        self.assertEqual(result["status"], "truncated")
        self.assertFalse(result["coverage"]["complete"])
        self.assertIn("total-xml-budget", result["coverage"]["reasons"])

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_package_run_budget_exhaustion_is_explicit(self):
        with patch.object(extractor, "MAX_RUNS_PER_PACKAGE", 1):
            result = extractor.extract_xps_glyph_indices(
                make_xps("the sea is quiet", split_at=7)
            )
        self.assertEqual(result["status"], "truncated")
        self.assertIn("run-count-limit", result["coverage"]["reasons"])
        self.assertEqual(result["streams"], [])

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_total_glyph_budget_exhaustion_is_explicit(self):
        with patch.object(extractor, "MAX_TOTAL_GLYPHS", 5):
            result = extractor.extract_xps_glyph_indices(make_xps("the sea is quiet"))
        self.assertEqual(result["status"], "truncated")
        self.assertIn("total-glyph-limit", result["coverage"]["reasons"])
        self.assertEqual(result["streams"], [])

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_candidate_adapter_fails_closed_on_incomplete_coverage(self):
        with patch.object(extractor, "MAX_TOTAL_XML_BYTES", 1):
            with self.assertRaisesRegex(ValueError, "incomplete XPS glyph extraction"):
                extractor.extract_xps_glyph_streams(make_xps("budget"))


class TestScannerIntegration(unittest.TestCase):
    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_k04_scanner_consumes_glyph_index_only_xps(self):
        import hashlib
        import h17_k04_binary_window_intake as scanner

        component = bytes(range(16))
        mask = bytes.fromhex(scanner.DEFAULT_MASK)
        payload = bytes(a ^ b for a, b in zip(component, mask))
        package = make_xps(payload.hex().upper(), split_at=16)
        result = scanner.scan_member(
            "synthetic.xps",
            package,
            0,
            [0, 64 * 1024 * 1024, 0, 1000],
            hashlib.sha256(component).digest(),
            mask,
            1,
            32 * 1024 * 1024,
            4,
        )
        self.assertTrue(
            any(
                hit.get("kind") == "payload_xor_route_mask"
                and hit.get("component_hex") == component.hex().upper()
                for hit in result.get("hits", [])
            ),
            result,
        )

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_k04_scanner_surfaces_incomplete_glyph_coverage(self):
        import hashlib
        import h17_k04_binary_window_intake as scanner

        package = make_xps("ambiguous", ambiguous_cmap=True)
        mask = bytes.fromhex(scanner.DEFAULT_MASK)
        result = scanner.scan_member(
            "ambiguous.xps",
            package,
            0,
            [0, 64 * 1024 * 1024, 0, 1000],
            hashlib.sha256(bytes(range(16))).digest(),
            mask,
            1,
            32 * 1024 * 1024,
            4,
        )
        self.assertTrue(
            any(error.get("extractor") == "xps-glyph-indices"
                for error in result.get("extraction_errors", [])),
            result,
        )

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_k08_scanner_consumes_spatial_glyph_index_only_xps(self):
        import hashlib
        import json
        import tempfile
        import h17_profile_k08_phrase_scan as scanner

        caption = "the voices stayed around the table after the long watch"
        nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        normalized = scanner.phrase.normalize(caption)
        component = scanner.phrase.k08_component(nonce, normalized)
        target = hashlib.sha256(component).digest()
        package = make_xps(caption, split_at=4, reverse_runs=True)

        with tempfile.TemporaryDirectory(prefix="h17-xps-scanner-integration-") as temp:
            root = Path(temp) / "profile"
            root.mkdir()
            source = root / "PS-0323.xps"
            source.write_bytes(package)
            inventory_path = Path(temp) / "inventory.json"
            inventory_path.write_text(json.dumps({
                "schema": "h17-profile-inventory/v1",
                "source_root": str(root),
                "files": [{
                    "path": source.name,
                    "size": source.stat().st_size,
                    "sha256": hashlib.sha256(package).hexdigest(),
                    "categories": ["printer"],
                }],
            }), encoding="utf-8")
            result = scanner.scan_inventory(
                inventory_path,
                nonce,
                target,
                max_phrase_words=16,
                max_file_bytes=32 * 1024 * 1024,
                max_total_bytes=64 * 1024 * 1024,
            )

        self.assertIn("xps-glyph:", json.dumps(result.get("hits", [])), result)

        errors = []
        streams = list(phrase_intake.iter_text_streams(
            "PS-0323.xps", package, 0, [0], errors
        ))
        intake_hits = []
        for source_name, payload in streams:
            for label, text in phrase_intake.decode_text_variants(payload, source_name):
                phrase_intake.scan_phrase_spans(
                    text, nonce, target, source_name + " [" + label + "]", 16, intake_hits
                )
        self.assertTrue(
            any(hit["normalized_phrase"] == normalized for hit in intake_hits),
            intake_hits,
        )
        self.assertTrue(
            any("xps-glyph" in hit["source"] for hit in intake_hits),
            intake_hits,
        )
        self.assertFalse(
            any("xps-glyph-indices:" in error.get("error", "") for error in errors),
            errors,
        )

    @unittest.skipIf(FontBuilder is None, "fontTools is not installed")
    def test_k08_scanner_surfaces_incomplete_glyph_coverage(self):
        import hashlib
        import json
        import tempfile
        import h17_profile_k08_phrase_scan as scanner

        nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        target = hashlib.sha256(scanner.phrase.k08_component(nonce, "not the caption")).digest()
        package = make_xps("ambiguous", ambiguous_cmap=True)

        with tempfile.TemporaryDirectory(prefix="h17-xps-scanner-coverage-") as temp:
            root = Path(temp) / "profile"
            root.mkdir()
            source = root / "ambiguous.xps"
            source.write_bytes(package)
            inventory_path = Path(temp) / "inventory.json"
            inventory_path.write_text(json.dumps({
                "schema": "h17-profile-inventory/v1",
                "source_root": str(root),
                "files": [{
                    "path": source.name,
                    "size": source.stat().st_size,
                    "sha256": hashlib.sha256(package).hexdigest(),
                    "categories": ["printer"],
                }],
            }), encoding="utf-8")
            result = scanner.scan_inventory(
                inventory_path,
                nonce,
                target,
                max_phrase_words=16,
                max_file_bytes=32 * 1024 * 1024,
                max_total_bytes=64 * 1024 * 1024,
            )

        self.assertTrue(
            any("xps-glyph-indices:" in error.get("error", "")
                for error in result.get("errors", [])),
            result,
        )

        intake_errors = []
        list(phrase_intake.iter_text_streams(
            "ambiguous.xps", package, 0, [0], intake_errors
        ))
        self.assertTrue(
            any("xps-glyph-indices:" in error.get("error", "") for error in intake_errors),
            intake_errors,
        )

if __name__ == "__main__":
    unittest.main()
