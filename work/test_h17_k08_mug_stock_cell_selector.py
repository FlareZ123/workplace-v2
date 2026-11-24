import hashlib
import hmac
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace

from h17_k08_mug_stock_cell_selector import (
    FallbackSheet, aes_ecb_decrypt, coordinate_sets, excel_address, excel_column,
    evaluate_candidate, inspect_workbook, k08_component, map_sheets, normalize, sample_cells,
)


try:
    import openpyxl  # noqa: F401
    from h17_xls_lo_fallback import extract as _fallback_extract  # noqa: F401
    HAS_REAL_XLS_FALLBACK = bool(shutil.which("libreoffice") or shutil.which("soffice"))
except ImportError:
    HAS_REAL_XLS_FALLBACK = False


class FakeSheet:
    def __init__(self, name, rows, cols, values=None):
        self.name = name
        self.nrows = rows
        self.ncols = cols
        self.values = values or {}

    def cell(self, row, col):
        return SimpleNamespace(value=self.values.get((row, col), ""), ctype=1)


class SelectorTests(unittest.TestCase):
    def test_coordinates_are_pinned(self):
        raw = bytes.fromhex("0102030405060708090A0B0C0D0E0F10")
        sets = coordinate_sets(raw)
        self.assertEqual(sets["high_byte_row_low_byte_column"],
                         [(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14),(15,16)])
        self.assertEqual(sets["low_byte_row_high_byte_column"],
                         [(2,1),(4,3),(6,5),(8,7),(10,9),(12,11),(14,13),(16,15)])

    def test_excel_addresses(self):
        self.assertEqual(excel_column(16), "P")
        self.assertEqual(excel_column(2), "B")
        self.assertEqual(excel_address(15,16), "P15")
        self.assertEqual(excel_address(1,2), "B1")

    def test_sheet_mapping_is_bounded(self):
        self.assertEqual(map_sheets(["Sheet1"], None), {"single":["Sheet1"]*8})
        self.assertIsNone(map_sheets(["A","B","C","D"], None))
        self.assertIsNone(map_sheets(["Sheet1","Sheet2","Sheet3"], None))
        self.assertEqual(map_sheets(["Sheet1","Sheet2"], "Sheet2"), {"single":["Sheet2"]*8})

    def test_sample_cells_one_based_and_zero_based(self):
        sheet = FakeSheet("A", 4, 4, {(0,0):"first",(1,1):"second"})
        one = sample_cells(sheet, [(1,1),(2,2)], 1)
        zero = sample_cells(sheet, [(0,0),(1,1)], 0)
        self.assertEqual([x["value"] for x in one], ["first","second"])
        self.assertEqual([x["address"] for x in zero], ["A1","B2"])

    def test_out_of_bounds_is_not_silently_used(self):
        sheet = FakeSheet("P212", 212, 256, {(0,0):"x"})
        cells = sample_cells(sheet, [(229,64)], 1)
        self.assertFalse(cells[0]["in_bounds"])
        self.assertIsNone(cells[0]["value"])

    def test_formula_cells_are_not_used_as_phrase_values(self):
        sheet = FallbackSheet("Sheet1", 2, 2, {
            ("Sheet1", "A1"): {"data_type":"f", "text":"=A2", "converted_cached_value":"keeper"}
        })
        cells = sample_cells(sheet, [(1,1)], 1)
        self.assertIsNone(cells[0]["value"])
        result = evaluate_candidate(cells, b"0" * 16, b"0" * 32, "high_low", 1, "single")
        self.assertFalse(result["complete"])
        self.assertFalse(result["match"])

    def test_aes_ecb_decrypt_standard_known_answer(self):
        key = bytes.fromhex("000102030405060708090A0B0C0D0E0F")
        ciphertext = bytes.fromhex("69C4E0D86A7B0430D8CDB78070B4C55A")
        self.assertEqual(aes_ecb_decrypt(key, ciphertext).hex().upper(),
                         "00112233445566778899AABBCCDDEEFF")

    def test_candidate_hmac_commitment_path(self):
        nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        phrase = "one two three four five six seven eight"
        component = k08_component(nonce, normalize(phrase))
        target = bytes.fromhex(__import__("hashlib").sha256(component).hexdigest())
        cells = [{"in_bounds":True,"value":word} for word in phrase.split()]
        result = evaluate_candidate(cells, nonce, target, "high_low", 1, "single")
        self.assertTrue(result["match"])

    def test_end_to_end_synthetic_workbook_match_and_read_only_hash(self):
        nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        phrase = "x x x x x x x x"
        component = k08_component(nonce, normalize(phrase))
        target = hashlib.sha256(component).hexdigest()

        fake_fallback = ModuleType("h17_xls_lo_fallback")

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "evidence" / "print").mkdir(parents=True)
            (root / "evidence" / "recovery-routing.json").write_text(
                json.dumps({"K08":{"desk_nonce":nonce.hex()}}), encoding="utf-8")
            (root / "acceptance.json").write_text(
                json.dumps({"slot_sha256":{"K08":target}}), encoding="utf-8")
            (root / "evidence" / "print" / "spool-reconstruction.log").write_text(
                "2026-10-03T18:25:00Z JOB=PS-261003-0323 ATTEMPT=1 STATE=ACK "
                "CLASS=RECOVER PAYLOAD=BF6529BE6D7553ABE7B4E048C65B3135 DEST=store\n",
                encoding="utf-8")
            workbook = root / "mug-stock.xls"
            workbook.write_bytes(b"synthetic workbook bytes")
            before = hashlib.sha256(workbook.read_bytes()).hexdigest()
            plaintext = bytes.fromhex("0102030405060708090A0B0C0D0E0F10")
            selected_addresses = set()
            for pairs in coordinate_sets(plaintext).values():
                for base in (0, 1):
                    for raw_row, raw_column in pairs:
                        row = raw_row + (1 if base == 0 else 0)
                        column = raw_column + (1 if base == 0 else 0)
                        selected_addresses.add(excel_address(row, column))
            extraction = {
                "source_bytes": workbook.stat().st_size,
                "source_sha256_before": before,
                "source_sha256_after": before,
                "source_unchanged": True,
                "converter": "synthetic-fallback",
                "sheets": [{"name":"Sheet1","max_row":257,"max_column":257,"state":"visible"}],
                "text_streams": [
                    {"source":f"Sheet1!{address}","kind":"cell","text":"x","data_type":"s"}
                    for address in sorted(selected_addresses)
                ] + [
                    {"source":"Sheet1!M10<comment>","kind":"comment",
                     "text":phrase,"comment_author":"Test Author"}
                ],
            }
            fake_fallback.extract = lambda path: extraction
            previous_fallback = sys.modules.get("h17_xls_lo_fallback")
            sys.modules["h17_xls_lo_fallback"] = fake_fallback
            try:
                result = inspect_workbook(workbook, root, reveal=True)
            finally:
                if previous_fallback is None:
                    sys.modules.pop("h17_xls_lo_fallback", None)
                else:
                    sys.modules["h17_xls_lo_fallback"] = previous_fallback
            after = hashlib.sha256(workbook.read_bytes()).hexdigest()

        self.assertEqual(result["status"], "MATCH_REVIEW")
        self.assertEqual(len(result["candidates"]), 4)
        self.assertTrue(all(candidate["match"] for candidate in result["candidates"]))
        self.assertEqual(before, after)
        self.assertEqual(result["workbook"]["sha256_before"], result["workbook"]["sha256_after"])
        self.assertEqual(result["workbook"]["converter"], "synthetic-fallback")
        self.assertEqual(len(result["m10_comment_candidates"]), 1)
        self.assertTrue(result["m10_comment_candidates"][0]["match"])
        self.assertEqual(result["m10_comment_candidates"][0]["comment_author"], "Test Author")

    @unittest.skipUnless(HAS_REAL_XLS_FALLBACK, "LibreOffice, openpyxl and repository XLS fallback are required")
    def test_real_legacy_xls_fallback_with_pinned_cell_selector(self):
        import openpyxl

        nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        phrase = "one two three four five six seven eight"
        component = k08_component(nonce, normalize(phrase))
        target = hashlib.sha256(component).hexdigest()
        synthetic_plaintext = bytes.fromhex("0102030405060708090A0B0C0D0E0F10")
        addresses = [
            excel_address(row, column)
            for row, column in coordinate_sets(synthetic_plaintext)["high_byte_row_low_byte_column"]
        ]
        words = phrase.split()

        with tempfile.TemporaryDirectory(prefix="h17-k08-selector-") as temp:
            root = Path(temp)
            (root / "evidence" / "print").mkdir(parents=True)
            (root / "evidence" / "recovery-routing.json").write_text(
                json.dumps({"K08":{"desk_nonce":nonce.hex()}}), encoding="utf-8")
            (root / "acceptance.json").write_text(
                json.dumps({"slot_sha256":{"K08":target}}), encoding="utf-8")
            (root / "evidence" / "print" / "spool-reconstruction.log").write_text(
                "2026-10-03T18:25:00Z JOB=PS-261003-0323 ATTEMPT=1 STATE=ACK "
                "CLASS=RECOVER PAYLOAD=BF6529BE6D7553ABE7B4E048C65B3135 DEST=store\n",
                encoding="utf-8")
            source_xlsx = root / "source.xlsx"
            xls_dir = root / "xls"
            xls_dir.mkdir()
            profile = root / "lo-profile"
            profile.mkdir()
            book = openpyxl.Workbook()
            sheet = book.active
            sheet.title = "Visible"
            for address, word in zip(addresses, words):
                sheet[address] = word
            from openpyxl.comments import Comment
            sheet["M10"].comment = Comment(phrase, "Test Author")
            book.save(source_xlsx)
            book.close()
            converter = shutil.which("libreoffice") or shutil.which("soffice")
            proc = subprocess.run(
                [converter, "--headless", "--nologo", "--nodefault", "--nolockcheck",
                 "--norestore", "--nofirststartwizard", f"-env:UserInstallation={profile.as_uri()}",
                 "--convert-to", "xls:MS Excel 97", "--outdir", str(xls_dir), str(source_xlsx)],
                capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            source_xls = xls_dir / "source.xls"
            self.assertTrue(source_xls.is_file(), proc.stderr or proc.stdout)
            before = hashlib.sha256(source_xls.read_bytes()).hexdigest()
            result = inspect_workbook(source_xls, root, reveal=True)
            after = hashlib.sha256(source_xls.read_bytes()).hexdigest()

        self.assertEqual(result["status"], "MATCH_REVIEW")
        self.assertTrue(any(candidate["match"] for candidate in result["candidates"]))
        self.assertEqual(before, after)
        self.assertEqual(result["workbook"]["sha256_before"], result["workbook"]["sha256_after"])
        self.assertIn(result["workbook"]["converter"], {"libreoffice", "soffice"})
        self.assertTrue(any(item["match"] and item["comment_author"] == "Test Author"
                            for item in result["m10_comment_candidates"]))

    def test_hmac_normalization_known_answer(self):
        nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        phrase = normalize("silver maple ocean amber")
        expected = hmac.new(nonce, phrase.encode("ascii"), hashlib.sha256).digest()[:16]
        self.assertEqual(k08_component(nonce, phrase), expected)


if __name__ == "__main__":
    unittest.main()
