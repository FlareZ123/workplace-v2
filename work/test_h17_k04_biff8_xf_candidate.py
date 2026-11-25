import hashlib
import struct
import unittest

from h17_k04_biff8_xf_candidate import (
    XFError,
    assemble_k04_payload,
    check_k04_commitment,
    derive_k01_cells,
    parse_xf_payload,
    parse_palette_payload,
    palette_color,
    verify_and_derive_k01_cells,
)


def xf_payload(*, is_style=False, parent=0xFFF, f_atr_pat=True,
               fill_pattern=1, fore=0, back=0, pivot=0, reserved=0):
    """Create a 20-byte BIFF8 XF payload with only relevant fields populated."""
    b = bytearray(20)
    protection = ((parent & 0xFFF) << 4) | (int(is_style) << 2)
    struct.pack_into("<H", b, 4, protection)
    used = int(f_atr_pat) << 14
    struct.pack_into("<H", b, 8, used)
    struct.pack_into("<I", b, 14, (fill_pattern & 0x3F) << 26)
    colour_word = ((fore & 0x7F) | ((back & 0x7F) << 7)
                   | ((pivot & 1) << 14) | ((reserved & 1) << 15))
    struct.pack_into("<H", b, 18, colour_word)
    return bytes(b)


class XFTests(unittest.TestCase):
    def test_k01_addresses_are_source_ordered(self):
        raw = "049AAB2E1CDE7A82CD7C60234303C91A"
        self.assertEqual(
            derive_k01_cells(raw),
            ("EX4", "AT171", "HN28", "DZ122", "DT205", "AI96", "C67", "Z201"),
        )
        digest = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
        self.assertEqual(verify_and_derive_k01_cells(raw, digest), derive_k01_cells(raw))
        with self.assertRaises(XFError):
            verify_and_derive_k01_cells(raw, "0" * 64)

    def test_extracts_packed_seven_bit_fore_back(self):
        p = parse_xf_payload(xf_payload(fore=0x35, back=0x52, fill_pattern=3))
        self.assertEqual(p.foreground_index, 0x35)
        self.assertEqual(p.background_index, 0x52)
        self.assertEqual(p.fill_pattern, 3)

    def test_parse_palette_payload_and_custom_indexes(self):
        payload = struct.pack("<H", 2) + bytes([0, 128, 128, 0, 0, 255, 255, 0])
        palette = parse_palette_payload(payload)
        self.assertEqual(palette[8], (0, 128, 128, 0))
        self.assertEqual(palette_color(8, palette), (0, 128, 128))
        self.assertIsNone(palette_color(64, palette))
        with self.assertRaises(XFError):
            parse_palette_payload(payload[:-1])

    def test_fatrpat_one_uses_cell_xf(self):
        parent = xf_payload(is_style=True, fore=0x11, back=0x22)
        cell = xf_payload(is_style=False, parent=0, f_atr_pat=True, fore=0x33, back=0x44)
        self.assertEqual(assemble_k04_payload([1] * 8, [parent, cell]), bytes([0x33, 0x44] * 8))

    def test_fatrpat_zero_inherits_parent_style(self):
        parent = xf_payload(is_style=True, fore=0x12, back=0x34, fill_pattern=4)
        cell = xf_payload(is_style=False, parent=0, f_atr_pat=False, fore=0x55, back=0x66)
        self.assertEqual(assemble_k04_payload([1] * 8, [parent, cell]), bytes([0x12, 0x34] * 8))

    def test_candidate_order_and_commitment(self):
        xfs = [xf_payload(is_style=True, fore=1, back=2)]
        xfs.extend(xf_payload(is_style=False, parent=0, f_atr_pat=True, fore=i, back=127-i) for i in range(8))
        payload = assemble_k04_payload(list(range(1, 9)), xfs)
        self.assertEqual(payload, b"".join(bytes([i, 127-i]) for i in range(8)))
        mask = bytes(range(16))
        expected = hashlib.sha256(bytes(a ^ b for a, b in zip(payload, mask))).hexdigest()
        public = check_k04_commitment(payload, mask, expected)
        self.assertTrue(public["pass"])
        self.assertNotIn("component_hex", public)
        self.assertNotIn("payload_hex", public)
        self.assertTrue(public["redaction_applied"])

    def test_rejects_style_xf_as_cell_xf(self):
        with self.assertRaises(XFError):
            assemble_k04_payload([0] * 8, [xf_payload(is_style=True, fore=1, back=2)])

    def test_rejects_missing_parent(self):
        with self.assertRaises(XFError):
            assemble_k04_payload([0] * 8, [xf_payload(is_style=False, parent=0x123, f_atr_pat=False)])

    def test_rejects_wrong_width(self):
        with self.assertRaises(XFError):
            parse_xf_payload(b"\x00" * 19)
        with self.assertRaises(XFError):
            assemble_k04_payload([0] * 7, [xf_payload(is_style=True)])


if __name__ == "__main__":
    unittest.main()
