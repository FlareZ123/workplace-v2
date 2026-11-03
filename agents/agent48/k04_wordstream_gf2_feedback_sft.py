"""H-17 K04 source-blind arbitrary four-word GF(2) recurrence falsifier.

Tests whether any single GF(2) linear or affine map from four 32-bit
visible words to the next 32-bit word can generate the intact ordinary
printer cohort. Selected target packet is excluded from reading.
Source checksum, source-based controls and genuine synthetic generators
are checked. Run: python agents/agent48/k04_wordstream_gf2_feedback_sft.py
"""
import hashlib
import json
import random
import re
from pathlib import Path

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROOT = Path(__file__).resolve().parents[2] / "resources"
MASK32 = (1 << 32) - 1


class Feedback:
    def __init__(self, affine):
        self.affine = affine
        self.basis = {}
        self.conflicts = []

    def input(self, four):
        assert len(four) == 4
        v = sum(w << (32 * j) for j, w in enumerate(four))
        return v | ((1 << 128) if self.affine else 0)

    def add(self, four, y, index):
        assert 0 <= y <= MASK32
        v = self.input(four)
        while v:
            pivot = v.bit_length() - 1
            if pivot in self.basis:
                b_v, b_y = self.basis[pivot]
                v ^= b_v
                y ^= b_y
            else:
                self.basis[pivot] = (v, y)
                return
        if y:
            self.conflicts.append(index)

    def predict(self, four):
        v, y = self.input(four), 0
        while v:
            pivot = v.bit_length() - 1
            if pivot not in self.basis:
                return None
            b_v, b_y = self.basis[pivot]
            v ^= b_v
            y ^= b_y
        return y


def original_words(reverse):
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = [row for row in raw.decode("ascii").splitlines() if "PAYLOAD=" in row]
    assert len(rows) == 133
    assert all("+00:00" in row for row in rows[:128])
    words = []
    for row in rows[:128]:
        match = re.search(r"PAYLOAD=([0-9A-F]{32})(?:\s|$)", row)
        assert match is not None
        packet = bytes.fromhex(match.group(1))
        chunk = [int.from_bytes(packet[i:i+4], "big") for i in range(0, 16, 4)]
        words.extend(reversed(chunk) if reverse else chunk)
    assert len(words) == 512
    return words


def evaluate(words, affine):
    assert len(words) == 512
    model = Feedback(affine)
    heldout = []
    for i in range(4, len(words)):
        history = words[i-4:i]
        if i >= 133:
            predicted = model.predict(history)
            heldout.append(predicted == words[i] if predicted is not None else None)
        model.add(history, words[i], i)
    return {
        "model": "affine" if affine else "homogeneous",
        "source_transitions": 508,
        "source_rank": len(model.basis),
        "first_source_conflict_word_index": model.conflicts[0] if model.conflicts else None,
        "conflicts": len(model.conflicts),
        "heldout_matches": sum(v is True for v in heldout),
        "heldout_mismatches": sum(v is False for v in heldout),
        "heldout_unpredictable": sum(v is None for v in heldout),
    }


def synthetic_words(seed, affine):
    rng = random.Random(seed)
    cols = [rng.getrandbits(32) for _ in range(128)]
    bias = rng.getrandbits(32) if affine else 0
    words = [rng.getrandbits(32) for _ in range(4)]
    for _ in range(508):
        val = sum(w << (32 * j) for j, w in enumerate(words[-4:]))
        out = bias
        while val:
            bit = val & -val
            out ^= cols[bit.bit_length() - 1]
            val ^= bit
        words.append(out)
    return words


def main():
    tests = []
    for reverse in (False, True):
        words = original_words(reverse)
        for affine in (False, True):
            r = evaluate(words, affine)
            assert r["first_source_conflict_word_index"] == (132 if reverse else 130)
            assert r["conflicts"] == (379 if affine else 380)
            r["reverse_four_words_in_packet"] = reverse
            tests.append(r)

    positives = []
    for affine in (False, True):
        original = synthetic_words(0x20261103 + int(affine), affine)
        result = evaluate(original, affine)
        assert result["conflicts"] == 0 and result["heldout_matches"] == 379
        corrupt = original.copy()
        corrupt[200] ^= 1
        broken = evaluate(corrupt, affine)
        assert broken["first_source_conflict_word_index"] <= 204
        positives.append({"affine": affine, "all_508_synthetic_transitions": "PASS",
                          "synthetic_one_bit_tamper": "REJECTED"})
    print(json.dumps({
        "original_spool_sha256": SOURCE_SHA,
        "disputed_row_not_read": True,
        "source_tests": tests,
        "synthetic_controls": positives,
        "result": "ORIGINAL_SOURCE_CONTRADICTION",
    }, indent=2))


if __name__ == "__main__":
    main()
