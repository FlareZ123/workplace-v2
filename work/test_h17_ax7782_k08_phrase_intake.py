#!/usr/bin/env python3
"""Positive controls for the source-backed AX-7782 K08 phrase scanner."""
import hashlib
import io
import json
from email.message import EmailMessage
import sys
import tempfile
import unittest
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
            ("ascii", b"\\x00\\xff" + phrase.encode("ascii") + b"\\xff\\x00"),
            ("utf16le", b"\\x00\\xff" + phrase.encode("utf-16le") + b"\\xff\\x00"),
        ]
        for label, payload in fixtures:
            hits = []
            variants = phrase_intake.decode_text_variants(payload, label + ".bin")
            for source, text in variants:
                phrase_intake.scan_phrase_spans(text, nonce, target, source, 16, hits)
            self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits), label)

    def test_encrypted_pdf_requires_and_accepts_supplied_password(self):
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.encrypt(user_password="8131")
        output = io.BytesIO()
        writer.write(output)
        payload = output.getvalue()

        errors = []
        list(phrase_intake.iter_text_streams("folio.pdf", payload, 0, [0], errors, False))
        self.assertTrue(any("supply --pdf-password" in item["error"] for item in errors))

        errors = []
        streams = list(phrase_intake.iter_text_streams(
            "folio.pdf", payload, 0, [0], errors, False, "8131"
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
            result = phrase_intake.inspect_object(archive_path, resources)
            hits = result["K08_search"]["original_commitment_hits"]
            self.assertTrue(any(hit["normalized_phrase"] == phrase for hit in hits))
            self.assertTrue(result["transfer"]["K07_commitment_pass"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
