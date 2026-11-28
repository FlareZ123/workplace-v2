#!/usr/bin/env python3
"""Target-blind K08 emitter calibration for the source-selected TAILBIT run.

Reads only the crew-note source. It reproduces the already selected seven-note
TAILBIT run, applies the literal TAILBIT and LEN operations, and checks whether
their two 7-bit ASCII outputs equal the first token of the independently
selected N13 destination. It never reads acceptance.json, the K08 nonce, or any
commitment and does not test a final-caption candidate.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
TAILBIT_IDS = (12, 13, 14, 17, 18, 20, 22)


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def pack_lsb(bits: list[int]) -> int:
    return sum((bit & 1) << i for i, bit in enumerate(bits))


def main() -> None:
    root = Path(__file__).resolve().parents[2] / "resources" / "evidence"
    path = root / "crew" / "noticeboard-and-desk-notes.txt"
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256
    text = raw.decode("utf-8")

    notes: dict[int, str] = {}
    authors: dict[int, str] = {}
    for m in re.finditer(r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$", text, re.M):
        n = int(m.group(1))
        authors[n] = m.group(2)
        line = m.group(3)
        notes[n] = line.split(": ", 1)[1] if ": " in line else line
    assert set(notes) == set(range(1, 25))

    selected_authors = {"Simon", "Emily", "Gabriel"}
    selected_ids = [n for n in range(1, 25) if authors[n] in selected_authors]
    selected_heads = "".join(words(notes[n])[0][0].upper() for n in selected_ids)
    start = selected_heads.index("TAILBIT")
    tailbit_ids = tuple(selected_ids[start:start + 7])
    assert tailbit_ids == TAILBIT_IDS

    tail_bits = [ord(words(notes[n])[-1][-1].lower()) & 1 for n in tailbit_ids]
    len_bits = [len(notes[n]) & 1 for n in tailbit_ids]
    tail_value = pack_lsb(tail_bits)
    len_value = pack_lsb(len_bits)
    assert (tail_value, len_value) == (0x41, 0x74)

    emitted = bytes((tail_value, len_value)).decode("ascii")
    first_tokens = {n: words(body)[0] for n, body in notes.items()}
    matching_note_ids = [n for n, token in first_tokens.items()
                         if token.casefold() == emitted.casefold()]
    assert matching_note_ids == [13]

    # The destination N13 is independently fixed by the previously frozen
    # N09 heading TAILBIT channel: 12 is even, so LOW IF EVEN moves to 13.
    n09_heading = re.search(
        r"^N09 / [^\n]+\n([^:\n]+): ", text, re.M
    )
    assert n09_heading is not None
    heading_words = words(n09_heading.group(1))
    tail_selector = pack_lsb([ord(w[-1].lower()) & 1 for w in heading_words])
    assert tail_selector == 12
    destination = tail_selector + 1 if tail_selector % 2 == 0 else tail_selector
    assert destination == 13

    print({
        "source_pin": "PASS",
        "tailbit_run_ids": tailbit_ids,
        "tailbit_ascii": f"0x{tail_value:02X}",
        "len_ascii": f"0x{len_value:02X}",
        "emitted_token_matches_independently_selected_destination": True,
        "matching_note_ids": matching_note_ids,
        "destination_note": destination,
        "corpus_first_token_match_count": len(matching_note_ids),
        "k08_target_or_nonce_read": False,
        "complete_final_wording_emitted": False,
    })


if __name__ == "__main__":
    main()
