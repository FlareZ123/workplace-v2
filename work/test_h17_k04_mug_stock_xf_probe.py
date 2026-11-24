import hashlib
import struct
import unittest

from h17_k04_biff8_xf_candidate import derive_k01_cells
from h17_k04_mug_stock_xf_probe import parse_workbook_stream, probe_sheet


def rec(record_id, payload):
    return struct.pack("<HH", record_id, len(payload)) + payload


def xf_payload(*, is_style=False, parent=0xFFF, f_atr_pat=True,
               fill_pattern=1, fore=0, back=0):
    b = bytearray(20)
    protection = ((parent & 0xFFF) << 4) | (int(is_style) << 2)
    struct.pack_into("<H", b, 4, protection)
    struct.pack_into("<H", b, 8, int(f_atr_pat) << 14)
    struct.pack_into("<I", b, 14, (fill_pattern & 0x3F) << 26)
    struct.pack_into("<H", b, 18, (fore & 0x7F) | ((back & 0x7F) << 7))
    return bytes(b)


class ProbeTests(unittest.TestCase):
    def make_stream(self):
        k01 = "049AAB2E1CDE7A82CD7C60234303C91A"
        cells = derive_k01_cells(k01)
        xfs = [xf_payload(is_style=True, fore=2, back=3)]
        xfs.extend(
            xf_payload(
                is_style=False,
                parent=0,
                f_atr_pat=True,
                fore=i + 8,
                back=40 + i,
                fill_pattern=1,
            )
            for i in range(8)
        )
        bof = rec(0x0809, bytes(16))
        palette = rec(
            0x0092,
            struct.pack("<H", 2) + bytes([0, 128, 128, 0, 0, 255, 255, 0]),
        )
        xf_records = [rec(0x00E0, x) for x in xfs]
        eof = rec(0x000A, b"")
        name = b"Sheet1"
        boundsheet_len = 4 + 8 + len(name)
        sheet_offset = (
            len(bof)
            + sum(map(len, xf_records))
            + len(palette)
            + boundsheet_len
            + len(eof)
        )
        boundsheet_payload = (
            struct.pack("<I", sheet_offset)
            + bytes([0, 0, len(name), 0])
            + name
        )
        global_stream = (
            bof
            + b"".join(xf_records)
            + palette
            + rec(0x0085, boundsheet_payload)
            + eof
        )
        sheet_records = [bof]
        for address, xf_index in zip(cells, range(1, 9)):
            import re

            match = re.fullmatch(r"([A-Z]+)([0-9]+)", address)
            col = 0
            for ch in match.group(1):
                col = col * 26 + ord(ch) - ord("A") + 1
            row = int(match.group(2))
            sheet_records.append(
                rec(0x0201, struct.pack("<HHH", row - 1, col - 1, xf_index))
            )
        sheet_records.append(eof)
        return global_stream + b"".join(sheet_records), cells

    def test_exact_cells_parse_and_candidate_commitment_match(self):
        stream, cells = self.make_stream()
        parsed = parse_workbook_stream(stream)
        self.assertEqual(len(parsed["xfs"]), 9)
        self.assertEqual(parsed["sheets"][0]["name"], "Sheet1")
        self.assertEqual(len(parsed["sheets"][0]["cell_xfs"]), 8)
        payload = bytes(x for i in range(8) for x in (i + 8, 40 + i))
        mask = bytes(range(16))
        expected = hashlib.sha256(bytes(a ^ b for a, b in zip(payload, mask))).hexdigest()
        result = probe_sheet(
            parsed["sheets"][0], parsed["xfs"], parsed["palette"], cells, mask, expected
        )
        self.assertEqual(result["status"], "COMMITMENT_MATCH_REQUIRES_SOURCE_REVIEW")
        self.assertEqual(result["payload_hex"], payload.hex().upper())
        self.assertEqual(result["styles"][0]["fore_rgb"], (0, 128, 128))

    def test_missing_selected_cell_is_incomplete(self):
        stream, cells = self.make_stream()
        parsed = parse_workbook_stream(stream)
        parsed["sheets"][0]["cell_xfs"].pop((3, 153))
        result = probe_sheet(
            parsed["sheets"][0],
            parsed["xfs"],
            parsed["palette"],
            cells,
            bytes(range(16)),
            "0" * 64,
        )
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("EX4", result["missing_cells"])

    def test_non_worksheet_is_skipped(self):
        stream, cells = self.make_stream()
        parsed = parse_workbook_stream(stream)
        parsed["sheets"][0]["sheet_type"] = 2
        result = probe_sheet(
            parsed["sheets"][0],
            parsed["xfs"],
            parsed["palette"],
            cells,
            bytes(range(16)),
            "0" * 64,
        )
        self.assertEqual(result["status"], "SKIPPED_NON_WORKSHEET")


if __name__ == "__main__":
    unittest.main()
