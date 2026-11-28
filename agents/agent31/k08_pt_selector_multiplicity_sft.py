#!/usr/bin/env python3
"""Source-only complete retry-mask K08 PT parity specificity audit.

No K08 desk nonce, HMAC, acceptance, or final wording read.
Run: python agents/agent31/k08_pt_selector_multiplicity_sft.py resources/evidence/transfers/transfer-audit.jsonl
"""
import collections
import itertools
import hashlib
import json
import sys
from pathlib import Path

PIN = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
EXPECTED = {
    "AX-7778": (0, 0, 8), "AX-7781": (0, 0, 0),
    "AX-7782": (32, 8, 64), "AX-7783": (0, 0, 0),
}


def pack_tailbits(buf: bytes, reversed_bits=False, reversed_bytes=False):
    assert len(buf) == 16
    vals = [sum((buf[8*i+j] & 1) << (7-j if reversed_bits else j)
                for j in range(8)) for i in range(2)]
    return bytes(vals[::-1] if reversed_bytes else vals)


def note_pair(packed):
    if any(x.bit_count() % 2 for x in packed):
        return None
    chars = bytes(x & 127 for x in packed)
    if all(65 <= c <= 88 for c in chars):
        return chars.decode("ascii")
    return None


def main(path):
    data = Path(path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == PIN
    chunks = collections.defaultdict(dict)
    for raw in data.splitlines():
        if not raw.strip():
            continue
        row = json.loads(raw)
        if row.get("kind") == "CHUNK":
            chunks[row["transfer"]][(row["seq"], row["attempt"])] = bytes.fromhex(row["checkpoint"])
    assert len(chunks) == 4
    for transfer, d in sorted(chunks.items()):
        assert set(d) == {(s, a) for s in range(8) for a in (1, 2)}
        masks_valid = []
        masks_pt = []
        variants_valid = variants_pt = 0
        for mask in range(256):
            raw = b"".join(d[(s, 1 + ((mask >> s) & 1))] for s in range(8))
            for reverse_bits in (False, True):
                for reverse_bytes in (False, True):
                    packed = pack_tailbits(raw, reverse_bits, reverse_bytes)
                    token = note_pair(packed)
                    if token is not None:
                        variants_valid += 1
                    if token == "PT":
                        variants_pt += 1
                    if not reverse_bits and not reverse_bytes:
                        if token is not None:
                            masks_valid.append(mask)
                        if token == "PT":
                            masks_pt.append(mask)
        assert (len(masks_valid), len(masks_pt), variants_valid) == EXPECTED[transfer]
        assert variants_pt == (8 if transfer == "AX-7782" else 0)
        frozen = 0xAA  # even seq -> attempt1, odd seq -> attempt2
        raw = b"".join(d[(s, 1 + ((frozen >> s) & 1))] for s in range(8))
        frozen_word = pack_tailbits(raw)
        assert frozen_word == bytes.fromhex({
            "AX-7778": "694A", "AX-7781": "C28A",
            "AX-7782": "50D4", "AX-7783": "CF59",
        }[transfer])
        print(transfer, "frozen=" + frozen_word.hex().upper(),
              "frozen_token=" + str(note_pair(frozen_word)),
              "canonical_valid=" + str(len(masks_valid)),
              "canonical_PT=" + str(len(masks_pt)),
              "PT_masks=" + str(masks_pt),
              "four_variant_valid=" + str(variants_valid),
              "four_variant_PT=" + str(variants_pt))

    # Independently test the claimed source seq0..7 order under all 8! permutations.
    # The selected mixed attempt mask is held fixed at 0xAA; no acceptance/HMAC involved.
    expected_perm = {"AX-7778": (0, 0), "AX-7781": (0, 0),
                     "AX-7782": (5184, 144), "AX-7783": (504, 0)}
    for transfer, d in sorted(chunks.items()):
        parts = [d[(s, 1 + ((0xAA >> s) & 1))] for s in range(8)]
        valid, exact_pt = 0, 0
        all_bytes = set()
        for seq_permutation in itertools.permutations(range(8)):
            blob = b"".join(parts[j] for j in seq_permutation)
            packed = pack_tailbits(blob)
            all_bytes.add(packed)
            token = note_pair(packed)
            if token is not None:
                valid += 1
            if token == "PT":
                exact_pt += 1
        assert (valid, exact_pt) == expected_perm[transfer]
        assert len(all_bytes) == (1120 if transfer == "AX-7783" else 280)
        print(transfer, "source_fixed_attempt_mask=0xAA",
              "seq_permutations=40320", "valid_A_X=" + str(valid),
              "exact_PT=" + str(exact_pt), "distinct_lowbit_pair=" + str(len(all_bytes)))


    # Exact *joint* retry-mask x chunk-order factorial, not a product of the
    # two conditional marginal rates. Every chunk contributes two successive
    # tail bits, and arbitrary chunk reordering never changes their pair type.
    target_bytes = bytes.fromhex("50D4")
    target_bits = tuple((target_bytes[i // 8] >> (i % 8)) & 1 for i in range(16))
    target_pairs = collections.Counter(tuple(target_bits[2*i:2*i+2]) for i in range(8))
    assert target_pairs == {(0, 0): 3, (1, 0): 4, (1, 1): 1}
    # Each matching multiset has exactly 3! * 4! * 1! = 144 permutations
    # of its eight *individually labeled* chunks with ordered bytes 50D4.
    per_matching_mask = 144
    whole_joint = 0
    for transfer, d in sorted(chunks.items()):
        compatible_masks = []
        for mask in range(256):
            chosen_pairs = collections.Counter(
                tuple(x & 1 for x in d[(s, 1 + ((mask >> s) & 1))])
                for s in range(8)
            )
            if chosen_pairs == target_pairs:
                compatible_masks.append(mask)
        assert len(compatible_masks) == (16 if transfer == "AX-7782" else 0)
        hit_count = per_matching_mask * len(compatible_masks)
        whole_joint += hit_count
        print(transfer, "joint_retry_masks=256", "joint_seq_orders=40320",
              "PT_eligible_masks=" + str(len(compatible_masks)),
              "joint_exact_PT=" + str(hit_count),
              "joint_denominator=10321920")
    assert whole_joint == 2304
    print("ALL_TRANSFERS joint_exact_PT=2304 joint_total=41287680"
          " conditional_AX7782_fraction=1/4480"
          " across_four_transfer_fraction=1/17920")

    print("PIN=PASS exact_transfer_controls=PASS target_or_nonce_read=False")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: script.py transfer-audit.jsonl")
    main(sys.argv[1])
