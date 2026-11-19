#!/usr/bin/env python3
"""Exact conditional author-label permutation null for the CREW4 -> LOW chain.

Run from the workplace-v2 repository root:
    python agents/agent9/k08_crew4_author_null.py
Only standard-library modules are used. The note source is hash-pinned.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
from collections import Counter
from fractions import Fraction
from math import comb, factorial, prod
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt"
EXPECTED_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def parse_notes() -> dict[int, dict]:
    raw = SOURCE.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA:
        raise AssertionError(f"note source hash mismatch: {actual}")
    text = raw.decode("utf-8")
    matches = re.findall(r"(?ms)^N(\d\d) / ([^\n]+)\n(.+?)(?=\n\nN\d\d /|\Z)", text)
    notes = {}
    for number, author_text, body_text in matches:
        number = int(number)
        body = body_text.strip()
        body = body.split(":", 1)[1].strip() if ":" in body else body
        tokens = re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", body)
        notes[number] = {
            "author": author_text.split()[0],
            "body": body,
            "tokens": tokens,
            "words": len(tokens),
            "head": tokens[0][0].upper(),
        }
    if set(notes) != set(range(1, 25)):
        raise AssertionError("note IDs are not exactly N01..N24")
    return notes


def decode_author(bits: list[int], base: int, bit_order: str) -> str:
    groups = []
    for start in range(0, 20, 5):
        if bit_order == "LSB":
            value = sum(bits[start + j] << j for j in range(5))
        else:
            value = sum(bits[start + j] << (4 - j) for j in range(5))
        groups.append(value)
    if bit_order == "LSB":
        tail = sum(bits[20 + j] << j for j in range(4))
    else:
        tail = sum(bits[20 + j] << (3 - j) for j in range(4))
    if base == 0:
        letters = "".join(chr(65 + value) if 0 <= value < 26 else "?" for value in groups)
    else:
        letters = "".join(chr(64 + value) if 1 <= value <= 26 else "?" for value in groups)
    return letters + str(tail)


def ways_david_fourth(k: int, other_counts: list[int]) -> int:
    """Assignments of four other author labels to 13 slots with exactly 2 labels in first k."""
    total = 0
    for i in range(4):
        for j in range(i + 1, 4):
            for count_i in range(1, min(other_counts[i], k) + 1):
                count_j = k - count_i
                if count_j < 1 or count_j > other_counts[j]:
                    continue
                remaining = other_counts.copy()
                remaining[i] -= count_i
                remaining[j] -= count_j
                total += comb(k, count_i) * factorial(13 - k) // prod(factorial(x) for x in remaining)
    return total


def main() -> None:
    notes = parse_notes()
    authors = [notes[n]["author"] for n in range(1, 25)]
    first_order = list(dict.fromkeys(authors))
    author_counts = Counter(authors)
    encoding_variants = {}
    for base in (0, 1):
        for bit_order in ("LSB", "MSB"):
            outputs = {}
            for author in first_order:
                bits = [int(notes[n]["author"] == author) for n in range(1, 25)]
                outputs[author] = decode_author(bits, base, bit_order)
            encoding_variants[f"A{base}_{bit_order}"] = outputs

    emily_positions = [n for n in range(1, 25) if notes[n]["author"] == "Emily"]
    david_positions = [n for n in range(1, 25) if notes[n]["author"] == "David"]
    david_counts = [notes[n]["words"] for n in david_positions]
    david_word = "".join(chr(65 + count) for count in david_counts)
    emily_heads = "".join(notes[n]["head"] for n in emily_positions)

    # Enumerate all source-valid one-row +1 edits: keep IDs sorted and unique.
    lowered = []
    for position, original in enumerate(emily_positions):
        candidate = emily_positions.copy()
        candidate[position] += 1
        if candidate != sorted(candidate) or len(set(candidate)) != len(candidate):
            continue
        initials = "".join(notes[n]["head"] for n in candidate)
        count_letters = "".join(chr(65 + notes[n]["words"]) if notes[n]["words"] < 26 else "?" for n in candidate)
        instruction = initials[0] + count_letters[1:4] + initials[5:8]
        lowered.append({"original_note": original, "replacement_note": candidate[position],
                        "initials": initials, "count_letters": count_letters,
                        "low_bit_instruction": instruction})
    exact_shift = [row for row in lowered if row["initials"] == "ATEALBIT"]
    exact_instruction = [row for row in lowered if row["low_bit_instruction"] == "ALOWBIT"]
    if len(lowered) != 7 or exact_shift != exact_instruction or len(exact_shift) != 1:
        raise AssertionError("Emily one-row lowering result changed")
    selected_shift = exact_shift[0]
    low_bits = [ord(letter) & 1 for letter in selected_shift["initials"]]
    low_byte = sum(bit << index for index, bit in enumerate(low_bits))
    if low_byte != 0x4D:
        raise AssertionError("ATEALBIT ASCII-low-bit result changed")

    # Conditional permutation null. CREW4 fixes Emily's exact 8-position subset.
    # Given those positions, the remaining 16 slots are assigned labels with
    # counts Jason=3, Zoey=4, David=3, Gabriel=3, Simon=3. David is fourth in
    # first-appearance order iff exactly two other labels occur before min(David).
    non_emily = [n for n in range(1, 25) if n not in emily_positions]
    low_triples = [
        triple for triple in itertools.combinations(non_emily, 3)
        if tuple(notes[n]["words"] for n in triple) == (11, 14, 22)
    ]
    other_counts = [3, 4, 3, 3]
    total_other_assignments = factorial(13) // prod(factorial(x) for x in other_counts)
    summed_ways = 0
    triple_details = []
    for triple in low_triples:
        earliest_david = min(triple)
        k = sum(n < earliest_david for n in non_emily)
        ways = ways_david_fourth(k, other_counts)
        summed_ways += ways
        triple_details.append({"david_positions": list(triple), "earliest": earliest_david,
                               "earlier_non_emily_positions": k,
                               "assignments_making_David_fourth": ways})

    p_emily_exact_crew4 = Fraction(1, comb(24, 8))
    p_david_fourth_and_low_given_emily = Fraction(
        summed_ways, total_other_assignments * comb(16, 3)
    )
    p_joint = p_emily_exact_crew4 * p_david_fourth_and_low_given_emily

    result = {
        "source_sha256": EXPECTED_SHA,
        "author_counts": dict(author_counts),
        "first_appearance_order": first_order,
        "encoding_variants": encoding_variants,
        "exact_CREW4_variant_hits": [
            {"variant": variant, "author": author}
            for variant, outputs in encoding_variants.items()
            for author, output in outputs.items() if output == "CREW4"
        ],
        "emily_positions": emily_positions,
        "emily_head_string": emily_heads,
        "valid_one_row_plus_one_edits": len(lowered),
        "one_row_plus_one_edits": lowered,
        "unique_ATEALBIT_and_ALOWBIT_edit": selected_shift,
        "ATEALBIT_ASCII_low_bits": low_bits,
        "ATEALBIT_ASCII_low_byte": low_byte,
        "N11_first_word": notes[11]["tokens"][0],
        "david_positions": david_positions,
        "david_body_word_counts": david_counts,
        "david_A0_word": david_word,
        "low_triple_count_among_560": len(low_triples),
        "low_triples": triple_details,
        "p_exact_CREW4_under_author_label_permutation": str(p_emily_exact_crew4),
        "p_David_fourth_and_LOW_given_Emily_positions": str(p_david_fourth_and_low_given_emily),
        "p_joint_exact_CREW4_fourth_David_LOW": str(p_joint),
        "joint_reciprocal": int(1 / p_joint),
        "null_scope": "uniform author-label permutation preserving author counts; encoding A0_LSB fixed; word target CREW4 and A0 word LOW conditioned on observed interpretation",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
