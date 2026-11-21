import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace

from h17_k08_mug_stock_cell_selector import (
    aes_ecb_decrypt, coordinate_sets, excel_address, excel_column,
    evaluate_candidate, k08_component, map_sheets, normalize, sample_cells,
)


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
        raw = bytes.fromhex("E5407654D33238607DFA324B94656E1D")
        sets = coordinate_sets(raw)
        self.assertEqual(sets["high_byte_row_low_byte_column"],
                         [(229,64),(118,84),(211,50),(56,96),(125,250),(50,75),(148,101),(110,29)])
        self.assertEqual(sets["low_byte_row_high_byte_column"],
                         [(64,229),(84,118),(50,211),(96,56),(250,125),(75,50),(101,148),(29,110)])

    def test_excel_addresses(self):
        self.assertEqual(excel_column(64), "BL")
        self.assertEqual(excel_column(250), "IP")
        self.assertEqual(excel_address(229,64), "BL229")
        self.assertEqual(excel_address(125,250), "IP125")

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

    def test_ps0323_aes_plaintext_is_pinned(self):
        nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
        ciphertext = bytes.fromhex("1E51EFD2E5CA8F4E1FC8B49297B3D74F")
        self.assertEqual(aes_ecb_decrypt(nonce, ciphertext).hex().upper(),
                         "E5407654D33238607DFA324B94656E1D")

    def test_candidate_hmac_commitment_path(self):
        nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
        phrase = "one two three four five six seven eight"
        component = k08_component(nonce, normalize(phrase))
        target = bytes.fromhex(__import__("hashlib").sha256(component).hexdigest())
        cells = [{"in_bounds":True,"value":word} for word in phrase.split()]
        result = evaluate_candidate(cells, nonce, target, "high_low", 1, "single")
        self.assertTrue(result["match"])

    def test_end_to_end_synthetic_workbook_match_and_read_only_hash(self):
        nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
        phrase = "x x x x x x x x"
        component = k08_component(nonce, normalize(phrase))
        target = hashlib.sha256(component).hexdigest()

        class FilledSheet:
            name = "Sheet1"
            nrows = 257
            ncols = 257
            def cell(self, row, col):
                return SimpleNamespace(value="x", ctype=1)

        class FakeBook:
            def __init__(self):
                self.sheet = FilledSheet()
            def sheet_names(self):
                return ["Sheet1"]
            def sheet_by_name(self, name):
                self.assert_name = name
                return self.sheet
            def release_resources(self):
                self.released = True

        fake_book = FakeBook()
        fake_xlrd = ModuleType("xlrd")
        fake_xlrd.open_workbook = lambda **kwargs: fake_book

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "evidence" / "print").mkdir(parents=True)
            (root / "evidence" / "recovery-routing.json").write_text(
                json.dumps({"K08":{"desk_nonce":nonce.hex()}}), encoding="utf-8")
            (root / "acceptance.json").write_text(
                json.dumps({"slot_sha256":{"K08":target}}), encoding="utf-8")
            (root / "evidence" / "print" / "spool-reconstruction.log").write_text(
                "2026-10-03T18:25:00Z JOB=PS-261003-0323 ATTEMPT=1 STATE=ACK "
                "CLASS=RECOVER PAYLOAD=1E51EFD2E5CA8F4E1FC8B49297B3D74F DEST=store\n",
                encoding="utf-8")
            workbook = root / "mug-stock.xls"
            workbook.write_bytes(b"synthetic workbook bytes")
            before = hashlib.sha256(workbook.read_bytes()).hexdigest()
            previous_xlrd = sys.modules.get("xlrd")
            sys.modules["xlrd"] = fake_xlrd
            try:
                result = inspect_workbook(workbook, root)
            finally:
                if previous_xlrd is None:
                    sys.modules.pop("xlrd", None)
                else:
                    sys.modules["xlrd"] = previous_xlrd
            after = hashlib.sha256(workbook.read_bytes()).hexdigest()

        self.assertEqual(result["status"], "MATCH_REVIEW")
        self.assertEqual(len(result["candidates"]), 4)
        self.assertTrue(all(candidate["match"] for candidate in result["candidates"]))
        self.assertEqual(before, after)
        self.assertEqual(result["workbook"]["sha256_before"], result["workbook"]["sha256_after"])
        self.assertTrue(getattr(fake_book, "released", False))

    def test_hmac_normalization_known_answer(self):
        nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
        phrase = normalize("A good watch leaves the room ready for the next pair of hands")
        self.assertEqual(k08_component(nonce, phrase).hex().upper(),
                         "BF889359B0303F2B2B2FD96AE841210B")


if __name__ == "__main__":
    unittest.main()
