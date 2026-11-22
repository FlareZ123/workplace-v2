"""Exact K08 source-phrase intake from Outlook MSG compressed RTF streams."""
from __future__ import annotations

import hashlib
import io
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

from compressed_rtf import compress

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_ax7782_k08_phrase_intake as intake


class CompressedMsgRtfTests(unittest.TestCase):
    def setUp(self):
        self.phrase = "there is room for everyone after the last watch"
        self.nonce = bytes(range(16))
        self.target = hashlib.sha256(
            intake.k08_component(self.nonce, self.phrase)
        ).digest()
        self.rtf = (
            r"{\rtf1\ansi\ansicpg1252\pard "
            r"there is {\b room} for everyone after the last watch\par}"
        )
        self.compressed = compress(self.rtf.encode("ascii"), compressed=True)
        self.assertIsInstance(self.compressed, bytes)
        self.assertEqual(self.compressed[8:12], b"LZFu")

    def streams(self, data: bytes, name: str):
        class FakeOle:
            def __init__(self, _source):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                pass

            def listdir(self, streams=True, storages=False):
                return [["__substg1.0_10090102"]]

            def openstream(self, _stream):
                return io.BytesIO(data)

        stub_ole = types.SimpleNamespace(OleFileIO=FakeOle)
        errs = []
        with mock.patch.dict(sys.modules, {"olefile": stub_ole}):
            found = list(intake.iter_text_streams(
                name, bytes.fromhex("D0CF11E0A1B11AE1") + bytes(64),
                0, [0], errs,
            ))
        return found, errs

    def test_original_msg_rtf_with_inline_style_recovers_exact_phrase(self):
        streams, errors = self.streams(self.compressed, "MAIL-20-native.msg")
        self.assertFalse(errors)
        self.assertTrue(any(
            "/<rtf-plain>" in source
            and self.phrase.encode("utf-8") in data
            for source, data in streams
        ), streams)
        hits = []
        for source, data in streams:
            for label, text in intake.decode_text_variants(data, source):
                intake.scan_phrase_spans(
                    text, self.nonce, self.target, f"{source} [{label}]", 48, hits,
                )
        self.assertTrue(any(hit["normalized_phrase"] == self.phrase for hit in hits))

    def test_same_payload_under_unrelated_ole_is_not_parsed_as_msg(self):
        streams, _errors = self.streams(self.compressed, "memo.xls")
        self.assertFalse(any("/<rtf-plain>" in source for source, _ in streams))

    def test_bounded_declared_size_fails_without_decompressing(self):
        damaged = bytearray(self.compressed)
        damaged[4:8] = (9 * 1024 * 1024).to_bytes(4, "little")
        streams, errors = self.streams(bytes(damaged), "MAIL-11-native.msg")
        self.assertFalse(any("/<rtf-plain>" in source for source, _ in streams))
        self.assertTrue(any("8 MiB bound" in e["error"] for e in errors))

    def test_invalid_header_does_not_yield_plain_text(self):
        damaged = bytearray(self.compressed)
        damaged[8:12] = b"ZZZZ"
        streams, errors = self.streams(bytes(damaged), "MAIL-11-native.msg")
        self.assertFalse(any("/<rtf-plain>" in source for source, _ in streams))
        self.assertTrue(any("invalid Outlook compressed RTF" in e["error"]
                            for e in errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
