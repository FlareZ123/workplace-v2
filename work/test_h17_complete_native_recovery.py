"""Read-only complete REC8/1 recovery assembly with synthetic source controls."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h17_ax7782_k08_phrase_intake import k08_component, normalize
from h17_complete_native_recovery import recover_complete
from resources.verify import evaluate


class CompleteNativeRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="h17-complete-native-sft-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.spool = root / "PS-261003-0417.spl"
        self.caption = root / "Emily-final-caption.txt"
        self.mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
        self.nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
        self.phrase = "there is room around the table when the night is almost done"
        self.component = bytes(range(16))
        self.payload = bytes(a ^ b for a, b in zip(self.component, self.mask))
        self.spool.write_bytes(
            bytes.fromhex("D0CF11E0A1B11AE1") + bytes(64)
            + self.payload + bytes(64)
        )
        self.caption.write_text(
            "Emily's final margin caption:\n" + self.phrase + "\n",
            encoding="utf-8",
        )
        self.six_pass = {
            f"K{i:02d}": bytes([i]) * 16 for i in (1, 2, 3, 5, 6, 7)
        }
        self.full = {
            **{k: value.hex().upper() for k, value in self.six_pass.items()},
            "K04": self.component.hex().upper(),
            "K08": k08_component(self.nonce, self.phrase).hex().upper(),
        }
        self.base = {
            **{k: value.hex().upper() for k, value in self.six_pass.items()},
            "K04": None,
            "K08": None,
        }
        self.targets = {
            "slot_sha256": {
                key: hashlib.sha256(bytes.fromhex(value)).hexdigest()
                for key, value in self.full.items()
            },
            "combined_prefix": "CEG-ARCHIVE-RECOVERY/v1\n",
        }
        self.targets["combined_sha256"] = hashlib.sha256(
            (self.targets["combined_prefix"] + "".join(
                self.full[f"K{i:02d}"] + "\n" for i in range(1, 9)
            )).encode("ascii")
        ).hexdigest()
        self.routing = {
            "K04": {"masked_component": self.mask.hex().upper()},
            "K08": {"desk_nonce": self.nonce.hex().upper()},
        }

    def execute(self, base=None, reveal=True):
        return recover_complete(
            self.spool, self.caption,
            targets=self.targets, routing=self.routing,
            six_pass=self.base if base is None else base,
            reveal=reveal,
        )

    def test_default_complete_result_redacts_key_material(self):
        result = self.execute(reveal=False)
        self.assertTrue(result["redaction_applied"])
        self.assertNotIn("candidate", result)
        self.assertNotIn("normalized_phrase", repr(result))
        self.assertNotIn("component_hex", repr(result))

    def test_complete_synthetic_eight_slot_acceptance(self):
        result = self.execute()
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["candidate"], self.full)
        self.assertEqual(result["verification"]["combined"], "PASS")
        self.assertEqual(result["verification"]["passed"], 8)
        self.assertEqual(result["k04_component_hits"], 1)
        self.assertEqual(result["k08_component_hits"], 1)
        self.assertTrue(any(
            hit["normalized_phrase"] == self.phrase
            for hit in result["k08_phrase_hits"]
        ))
        self.assertTrue(evaluate(result["candidate"], self.targets)["accepted"])

    def test_corrupted_spool_does_not_emit_candidate(self):
        changed = bytearray(self.spool.read_bytes())
        changed[72] ^= 1
        self.spool.write_bytes(changed)
        result = self.execute()
        self.assertIsNone(result["candidate"])
        self.assertFalse(result["accepted"])
        self.assertEqual(result["k04_component_hits"], 0)

    def test_wrong_caption_does_not_emit_candidate(self):
        self.caption.write_text("other words entirely\n", encoding="utf-8")
        result = self.execute()
        self.assertIsNone(result["candidate"])
        self.assertFalse(result["accepted"])
        self.assertEqual(result["k08_component_hits"], 0)

    def test_wrong_known_slot_never_bypasses_original_verifier(self):
        bad_baseline = {**self.base, "K01": "F" * 32}
        result = self.execute(base=bad_baseline)
        self.assertFalse(result["accepted"])
        self.assertIsNone(result["candidate"])
        self.assertEqual(result["verification"]["slots"]["K01"], "NO_MATCH")
        self.assertEqual(result["verification"]["combined"], "NO_MATCH")

    def _install_long_caption(self, wrapped: bool):
        phrase = (
            "After the last cup the sea is still outside the window and "
            "the little lamp waits for the tired people making room for "
            "the next watch"
        )
        self.assertGreater(len(normalize(phrase)), 96)
        new_k08 = k08_component(self.nonce, normalize(phrase)).hex().upper()
        self.full["K08"] = new_k08
        self.targets["slot_sha256"]["K08"] = hashlib.sha256(
            bytes.fromhex(new_k08)
        ).hexdigest()
        self.targets["combined_sha256"] = hashlib.sha256(
            (self.targets["combined_prefix"] + "".join(
                self.full[f"K{i:02d}"] + "\n" for i in range(1, 9)
            )).encode("ascii")
        ).hexdigest()
        original = (
            phrase.replace("window and the little", "window\nand the little")
            if wrapped else phrase
        )
        self.caption.write_text(
            "Authentic margin caption:\n\n" + original + "\n\n",
            encoding="utf-8",
        )

    def test_complete_acceptance_with_long_whole_line(self):
        self._install_long_caption(wrapped=False)
        result = self.execute()
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["verification"]["combined"], "PASS")
        self.assertTrue(any(
            hit.get("whole_text_unit") == "line"
            for hit in result["k08_phrase_hits"]
        ))

    def test_complete_acceptance_with_hard_wrapped_long_paragraph(self):
        self._install_long_caption(wrapped=True)
        result = self.execute()
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["verification"]["combined"], "PASS")
        self.assertTrue(any(
            hit.get("whole_text_unit") == "paragraph"
            for hit in result["k08_phrase_hits"]
        ))

    def test_long_caption_after_same_line_colon_label(self):
        self._install_long_caption(wrapped=False)
        current = self.caption.read_text(encoding="utf-8")
        self.caption.write_text(
            current.replace("Authentic margin caption:\n\n",
                            "Authentic margin caption: ", 1),
            encoding="utf-8",
        )
        result = self.execute()
        self.assertTrue(result["accepted"], result)
        self.assertTrue(any(
            hit.get("source_field") == "value-after-:"
            for hit in result["k08_phrase_hits"]
        ))

    def test_long_caption_wrapped_after_colon_label(self):
        self._install_long_caption(wrapped=True)
        current = self.caption.read_text(encoding="utf-8")
        self.caption.write_text(
            current.replace("Authentic margin caption:\n\n",
                            "Authentic margin caption: ", 1),
            encoding="utf-8",
        )
        result = self.execute()
        self.assertTrue(result["accepted"], result)
        self.assertTrue(any(
            hit.get("source_field") == "value-after-:"
            and hit.get("whole_text_unit") == "paragraph"
            for hit in result["k08_phrase_hits"]
        ))

    def test_long_caption_after_equals_label(self):
        self._install_long_caption(wrapped=False)
        current = self.caption.read_text(encoding="utf-8")
        self.caption.write_text(
            current.replace("Authentic margin caption:\n\n",
                            "FinalCaption = ", 1),
            encoding="utf-8",
        )
        result = self.execute()
        self.assertTrue(result["accepted"], result)
        self.assertTrue(any(
            hit.get("source_field") == "value-after-="
            for hit in result["k08_phrase_hits"]
        ))

    def test_full_rec8_from_native_docx_split_styling_runs(self):
        from zipfile import ZipFile
        from xml.sax.saxutils import escape

        self._install_long_caption(wrapped=False)
        caption = self.caption.read_text(encoding="utf-8").split("\n\n", 1)[1].strip()
        component = self.payload.hex().upper()
        self.spool = self.spool.with_name("original-escrow-and-margin.docx")
        self.caption = self.spool
        midpoint = len(caption) // 2
        paragraphs = (
            ("ESC-N coupon: " + component[:16], component[16:]),
            ("Final Caption: " + caption[:midpoint], caption[midpoint:]),
        )
        body = "".join(
            "<w:p><w:r><w:t xml:space=\"preserve\">" + escape(left)
            + "</w:t></w:r><w:r><w:t xml:space=\"preserve\">"
            + escape(right) + "</w:t></w:r></w:p>"
            for left, right in paragraphs
        )
        xml = (
            "<w:document xmlns:w=\"http://schemas.openxmlformats.org/"
            "wordprocessingml/2006/main\"><w:body>"
            + body + "</w:body></w:document>"
        )
        with ZipFile(self.spool, "w") as package:
            package.writestr("[Content_Types].xml", "<Types/>")
            package.writestr("word/document.xml", xml)
        original_sha = hashlib.sha256(self.spool.read_bytes()).hexdigest()
        result = self.execute()
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["candidate"], self.full)
        self.assertEqual(result["verification"]["combined"], "PASS")
        self.assertGreater(result["k04_component_hits"], 0)
        self.assertTrue(any(
            "word/document.xml#authored-unit" in hit["source"]
            for hit in result["k08_phrase_hits"]
        ))
        self.assertEqual(hashlib.sha256(self.spool.read_bytes()).hexdigest(), original_sha)

    def test_wrong_long_caption_never_reaches_verifier(self):
        self._install_long_caption(wrapped=False)
        self.caption.write_text(
            self.caption.read_text(encoding="utf-8").replace(
                "next watch", "next shift"
            ), encoding="utf-8",
        )
        result = self.execute()
        self.assertFalse(result["accepted"])
        self.assertEqual(result["k08_component_hits"], 0)

    def test_complete_acceptance_with_original_msg_rtf_body(self):
        import io
        import types
        from unittest import mock
        from compressed_rtf import compress

        rtf = (
            r"{\rtf1\ansi\pard there is {\b room} around the table "
            r"when the night is almost done\par}"
        )
        packed = compress(rtf.encode("ascii"), compressed=True)
        self.caption = self.caption.with_name("MAIL-20-original.msg")
        self.caption.write_bytes(
            bytes.fromhex("D0CF11E0A1B11AE1") + bytes(64)
        )

        class FakeOle:
            def __init__(self, _data):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                pass

            def listdir(self, streams=True, storages=False):
                return [["__substg1.0_10090102"]]

            def openstream(self, _stream):
                return io.BytesIO(packed)

        with mock.patch.dict(sys.modules, {
            "olefile": types.SimpleNamespace(OleFileIO=FakeOle),
        }):
            result = self.execute()
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["candidate"], self.full)
        self.assertEqual(result["verification"]["combined"], "PASS")

    def test_complete_acceptance_with_original_msg_compressed_coupon(self):
        import io
        import types
        from unittest import mock
        from compressed_rtf import compress

        rtf = (
            r"{\rtf1\ansi\pard Escrow coupon recovered from the "
            r"north print job:\line "
            + self.payload.hex().upper()
            + r"\par}"
        )
        packed = compress(rtf.encode("ascii"), compressed=True)
        self.spool = self.spool.with_name("MAIL-20-original-coupon.msg")
        self.spool.write_bytes(
            bytes.fromhex("D0CF11E0A1B11AE1") + bytes(64)
        )

        class FakeOle:
            def __init__(self, _data):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                pass

            def listdir(self, streams=True, storages=False):
                return [["__substg1.0_10090102"]]

            def openstream(self, _stream):
                return io.BytesIO(packed)

        with mock.patch.dict(sys.modules, {
            "olefile": types.SimpleNamespace(OleFileIO=FakeOle),
        }):
            result = self.execute()
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["verification"]["combined"], "PASS")
        self.assertEqual(result["k04_component_hits"], 1)
        self.assertEqual(result["k08_component_hits"], 1)

    def test_source_files_are_read_only(self):
        before = {
            self.spool: hashlib.sha256(self.spool.read_bytes()).hexdigest(),
            self.caption: hashlib.sha256(self.caption.read_bytes()).hexdigest(),
        }
        self.execute()
        for path, original in before.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
