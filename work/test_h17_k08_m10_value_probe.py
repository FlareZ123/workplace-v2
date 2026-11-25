import hashlib
import unittest

from h17_k08_m10_value_probe import (
    EXPECTED_SYNTHETIC_HMAC16, evaluate_m10_values, k08_component, normalize,
)

NONCE = bytes(range(16))
PHRASE = "The sea is quiet and the mugs are waiting by the window."


def target_for(phrase):
    return hashlib.sha256(k08_component(NONCE, phrase)).digest()


class M10ValueProbeTests(unittest.TestCase):
    def test_route_normalization_known_answer(self):
        phrase = "A good watch leaves the room ready for the next pair of hands"
        self.assertEqual(k08_component(NONCE, phrase).hex().upper(), EXPECTED_SYNTHETIC_HMAC16)
        self.assertEqual(normalize("  A-GOOD, watch!\nLEAVES "), "a good watch leaves")

    def test_literal_m10_value_hits_only_exact_cell(self):
        extracted = {
            "sheets": [{"name": "Stock", "state": "visible"}],
            "text_streams": [
                {"kind": "cell", "source": "Stock!M10", "data_type": "s", "text": PHRASE,
                 "converted_cached_value": PHRASE},
                {"kind": "cell", "source": "Stock!M11", "data_type": "s", "text": PHRASE,
                 "converted_cached_value": PHRASE},
            ],
        }
        result = evaluate_m10_values(extracted, NONCE, target_for(PHRASE), reveal=True)
        self.assertEqual(result["status"], "MATCH_REQUIRES_SOURCE_REVIEW")
        self.assertEqual(result["match_count"], 1)
        self.assertEqual(result["candidates"][0]["source"], "Stock!M10")
        self.assertEqual(result["candidates"][0]["value_kind"], "literal_cell_value")

    def test_formula_text_is_never_hashed_but_cache_is_separate_candidate(self):
        extracted = {
            "sheets": [{"name": "Hidden", "state": "hidden"}],
            "text_streams": [{
                "kind": "cell", "source": "Hidden!M10", "data_type": "f",
                "text": '=CONCATENATE("The sea"," is quiet")',
                "converted_cached_value": PHRASE,
            }],
        }
        result = evaluate_m10_values(extracted, NONCE, target_for(PHRASE), reveal=True)
        self.assertEqual(result["match_count"], 1)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["value_kind"], "converted_formula_cache")
        self.assertIn("CONCATENATE", candidate["formula_text"])
        self.assertIn("may have been recalculated", candidate["cache_provenance"])
        self.assertEqual(result["formula_records"][0]["sheet_state"], "hidden")

    def test_formula_without_cache_is_incomplete_not_negative(self):
        extracted = {
            "sheets": [{"name": "Stock", "state": "visible"}],
            "text_streams": [{"kind": "cell", "source": "Stock!M10", "data_type": "f",
                              "text": "=A1&B1", "converted_cached_value": None}],
        }
        result = evaluate_m10_values(extracted, NONCE, target_for(PHRASE), reveal=True)
        self.assertEqual(result["status"], "M10_FORMULA_WITHOUT_TEXT_CACHE")
        self.assertEqual(result["candidate_count"], 0)

    def test_default_evaluation_redacts_phrase_and_component_material(self):
        extracted = {
            "sheets": [{"name": "Stock", "state": "visible"}],
            "text_streams": [{"kind": "cell", "source": "Stock!M10", "data_type": "s", "text": PHRASE}],
        }
        result = evaluate_m10_values(extracted, NONCE, target_for(PHRASE))
        self.assertTrue(result["redaction_applied"])
        self.assertEqual(result["match_count"], 1)
        candidate = result["candidates"][0]
        for key in ("raw_text", "normalized_phrase", "hmac16", "component_sha256"):
            self.assertNotIn(key, candidate)

    def test_no_m10_value_is_not_a_global_k08_negative(self):
        extracted = {
            "sheets": [{"name": "Stock", "state": "visible"}],
            "text_streams": [{"kind": "cell", "source": "Stock!C3", "data_type": "s", "text": PHRASE}],
        }
        result = evaluate_m10_values(extracted, NONCE, target_for(PHRASE), reveal=True)
        self.assertEqual(result["status"], "NO_M10_TEXT_VALUE")
        self.assertEqual(result["candidate_count"], 0)

    def test_each_sheet_m10_is_independently_reported(self):
        extracted = {
            "sheets": [
                {"name": "Visible", "state": "visible"},
                {"name": "Hidden", "state": "hidden"},
            ],
            "text_streams": [
                {"kind": "cell", "source": "Visible!M10", "data_type": "s", "text": "decoy"},
                {"kind": "cell", "source": "Hidden!M10", "data_type": "s", "text": PHRASE},
            ],
        }
        result = evaluate_m10_values(extracted, NONCE, target_for(PHRASE), reveal=True)
        self.assertEqual([x["sheet"] for x in result["candidates"]], ["Visible", "Hidden"])
        self.assertEqual(result["candidates"][1]["sheet_state"], "hidden")
        self.assertTrue(result["candidates"][1]["match"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
