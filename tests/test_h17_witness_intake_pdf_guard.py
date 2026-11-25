import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from work import h17_witness_intake as intake


ROOT = Path(__file__).resolve().parents[1]


class HashOnlyPdfWitnessGuardTests(unittest.TestCase):
    def test_quarantined_pdf_is_rejected_for_every_witness_input_before_content_read(self):
        opaque_hash = intake.OPAQUE_PDF_SHA256
        real_read_bytes = Path.read_bytes

        for role in (
            "coupon transcription",
            "coupon original",
            "caption transcription",
            "caption original",
        ):
            with self.subTest(role=role), TemporaryDirectory() as tmp:
                directory = Path(tmp)
                coupon = directory / "coupon.json"
                coupon_original = directory / "coupon-original.bin"
                caption = directory / "caption.txt"
                caption_original = directory / "caption-original.bin"
                for path in (coupon, coupon_original, caption, caption_original):
                    path.write_bytes(b"synthetic fixture only")

                opaque_path = {
                    "coupon transcription": coupon,
                    "coupon original": coupon_original,
                    "caption transcription": caption,
                    "caption original": caption_original,
                }[role]

                def fake_sha256(path):
                    return opaque_hash if Path(path) == opaque_path else "a" * 64

                witness_paths = {coupon, coupon_original, caption, caption_original}

                def reject_content_read(path):
                    if path in witness_paths:
                        raise AssertionError("witness contents must not be read after hash-only match")
                    return real_read_bytes(path)

                args = (
                    (coupon, coupon_original, None, None)
                    if role.startswith("coupon")
                    else (None, None, caption, caption_original)
                )
                with patch.object(intake, "sha256_file", side_effect=fake_sha256):
                    with patch.object(Path, "read_bytes", reject_content_read):
                        with self.assertRaisesRegex(ValueError, "hash-only"):
                            intake.assess(*args, resources=ROOT / "resources")


if __name__ == "__main__":
    unittest.main()
