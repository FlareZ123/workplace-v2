import builtins
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from work import h17_k08_teal_bit_image_scan as image_scan
from work import h17_k04_pdf_barcode_intake as pdf_intake


class IntakeCliRedactionTests(unittest.TestCase):
    def test_teal_image_cli_redacts_caption_and_component_material(self):
        phrase = "private keeper caption"
        component = "89ABCDEF01234567" * 2
        synthetic_result = {
            "image": {"path": "/private/source/photo.png", "sha256": "f" * 64},
            "matches": [
                {
                    "normalized_phrase": phrase,
                    "component_hex": component,
                    "hmac16": component,
                }
            ],
        }
        stdout = io.StringIO()
        with patch.object(image_scan, "load_commitment", return_value=(b"nonce", "commitment")):
            with patch.object(image_scan, "scan_authorized_n14_image", return_value=synthetic_result):
                with patch.object(
                    sys,
                    "argv",
                    [
                        "h17_k08_teal_bit_image_scan.py",
                        "--image", "photo.png",
                        "--source-manifest", "manifest.json",
                        "--evidence-root", "resources",
                    ],
                ):
                    with redirect_stdout(stdout):
                        status = image_scan.main()

        rendered = stdout.getvalue()
        self.assertEqual(status, 0)
        self.assertNotIn(phrase, rendered)
        self.assertNotIn(component, rendered)
        self.assertNotIn("/private/source/photo.png", rendered)
        self.assertIn("redaction_applied", rendered)


    def test_teal_image_scanner_rejects_hash_pinned_pdf_before_decoding(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            image_path = directory / "renamed.png"
            manifest_path = directory / "manifest.json"
            image_path.write_bytes(b"synthetic bytes; no PDF content")
            manifest_path.write_text(
                json.dumps(
                    {
                        "note_id": "N14",
                        "image_path": "renamed.png",
                        "image_sha256": image_scan.OPAQUE_PDF_SHA256,
                        "photo_author": "Gabriel",
                        "final_caption_author": "Emily",
                        "link_type": sorted(image_scan.SOURCE_LINK_TYPES)[0],
                        "evidence_ref": "crew/N14 original photograph",
                        "link_evidence": "A source-authenticated link to Emily's final caption.",
                    }
                ),
                encoding="utf-8",
            )

            class FakeDigest:
                def hexdigest(self):
                    return image_scan.OPAQUE_PDF_SHA256

            with patch.object(image_scan.hashlib, "sha256", return_value=FakeDigest()):
                with patch.object(image_scan, "scan_image") as scan:
                    with self.assertRaisesRegex(ValueError, "hash-only"):
                        image_scan.scan_authorized_n14_image(
                            image_path, manifest_path, b"nonce", "commitment"
                        )
                    scan.assert_not_called()

    def test_pdf_barcode_iterators_skip_hash_pinned_pdf_before_parser_import(self):
        class FakeDigest:
            def hexdigest(self):
                return pdf_intake.OPAQUE_PDF_SHA256

        real_import = builtins.__import__

        def reject_pdf_parser(name, *args, **kwargs):
            if name == "pymupdf":
                raise AssertionError("quarantined PDF parser must not be imported")
            return real_import(name, *args, **kwargs)

        with patch.object(pdf_intake.hashlib, "sha256", return_value=FakeDigest()):
            with patch("builtins.__import__", side_effect=reject_pdf_parser):
                self.assertEqual(list(pdf_intake.iter_pdf_embedded_files(b"fixture")), [])
                self.assertEqual(list(pdf_intake.iter_pdf_coupon_text(b"fixture")), [])
                self.assertEqual(list(pdf_intake.iter_pdf_barcode_images(b"fixture")), [])


if __name__ == "__main__":
    unittest.main()
