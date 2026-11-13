#!/usr/bin/env python3
"""Focused regression tests for the read-only AX-7782 intake helper."""
import hashlib
import io
import json
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_ax7782_object_intake as intake

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
        acceptance = json.loads((REPO / "acceptance.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(component).hexdigest(), acceptance["slot_sha256"]["K07"])

    def test_zip_member_text_is_found_without_extraction(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("records/final-envelope.txt",
                             "IR-261003-H17 final envelope caption coupon handoff N23")
        result = intake.scan_member("fixture.zip", payload.getvalue(), 0, [0])
        self.assertEqual(result["magic"], "zip")
        self.assertEqual(len(result["members"]), 1)
        hits = result["members"][0]["raw_hits"]
        terms = {hit["term"] for hit in hits}
        self.assertIn("IR-261003-H17", terms)
        self.assertIn("final envelope", terms)
        self.assertIn("caption", terms)


if __name__ == "__main__":
    unittest.main()
