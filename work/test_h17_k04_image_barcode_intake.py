"""Synthetic exact-K04 tests for complete coupons printed as QR symbols."""
from __future__ import annotations

import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qrcode
from h17_k04_binary_window_intake import run_scan
from h17_k04_image_barcode_intake import read_image_barcodes


class OriginalHashBarcodeTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory(prefix="h17-barcode-sft-")
        self.addCleanup(self.root.cleanup)
        self.path = Path(self.root.name) / "recovered-original-coupon.png"
        self.mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
        self.component = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        self.payload = bytes(a ^ b for a, b in zip(self.mask, self.component))
        self.target = hashlib.sha256(self.component).hexdigest()

    def embed(self, payload: bytes) -> None:
        code = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8, border=4,
        )
        code.add_data(payload)
        code.make(fit=True)
        image = code.make_image(fill_color="black", back_color="white")
        out = io.BytesIO()
        image.save(out, "PNG")
        self.path.write_bytes(out.getvalue())

    def scan(self, digest=None):
        return run_scan(
            self.path, self.target if digest is None else digest,
            self.mask.hex().upper(), 1, 256 * 1024 * 1024,
            512 * 1024 * 1024, 4, 10000,
        )

    def test_printed_hex_masked_payload_reaches_complete_commitment(self):
        self.embed(b"K04-PAYLOAD=" + self.payload.hex().upper().encode("ascii"))
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        hit = result["hits"][0]
        self.assertEqual(hit["component_hex"], self.component.hex().upper())
        self.assertEqual(hit["kind"], "payload_xor_route_mask")
        self.assertIn("image-", hit["encoding"])
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), before)

    def test_binary_qr_with_8bit_octets_recovered_without_utf8_damage(self):
        self.embed(self.payload)
        decoded, errors = read_image_barcodes(self.path.read_bytes())
        self.assertTrue(any(raw == self.payload for _, raw in decoded), (decoded, errors))
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        self.assertEqual(result["hits"][0]["component_hex"], self.component.hex().upper())

    def test_original_commitment_mismatch_is_never_accepted(self):
        self.embed(b"K04-PAYLOAD=" + self.payload.hex().upper().encode("ascii"))
        wrong_target = hashlib.sha256(b"not the component").hexdigest()
        self.assertEqual(self.scan(digest=wrong_target)["hits"], [])

    def test_direct_component_barcode_remains_independent(self):
        self.embed(self.component.hex().upper().encode("ascii"))
        hits = self.scan()["hits"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["kind"], "direct_component")


if __name__ == "__main__":
    unittest.main(verbosity=2)
