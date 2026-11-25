import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from work import h17_k08_teal_bit_image_scan as image_scan


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


if __name__ == "__main__":
    unittest.main()
