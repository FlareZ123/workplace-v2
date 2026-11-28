#!/usr/bin/env python3
"""Target-blind STOW14 -> LEN -> N02 -> N13 -> N23 version-lineage control."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s.lower())


def pack_lsb(bits: list[int]) -> int:
    return sum((b & 1) << i for i, b in enumerate(bits))


def lowbit(text: str) -> int:
    return pack_lsb([ord(c.lower()) & 1 for c in text])


def low_if_even(value: int) -> int:
    return value + 1 if value % 2 == 0 else value


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256

    notes = {}
    authors = {}
    raw_body = {}
    labels = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw.decode("utf-8"),
        re.M,
    ):
        n = int(m.group(1))
        authors[n] = m.group(2)
        line = m.group(3)
        if ": " in line:
            label, body = line.split(": ", 1)
            labels[n] = label
        else:
            body = line
            labels[n] = ""
        raw_body[n] = body
        notes[n] = words(body)
    assert set(notes) == set(range(1, 25))

    # Reproduce the fixed STOW14 author-bit selector from the source.
    chosen = {"Simon", "Emily", "Gabriel"}
    author_bits = [1 if authors[n] in chosen else 0 for n in range(1, 25)]
    groups = [
        pack_lsb(author_bits[offset:offset + 5])
        for offset in (0, 5, 10, 15)
    ]
    stow = "".join(chr(ord("A") + value) for value in groups)
    suffix = pack_lsb(author_bits[20:24])
    assert stow == "STOW" and suffix == 14

    stow_ids = [ord(c) - ord("A") + 1 for c in stow]
    assert stow_ids == [19, 20, 15, 23]

    # Use the literal STOW suffix as the one-based character column, exactly
    # on the already-established post-label bodies.
    column = "".join(raw_body[n][suffix - 1] for n in stow_ids)
    assert column == " len"
    emitted = column.strip().upper()
    assert emitted == "LEN"

    # Existing whole-token LOW BIT convention turns LEN into selector 2.
    selector = lowbit(emitted)
    assert selector == 2
    assert labels[selector].lower().startswith("first draft")

    # Independent N10/THE branch also selects the same first draft.
    def lower_if_even_word(w: str) -> int:
        return low_if_even(lowbit(w))

    n10_selectors = tuple(lower_if_even_word(w) for w in notes[10][:3])
    assert n10_selectors == (5, 15, 11)
    the = "".join(notes[n][0][0].upper() for n in n10_selectors)
    assert the == "THE"
    the_ids = [ord(c) - ord("A") + 1 for c in the]
    assert the_ids == [20, 8, 5]
    the_counts = [len(notes[n]) for n in the_ids]
    assert the_counts == [30, 13, 14]
    the_selector = pack_lsb([count & 1 for count in the_counts])
    assert the_selector == selector == 2

    # Apply the already reconstructed COUNT LINE / LOW IF EVEN operation
    # starting at the independently selected First draft.
    lineage = []
    cur = selector
    for _ in range(2):
        count = len(notes[cur])
        nxt = low_if_even(count)
        lineage.append((cur, count, nxt))
        cur = nxt
    assert lineage == [(2, 13, 13), (13, 22, 23)]
    assert "margin" in notes[23]
    assert "finally" in notes[23]

    print({
        "source_pin": "PASS",
        "target_or_nonce_read": False,
        "stow": stow,
        "suffix": suffix,
        "stow_note_ids": stow_ids,
        "column14_raw": repr(column),
        "column14_token": emitted,
        "LEN_lowbit_selector": selector,
        "selected_role": "N02 First draft",
        "independent_THE_selector": the_selector,
        "selectors_agree": selector == the_selector,
        "count_line_low_if_even_lineage": lineage,
        "terminal_note": 23,
        "terminal_role": "final-margin witness",
        "complete_author_final_wording_emitted": False,
    })


if __name__ == "__main__":
    main()
