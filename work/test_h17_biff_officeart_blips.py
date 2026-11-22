from __future__ import annotations

import base64
import hashlib
import struct
import unittest
import zlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h17_biff_officeart_blips import extract_xls_officeart_blips  # noqa: E402
from test_h17_biff_officeart import br, er, cfb, drawing  # noqa: E402


def regular_workbook_fixture(workbook: bytes) -> bytes:
    """Keep the declared Workbook stream at or above the CFB mini-stream cutoff."""
    return cfb(workbook + bytes(max(0, 4096 - len(workbook))))


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def one_pixel_png() -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    idat = zlib.compress(b"\x00\x00\x00\x00\x00")
    return (
        signature
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", idat)
        + png_chunk(b"IEND", b"")
    )


def png_blip(image: bytes, uid: bytes = b"\x11" * 16) -> bytes:
    # OfficeArtBlipPNG: one 16-byte UID, one tag byte, then PNG bytes.
    return er(0xF01E, uid + b"\xFF" + image, instance=0x6E0, version=0)


def bse_record(blip: bytes | None, *, name: str = "photo.png",
               fo_delay: int = 0xFFFFFFFF, declared_size: int | None = None,
               uid: bytes = b"\x11" * 16) -> bytes:
    name_bytes = name.encode("utf-16le") if name else b""
    size = len(blip) if declared_size is None and blip else (declared_size or 0)
    fixed = struct.pack(
        "<BB16sHIIIBBBB",
        6, 6, uid, 0xFF00, size, 1 if blip else 0, fo_delay,
        0, len(name_bytes), 0, 0,
    )
    payload = fixed + name_bytes + (blip or b"")
    return er(0xF007, payload, instance=0, version=2)


def workbook_with_bstore(bstore_entries: list[bytes], *,
                         pib: int = 1, fbid: bool = True,
                         split_group: bool = False) -> bytes:
    bstore = er(
        0xF001,
        b"".join(bstore_entries),
        instance=len(bstore_entries),
        version=0xF,
    )
    dgg = er(0xF000, bstore, instance=0, version=0xF)
    if split_group and len(dgg) > 8:
        split = len(dgg) // 2
        drawing_group = br(0x00EB, dgg[:split]) + br(0x003C, dgg[split:])
    else:
        drawing_group = br(0x00EB, dgg)

    bof = br(0x0809, b"\x00" * 16)
    sheet_name = bytes([0, 0, 6, 0]) + b"Sheet1"
    sheet0 = br(0x0085, struct.pack("<I", 0) + sheet_name)
    global_eof = br(0x000A)
    sheet_offset = len(bof) + len(drawing_group) + len(sheet0) + len(global_eof)
    sheet0 = br(0x0085, struct.pack("<I", sheet_offset) + sheet_name)
    globals_stream = bof + drawing_group + sheet0 + global_eof

    sheet_stream = br(0x0809, b"\x00" * 16)
    # Rebuild the shape's pib property for the requested index/flag.
    props = [(0x0380, "M10 photo"), (0x0381, "SYNTHETIC_ONLY_OFFICEART_DESC_6F31")]
    entries = [struct.pack("<HI", (0x4104 if fbid else 0x0104), pib)]
    complex_data = []
    for prop_id, value in props:
        raw = value.encode("utf-16le") + b"\x00\x00"
        entries.append(struct.pack("<HI", 0x8000 | prop_id, len(raw)))
        complex_data.append(raw)
    opt = er(0xF00B, b"".join(entries + complex_data), len(entries), 3)
    sp = er(0xF00A, struct.pack("<II", 0x1234, 10), 75, 2)
    anchor = er(
        0xF010,
        struct.pack("<H H h H h H h H h", 3, 12, 100, 9, 12, 13, 900, 10, 200),
    )
    shape = er(0xF004, sp + opt + anchor, version=15)
    dg = er(
        0xF002,
        er(0xF008, struct.pack("<II", 1, 0x1234)) + er(0xF003, shape, version=15),
        version=15,
    )
    sheet_stream += br(0x00EC, dg) + br(0x000A)
    return globals_stream + sheet_stream


