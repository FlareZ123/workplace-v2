"""Synthetic round-trip tests for the optional LibreOffice BIFF adapter."""
from __future__ import annotations

import base64
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from h17_xls_lo_fallback import extract, extract_bytes  # noqa: E402
try:
    from h17_ax7782_k08_phrase_intake import iter_text_streams  # noqa: E402
except ImportError:  # standalone helper test outside the repository
    iter_text_streams = None

try:
    from openpyxl import Workbook
    from openpyxl.comments import Comment
    from openpyxl.drawing.image import Image as XLImage
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.workbook.defined_name import DefinedName
    from PIL import Image as PILImage
except ImportError:  # pragma: no cover - environment-dependent
    Workbook = None
    Alignment = Font = PatternFill = XLImage = PILImage = None


class LegacyXlsFallbackTests(unittest.TestCase):
    @unittest.skipUnless(
        (shutil.which("libreoffice") or shutil.which("soffice")) and Workbook and XLImage and PILImage,
        "LibreOffice, openpyxl and Pillow are required",
    )
    def test_ordered_cells_comments_hidden_sheet_and_formula_cache(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h17-xls-test-") as tmp_name:
            root = Path(tmp_name)
            source_xlsx = root / "fixture.xlsx"
            xls_dir = root / "xls"
            xls_dir.mkdir()
            profile = root / "lo-create-profile"
            profile.mkdir()

            book = Workbook()
            sheet = book.active
            sheet.title = "Visible"
            sheet["A1"] = "sea"
            sheet["B1"] = "at the end"
            sheet["C1"] = "of the night"
            sheet["A1"].comment = Comment("Emily margin caption", "Emily")
            sheet["B1"].hyperlink = "https://example.invalid/x"
            sheet["D1"] = "=1+1"
            sheet["M10"].fill = PatternFill(fill_type="solid", fgColor="FF008080", bgColor="FF008080")
            sheet["M10"].font = Font(color="FFFFFFFF")
            sheet["M10"].alignment = Alignment(wrap_text=True, horizontal="left", vertical="top")
            sheet["C3"].fill = PatternFill(fill_type="solid", fgColor="FFFFFFFF", bgColor="FFFFFFFF")
            sheet["C3"].font = Font(color="FF000000")
            sheet["C3"].alignment = Alignment(wrap_text=False, horizontal="left", vertical="top")
            image_path = root / "fixture.png"
            PILImage.new("RGB", (16, 16), (0, 160, 160)).save(image_path, format="PNG")
            image_bytes = image_path.read_bytes()
            sheet.add_image(XLImage(str(image_path)), "M10")
            hidden = book.create_sheet("Hidden")
            hidden.sheet_state = "hidden"
            hidden["A1"] = "hidden sheet phrase"
            book.defined_names.add(
                DefinedName("DeskCaption", attr_text="'Visible'!$A$1:$C$1")
            )
            book.save(source_xlsx)
            book.close()

            converter = shutil.which("libreoffice") or shutil.which("soffice")
            proc = subprocess.run(
                [
                    converter, "--headless", "--nologo", "--nodefault", "--nolockcheck",
                    "--norestore", "--nofirststartwizard",
                    f"-env:UserInstallation={profile.as_uri()}",
                    "--convert-to", "xls:MS Excel 97", "--outdir", str(xls_dir),
                    str(source_xlsx),
                ],
                capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            source_xls = xls_dir / "fixture.xls"
            self.assertTrue(source_xls.is_file(), proc.stderr or proc.stdout)
            original_hash = hashlib.sha256(source_xls.read_bytes()).hexdigest()

            result = extract(source_xls)
            member_bytes = source_xls.read_bytes()
            member_result = extract_bytes(
                member_bytes, "archive/mug-stock.xls",
                include_image_data=True, allowed_image_anchors={"M10"},
            )
            nonmatching_image_result = extract_bytes(
                member_bytes, "archive/mug-stock.xls",
                include_image_data=True, allowed_image_anchors={"C3"},
            )
            with self.assertRaises(ValueError):
                extract_bytes(member_bytes, "archive/mug-stock.xls", include_image_data=True)
            self.assertEqual(member_result["source_name"], "archive/mug-stock.xls")
            self.assertTrue(member_result["source_unchanged"])
            self.assertEqual(member_result["source_sha256_before"], original_hash)
            image_meta = result["embedded_images"]
            self.assertEqual(len(image_meta), 1)
            self.assertEqual(image_meta[0]["anchor"], "M10")
            self.assertEqual(image_meta[0]["format"], "png")
            self.assertFalse(image_meta[0]["data_included"])
            self.assertNotIn("data_base64", image_meta[0])
            self.assertEqual(image_meta[0]["sha256"], hashlib.sha256(image_bytes).hexdigest())
            member_image = member_result["embedded_images"][0]
            self.assertTrue(member_image["data_included"])
            self.assertEqual(base64.b64decode(member_image["data_base64"]), image_bytes)
            self.assertEqual(member_image["sha256"], hashlib.sha256(image_bytes).hexdigest())
            blocked_image = nonmatching_image_result["embedded_images"][0]
            self.assertFalse(blocked_image["data_included"])
            self.assertEqual(blocked_image["reason"], "anchor_not_allowlisted")
            self.assertEqual(nonmatching_image_result["source_sha256_before"], original_hash)
            member_texts = [item["text"] for item in member_result["text_streams"]]
            self.assertTrue(any("sea at the end of the night" in text for text in member_texts))
            streams = result["text_streams"]
            texts = [item["text"] for item in streams]
            self.assertTrue(result["source_unchanged"])
            self.assertEqual(result["source_sha256_before"], original_hash)
            self.assertEqual(result["source_sha256_after"], original_hash)
            self.assertTrue(any("sea at the end of the night" in text for text in texts))
            self.assertIn("Emily margin caption", texts)
            self.assertIn("https://example.invalid/x", texts)
            self.assertIn("hidden sheet phrase", texts)
            self.assertIn("=1+1", texts)
            self.assertIn("2", texts)  # converted cached formula value
            self.assertTrue(any("Visible!$A$1:$C$1" in text for text in texts))
            self.assertEqual(
                [(s["name"], s["state"]) for s in result["sheets"]],
                [("Visible", "visible"), ("Hidden", "hidden")],
            )
            styles = {item["coordinate"]: item for item in result["style_metadata"]
                      if item["sheet"] == "Visible"}
            self.assertTrue(styles["M10"]["wrap_text"])
            self.assertEqual(styles["M10"]["fill_type"], "solid")
            self.assertEqual(styles["M10"]["fill_foreground"]["rgb"], "FF008080")
            self.assertEqual(styles["M10"]["font_color"]["rgb"], "FFFFFFFF")
            self.assertFalse(styles["C3"]["wrap_text"])
            self.assertEqual(styles["C3"]["fill_foreground"]["rgb"], "FFFFFFFF")
            self.assertEqual(styles["C3"]["font_color"]["rgb"], "FF000000")
            self.assertEqual(styles["M10"]["number_format"], "General")
            self.assertFalse(styles["M10"]["row_hidden"])
            self.assertFalse(styles["M10"]["column_hidden"])
            self.assertEqual(set(result["style_metadata_scope"]),
                             {"M10", "C3", "EX4", "AT171", "HN28", "DZ122", "DT205", "AI96", "C67", "Z201"})

            # Exercise the repository dispatcher when its sibling modules
            # are available; standalone helper tests may run outside the repo.
            if iter_text_streams is not None:
                budget = [0]
                errors = []
                integrated = list(iter_text_streams(
                    "AX-7782!/mug-stock.xls", source_xls.read_bytes(), 0, budget, errors
                ))
                integrated_text = [
                    payload.decode("utf-8", "replace") for _, payload in integrated
                ]
                self.assertTrue(any("sea at the end of the night" in text
                                    for text in integrated_text))
                self.assertTrue(any(
                    "!/<image:Visible!M10>.png" in source
                    and hashlib.sha256(payload).hexdigest() == hashlib.sha256(image_bytes).hexdigest()
                    for source, payload in integrated
                ), "M10 embedded image bytes never reached the generic K08 image decoder")
                self.assertFalse(any("BIFF fallback failed" in e.get("error", "")
                                     for e in errors))


if __name__ == "__main__":
    unittest.main()
