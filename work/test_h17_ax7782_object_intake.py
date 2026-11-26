#!/usr/bin/env python3
"""Focused regression tests for the read-only AX-7782 intake helper."""
import hashlib
import io
import json
import sys
import unittest
from unittest.mock import patch
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_ax7782_object_intake as intake
import h17_k04_binary_window_intake as k04

REPO = Path(__file__).resolve().parents[1]


class IntakeTests(unittest.TestCase):
    def test_crc16_standard_check_vectors(self):
        expected = {
            "ARC": 0xBB3D, "MODBUS": 0x4B37, "CCITT_FALSE": 0x29B1,
            "CCITT_XMODEM": 0x31C3, "CCITT_AUG": 0xE5CC,
            "X25": 0x906E, "KERMIT": 0x2189, "DNP": 0xEA82,
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(intake.crc16(b"123456789", **intake.CRC16S[name]), value)

    def test_selected_ax7782_chain_is_accepted_k07_component(self):
        selected, meta = intake.select_chain(REPO / "resources", "AX-7782")
        self.assertEqual(meta["object"], "IR-261003-H17")
        self.assertEqual(meta["selected_attempts"], [2] * 8)
        self.assertTrue(meta["handoff_email_confirms_retained_object"])
        raw = b"".join(bytes.fromhex(row["checkpoint"]) for row in selected)
        component = hashlib.sha256(raw).digest()[:16]
        acceptance = json.loads((REPO / "resources" / "acceptance.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(component).hexdigest(), acceptance["slot_sha256"]["K07"])

    def test_source_named_bx25_pdf_is_skipped_before_magic_or_raw_scan(self):
        # Synthetic fixture only; never read the quarantined source bytes.
        name = "BX25-08.pdf"
        payload = b"%PDF-1.7 synthetic quarantined-member fixture"
        with patch.object(intake, "magic", side_effect=AssertionError("opaque PDF reached magic")), patch.object(intake, "raw_hits", side_effect=AssertionError("opaque PDF reached raw scan")):
            result = intake.scan_member(name, payload, 0, [0])
        self.assertEqual(result, {
            "name": name, "size": len(payload),
            "status": "skipped_opaque_pdf_by_name",
            "pinned_sha256": intake.OPAQUE_PDF_SHA256,
        })

    def test_source_named_bx25_derivative_is_skipped_before_magic(self):
        payload = b"%PDF-1.7 transformed derivative"
        with patch.object(intake, "magic", side_effect=AssertionError("quarantined derivative reached magic")), patch.object(intake, "raw_hits", side_effect=AssertionError("quarantined derivative reached raw scan")):
            result = intake.scan_member("nested/BX25-08-redacted.pdf", payload, 0, [0])
        self.assertEqual(result["status"], "skipped_opaque_pdf_by_name")

    def test_k04_scanner_skips_source_named_bx25_derivative_before_magic(self):
        payload = b"%PDF-1.7 transformed derivative"
        with patch.object(k04, "magic", side_effect=AssertionError("quarantined derivative reached magic")):
            result = k04.scan_member(
                "nested/BX25-08-redacted.pdf", payload, 0, [0, 1024, 0, 10],
                bytes(32), bytes(16), 1, 1024, 2,
            )
        self.assertEqual(result["status"], "skipped_opaque_pdf_by_name")

    def test_k04_zip_member_name_is_skipped_before_open(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("BX25-08-redacted.pdf", b"%PDF-1.7 transformed derivative")
        with patch.object(zipfile.ZipFile, "open", side_effect=AssertionError("quarantined ZIP member was opened")):
            result = k04.scan_member(
                "bundle.zip", payload.getvalue(), 0, [0, 1024 * 1024, 0, 10],
                bytes(32), bytes(16), 1, 1024 * 1024, 2,
            )
        self.assertEqual(result["members"][0]["status"], "skipped_opaque_pdf_by_name")

    def test_container_does_not_raw_scan_source_named_pdf_member(self):
        # Synthetic fixture only; never read the quarantined source bytes.
        pdf = b"%PDF-1.7 synthetic quarantined-member fixture"
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("BX25-08.pdf", pdf)
        with patch.object(intake, "raw_hits", side_effect=AssertionError("container raw scan could inspect opaque member")):
            result = intake.scan_member("bundle.zip", payload.getvalue(), 0, [0])
        self.assertEqual(result["raw_hits"], [])
        self.assertEqual(result["members"][0]["status"], "skipped_opaque_pdf_by_name")
        self.assertEqual(result["members"][0]["pinned_sha256"], intake.OPAQUE_PDF_SHA256)
        self.assertNotIn("sha256", result["members"][0])

    def test_zip_member_text_is_found_without_extraction(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("records/IR-261003-H17.txt",
                             "IR-261003-H17 final envelope caption coupon handoff N23")
        result = intake.scan_member("fixture.zip", payload.getvalue(), 0, [0])
        self.assertEqual(result["magic"], "zip")
        self.assertEqual(len(result["members"]), 1)
        self.assertIn("IR-261003-H17.txt", result["members"][0]["name_hits"])
        hits = result["members"][0]["raw_hits"]
        terms = {hit["term"] for hit in hits}
        self.assertIn("IR-261003-H17", terms)
        self.assertIn("final envelope", terms)
        self.assertIn("caption", terms)


    def test_neutral_name_pdf_magic_is_skipped_before_magic_or_raw_scan(self):
        payload = b"neutral-prefix%PDF-1.7 transformed derivative"
        with patch.object(intake, "magic", side_effect=AssertionError("PDF reached magic")), patch.object(intake, "raw_hits", side_effect=AssertionError("PDF reached raw scan")):
            result = intake.scan_member("neutral.bin", payload, 0, [0])
        self.assertEqual(result["status"], "skipped_pdf_pending_provenance")

    def test_k04_scanner_skips_neutral_name_pdf_magic_before_any_scan(self):
        payload = b"neutral-prefix%PDF-1.7 transformed derivative"
        with patch.object(k04, "magic", side_effect=AssertionError("PDF reached magic")), patch.object(k04, "scan_bytes", side_effect=AssertionError("PDF reached binary scan")):
            result = k04.scan_member(
                "neutral.bin", payload, 0, [0, 1024, 0, 10],
                bytes(32), bytes(16), 1, 1024, 2,
            )
        self.assertEqual(result["status"], "skipped_pdf_pending_provenance")

if __name__ == "__main__":
    unittest.main()
