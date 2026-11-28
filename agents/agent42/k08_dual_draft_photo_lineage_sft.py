#!/usr/bin/env python3
"""Target-blind THE/MHI -> N02/N06 + shared N01 draft/photo lineage."""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def pack_lsb(bits):
    return sum((bit & 1) << i for i, bit in enumerate(bits))


def lowbit(word: str) -> int:
    return sum((ord(c.lower()) & 1) << i for i, c in enumerate(word))


def lower_if_even(value: int) -> int:
    return value + 1 if value % 2 == 0 else value


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256

    notes = {}
    lines = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw.decode("utf-8"),
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3)
        body = line.split(": ", 1)[1] if ": " in line else line
        notes[n] = re.findall(r"[A-Za-z0-9]+", body.lower())
        lines[n] = line
    assert set(notes) == set(range(1, 25))

    # Upstream token 1: independently established raw N20 body LOW BIT head -> MHI.
    n20_body = (
        re.search(
            r"^N20 / \w+ \[censored\]\n([^\n]+)$",
            raw.decode("utf-8"),
            re.M,
        )
        .group(1)
    )
    n20_bits = [ord(c) & 1 for c in n20_body]
    mhi = bytes(pack_lsb(n20_bits[i:i + 8]) for i in (0, 8, 16)).decode("ascii")
    assert mhi == "MHI"

    # Upstream token 2: N10's fixed opening window under the established
    # LOW BIT -> LOW IF EVEN -> selected-note-head transform -> THE.
    selectors = tuple(lower_if_even(lowbit(w)) for w in notes[10][:3])
    assert selectors == (5, 15, 11)
    the = "".join(notes[s][0][0].upper() for s in selectors)
    assert the == "THE"

    def lineage(token: str):
        ids = [ord(c) - ord("A") + 1 for c in token]
        assert all(1 <= n <= 24 for n in ids)
        counts = [len(notes[n]) for n in ids]
        count_selector = pack_lsb([c & 1 for c in counts])
        head_letters = [notes[n][0][0] for n in ids]
        head_selector = pack_lsb(
            [((ord(c.upper()) - ord("A") + 1) & 1) for c in head_letters]
        )
        return ids, counts, count_selector, head_letters, head_selector

    mhi_path = lineage(mhi)
    the_path = lineage(the)

    assert mhi_path == ([13, 8, 9], [22, 13, 13], 6, ["a", "b", "n"], 1)
    assert the_path == ([20, 8, 5], [30, 13, 14], 2, ["i", "b", "t"], 1)

    assert lines[2].lower().startswith("first draft for the crew board:")
    assert lines[6].lower().startswith("second desk draft:")
    assert lines[1].lower().startswith("for the photograph of the empty bench:")

    # Matched denominator: the downstream parity pair alone is not claimed to
    # select these tokens. Enumerate all 24^3 A1Z26 note triples to make that
    # explicit; THE/MHI are privileged only by their independent emitters.
    pair_counts = Counter()
    for ids in product(range(1, 25), repeat=3):
        token = "".join(chr(ord("A") + n - 1) for n in ids)
        _, _, count_sel, _, head_sel = lineage(token)
        pair_counts[(count_sel, head_sel)] += 1

    assert pair_counts[(2, 1)] == 300
    assert pair_counts[(6, 1)] == 600

    print({
        "source_pin": "PASS",
        "target_or_nonce_read": False,
        "upstream_tokens": [the, mhi],
        "THE_note_ids": the_path[0],
        "THE_word_counts": the_path[1],
        "THE_count_selector": the_path[2],
        "THE_head_selector": the_path[4],
        "MHI_note_ids": mhi_path[0],
        "MHI_word_counts": mhi_path[1],
        "MHI_count_selector": mhi_path[2],
        "MHI_head_selector": mhi_path[4],
        "selected_versions": ["N02 first draft", "N06 second desk draft"],
        "shared_photo": "N01 photograph",
        "all_note_triples_THE_pair_count": pair_counts[(2, 1)],
        "all_note_triples_MHI_pair_count": pair_counts[(6, 1)],
        "complete_author_final_wording_emitted": False,
    })


if __name__ == "__main__":
    main()
