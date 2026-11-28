#!/usr/bin/env python3
"""Source-only N23 landmark gaps -> draft/photo roles -> HEAD twice -> N01."""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s.lower())


def pack(bits) -> int:
    return sum((b & 1) << i for i, b in enumerate(bits))


def head_low(ws: list[str]) -> int:
    return pack((ord(w[0].upper()) - ord("A") + 1) & 1 for w in ws)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256

    labels: dict[int, str] = {}
    bodies: dict[int, list[str]] = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw.decode("utf-8"),
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3)
        if ": " in line:
            label, body = line.split(": ", 1)
        else:
            label, body = "", line
        labels[n] = label
        bodies[n] = words(body)
    assert set(bodies) == set(range(1, 25))

    # Primary path: N23's explicit final-text/carrier vocabulary in source
    # order, ending on the literal finality marker "finally".
    n23 = bodies[23]
    final_landmarks = ["wording", "margin", "envelope", "words", "finally"]
    assert all(n23.count(x) == 1 for x in final_landmarks)
    final_positions = [n23.index(x) + 1 for x in final_landmarks]
    assert final_positions == [2, 5, 12, 16, 18]
    final_gaps = [
        final_positions[i + 1] - final_positions[i] - 1
        for i in range(4)
    ]
    assert final_gaps == [2, 6, 3, 1]
    assert labels[2] == "First draft for the crew board"
    assert labels[6] == "Second desk draft"
    assert labels[3] == "Kitchen photograph"
    assert labels[1] == "For the photograph of the empty bench"

    # Full positional denominator for the primary four-gap vector.
    final_same_gap_sets = []
    for comb in combinations(range(1, len(n23) + 1), 5):
        got = [comb[i + 1] - comb[i] - 1 for i in range(4)]
        if got == final_gaps:
            final_same_gap_sets.append((comb, [n23[i - 1] for i in comb]))
    assert len(final_same_gap_sets) == 5
    assert (tuple(final_positions), final_landmarks) in final_same_gap_sets

    # Secondary path: use the sentence-final coreference "it" instead of
    # "finally". This reaches N04, whose text supplies a literal continuation.
    coref_landmarks = ["wording", "margin", "envelope", "words", "it"]
    assert all(n23.count(x) == 1 for x in coref_landmarks)
    coref_positions = [n23.index(x) + 1 for x in coref_landmarks]
    assert coref_positions == [2, 5, 12, 16, 21]
    coref_gaps = [
        coref_positions[i + 1] - coref_positions[i] - 1
        for i in range(4)
    ]
    assert coref_gaps == [2, 6, 3, 4]
    assert labels[4] == "Under the old shift photograph"

    coref_same_gap_sets = []
    for comb in combinations(range(1, len(n23) + 1), 5):
        got = [comb[i + 1] - comb[i] - 1 for i in range(4)]
        if got == coref_gaps:
            coref_same_gap_sets.append((comb, [n23[i - 1] for i in comb]))
    assert coref_same_gap_sets == [
        ((1, 4, 11, 15, 20), ["the", "my", "the", "the", "on"]),
        ((2, 5, 12, 16, 21), coref_landmarks),
    ]

    # N04 literally instructs "Count the heads twice". Use the established
    # A1Z26-head low-bit pack. First pass across F/S/K/U -> 14.
    heading_heads = [words(labels[n])[0] for n in coref_gaps]
    assert heading_heads == ["first", "second", "kitchen", "under"]
    first_head = head_low(heading_heads)
    assert first_head == 14
    assert labels[first_head] == "Sunrise photograph"

    # Second pass on the selected N14 heading "Sunrise photograph" -> 1.
    second_head = head_low(words(labels[first_head]))
    assert second_head == 1
    assert labels[second_head] == "For the photograph of the empty bench"

    # Independent N10 semantic control: among all five photograph-labelled
    # records, N01 alone contains a tea/cup token, matching N10's explicit
    # return to "the photograph after the last cup."
    photo_notes = [n for n in range(1, 25) if "photograph" in labels[n].lower()]
    assert photo_notes == [1, 3, 4, 8, 14]
    tea_or_cup = [
        n for n in photo_notes
        if any(w in {"tea", "cup"} for w in bodies[n])
    ]
    assert tea_or_cup == [1]

    print({
        "source_pin": "PASS",
        "target_or_nonce_read": False,
        "primary_landmarks": final_landmarks,
        "primary_positions": final_positions,
        "primary_between_counts": final_gaps,
        "primary_selected_roles": [labels[n] for n in final_gaps],
        "primary_same_gap_position_sets": len(final_same_gap_sets),
        "coref_landmarks": coref_landmarks,
        "coref_positions": coref_positions,
        "coref_between_counts": coref_gaps,
        "coref_same_gap_position_sets": len(coref_same_gap_sets),
        "coref_other_same_gap_tokens": coref_same_gap_sets[0][1],
        "heading_heads": heading_heads,
        "HEAD_pass1": first_head,
        "HEAD_pass1_role": labels[first_head],
        "HEAD_pass2": second_head,
        "HEAD_pass2_role": labels[second_head],
        "photograph_records": photo_notes,
        "photo_records_with_tea_or_cup": tea_or_cup,
        "complete_author_final_wording_emitted": False,
    })


if __name__ == "__main__":
    main()
