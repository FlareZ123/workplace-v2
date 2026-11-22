"""Single-file, read-only OOXML authored-unit coupon reconstruction regression."""
from __future__ import annotations

import hashlib
import io
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h17_k04_binary_window_intake import candidate_hit, scan_bytes
from h17_ooxml_text_intake import iter_ooxml_text_units


class ExactOoxmlTextTests(unittest.TestCase):
    def setUp(self):
        self.mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
        self.component = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
        self.payload = bytes(a ^ b for a, b in zip(self.component, self.mask))
        self.target = hashlib.sha256(self.component).digest()

    def package(self, part: str, xml: str, with_manifest: bool = True):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            if with_manifest:
                archive.writestr("[Content_Types].xml", "<Types/>")
            archive.writestr(part, xml)
        return stream.getvalue()

    def check_native(self, part: str, xml: str):
        archive = self.package(part, xml)
        emitted = list(iter_ooxml_text_units(archive))
        self.assertEqual(len(emitted), 1, emitted)
        matches = scan_bytes(emitted[0][0], emitted[0][1], self.target, self.mask, 1)
        self.assertTrue(matches, emitted)
        self.assertEqual(matches[0]["component_hex"], self.component.hex().upper())
        self.assertEqual(matches[0]["kind"], "payload_xor_route_mask")
        return emitted[0]

    def test_docx_paragraph_multiple_formatting_runs(self):
        token = self.payload.hex().upper()
        xml = (
            '<w:document xmlns:w="http://schemas.openxmlformats.org/'
            'wordprocessingml/2006/main"><w:body><w:p>'
            '<w:r><w:t>Coupon=' + token[:16] + '</w:t></w:r>'
            '<w:r><w:t>' + token[16:] + '</w:t></w:r>'
            '</w:p></w:body></w:document>'
        )
        self.check_native("word/document.xml", xml)

    def test_pptx_slide_multiple_formatting_runs(self):
        token = self.payload.hex().upper()
        xml = (
            '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
            ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:p><a:r><a:t>' + token[:12] + '</a:t></a:r>'
            '<a:r><a:t>' + token[12:] + '</a:t></a:r></a:p></p:sld>'
        )
        self.check_native("ppt/slides/slide1.xml", xml)

    def test_xlsx_shared_string_multiple_runs(self):
        token = self.payload.hex().upper()
        xml = (
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<si><r><t>' + token[:15] + '</t></r>'
            '<r><t>' + token[15:] + '</t></r></si></sst>'
        )
        self.check_native("xl/sharedStrings.xml", xml)

    def test_two_separate_paragraphs_never_form_a_fabricated_coupon(self):
        token = self.payload.hex().upper()
        xml = (
            '<w:document xmlns:w="http://schemas.openxmlformats.org/'
            'wordprocessingml/2006/main"><w:body>'
            '<w:p><w:r><w:t>' + token[:16] + '</w:t></w:r></w:p>'
            '<w:p><w:r><w:t>' + token[16:] + '</w:t></w:r></w:p>'
            '</w:body></w:document>'
        )
        units = list(iter_ooxml_text_units(
            self.package("word/document.xml", xml)
        ))
        self.assertEqual(len(units), 2)
        self.assertFalse(any(
            scan_bytes(name, payload, self.target, self.mask, 1)
            for name, payload in units
        ))

    def test_plain_zip_without_ooxml_manifest_never_emits_authored_units(self):
        self.assertEqual(
            list(iter_ooxml_text_units(self.package(
                "word/document.xml",
                "<w:document/>",
                with_manifest=False,
            ))), [],
        )

    def test_malformed_ooxml_xml_is_rejected(self):
        self.assertEqual(
            list(iter_ooxml_text_units(self.package(
                "word/document.xml", "<not-valid",
            ))), [],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
