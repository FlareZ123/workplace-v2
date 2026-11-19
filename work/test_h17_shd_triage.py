import hashlib
import tempfile
import unittest
from pathlib import Path

from h17_shd_triage import extract_strings, inspect


class ShdTriageTests(unittest.TestCase):
    def test_ascii_and_utf16le_offsets(self):
        prefix = b"\xff\xff\x03\x00"
        wide = "PS-261003-0323".encode("utf-16le") + b"\x00\x00"
        ascii_value = b"Recovery Envelope"
        data = prefix + wide + b"\x00\x00" + ascii_value + b"\x00"
        before = hashlib.sha256(data).digest()
        hits = extract_strings(data)
        pairs = {(h["encoding"], h["text"]) for h in hits}
        self.assertIn(("utf-16le-ascii", "PS-261003-0323"), pairs)
        self.assertIn(("ascii", "Recovery Envelope"), pairs)
        self.assertEqual(hashlib.sha256(data).digest(), before)

    def test_minimum_length(self):
        hits = extract_strings(b"\xff\x01\xfe\x02\xfd\x03", min_chars=4)
        self.assertEqual(hits, [])

    def test_max_strings(self):
        data = b"AAAA\x00\x00BBBB\x00\x00CCCC"
        hits = extract_strings(data, max_strings=2)
        self.assertEqual(len(hits), 2)

    def test_invalid_limits(self):
        with self.assertRaises(ValueError):
            extract_strings(b"abc", min_chars=0)

    def test_file_size_limit(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "job.shd"
            p.write_bytes(b"A" * 20)
            with self.assertRaisesRegex(ValueError, "max-bytes"):
                inspect(p, min_chars=4, max_strings=10, max_bytes=10)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = base / "real.shd"
            target.write_bytes(b"job metadata")
            link = base / "link.shd"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(ValueError, "non-symlink"):
                inspect(link, min_chars=4, max_strings=10, max_bytes=100)


if __name__ == "__main__":
    unittest.main()
