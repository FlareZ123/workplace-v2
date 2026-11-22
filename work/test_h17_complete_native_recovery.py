"""Read-only complete REC8/1 recovery assembly with synthetic source controls."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h17_ax7782_k08_phrase_intake import k08_component
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

    def execute(self, base=None):
        return recover_complete(
            self.spool, self.caption,
            targets=self.targets, routing=self.routing,
            six_pass=self.base if base is None else base,
        )

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
