import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h17_redaction import redact_sensitive, redact_by_default


class RedactionTests(unittest.TestCase):
    def test_removes_recovery_material_recursively_but_keeps_status(self):
        value = {
            "accepted": True,
            "candidate_count": 2,
            "candidate": {"K04": "A1B2", "K08": "secret"},
            "k07_chain_validation": {
                "chain_hex": "0011",
                "K07_component_hex": "2233",
                "matches_acceptance": True,
            },
            "K08_search": {
                "original_commitment_hits": [{
                    "source": "notes/N23",
                    "normalized_phrase": "secret phrase",
                    "component_hex": "4455",
                    "hmac16": "6677",
                    "word_count": 3,
                }],
                "match_count": 1,
            },
            "k08_desk_nonce_hex": "8899",
            "target_sha256": "aabb",
            "route_mask_hex": "ccdd",
        }
        clean = redact_sensitive(value)
        self.assertTrue(clean["accepted"])
        self.assertEqual(clean["candidate_count"], 2)
        self.assertTrue(clean["k07_chain_validation"]["matches_acceptance"])
        self.assertEqual(clean["K08_search"]["match_count"], 1)
        self.assertEqual(clean["K08_search"]["original_commitment_hits"][0]["source"], "notes/N23")
        self.assertEqual(clean["K08_search"]["original_commitment_hits"][0]["word_count"], 3)
        serialized = repr(clean)
        for secret in ("A1B2", "secret phrase", "2233", "4455", "6677", "8899", "aabb", "ccdd"):
            self.assertNotIn(secret, serialized)
        self.assertTrue(clean["redaction_applied"])

    def test_removes_source_text_and_sensitive_checksums(self):
        clean = redact_sensitive({
            "candidates": [{
                "raw_text": "keeper words",
                "formula_text": "=A1",
                "component_sha256": "deadbeef",
                "text_sha256": "cafe",
                "match": False,
                "cell": "M10",
            }],
            "chunks": [{"checkpoint": "1234", "crc16": {"x": "abcd"}, "seq": 1}],
        })
        candidate = clean["candidates"][0]
        self.assertEqual(candidate, {"match": False, "cell": "M10"})
        self.assertEqual(clean["chunks"], [{"seq": 1}])

    def test_redacts_bytes_and_absolute_paths(self):
        clean = redact_sensitive({"path": "/tmp/private/source.bin", "payload": b"secret", "blob": b"abc"})
        self.assertEqual(clean["path"], "source.bin")
        self.assertNotIn("secret", repr(clean))
        self.assertEqual(clean["blob"], {"redacted": True, "byte_length": 3})

    def test_windows_paths_pathlike_and_hmac_key_variants(self):
        windows = r"C:\Users\Operator\Documents\H17\native.psh"
        clean = redact_sensitive({
            "path": windows,
            "url": "https://example.com/private/file",
            "path_object": Path(windows),
            "nested": {"source_path": Path(r"D:\private\mug-stock.xls")},
            "hmac_sha256": "A" * 64,
            "expected_hmac": "B" * 64,
            "hmac_key": "C" * 32,
            "hmac_digest": "D" * 64,
            "hmac_match_count": 2,
            "hmac_status": "no_match",
        })
        self.assertEqual(clean["path"], "native.psh")
        self.assertEqual(clean["url"], "https://example.com/private/file")
        self.assertEqual(clean["path_object"], "native.psh")
        self.assertEqual(clean["nested"]["source_path"], "mug-stock.xls")
        self.assertEqual(clean["hmac_match_count"], 2)
        self.assertEqual(clean["hmac_status"], "no_match")
        serialized = repr(clean)
        for secret in ("A" * 64, "B" * 64, "C" * 32, "D" * 64, "C:\\Users", "D:\\private"):
            self.assertNotIn(secret, serialized)

    def test_redacts_paths_and_hmac_values_inside_error_strings(self):
        clean = redact_sensitive({
            "errors": [{"error": r"cannot read C:\Users\Operator\H17\native.psh; expected_hmac=" + "A" * 64}],
        })
        error = clean["errors"][0]["error"]
        self.assertEqual(error, "[redacted diagnostic]")
        self.assertNotIn("C:\\Users", error)
        self.assertNotIn("A" * 64, error)

    def test_decorator_redacts_exception_diagnostics(self):
        @redact_by_default
        def fail(path):
            raise ValueError(f"original source unavailable: {path}")
        with self.assertRaises(ValueError) as caught:
            fail(Path(r"C:\Users\Operator\Documents\H17\native.psh"))
        self.assertIn("native.psh", str(caught.exception))
        self.assertNotIn("C:\\Users", str(caught.exception))
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)

    def test_redacts_phrase_text_inside_diagnostics_and_exception_messages(self):
        secret_phrase = "The sea keeps watch while the last voices gather at the table"
        clean = redact_sensitive({"error": f"phrase did not match: {secret_phrase}"})
        self.assertEqual(clean["error"], "[redacted diagnostic]")

        @redact_by_default
        def fail_phrase():
            raise ValueError(f"caption rejected: {secret_phrase}")
        with self.assertRaises(ValueError) as caught:
            fail_phrase()
        self.assertNotIn(secret_phrase, str(caught.exception))
        self.assertIn("redacted diagnostic", str(caught.exception))
        self.assertIsNone(caught.exception.__context__)

    def test_reveal_preserves_original_exception_for_authorized_in_process_use(self):
        @redact_by_default
        def fail(path):
            raise ValueError(f"original source unavailable: {path}")
        with self.assertRaisesRegex(ValueError, r"C:\\Users"):
            fail(Path(r"C:\Users\Operator\Documents\H17\native.psh"), reveal=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
