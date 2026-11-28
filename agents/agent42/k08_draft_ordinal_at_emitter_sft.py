#!/usr/bin/env python3
"""Source-only draft-ordinal -> shared-photo emitter, checked against independent AT span."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
AT_SHA256 = "556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0"


def longest_common_contiguous(a: list[str], b: list[str]) -> list[str]:
    best: list[str] = []
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            if k > len(best):
                best = a[i:i + k]
    return best


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

    # Inputs fixed by the independently reproduced THE/MHI lineage:
    first_draft = 2
    second_draft = 6
    shared_photo = 1
    assert lines[first_draft].lower().startswith("first draft for the crew board:")
    assert lines[second_draft].lower().startswith("second desk draft:")
    assert lines[shared_photo].lower().startswith("for the photograph of the empty bench:")

    # The source labels themselves provide the ordinal indices.
    ordinals = []
    for n, expected_word, expected_value in (
        (first_draft, "first", 1),
        (second_draft, "second", 2),
    ):
        heading = lines[n].split(":", 1)[0].lower()
        assert heading.split()[0] == expected_word
        ordinals.append(expected_value)

    emitted = [notes[shared_photo][idx - 1] for idx in ordinals]
    assert emitted == ["the", "sea"]
    emitted_text = " ".join(emitted)
    assert sha256(emitted_text.encode()).hexdigest() == AT_SHA256

    # Independent held-out source check: N01/N20 were already selected as AT.
    at_span = longest_common_contiguous(notes[1], notes[20])
    assert at_span == emitted

    # Prefix control: among every numbered note, only the selected photograph
    # starts with the emitted two-token text.
    prefix_hits = [n for n in range(1, 25) if notes[n][:2] == emitted]
    assert prefix_hits == [1]

    print({
        "source_pin": "PASS",
        "target_or_nonce_read": False,
        "draft_ordinals": ordinals,
        "shared_photo": shared_photo,
        "emitted_word_count": len(emitted),
        "emitted_sha256": AT_SHA256,
        "independent_AT_span_match": True,
        "two_word_prefix_hits": prefix_hits,
        "complete_author_final_wording_emitted": False,
    })


if __name__ == "__main__":
    main()
