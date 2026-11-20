from __future__ import annotations

import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h17_biff_officeart import (  # noqa: E402
    CFB_SIGNATURE, ENDOFCHAIN, FATSECT, FREESECT,
    extract_xls_officeart, OfficeArtParseError,
)


def br(record_id, payload=b""):
    return struct.pack("<HH", record_id, len(payload)) + payload


def er(record_type, payload, instance=0, version=0):
    return struct.pack("<HHI", (instance << 4) | version, record_type, len(payload)) + payload


def drawing():
    props = [(0x0380, "M10 photo"), (0x0381, "SYNTHETIC_ONLY_OFFICEART_DESC_6F31")]
    entries = [struct.pack("<HI", 0x0104, 1)]
    complex_data = []
    for prop_id, value in props:
        raw = value.encode("utf-16le") + b"\x00\x00"
        entries.append(struct.pack("<HI", 0x8000 | prop_id, len(raw)))
        complex_data.append(raw)
    opt = er(0xF00B, b"".join(entries + complex_data), len(entries), 3)
    sp = er(0xF00A, struct.pack("<II", 0x1234, 10), 75, 2)
    anchor = er(0xF010, struct.pack("<H H h H h H h H h", 3, 12, 100, 9, 12, 13, 900, 10, 200))
    shape = er(0xF004, sp + opt + anchor, version=15)
    return er(0xF002, er(0xF008, struct.pack("<II", 1, 0x1234)) + er(0xF003, shape, version=15), version=15)


def workbook_stream(include_drawing=True, regular=True):
    bof = br(0x0809, b"\x00" * 16)
    sheet0 = br(0x0085, struct.pack("<I", 0) + bytes([0, 0, 6, 0]) + b"Sheet1")
    glob = bof + sheet0 + br(0x000A)
    offset = len(glob)
    glob = bof + br(0x0085, struct.pack("<I", offset) + bytes([0, 0, 6, 0]) + b"Sheet1") + br(0x000A)
    sheet = br(0x0809, b"\x00" * 16)
    if include_drawing:
        raw = drawing()
        split = len(raw) // 2
        sheet += br(0x00EC, raw[:split]) + br(0x005D, b"\x00" * 8) + br(0x00EC, raw[split:])
    result = glob + sheet + br(0x000A)
    if regular and len(result) < 4097:
        result += br(0xFFFF, b"P" * (4097 - len(result) - 4))
    return result


def dirent(name, kind, start, size, child=0xFFFFFFFF):
    b = bytearray(128)
    encoded = name.encode("utf-16le") + b"\x00\x00"
    b[:len(encoded)] = encoded
    struct.pack_into("<H", b, 64, len(encoded))
    b[66], b[67] = kind, 1
    struct.pack_into("<III", b, 68, 0xFFFFFFFF, 0xFFFFFFFF, child)
    struct.pack_into("<IQ", b, 116, start, size)
    return bytes(b)


def cfb(workbook, mini=False):
    sector = 512
    if mini:
        count = (len(workbook) + 63) // 64
        mini_fat = [FREESECT] * 128
        for i in range(count):
            mini_fat[i] = i + 1 if i + 1 < count else ENDOFCHAIN
        mini_fat_sector = struct.pack("<128I", *mini_fat)
        mini_stream = workbook + b"\x00" * (count * 64 - len(workbook))
        fat = [FREESECT] * 128
        fat[0], fat[1], fat[2], fat[3] = FATSECT, ENDOFCHAIN, ENDOFCHAIN, ENDOFCHAIN
        directory = dirent("Root Entry", 5, 3, len(mini_stream), 1) + dirent("Workbook", 2, 0, len(workbook))
        header = bytearray(512)
        header[:8] = CFB_SIGNATURE
        struct.pack_into("<HHHHH", header, 24, 0x003E, 3, 0xFFFE, 9, 6)
        struct.pack_into("<IIIIIIII", header, 40, 0, 1, 1, 0, 4096, 2, 1, ENDOFCHAIN)
        struct.pack_into("<I", header, 72, 0)
        struct.pack_into("<109I", header, 76, *([0] + [FREESECT] * 108))
        return bytes(header) + struct.pack("<128I", *fat) + directory + b"\x00" * (sector - len(directory)) + mini_fat_sector + mini_stream + b"\x00" * (sector - len(mini_stream))
    count = (len(workbook) + 511) // 512
    fat = [FREESECT] * 128
    fat[0], fat[1] = FATSECT, ENDOFCHAIN
    for i in range(count):
        sid = i + 2
        fat[sid] = sid + 1 if i + 1 < count else ENDOFCHAIN
    directory = dirent("Root Entry", 5, ENDOFCHAIN, 0, 1) + dirent("Workbook", 2, 2, len(workbook))
    header = bytearray(512)
    header[:8] = CFB_SIGNATURE
    struct.pack_into("<HHHHH", header, 24, 0x003E, 3, 0xFFFE, 9, 6)
    struct.pack_into("<IIIIIIII", header, 40, 0, 1, 1, 0, 4096, ENDOFCHAIN, 0, ENDOFCHAIN)
    struct.pack_into("<I", header, 72, 0)
    struct.pack_into("<109I", header, 76, *([0] + [FREESECT] * 108))
    padded = workbook + b"\x00" * (count * 512 - len(workbook))
    return bytes(header) + struct.pack("<128I", *fat) + directory + b"\x00" * (sector - len(directory)) + padded


