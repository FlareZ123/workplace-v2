"""Synthetic round-trip tests for the optional LibreOffice BIFF adapter."""
from __future__ import annotations

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
    from openpyxl import Workbook
    from openpyxl.comments import Comment
    from openpyxl.workbook.defined_name import DefinedName
except ImportError:  # pragma: no cover - environment-dependent
    Workbook = None


class LegacyXlsFallbackTests(unittest.TestCase):
    @unittest.skipUnless(
        (shutil.which("libreoffice") or shutil.which("soffice")) and Workbook,
        "LibreOffice and openpyxl are required",
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
            member_result = extract_bytes(source_xls.read_bytes(), "archive/mug-stock.xls")
            self.assertEqual(member_result["source_name"], "archive/mug-stock.xls")
            self.assertTrue(member_result["source_unchanged"])
            self.assertEqual(member_result["source_sha256_before"], original_hash)
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


if __name__ == "__main__":
    unittest.main()
