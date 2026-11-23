import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "work"
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

from work.h17_k08_mug_stock_cell_selector import (
    evaluate_m10_comments,
    k08_component,
    normalize,
    sha256,
)
if str(WORK_DIR) in sys.path:
    sys.path.remove(str(WORK_DIR))


class K08M10CommentSelectorTests(unittest.TestCase):
    def test_only_selected_sheet_m10_comment_is_checked_and_author_retained(self):
        nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        phrase = "The sea is quiet when the last watch ends."
        target = bytes.fromhex(sha256(k08_component(nonce, normalize(phrase))))
        extracted = {
            "text_streams": [
                {"source": "Sheet1!M10<comment>", "kind": "comment",
                 "text": phrase, "comment_author": "Emily"},
                {"source": "Sheet1!M9<comment>", "kind": "comment",
                 "text": phrase, "comment_author": "Emily"},
                {"source": "Sheet2!M10<comment>", "kind": "comment",
                 "text": phrase, "comment_author": "Other"},
                {"source": "Sheet1!A1<comment>", "kind": "comment",
                 "text": phrase, "comment_author": "Emily"},
            ]
        }
        result = evaluate_m10_comments(extracted, "Sheet1", nonce, target)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["match"])
        self.assertEqual(result[0]["source"], "Sheet1!M10<comment>")
        self.assertEqual(result[0]["comment_author"], "Emily")
        self.assertEqual(result[0]["normalized_phrase"], normalize(phrase))

    def test_no_sheet_mapping_means_no_comment_search(self):
        nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        phrase = "A synthetic margin note."
        target = hashlib.sha256(k08_component(nonce, normalize(phrase))).digest()
        extracted = {"text_streams": [
            {"source": "Sheet1!M10<comment>", "kind": "comment",
             "text": phrase, "comment_author": "Emily"}
        ]}
        self.assertEqual(evaluate_m10_comments(extracted, None, nonce, target), [])

    def test_non_comment_stream_at_m10_is_not_promoted(self):
        nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        phrase = "A synthetic margin note."
        target = hashlib.sha256(k08_component(nonce, normalize(phrase))).digest()
        extracted = {"text_streams": [
            {"source": "Sheet1!M10", "kind": "cell",
             "text": phrase, "comment_author": "Emily"}
        ]}
        self.assertEqual(evaluate_m10_comments(extracted, "Sheet1", nonce, target), [])


if __name__ == "__main__":
    unittest.main()