class OfficeArtBiffTests(unittest.TestCase):
    def test_regular_stream_description_name_and_m10_anchor(self):
        result = extract_xls_officeart(cfb(workbook_stream()))
        self.assertEqual(result["workbook_stream"], "Workbook")
        self.assertEqual(len(result["shapes"]), 1)
        shape = result["shapes"][0]
        self.assertEqual(shape["shape_type"], 75)
        self.assertEqual(shape["shape_id"], 0x1234)
        self.assertTrue(shape["is_picture_shape"])
        self.assertEqual(shape["anchor_cell"], "M10")
        self.assertEqual(shape["anchor"]["bottom_right_cell"], "N11")
        self.assertEqual(shape["wz_name"], "M10 photo")
        self.assertEqual(shape["wz_description"], "SYNTHETIC_ONLY_OFFICEART_DESC_6F31")
        self.assertEqual(shape["pib"], 1)
        self.assertEqual(result["warnings"], [])

    def test_mini_stream_workbook(self):
        result = extract_xls_officeart(cfb(workbook_stream(regular=False), mini=True))
        self.assertEqual(result["shapes"][0]["anchor_cell"], "M10")
        self.assertEqual(result["shapes"][0]["wz_description"], "SYNTHETIC_ONLY_OFFICEART_DESC_6F31")

    def test_no_drawing_returns_empty_shapes(self):
        self.assertEqual(extract_xls_officeart(cfb(workbook_stream(False)))["shapes"], [])

    def test_non_cfb_and_oversized_inputs_fail_closed(self):
        with self.assertRaises(OfficeArtParseError):
            extract_xls_officeart(b"not an xls")
        with self.assertRaises(OfficeArtParseError):
            extract_xls_officeart(b"x" * (64 * 1024 * 1024 + 1))

    @unittest.skipUnless(
        (shutil.which("libreoffice") or shutil.which("soffice"))
        and __import__("importlib").util.find_spec("openpyxl")
        and __import__("importlib").util.find_spec("PIL"),
        "LibreOffice, openpyxl and Pillow are required",
    )
    def test_real_libreoffice_biff_picture_anchor_is_read_before_conversion(self):
        from openpyxl import Workbook
        from openpyxl.drawing.image import Image as XLImage
        from PIL import Image as PILImage
        with tempfile.TemporaryDirectory(prefix="h17-officeart-lo-") as temp:
            root = Path(temp)
            xlsx, out, profile, image = root / "source.xlsx", root / "out", root / "profile", root / "p.png"
            out.mkdir(); profile.mkdir()
            PILImage.new("RGB", (24, 24), (0, 128, 128)).save(image, format="PNG")
            book = Workbook(); book.active.add_image(XLImage(str(image)), "M10")
            book.save(xlsx); book.close()
            converter = shutil.which("libreoffice") or shutil.which("soffice")
            proc = subprocess.run(
                [converter, "--headless", "--nologo", "--nodefault", "--nolockcheck",
                 "--norestore", "--nofirststartwizard", f"-env:UserInstallation={profile.as_uri()}",
                 "--convert-to", "xls:MS Excel 97", "--outdir", str(out), str(xlsx)],
                capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            result = extract_xls_officeart((out / "source.xls").read_bytes())
            pictures = [shape for shape in result["shapes"] if shape["is_picture_shape"]]
            self.assertEqual(len(pictures), 1)
            self.assertEqual(pictures[0]["anchor_cell"], "M10")
            self.assertEqual(pictures[0]["wz_name"], "Image 1")
            self.assertIsNone(pictures[0]["wz_description"])


if __name__ == "__main__":
    unittest.main()
