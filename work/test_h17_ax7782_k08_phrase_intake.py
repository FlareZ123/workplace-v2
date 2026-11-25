#!/usr/bin/env python3
"""Positive controls for the source-backed AX-7782 K08 phrase scanner."""
import base64
import hashlib
import io
import json
from email.message import EmailMessage
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_ax7782_k08_phrase_intake as phrase_intake

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "resources"


class K08PhraseIntakeTests(unittest.TestCase):
    def test_original_normalization_and_hmac_known_answer(self):
        resources = SOURCE_ROOT
        nonce, target = phrase_intake.load_k08_rules(resources)
        normalized = phrase_intake.normalize("A good watch leaves the room ready for the next pair of hands.")
        self.assertEqual(normalized, "a good watch leaves the room ready for the next pair of hands")
        self.assertEqual(phrase_intake.k08_component(nonce, normalized).hex().upper(),
                         "BF889359B0303F2B2B2FD96AE841210B")
        self.assertEqual(len(target), 32)

    def test_exact_span_match_with_original_normalization(self):
        nonce = bytes(range(16))
        phrase = "the keeper leaves the lamp for the next watch"
        component = phrase_intake.k08_component(nonce, phrase)
        target = hashlib.sha256(component).digest()
        hits = []
        tested = phrase_intake.scan_phrase_spans(
            "Draft discarded. The keeper—leaves the lamp for the next watch! Signed copy.",
            nonce, target, "fixture.txt", 16, hits,
        )
        self.assertGreater(tested, 0)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["normalized_phrase"], phrase)
        self.assertEqual(hits[0]["component_hex"], component.hex().upper())
        wrong_hits = []
        phrase_intake.scan_phrase_spans("the keeper left a different lamp", nonce, target,
                                        "negative.txt", 16, wrong_hits)
        self.assertEqual(wrong_hits, [])

    def test_embedded_ascii_and_utf16_runs_are_scanned(self):
        nonce = bytes(range(16))
        phrase = "the keeper leaves the lamp for the next watch"
        target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()
        fixtures = [
            ("ascii", b"\x00\xff" + phrase.encode("ascii") + b"\xff\x00"),
            ("utf16le", b"\xff\x01" + phrase.encode("utf-16le") + b"\xfe"),
            ("utf16be", b"\xff\x01" + phrase.encode("utf-16be") + b"\xfe"),
            
            
        ]
        for label, payload in fixtures:
            hits = []
            variants = phrase_intake.decode_text_variants(payload, label + ".bin")
            expected_prefix = {
                "ascii": "embedded-ascii@",
                "utf16le": "embedded-utf-16le@",
                "utf16be": "embedded-utf-16be@",
            }[label]
            self.assertTrue(
                any(source.startswith(expected_prefix) and text == phrase
                    for source, text in variants),
                f"{label}: embedded run was not isolated",
            )
            for source, text in variants:
                phrase_intake.scan_phrase_spans(text, nonce, target, source, 16, hits)
            self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits), label)

    def test_hex_and_base64_utf16_carriers_are_scanned(self):
        nonce = bytes(range(16))
        phrase = "the keeper leaves the lamp for the next watch"
        target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()
        carriers = [
            ("hex", ("hex:" + phrase.encode("utf-16be").hex()).encode("ascii"),
             "hex-decoded-utf-16be"),
            ("base64", ("base64:" + base64.b64encode(phrase.encode("utf-16le")).decode("ascii")).encode("ascii"),
             "base64-decoded-utf-16le"),
        ]
        for name, payload, expected_label in carriers:
            variants = phrase_intake.decode_text_variants(payload, name + ".bin")
            self.assertTrue(
                any(label.startswith(expected_label) and text.lstrip("\ufeff") == phrase
                    for label, text in variants),
                f"{name}: UTF-16 carrier was not decoded",
            )
            hits = []
            for label, text in variants:
                phrase_intake.scan_phrase_spans(text, nonce, target, name + " [" + label + "]", 16, hits)
            self.assertTrue(
                any(hit["normalized_phrase"] == phrase for hit in hits),
                f"{name}: decoded carrier did not reach K08 commitment scan",
            )

    def test_opaque_bx25_pdf_is_skipped_before_magic_even_with_password(self):
        path = SOURCE_ROOT / "evidence" / "h17-supplemental-office-files" / "BX25-08.pdf"
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual(digest, phrase_intake.intake.OPAQUE_PDF_SHA256)
        errors = []
        budget = [0]
        with patch.object(phrase_intake.intake, "magic",
                          side_effect=AssertionError("opaque PDF reached content classification")):
            streams = list(phrase_intake.iter_text_streams(
                str(path), payload, 0, budget, errors, pdf_password="must-not-be-used"
            ))
        self.assertEqual(streams, [])
        self.assertEqual(errors, [{
            "source": str(path), "status": "skipped_opaque_pdf",
            "size": len(payload), "sha256": digest,
        }])
        self.assertEqual(budget, [len(payload)])

    def test_nested_opaque_bx25_pdf_is_not_yielded_as_content(self):
        path = SOURCE_ROOT / "evidence" / "h17-supplemental-office-files" / "BX25-08.pdf"
        pdf = path.read_bytes()
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("BX25-08.pdf", pdf)
        errors = []
        streams = list(phrase_intake.iter_text_streams(
            "bundle.zip", payload.getvalue(), 0, [0], errors, pdf_password="must-not-be-used"
        ))
        self.assertFalse(any(b"%PDF-" in data for _, data in streams))
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["status"], "skipped_opaque_pdf")
        self.assertEqual(errors[0]["sha256"], phrase_intake.intake.OPAQUE_PDF_SHA256)

    def test_encrypted_pdf_requires_and_accepts_supplied_password(self):
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.add_metadata({"/Title": "Authorized password fixture"})
        writer.encrypt(user_password="synthetic-fixture-password")
        output = io.BytesIO()
        writer.write(output)
        payload = output.getvalue()

        errors = []
        list(phrase_intake.iter_text_streams("folio.pdf", payload, 0, [0], errors, False))
        self.assertTrue(any("supply --pdf-password" in item["error"] for item in errors))

        errors = []
        streams = list(phrase_intake.iter_text_streams(
            "folio.pdf", payload, 0, [0], errors, False, "synthetic-fixture-password"
        ))
        self.assertFalse(errors)
        self.assertTrue(streams)

        errors = []
        list(phrase_intake.iter_text_streams(
            "folio.pdf", payload, 0, [0], errors, False, "0000"
        ))
        self.assertTrue(any("did not decrypt" in item["error"] for item in errors))

    def test_nested_zip_exposes_final_envelope_text(self):
        nonce = bytes(range(16))
        phrase = "the keeper leaves the lamp for the next watch"
        component = phrase_intake.k08_component(nonce, phrase)
        target = hashlib.sha256(component).digest()
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("envelope/final-caption.txt", "Discarded draft. " + phrase + ".")
        streams = list(phrase_intake.iter_text_streams("fixture.zip", payload.getvalue(), 0, [0], []))
        self.assertGreaterEqual(len(streams), 2)
        hits = []
        total = 0
        for source, data in streams:
            for label, text in phrase_intake.decode_text_variants(data, source):
                total += phrase_intake.scan_phrase_spans(text, nonce, target,
                                                         source + " [" + label + "]", 16, hits)
        self.assertGreater(total, 0)
        self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits))

    def test_mime_email_attachment_text_is_scanned(self):
        nonce = bytes(range(16))
        phrase = "the keeper leaves the lamp for the next watch"
        target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()
        message = EmailMessage()
        message["Subject"] = "Final envelope copy"
        message.set_content("See the attached final caption.")
        message.add_attachment(("Discarded. " + phrase + ".").encode(),
                               maintype="text", subtype="plain", filename="final-caption.txt")
        streams = list(phrase_intake.iter_text_streams("handoff.eml", message.as_bytes(), 0, [0], []))
        hits = []
        for source, data in streams:
            for label, text in phrase_intake.decode_text_variants(data, source):
                phrase_intake.scan_phrase_spans(text, nonce, target, source + " [" + label + "]", 16, hits)
        self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits))

    def test_full_96_character_phrase_domain(self):
        nonce = bytes(range(16))
        phrase = " ".join(chr(ord("a") + (i % 26)) for i in range(48))
        self.assertEqual(len(phrase), 95)
        target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()
        hits = []
        tested = phrase_intake.scan_phrase_spans(
            "prefix " + phrase + " suffix", nonce, target, "48-word-positive", 48, hits
        )
        self.assertGreater(tested, 0)
        self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits))

        too_long = " ".join(chr(ord("a") + (i % 26)) for i in range(49))
        self.assertEqual(len(too_long), 97)
        long_target = hashlib.sha256(phrase_intake.k08_component(nonce, too_long)).digest()
        long_hits = []
        phrase_intake.scan_phrase_spans(
            too_long, nonce, long_target, "49-word-out-of-domain", 49, long_hits
        )
        self.assertEqual(long_hits, [])

    def test_original_ax7782_transfer_chain_is_selected(self):
        import h17_ax7782_object_intake as object_intake
        selected, meta = object_intake.select_chain(SOURCE_ROOT, "AX-7782")
        self.assertEqual(meta["object"], "IR-261003-H17")
        self.assertTrue(meta["handoff_email_confirms_retained_object"])
        self.assertEqual([int(row["attempt"]) for row in selected], [2] * 8)
        chain = b"".join(bytes.fromhex(row["checkpoint"]) for row in selected)
        component = hashlib.sha256(chain).digest()[:16]
        acceptance = json.loads((SOURCE_ROOT / "acceptance.json").read_text())
        self.assertEqual(hashlib.sha256(component).hexdigest(), acceptance["slot_sha256"]["K07"])

    def test_end_to_end_synthetic_8mib_object(self):
        with tempfile.TemporaryDirectory(prefix="h17-k08-e2e-") as tmp:
            base = Path(tmp)
            resources = base / "resources"
            (resources / "evidence" / "transfers").mkdir(parents=True)
            (resources / "evidence" / "mail").mkdir(parents=True)
            original_route = json.loads((SOURCE_ROOT / "evidence" / "recovery-routing.json").read_text())
            nonce = bytes.fromhex(original_route["K08"]["desk_nonce"])
            phrase = "the keeper leaves the lamp on for the incoming watch"
            component = phrase_intake.k08_component(nonce, phrase)
            checkpoints = [bytes((i, 255 - i)) for i in range(8)]
            rows = []
            for seq, checkpoint in enumerate(checkpoints):
                rows.append({"kind": "CHUNK", "transfer": "AX-7782", "seq": seq,
                             "attempt": 1, "checkpoint": "0000", "bytes": 1048576,
                             "object": "IR-261003-H17"})
                rows.append({"kind": "CHUNK", "transfer": "AX-7782", "seq": seq,
                             "attempt": 2, "checkpoint": checkpoint.hex().upper(),
                             "bytes": 1048576, "object": "IR-261003-H17"})
            rows.append({"kind": "COMMIT", "transfer": "AX-7782", "dry_run": False,
                         "chunks": 8, "object": "IR-261003-H17"})
            (resources / "evidence" / "transfers" / "transfer-audit.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n")
            (resources / "evidence" / "mail" / "13.eml").write_text(
                "AX-7782 IR-261003-H17 actual retained copy")
            (resources / "evidence" / "recovery-routing.json").write_text(json.dumps(original_route))
            chain = b"".join(checkpoints)
            k07 = hashlib.sha256(hashlib.sha256(chain).digest()[:16]).hexdigest()
            acceptance = {"slot_sha256": {"K07": k07, "K08": hashlib.sha256(component).hexdigest()}}
            (resources / "acceptance.json").write_text(json.dumps(acceptance))

            archive_path = base / "AX-7782.bin"
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as archive:
                archive.writestr("envelope/final-caption.txt", "Draft discarded. " + phrase + ".")
            initial = archive_path.stat().st_size
            name = "filler.bin"
            filler_len = 8 * 1048576 - initial - (30 + len(name) + 46 + len(name))
            with zipfile.ZipFile(archive_path, "a", compression=zipfile.ZIP_STORED) as archive:
                archive.writestr(name, b"\x00" * filler_len)
            self.assertEqual(archive_path.stat().st_size, 8 * 1048576)
            result = phrase_intake.inspect_object(archive_path, resources, reveal=True)
        public = phrase_intake.inspect_object(archive_path, resources)
        self.assertTrue(public["redaction_applied"])
        self.assertNotIn("normalized_phrase", repr(public))
        self.assertNotIn("component_hex", repr(public))
            hits = result["K08_search"]["original_commitment_hits"]
            self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits))
            self.assertTrue(result["transfer"]["K07_commitment_pass"])



    def test_legacy_xls_biff_cells_are_joined_and_scanned(self):
        import types
        from unittest import mock

        nonce = bytes(range(16))
        phrase = "the sea is calm and the watch is over"
        target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()

        class FakeCell:
            def __init__(self, value, ctype=1):
                self.value = value
                self.ctype = ctype

        class FakeSheet:
            name = "Mug stock"
            nrows = 2
            ncols = 2
            cells = [
                [FakeCell("the sea"), FakeCell("is calm")],
                [FakeCell("and the"), FakeCell("watch is over")],
            ]

            def cell(self, row, col):
                return self.cells[row][col]

        class FakeBook:
            def sheets(self):
                return [FakeSheet()]

            def release_resources(self):
                pass

        class FakeOleFile:
            def __init__(self, _stream):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                pass

            def listdir(self, streams=True, storages=False):
                return [["Workbook"]]

            def openstream(self, _stream_path):
                return io.BytesIO(b"author margin comment")

        fake_xlrd = types.SimpleNamespace(
            XL_CELL_EMPTY=0,
            XL_CELL_BLANK=6,
            open_workbook=lambda **_kwargs: FakeBook(),
        )
        fake_olefile = types.SimpleNamespace(OleFileIO=FakeOleFile)
        payload = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 32
        errors = []
        with mock.patch.dict(sys.modules, {"xlrd": fake_xlrd, "olefile": fake_olefile}):
            streams = list(phrase_intake.iter_text_streams(
                "ordinary-biff-fixture.xls", payload, 0, [0], errors, False
            ))

        self.assertFalse(errors)
        self.assertTrue(any("the sea is calm" in data.decode("utf-8")
                            for _source, data in streams))
        self.assertTrue(any("author margin comment" in data.decode("utf-8")
                            for _source, data in streams))
        hits = []
        for source, data in streams:
            for label, text in phrase_intake.decode_text_variants(data, source):
                phrase_intake.scan_phrase_spans(
                    text, nonce, target, source + " [" + label + "]", 16, hits
                )
        self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits))

    def test_native_m10_officeart_image_and_shape_caption_without_conversion(self):
        import types
        from unittest import mock
        from PIL import Image
        from PIL.PngImagePlugin import PngInfo
        import h17_xls_lo_fallback
        from test_h17_biff_officeart import cfb
        from test_h17_biff_officeart_blips import bse_record, png_blip, workbook_with_bstore

        phrase = "the last light falls across the cups by the window"
        nonce = bytes(range(16))
        target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()
        # Encode the complete caption only in the source-literal teal-bit
        # layout. The PNG contains no clear-text caption metadata.
        pixels = Image.new("RGB", (8, len(phrase) + 2), (0, 128, 128))
        for byte_index, letter in enumerate(phrase.encode("ascii") + bytes(1)):
            for bit_index in range(8):
                offset = byte_index * 8 + bit_index
                position = (offset % 8, offset // 8)
                red, green, blue = pixels.getpixel(position)
                plane = offset & 1
                bit = (letter >> (7 - bit_index)) & 1
                green = (green & ~(1 << plane)) | (bit << plane)
                pixels.putpixel(position, (red, green, blue))
        image = io.BytesIO()
        pixels.save(image, format="PNG")
        png = image.getvalue()
        workbook = workbook_with_bstore([bse_record(png_blip(png))])
        source = cfb(workbook + bytes(max(0, 4096 - len(workbook))))
        source_sha = hashlib.sha256(source).hexdigest()

        class FakeBook:
            def sheets(self):
                return []

            def release_resources(self):
                pass

        class FakeOle:
            def __init__(self, _data):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                pass

            def listdir(self, streams=True, storages=False):
                return []

        fake_xlrd = types.SimpleNamespace(open_workbook=lambda **_kwargs: FakeBook())
        fake_olefile = types.SimpleNamespace(OleFileIO=FakeOle)

        with mock.patch.dict(sys.modules, {"xlrd": fake_xlrd, "olefile": fake_olefile}):
            with mock.patch.object(h17_xls_lo_fallback, "extract_bytes",
                                   side_effect=RuntimeError("conversion disabled")):
                errors = []
                streams = list(phrase_intake.iter_text_streams(
                    "AX-7782!/mug-stock.xls", source, 0, [0], errors,
                ))
        self.assertEqual(hashlib.sha256(source).hexdigest(), source_sha)
        self.assertTrue(any(
            "<native-officeart:Sheet1!M10>:wz_description" in carrier
            and b"SYNTHETIC_ONLY_OFFICEART_DESC_6F31" in value
            for carrier, value in streams
        ))
        self.assertTrue(any(
            "<native-officeart:Sheet1!M10>.png" in carrier
            and hashlib.sha256(value).digest() == hashlib.sha256(png).digest()
            for carrier, value in streams
        ))
        self.assertTrue(any(
            "<teal-bit:teal-mask-green-low-if-even:" in carrier
            and phrase.encode("ascii") in value
            for carrier, value in streams
        ), "source-literal teal-bit payload was not emitted into K08 scanning")
        hits = []
        for carrier, value in streams:
            for label, text in phrase_intake.decode_text_variants(value, carrier):
                phrase_intake.scan_phrase_spans(text, nonce, target,
                                                carrier + " [" + label + "]", 48, hits)
        self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits))
        self.assertFalse(any("native M10 OfficeArt inspection failed" in e.get("error", "")
                             for e in errors))

        # The same intact blip under a non-M10 anchor is deliberately excluded.
        # Change only the original 18-byte OfficeArtClientAnchorSheet payload.
        import struct
        m10_anchor = struct.pack(
            "<H H h H h H h H h", 3, 12, 100, 9, 12, 13, 900, 10, 200,
        )
        c3_anchor = struct.pack(
            "<H H h H h H h H h", 3, 2, 100, 2, 12, 3, 900, 3, 200,
        )
        self.assertEqual(workbook.count(m10_anchor), 1)
        off_anchor_workbook = workbook.replace(m10_anchor, c3_anchor, 1)
        off_anchor_source = cfb(
            off_anchor_workbook + bytes(max(0, 4096 - len(off_anchor_workbook)))
        )
        with mock.patch.dict(sys.modules, {"xlrd": fake_xlrd, "olefile": fake_olefile}):
            with mock.patch.object(h17_xls_lo_fallback, "extract_bytes",
                                   side_effect=RuntimeError("conversion disabled")):
                off_anchor_streams = list(phrase_intake.iter_text_streams(
                    "AX-7782!/mug-stock.xls", off_anchor_source, 0, [0], [],
                ))
        self.assertFalse(any("<native-officeart:" in carrier
                             for carrier, _ in off_anchor_streams))

    def test_m10_image_payload_reaches_exact_k08_and_other_workbook_is_excluded(self):
        import types
        from unittest import mock
        from PIL import Image
        from PIL.PngImagePlugin import PngInfo
        import h17_xls_lo_fallback

        phrase = "there is room at the table after the last watch"
        nonce = bytes(range(16))
        target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()
        metadata = PngInfo()
        metadata.add_text("caption", phrase)
        image = io.BytesIO()
        Image.new("RGB", (8, 8), (0, 128, 128)).save(image, format="PNG", pnginfo=metadata)
        png = image.getvalue()
        image_record = {
            "sheet": "Galley",
            "anchor": "M10",
            "format": "png",
            "sha256": hashlib.sha256(png).hexdigest(),
            "data_base64": base64.b64encode(png).decode("ascii"),
            "data_included": True,
        }

        class FakeBook:
            def sheets(self):
                return []

            def release_resources(self):
                pass

        class FakeOle:
            def __init__(self, _data):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                pass

            def listdir(self, streams=True, storages=False):
                return []

        fake_xlrd = types.SimpleNamespace(open_workbook=lambda **_kwargs: FakeBook())
        fake_olefile = types.SimpleNamespace(OleFileIO=FakeOle)
        payload = bytes.fromhex("D0CF11E0A1B11AE1") + bytes(64)
        with mock.patch.dict(sys.modules, {"xlrd": fake_xlrd, "olefile": fake_olefile}):
            with mock.patch.object(h17_xls_lo_fallback, "extract_bytes",
                                   return_value={"embedded_images": [image_record]}) as extractor:
                errors = []
                streams = list(phrase_intake.iter_text_streams(
                    "AX-7782!/mug-stock.xls", payload, 0, [0], errors,
                ))
                extractor.assert_called_once_with(
                    payload, "AX-7782!/mug-stock.xls", include_image_data=True,
                    allowed_image_anchors={"M10"},
                )
                self.assertTrue(any(
                    "<image:Galley!M10>.png" in source
                    and hashlib.sha256(data).hexdigest() == image_record["sha256"]
                    for source, data in streams
                ))
                hits = []
                for source, data in streams:
                    for label, text in phrase_intake.decode_text_variants(data, source):
                        phrase_intake.scan_phrase_spans(
                            text, nonce, target, source + " [" + label + "]", 48, hits,
                        )
                self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits))
                self.assertFalse(any("M10 image extraction failed" in e.get("error", "")
                                     for e in errors))

            with mock.patch.object(h17_xls_lo_fallback, "extract_bytes") as extractor:
                errors = []
                streams = list(phrase_intake.iter_text_streams(
                    "AX-7782!/unrelated.xls", payload, 0, [0], errors,
                ))
                extractor.assert_not_called()
                self.assertFalse(any("<image:" in source for source, _ in streams))

            blocked = dict(image_record, anchor="C3")
            with mock.patch.object(h17_xls_lo_fallback, "extract_bytes",
                                   return_value={"embedded_images": [blocked]}):
                errors = []
                streams = list(phrase_intake.iter_text_streams(
                    "AX-7782!/mug-stock.xls", payload, 0, [0], errors,
                ))
                self.assertFalse(any("<image:" in source for source, _ in streams))
                self.assertTrue(any("non-M10" in e.get("error", "") for e in errors))

    def test_emf_spool_and_xps_rendered_text_dispatch_to_k08_hmac(self):
        nonce = bytes(range(16))

        xps_phrase = "the water held the last light around the table"
        xps_target = hashlib.sha256(phrase_intake.k08_component(nonce, xps_phrase)).digest()
        xps_page = (
            '<FixedPage xmlns="http://schemas.microsoft.com/xps/2005/06">'
            f'<Glyphs UnicodeString="{xps_phrase}"/>'
            '</FixedPage>'
        ).encode("utf-8")
        package = io.BytesIO()
        with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(
                "[Content_Types].xml",
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
            )
            archive.writestr("Documents/1/Pages/1.fpage", xps_page)
        errors = []
        xps_streams = list(phrase_intake.iter_text_streams(
            "PS-0323.xps", package.getvalue(), 0, [0], errors
        ))
        xps_hits = []
        for source, payload in xps_streams:
            for label, text in phrase_intake.decode_text_variants(payload, source):
                phrase_intake.scan_phrase_spans(
                    text, nonce, xps_target, source + " [" + label + "]", 16, xps_hits
                )
        self.assertTrue(any(hit["normalized_phrase"] == xps_phrase for hit in xps_hits), xps_hits)
        self.assertFalse(any("xps-glyph-indices" in item["error"] for item in errors), errors)

        from test_h17_emf_text import page as emf_page, record as emf_record

        emf_phrase = "the voices stayed around the table after the long watch"
        emf_target = hashlib.sha256(phrase_intake.k08_component(nonce, emf_phrase)).digest()
        envelope = bytes.fromhex("454D4653504F4F4C20726561642D6F6E6C7920666978747572650000") + emf_page(emf_record(84, [emf_phrase]))
        errors = []
        emf_streams = list(phrase_intake.iter_text_streams(
            "PS-0323.SPL", envelope, 0, [0], errors
        ))
        emf_hits = []
        for source, payload in emf_streams:
            for label, text in phrase_intake.decode_text_variants(payload, source):
                phrase_intake.scan_phrase_spans(
                    text, nonce, emf_target, source + " [" + label + "]", 16, emf_hits
                )
        self.assertTrue(any(hit["normalized_phrase"] == emf_phrase for hit in emf_hits), emf_hits)
        self.assertTrue(any("emf-page" in hit["source"] for hit in emf_hits), emf_hits)


if __name__ == "__main__":
    unittest.main(verbosity=2)