class OfficeArtBlipStoreTests(unittest.TestCase):
    def test_pib_resolves_to_embedded_png_and_optional_bytes(self):
        image = one_pixel_png()
        uid = b"\x22" * 16
        workbook = workbook_with_bstore([bse_record(png_blip(image, uid), uid=uid)])
        result = extract_xls_officeart_blips(regular_workbook_fixture(workbook), include_image_data=True)

        self.assertEqual(len(result["blip_store"]), 1)
        blip = result["blip_store"][0]
        self.assertEqual(blip["format"], "PNG")
        self.assertTrue(blip["magic_valid"])
        self.assertEqual(blip["length"], len(image))
        self.assertEqual(blip["sha256"], hashlib.sha256(image).hexdigest())
        self.assertEqual(base64.b64decode(blip["data_base64"]), image)

        shape = result["shapes"][0]
        self.assertEqual(shape["pib"], 1)
        self.assertTrue(shape["pib_fbid"])
        self.assertEqual(shape["blip_ref_status"], "resolved")
        self.assertEqual(shape["blip_ref"]["index"], 1)
        self.assertEqual(shape["blip_ref"]["sha256"], hashlib.sha256(image).hexdigest())

    def test_bstore_index_is_preserved_across_empty_entry(self):
        image = one_pixel_png()
        uid = b"\x33" * 16
        empty = bse_record(None, name="", fo_delay=0xFFFFFFFF, uid=b"\x00" * 16)
        picture = bse_record(png_blip(image, uid), name="second.png", uid=uid)
        result = extract_xls_officeart_blips(
            regular_workbook_fixture(workbook_with_bstore([empty, picture], pib=2)),
            include_image_data=True,
        )
        self.assertEqual(len(result["blip_store"]), 2)
        self.assertIsNone(result["blip_store"][0]["sha256"])
        self.assertEqual(result["shapes"][0]["blip_ref_status"], "resolved")
        self.assertEqual(result["shapes"][0]["blip_ref"]["index"], 2)
        self.assertEqual(result["shapes"][0]["blip_ref"]["name"], "second.png")

    def test_global_drawing_group_continue_is_joined(self):
        image = one_pixel_png()
        uid = b"\x44" * 16
        result = extract_xls_officeart_blips(
            regular_workbook_fixture(workbook_with_bstore(
                [bse_record(png_blip(image, uid), uid=uid)],
                split_group=True,
            ))
        )
        self.assertEqual(result["shapes"][0]["blip_ref_status"], "resolved")
        self.assertEqual(result["blip_store"][0]["sha256"], hashlib.sha256(image).hexdigest())

    def test_pib_without_fbid_is_not_resolved(self):
        image = one_pixel_png()
        uid = b"\x55" * 16
        result = extract_xls_officeart_blips(
            regular_workbook_fixture(workbook_with_bstore(
                [bse_record(png_blip(image, uid), uid=uid)],
                fbid=False,
            ))
        )
        self.assertEqual(result["shapes"][0]["blip_ref_status"], "pib-without-fBid")
        self.assertNotIn("blip_ref", result["shapes"][0])

    def test_missing_bstore_does_not_promote_pib(self):
        # A BIFF workbook with a shape reference but no global BStore.
        from test_h17_biff_officeart import workbook_stream
        result = extract_xls_officeart_blips(cfb(workbook_stream()))
        self.assertEqual(result["blip_store"], [])
        self.assertEqual(result["shapes"][0]["blip_ref_status"], "out-of-range")

    def test_delayed_blip_is_reported_but_not_followed(self):
        delayed = bse_record(None, name="delayed.png", fo_delay=1234, uid=b"\x66" * 16)
        result = extract_xls_officeart_blips(regular_workbook_fixture(workbook_with_bstore([delayed])))
        self.assertTrue(result["blip_store"][0]["delayed"])
        self.assertEqual(result["shapes"][0]["blip_ref_status"], "unresolved")
        self.assertTrue(any("delayed blip reference is not resolved" in w
                            for w in result["blip_warnings"]))

    def test_bse_size_mismatch_is_warned_without_discarding_bounded_blip(self):
        image = one_pixel_png()
        uid = b"\x77" * 16
        bad_size = bse_record(
            png_blip(image, uid), uid=uid, declared_size=9999
        )
        result = extract_xls_officeart_blips(regular_workbook_fixture(workbook_with_bstore([bad_size])))
        self.assertEqual(result["shapes"][0]["blip_ref_status"], "resolved")
        self.assertTrue(any("declared blip size" in w for w in result["blip_warnings"]))


if __name__ == "__main__":
    unittest.main()
