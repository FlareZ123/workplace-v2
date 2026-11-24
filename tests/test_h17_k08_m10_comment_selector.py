import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "work"
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

from work.h17_k08_mug_stock_cell_selector import (
    evaluate_m10_comments, k08_component, normalize, redact_result, sha256,
)
if str(WORK_DIR) in sys.path:
    sys.path.remove(str(WORK_DIR))


class K08M10CommentSelectorTests(unittest.TestCase):
    def setUp(self):
        self.nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        self.phrase = "silver maple ocean amber"
        self.target = bytes.fromhex(
            sha256(k08_component(self.nonce, normalize(self.phrase)))
        )

    def test_explicit_sheet_checks_only_its_m10_comment(self):
        extracted = {
            "sheets": [{"name": "Sheet1"}, {"name": "Sheet2"}],
            "text_streams": [
                {"source": "Sheet1!M10<comment>", "kind": "comment",
                 "text": self.phrase, "comment_author": "Test Author"},
                {"source": "Sheet1!M9<comment>", "kind": "comment",
                 "text": self.phrase, "comment_author": "Test Author"},
                {"source": "Sheet2!M10<comment>", "kind": "comment",
                 "text": self.phrase, "comment_author": "Other Test Author"},
                {"source": "Sheet1!A1<comment>", "kind": "comment",
                 "text": self.phrase, "comment_author": "Test Author"},
            ],
        }
        result = evaluate_m10_comments(extracted, "Sheet1", self.nonce, self.target)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["match"])
        self.assertEqual(result[0]["source"], "Sheet1!M10<comment>")
        self.assertEqual(result[0]["comment_author"], "Test Author")
        self.assertEqual(result[0]["normalized_phrase"], normalize(self.phrase))

    def test_no_sheet_mapping_means_no_comment_search(self):
        extracted = {
            "sheets": [{"name": "Sheet1"}, {"name": "Sheet2"}],
            "text_streams": [
                {"source": "Sheet1!M10<comment>", "kind": "comment",
                 "text": self.phrase, "comment_author": "Test Author"},
                {"source": "Sheet2!M10<comment>", "kind": "comment",
                 "text": self.phrase, "comment_author": "Other Test Author"},
            ],
        }
        self.assertEqual(
            evaluate_m10_comments(extracted, None, self.nonce, self.target), []
        )

    def test_non_comment_stream_at_m10_is_not_promoted(self):
        extracted = {
            "sheets": [{"name": "Sheet1"}],
            "text_streams": [
                {"source": "Sheet1!M10", "kind": "cell",
                 "text": self.phrase, "comment_author": "Test Author"}
            ],
        }
        self.assertEqual(
            evaluate_m10_comments(extracted, "Sheet1", self.nonce, self.target), []
        )

    def test_public_redaction_removes_selector_and_candidate_material(self):
        raw = {
            "status": "MATCH_REVIEW",
            "workbook": {
                "path": "/private/mug-stock.xls",
                "size": 100,
                "sha256_before": "private-workbook-hash",
                "sha256_after": "private-workbook-hash",
                "source_unchanged": True,
                "converter": "synthetic",
            },
            "ps0323_selector": {
                "payload_hex": "private-ciphertext",
                "desk_nonce_hex": "private-nonce",
                "aes_plaintext_hex": "private-selector",
                "coordinate_sets": {"high_low": [[1, 2]]},
            },
            "sheets": [{"name": "Sheet1", "rows": 100, "columns": 20}],
            "sheet_mapping": None,
            "k08_target_sha256": "private-target-digest",
            "candidates": [{
                "orientation": "high_low",
                "input_base": 0,
                "sheet_mapping": "single",
                "cells": [{"address": "A1", "value": "private phrase"}],
                "complete": True,
                "match": True,
                "raw_joined_values": "private phrase",
                "normalized_phrase": "private phrase",
                "hmac16": "private-hmac",
                "component_sha256": "private-component-digest",
            }],
            "m10_comment_candidates": [{
                "source": "Sheet1!M10<comment>",
                "cell": "M10",
                "sheet": "Sheet1",
                "comment_author": "Private Author",
                "raw_comment_text": "private phrase",
                "normalized_phrase": "private phrase",
                "hmac16": "private-hmac",
                "component_sha256": "private-component-digest",
                "match": True,
                "interpretation": "M10 candidate",
            }],
            "m10_comment_sheet": "Sheet1",
        }
        public = redact_result(raw)
        encoded = json.dumps(public)
        for secret in (
            "/private/mug-stock.xls", "private-workbook-hash",
            "private-ciphertext", "private-nonce", "private-selector",
            "private-target-digest", "private phrase", "private-hmac",
            "private-component-digest", "Private Author",
        ):
            self.assertNotIn(secret, encoded)
        self.assertTrue(public["candidates"][0]["match"])
        self.assertTrue(public["m10_comment_candidates"][0]["match"])
        self.assertTrue(public["m10_comment_candidates"][0]["author_present"])
        self.assertTrue(public["ps0323_selector"]["redacted"])


if __name__ == "__main__":
    unittest.main()
