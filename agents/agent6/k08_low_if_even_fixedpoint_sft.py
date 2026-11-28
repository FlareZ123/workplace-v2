#!/usr/bin/env python3
"""Source-only LOW IF EVEN fixed-point check for the selected N13/N20 K08 records.

Reads only the crew-note text, pins its SHA-256, reproduces the existing N09
heading-tail selector -> N13 route, and asks which words are fixed points of
the already-established LOW IF EVEN one-based selector. It does not read the
K08 nonce, acceptance commitment, routing file, or any final-caption candidate.
"""
from __future__ import annotations
import hashlib
import re
import sys
from pathlib import Path

CREW_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def strip_label(text: str) -> str:
    return text.split(":", 1)[1].lstrip() if ":" in text else text


def low_value(word: str) -> int:
    return sum((ord(ch.upper()) & 1) << i
               for i, ch in enumerate(word) if ch.isalnum())


def low_if_even(value: int) -> int:
    return value + 1 if value % 2 == 0 else value


def fixed_points(body: str) -> list[tuple[int, str, int, int]]:
    out = []
    for position, word in enumerate(words(strip_label(body)), 1):
        value = low_value(word)
        adjusted = low_if_even(value)
        if adjusted == position:
            out.append((position, word, value, adjusted))
    return out


def main(path: str) -> None:
    raw = Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CREW_SHA
    text = raw.decode("utf-8")
    notes = {}
    for match in re.finditer(r"^N(\d{2}) / [^\n]+\n([^\n]+)$", text, re.M):
        notes[int(match.group(1))] = match.group(2)
    assert set(notes) == set(range(1, 25))

    heading_words = words(notes[9].split(":", 1)[0])
    heading_tail_selector = sum(
        (ord(word[-1].lower()) & 1) << i
        for i, word in enumerate(heading_words)
    )
    assert heading_tail_selector == 12
    destination = low_if_even(heading_tail_selector)
    assert destination == 13

    n13 = fixed_points(notes[destination])
    n20 = fixed_points(notes[20])
    assert n13 == [(1, "At", 1, 1), (5, "the", 4, 5)]
    assert n20 == [(1, "I", 1, 1), (19, "table", 18, 19)]

    print({
        "source_pin": "PASS",
        "n09_heading_tail_selector": heading_tail_selector,
        "destination_note": destination,
        "n13_fixed_points": n13,
        "n20_fixed_points": n20,
        "n13_emits": "At the",
        "n20_nontrivial_fixed_point": "table",
        "acceptance_or_nonce_read": False,
        "complete_final_wording_emitted": False,
    })


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: script noticeboard-and-desk-notes.txt")
    main(sys.argv[1])
