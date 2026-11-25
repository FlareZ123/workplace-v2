import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h17_redaction import redact_sensitive


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
