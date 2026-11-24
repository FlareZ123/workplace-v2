import hashlib
import struct
import unittest

from h17_k04_biff8_xf_candidate import derive_k01_cells
from h17_k04_mug_stock_xf_multitab_probe import (
    ProbeError, parse_group_sheets, probe_group_mapping,
)


def xf_payload(*, is_style=False, parent=0xFFF, fore=0, back=0):
    b = bytearray(20)
    struct.pack_into("<H", b, 4, ((parent & 0xFFF) << 4) | (int(is_style) << 2))
    struct.pack_into("<H", b, 8, 1 << 14)
    struct.pack_into("<I", b, 14, 1 << 26)
    struct.pack_into("<H", b, 18, (fore & 0x7F) | ((back & 0x7F) << 7))
    return bytes(b)


def make_parsed():
    cells = derive_k01_cells("049AAB2E1CDE7A82CD7C60234303C91A")
    xfs = [xf_payload(is_style=True, fore=2, back=3)]
    xfs.extend(xf_payload(parent=0, fore=i + 8, back=i + 40) for i in range(8))
    sheets = []
    for group_index, name in enumerate(("TabA", "TabB", "TabC", "TabD")):
        cell_xfs = {}
        for j in range(2):
            address = cells[group_index * 2 + j]
            import re
            letters, row = re.fullmatch(r"([A-Z]+)([0-9]+)", address).groups()
            col = 0
            for ch in letters:
                col = col * 26 + ord(ch) - ord("A") + 1
            cell_xfs[(int(row) - 1, col - 1)] = 1 + group_index * 2 + j
        sheets.append({"name": name, "visibility": 0, "sheet_type": 0, "cell_xfs": cell_xfs})
    return {"xfs": xfs, "palette": {}, "sheets": sheets}, cells


def target(payload, mask):
    return hashlib.sha256(bytes(a ^ b for a, b in zip(payload, mask))).hexdigest()


class MultiTabProbeTests(unittest.TestCase):
    def setUp(self):
        self.parsed, self.cells = make_parsed()
        self.sheets = ("TabA", "TabB", "TabC", "TabD")
        self.mask = bytes(range(16))

    def test_four_tab_colour_candidate_and_redaction(self):
        payload = bytes(v for i in range(8) for v in (i + 8, i + 40))
        result = probe_group_mapping(
            self.parsed, self.sheets, self.cells, self.mask, target(payload, self.mask)
        )
        self.assertEqual(result["status"], "COMMITMENT_MATCH_REQUIRES_SOURCE_REVIEW")
        self.assertTrue(result["colour_index_check"]["pass"])
        self.assertFalse(result["raw_ixfe_little_endian_check"]["pass"])
        self.assertEqual(result["group_sheet_mapping"],
                         {"A": "TabA", "B": "TabB", "C": "TabC", "D": "TabD"})
        self.assertEqual(len(result["selected_cell_sheets"]), 8)
        self.assertNotIn("payload_hex", result)
        self.assertNotIn("component_hex", result)

    def test_four_tab_raw_ixfe_candidate(self):
        payload = b"".join(struct.pack("<H", i) for i in range(1, 9))
        result = probe_group_mapping(
            self.parsed, self.sheets, self.cells, self.mask, target(payload, self.mask)
        )
        self.assertEqual(result["status"], "COMMITMENT_MATCH_REQUIRES_SOURCE_REVIEW")
        self.assertTrue(result["raw_ixfe_little_endian_check"]["pass"])
        self.assertFalse(result["colour_index_check"]["pass"])

    def test_wrong_group_mapping_is_not_silently_reordered(self):
        result = probe_group_mapping(
            self.parsed, ("TabB", "TabA", "TabC", "TabD"), self.cells,
            self.mask, "0" * 64,
        )
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(result["missing_cells"])

    def test_missing_selected_cell_is_incomplete(self):
        address = self.cells[4]
        letters, row = __import__("re").fullmatch(r"([A-Z]+)([0-9]+)", address).groups()
        col = 0
        for ch in letters:
            col = col * 26 + ord(ch) - ord("A") + 1
        self.parsed["sheets"][2]["cell_xfs"].pop((int(row) - 1, col - 1))
        result = probe_group_mapping(
            self.parsed, self.sheets, self.cells, self.mask, "0" * 64
        )
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn(address, result["missing_cells"])

    def test_missing_sheet_is_incomplete(self):
        result = probe_group_mapping(
            self.parsed, ("TabA", "Missing", "TabC", "TabD"), self.cells,
            self.mask, "0" * 64,
        )
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["missing_sheets"], ["Missing"])

    def test_non_worksheet_group_is_skipped(self):
        self.parsed["sheets"][1]["sheet_type"] = 2
        result = probe_group_mapping(
            self.parsed, self.sheets, self.cells, self.mask, "0" * 64
        )
        self.assertEqual(result["status"], "SKIPPED_NON_WORKSHEET")

    def test_four_distinct_names_are_required(self):
        with self.assertRaises(ProbeError):
            parse_group_sheets("TabA,TabB,TabC")
        with self.assertRaises(ProbeError):
            parse_group_sheets("TabA,TabB,TabB,TabD")


if __name__ == "__main__":
    unittest.main()
