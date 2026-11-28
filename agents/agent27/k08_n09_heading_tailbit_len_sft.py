#!/usr/bin/env python3
"""Source-pinned K08 heading operator test: TAILBIT/LEN lineage.

This script reproduces only note IDs, operator outputs, and matched-control counts.
It does not read acceptance.json, the K08 nonce/commitment, or emit candidate wording.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import re

PINS = {
    "crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "mail/10.eml": "ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48",
    "mail/11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "mail/13.eml": "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
}


def load(root: Path, rel: str) -> str:
    raw = (root / rel).read_bytes()
    assert sha256(raw).hexdigest() == PINS[rel], rel
    return raw.decode("utf-8")


def pack_lsb(bits: list[int]) -> int:
    return sum((bit & 1) << i for i, bit in enumerate(bits))


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def low_if_even(value: int) -> int:
    return value + 1 if value % 2 == 0 else value


def author_mask_decode(authors: list[str], selected: set[str]) -> tuple[str, int, str]:
    bits = [int(author in selected) for author in authors]
    values = [pack_lsb(bits[start : start + 5]) for start in (0, 5, 10, 15)]
    word = "".join(chr(65 + value) if value < 26 else "?" for value in values)
    suffix = pack_lsb(bits[20:24])
    return word, suffix, "".join(map(str, bits))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("resources/evidence"))
    args = parser.parse_args()

    note_text = load(args.root, "crew/noticeboard-and-desk-notes.txt")
    headers = re.findall(r"^N(\\d{2}) / (\\w+) \\[censored\\]$", note_text, re.M)
    assert [int(n) for n, _ in headers] == list(range(1, 25))
    authors = [author for _, author in headers]
    author_by_note = {int(n): author for n, author in headers}
    assert Counter(authors) == {
        "Jason": 3,
        "Emily": 8,
        "Zoey": 4,
        "David": 3,
        "Gabriel": 3,
        "Simon": 3,
    }

    notes: dict[int, tuple[str | None, str]] = {}
    for match in re.finditer(r"^N(\\d{2}) / [^\\n]+\\n([^\\n]+)$", note_text, re.M):
        note_id = int(match.group(1))
        line = match.group(2)
        if ": " in line:
            heading, body = line.split(": ", 1)
        else:
            heading, body = None, line
        notes[note_id] = heading, body
    assert set(notes) == set(range(1, 25))

    senders: dict[str, str] = {}
    for slot, rel in {
        "K05": "mail/10.eml",
        "K06": "mail/11.eml",
        "K07": "mail/13.eml",
    }.items():
        mail = load(args.root, rel)
        sender = re.search(r"^From: (\\w+) \\[censored\\]", mail, re.M)
        assert sender is not None
        senders[slot] = sender.group(1)
    assert senders == {"K05": "Simon", "K06": "Emily", "K07": "Gabriel"}

    selected_authors = set(senders.values())
    stow_word, stow_suffix, stow_bits = author_mask_decode(authors, selected_authors)
    assert (stow_word, stow_suffix) == ("STOW", 14)
    selected_ids = [n for n in range(1, 25) if author_by_note[n] in selected_authors]
    assert selected_ids == [2, 5, 6, 7, 10, 12, 13, 14, 17, 18, 20, 22, 23, 24]

    selected_heads = "".join(words(notes[n][1])[0][0].upper() for n in selected_ids)
    assert selected_heads == "ATTPTTAILBITTE"
    tailbit_start = selected_heads.index("TAILBIT")
    tailbit_ids = selected_ids[tailbit_start : tailbit_start + len("TAILBIT")]
    assert tailbit_ids == [12, 13, 14, 17, 18, 20, 22]

    # Independent STOW A1Z26 route: character 14 of the four post-label bodies.
    stow_note_ids = [ord(letter) - 64 for letter in stow_word]
    assert stow_note_ids == [19, 20, 15, 23]
    char14 = "".join(notes[n][1][13] for n in stow_note_ids)
    assert char14 == " len"
    assert char14.strip().upper() == "LEN"

    # Existing cue-initial LOW BIT route selects N09; do not emit cue/source wording.
    cue_initial_values = [3, 12, 2, 13]
    n09_selector = pack_lsb([value & 1 for value in cue_initial_values])
    assert n09_selector == 9

    heading = notes[n09_selector][0]
    assert heading is not None
    heading_words = words(heading)
    assert len(heading_words) == 5

    head_value = pack_lsb([(ord(w[0].upper()) - 64) & 1 for w in heading_words])
    tail_value = pack_lsb([ord(w[-1].lower()) & 1 for w in heading_words])
    len_value = pack_lsb([len(w) & 1 for w in heading_words])
    assert (head_value, tail_value, len_value) == (9, 12, 23)
    tail_next = low_if_even(tail_value)
    len_next = low_if_even(len_value)
    assert (tail_next, len_next) == (13, 23)
    assert author_by_note[tail_next] == author_by_note[len_next] == "Emily"
    assert notes[tail_next][0] is None and notes[len_next][0] is None

    # Matched control over every colon-prefix heading under exactly the same parser.
    controls = []
    for note_id, (candidate_heading, _) in notes.items():
        if candidate_heading is None:
            continue
        candidate_words = words(candidate_heading)
        head = pack_lsb([(ord(w[0].upper()) - 64) & 1 for w in candidate_words])
        tail = pack_lsb([ord(w[-1].lower()) & 1 for w in candidate_words])
        length = pack_lsb([len(w) & 1 for w in candidate_words])
        tail_after = low_if_even(tail)
        len_after = low_if_even(length)
        controls.append((note_id, head, tail, length, tail_after, len_after))

    assert len(controls) == 19
    self_indexing = [row for row in controls if row[0] == row[1]]
    assert self_indexing == [(9, 9, 12, 23, 13, 23)]
    emily_pair = [
        row
        for row in controls
        if author_by_note.get(row[4]) == "Emily" and author_by_note.get(row[5]) == "Emily"
    ]
    assert emily_pair == [(9, 9, 12, 23, 13, 23)]

    # On the source-selected seven-note TAILBIT run, LEN and TAILBIT also each
    # yield one seven-bit ASCII value. This is recorded numerically only.
    run_len_value = pack_lsb([len(notes[n][1]) & 1 for n in tailbit_ids])
    run_tail_value = pack_lsb([ord(words(notes[n][1])[-1][-1].lower()) & 1 for n in tailbit_ids])
    assert (run_len_value, run_tail_value) == (116, 65)

    print("SOURCE_PINS PASS")
    print("STOW14", stow_bits, "selected_notes", selected_ids)
    print("TAILBIT_RUN", tailbit_ids)
    print("LEN_OPERATOR_FROM_STOW_CHAR14 PASS")
    print("N09_HEADING_CHANNELS", {"HEAD_LOWBIT": head_value, "TAILBIT": tail_value, "LEN_LOWBIT": len_value})
    print("LOW_IF_EVEN_TARGETS", {"TAILBIT": tail_next, "LEN_LOWBIT": len_next})
    print("HEADING_CONTROLS", {"colon_headings": len(controls), "self_indexing": len(self_indexing), "both_targets_emily": len(emily_pair)})
    print("TAILBIT_RUN_NUMERIC_OUTPUTS", {"TAILBIT": run_tail_value, "LEN_LOWBIT": run_len_value})
    print("K08_COMPLETE_CANDIDATE_EMITTED", False)


if __name__ == "__main__":
    main()
