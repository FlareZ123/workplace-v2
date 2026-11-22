"""Synthetic exact-K04 tests for complete coupons printed as QR symbols."""
from __future__ import annotations

import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qrcode
from h17_k04_binary_window_intake import run_scan
from h17_k04_image_barcode_intake import read_image_barcodes


class OriginalHashBarcodeTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory(prefix="h17-barcode-sft-")
        self.addCleanup(self.root.cleanup)
        self.path = Path(self.root.name) / "recovered-original-coupon.png"
        self.mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
        self.component = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        self.payload = bytes(a ^ b for a, b in zip(self.mask, self.component))
        self.target = hashlib.sha256(self.component).hexdigest()

    def embed(self, payload: bytes) -> None:
        code = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8, border=4,
        )
        code.add_data(payload)
        code.make(fit=True)
        image = code.make_image(fill_color="black", back_color="white")
        out = io.BytesIO()
        image.save(out, "PNG")
        self.path.write_bytes(out.getvalue())

    def scan(self, digest=None):
        return run_scan(
            self.path, self.target if digest is None else digest,
            self.mask.hex().upper(), 1, 256 * 1024 * 1024,
            512 * 1024 * 1024, 4, 10000,
        )

    def test_printed_hex_masked_payload_reaches_complete_commitment(self):
        self.embed(b"K04-PAYLOAD=" + self.payload.hex().upper().encode("ascii"))
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        hit = result["hits"][0]
        self.assertEqual(hit["component_hex"], self.component.hex().upper())
        self.assertEqual(hit["kind"], "payload_xor_route_mask")
        self.assertIn("image-", hit["encoding"])
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), before)

    def test_binary_qr_with_8bit_octets_recovered_without_utf8_damage(self):
        self.embed(self.payload)
        decoded, errors = read_image_barcodes(self.path.read_bytes())
        self.assertTrue(any(raw == self.payload for _, raw in decoded), (decoded, errors))
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        self.assertEqual(result["hits"][0]["component_hex"], self.component.hex().upper())

    def test_second_frame_of_multiframe_tiff_is_recovered(self):
        from PIL import Image

        code = qrcode.QRCode(box_size=8, border=4)
        code.add_data(self.payload)
        code.make(fit=True)
        coupon = code.make_image(fill_color="black", back_color="white").convert("RGB")
        blank = Image.new("RGB", coupon.size, "white")
        self.path = self.path.with_suffix(".tiff")
        blank.save(self.path, format="TIFF", save_all=True,
                   append_images=[coupon])
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        self.assertEqual(result["hits"][0]["component_hex"], self.component.hex().upper())
        self.assertIn("frame1", result["hits"][0]["source"])

    def make_emf_bitmap_spool(self, kind: int) -> None:
        import struct
        from PIL import Image

        self.embed(b"K04-PAYLOAD=" + self.payload.hex().upper().encode("ascii"))
        with Image.open(self.path) as source:
            bmp_image = io.BytesIO()
            source.convert("1").save(bmp_image, format="BMP")
        bmp = bmp_image.getvalue()
        pixel_offset = struct.unpack_from("<I", bmp, 10)[0]
        bitmap_header = bmp[14:pixel_offset]
        pixels = bmp[pixel_offset:]
        width, height = struct.unpack_from("<ii", bitmap_header, 4)
        base_size = 76 if kind == 80 else 80
        record_bytes = base_size + len(bitmap_header) + len(pixels)
        record = bytearray((record_bytes + 3) & ~3)
        struct.pack_into("<II", record, 0, kind, len(record))
        struct.pack_into("<4i", record, 8, 0, 0, width, height)
        struct.pack_into("<4i", record, 24, 0, 0, 0, 0)
        struct.pack_into("<2i", record, 40, width, height)
        struct.pack_into(
            "<4I", record, 48, base_size, len(bitmap_header),
            base_size + len(bitmap_header), len(pixels),
        )
        record[base_size:base_size + len(bitmap_header)] = bitmap_header
        record[
            base_size + len(bitmap_header):
            base_size + len(bitmap_header) + len(pixels)
        ] = pixels
        header = bytearray(88)
        struct.pack_into("<II", header, 0, 1, 88)
        header[40:44] = b" EMF"
        struct.pack_into("<II", header, 48, 88 + len(record) + 20, 3)
        footer = bytearray(20)
        struct.pack_into("<II", footer, 0, 14, 20)
        self.path = self.path.with_suffix(".spl")
        self.path.write_bytes(b"SHD-FAKE\x00\x01" + header + record + footer)

    def test_original_coupon_from_emf_stretchdibits(self):
        self.make_emf_bitmap_spool(81)
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        self.assertEqual(result["hits"][0]["component_hex"], self.component.hex().upper())
        self.assertIn("emf-bitmap-", result["hits"][0]["encoding"])

    def test_original_coupon_from_emf_setdibitstodevice(self):
        self.make_emf_bitmap_spool(80)
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        self.assertEqual(result["hits"][0]["component_hex"], self.component.hex().upper())

    def test_corrupted_emf_record_rejected(self):
        self.make_emf_bitmap_spool(81)
        blob = bytearray(self.path.read_bytes())
        signature = blob.index(b" EMF")
        start = signature - 40
        struct_offset = start + 48
        blob[struct_offset] ^= 1
        self.path.write_bytes(blob)
        result = self.scan()
        self.assertEqual(result["hits"], [])

    def test_pdf_image_xobject_coupon_reaches_original_commitment(self):
        import pymupdf

        self.embed(b"K04-PAYLOAD=" + self.payload.hex().upper().encode("ascii"))
        document = pymupdf.open()
        page = document.new_page(width=260, height=260)
        page.insert_image(page.rect, stream=self.path.read_bytes())
        self.path = self.path.with_suffix(".pdf")
        self.path.write_bytes(document.tobytes())
        document.close()
        result = self.scan()
        self.assertTrue(result["hits"], result)
        self.assertTrue(any(
            hit["component_hex"] == self.component.hex().upper()
            and "pdf-image" in hit["encoding"]
            for hit in result["hits"]
        ), result)

    def test_vector_pdf_qr_coupon_recovered_from_rendered_page(self):
        import pymupdf

        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
        qr.add_data(self.payload.hex().upper().encode("ascii"))
        qr.make(fit=True)
        cells = qr.get_matrix()
        document = pymupdf.open()
        page = document.new_page(width=240, height=240)
        painter = page.new_shape()
        cell = 240 / len(cells)
        for y, row in enumerate(cells):
            for x, dark in enumerate(row):
                if dark:
                    painter.draw_rect(pymupdf.Rect(
                        x * cell, y * cell, (x + 1) * cell, (y + 1) * cell
                    ))
        painter.finish(color=(0, 0, 0), fill=(0, 0, 0))
        painter.commit()
        self.path = self.path.with_suffix(".pdf")
        self.path.write_bytes(document.tobytes())
        document.close()
        result = self.scan()
        self.assertTrue(result["hits"], result)
        self.assertTrue(any(
            "pdf-page-1-rendered" in hit["source"]
            and hit["component_hex"] == self.component.hex().upper()
            for hit in result["hits"]
        ), result)

    def test_encrypted_pdf_coupon_not_read_without_authorized_key(self):
        import pymupdf

        self.embed(self.payload.hex().upper().encode("ascii"))
        document = pymupdf.open()
        page = document.new_page(width=260, height=260)
        page.insert_image(page.rect, stream=self.path.read_bytes())
        self.path = self.path.with_suffix(".pdf")
        self.path.write_bytes(document.tobytes(
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            user_pw="test-only-fixture-secret",
            owner_pw="test-only-fixture-secret",
        ))
        document.close()
        self.assertEqual(self.scan()["hits"], [])

    def test_full_rec8_reconstruction_from_pdf_coupon_and_long_caption(self):
        import pymupdf

        from h17_ax7782_k08_phrase_intake import k08_component, normalize
        from h17_complete_native_recovery import recover_complete

        self.embed(b"ORIGINAL-COUPON=" + self.payload.hex().upper().encode("ascii"))
        doc = pymupdf.open()
        page = doc.new_page(width=260, height=260)
        page.insert_image(page.rect, stream=self.path.read_bytes())
        self.path = self.path.with_suffix(".pdf")
        self.path.write_bytes(doc.tobytes())
        doc.close()

        caption = (
            "after the last cup the sea remained beyond the window and "
            "the little lamp waited for the next watch to gather around "
            "the table"
        )
        self.assertGreater(len(normalize(caption)), 96)
        caption_source = Path(self.root.name) / "Emily-original-final.txt"
        caption_source.write_text("Final author margin:\n\n" + caption + "\n\n", encoding="utf-8")
        nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
        final = {
            f"K{i:02d}": (bytes([i]) * 16).hex().upper()
            for i in (1, 2, 3, 5, 6, 7)
        }
        final["K04"] = self.component.hex().upper()
        final["K08"] = k08_component(nonce, normalize(caption)).hex().upper()
        prefix = "CEG-ARCHIVE-RECOVERY/v1\n"
        slots = {
            key: hashlib.sha256(bytes.fromhex(value)).hexdigest()
            for key, value in final.items()
        }
        combined = hashlib.sha256(
            (prefix + "".join(
                final[f"K{i:02d}"] + "\n" for i in range(1, 9)
            )).encode("ascii")
        ).hexdigest()
        original_pdf_sha = hashlib.sha256(self.path.read_bytes()).hexdigest()
        original_caption_sha = hashlib.sha256(caption_source.read_bytes()).hexdigest()
        recovered = recover_complete(
            self.path, caption_source,
            targets={
                "slot_sha256": slots,
                "combined_prefix": prefix,
                "combined_sha256": combined,
            },
            routing={
                "K04": {"masked_component": self.mask.hex().upper()},
                "K08": {"desk_nonce": nonce.hex().upper()},
            },
            six_pass={key: value for key, value in final.items()
                      if key not in ("K04", "K08")},
        )
        self.assertTrue(recovered["accepted"], recovered)
        self.assertEqual(recovered["candidate"], final)
        self.assertEqual(recovered["verification"]["passed"], 8)
        self.assertEqual(recovered["verification"]["combined"], "PASS")
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), original_pdf_sha)
        self.assertEqual(
            hashlib.sha256(caption_source.read_bytes()).hexdigest(),
            original_caption_sha,
        )

    def test_pdf_native_text_complete_coupon(self):
        import pymupdf

        document = pymupdf.open()
        page = document.new_page(width=420, height=220)
        page.insert_text(
            (20, 60), "PAYLOAD=" + self.payload.hex().upper(), fontsize=11,
        )
        self.path = self.path.with_suffix(".pdf")
        self.path.write_bytes(document.tobytes(deflate=True))
        document.close()
        result = self.scan()
        self.assertTrue(any(
            hit["component_hex"] == self.component.hex().upper()
            and "pdf-page-1-native-text" in hit["source"]
            for hit in result["hits"]
        ), result)

    def test_pdf_native_text_spacing_can_be_collapsed(self):
        import pymupdf

        document = pymupdf.open()
        page = document.new_page(width=480, height=220)
        page.insert_text(
            (20, 60),
            " ".join(self.payload.hex().upper()),
            fontsize=9,
        )
        self.path = self.path.with_suffix(".pdf")
        self.path.write_bytes(document.tobytes(deflate=True))
        document.close()
        result = self.scan()
        self.assertTrue(any(
            hit["component_hex"] == self.component.hex().upper()
            and "pdf-page-1-condensed-text" in hit["source"]
            for hit in result["hits"]
        ), result)

    def make_pcl_raster_spool(self, mode: int) -> None:
        from PIL import Image

        self.embed(b"K04-PAYLOAD=" + self.payload.hex().upper().encode("ascii"))
        with Image.open(self.path) as source:
            qr = source.convert("1")
            width, height = qr.size
            row_bytes = (width + 7) // 8
            image_bytes = qr.tobytes()
        self.assertEqual(len(image_bytes), row_bytes * height)
        payload = bytearray(
            b"\x1b*r" + str(width).encode("ascii") + b"S"
            + b"\x1b*r" + str(height).encode("ascii") + b"T"
            + b"\x1b*r1A"
        )
        for row_index in range(height):
            base = row_index * row_bytes
            # Inverse of Pillow's ink polarity: black PCL pixel is 1.
            row = bytes(byte ^ 255 for byte in image_bytes[base:base + row_bytes])
            if mode == 0:
                compressed = row
            elif mode == 1:
                compressed = b"".join(bytes([0, byte]) for byte in row)
            elif mode == 2:
                compressed = bytes([len(row) - 1]) + row
            else:
                raise AssertionError("unsupported test mode")
            if row_index == 0:
                # PCL lower-case m continues same ESC*b parameter group.
                header = b"\x1b*b" + str(mode).encode("ascii") + b"m"
            else:
                header = b"\x1b*b"
            payload.extend(
                header + str(len(compressed)).encode("ascii") + b"W" + compressed
            )
        payload.extend(b"\x1b*rB")
        self.path = self.path.with_suffix(".prn")
        self.path.write_bytes(b"\x1b%-12345X@PJL JOB\n" + payload)

    def test_native_pcl_uncompressed_raster_coupon(self):
        self.make_pcl_raster_spool(0)
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        self.assertEqual(result["hits"][0]["component_hex"], self.component.hex().upper())
        self.assertIn("pcl-raster-", result["hits"][0]["encoding"])

    def test_native_pcl_rle_raster_coupon(self):
        self.make_pcl_raster_spool(1)
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        self.assertEqual(result["hits"][0]["component_hex"], self.component.hex().upper())

    def test_native_pcl_tiff_packbits_raster_coupon(self):
        self.make_pcl_raster_spool(2)
        result = self.scan()
        self.assertEqual(len(result["hits"]), 1, result)
        self.assertEqual(result["hits"][0]["component_hex"], self.component.hex().upper())

    def test_native_pcl_corrupt_unterminated_raster_rejected(self):
        self.make_pcl_raster_spool(2)
        self.path.write_bytes(self.path.read_bytes()[:-5])
        self.assertEqual(self.scan()["hits"], [])

    def test_original_commitment_mismatch_is_never_accepted(self):
        self.embed(b"K04-PAYLOAD=" + self.payload.hex().upper().encode("ascii"))
        wrong_target = hashlib.sha256(b"not the component").hexdigest()
        self.assertEqual(self.scan(digest=wrong_target)["hits"], [])

    def test_direct_component_barcode_remains_independent(self):
        self.embed(self.component.hex().upper().encode("ascii"))
        hits = self.scan()["hits"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["kind"], "direct_component")


if __name__ == "__main__":
    unittest.main(verbosity=2)
