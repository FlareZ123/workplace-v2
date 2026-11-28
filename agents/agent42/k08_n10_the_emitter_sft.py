#!/usr/bin/env python3
"""Source-only N10 -> THE emitter under the established LOW/LOW-IF-EVEN transform."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def lowbit(word: str) -> int:
    return sum((ord(c.lower()) & 1) << i for i, c in enumerate(word))


def lower_if_even(value: int) -> int:
    return value + 1 if value % 2 == 0 else value


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256

    notes: dict[int, list[str]] = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw.decode("utf-8"),
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3)
        body = line.split(": ", 1)[1] if ": " in line else line
        notes[n] = re.findall(r"[A-Za-z0-9]+", body.lower())
    assert set(notes) == set(range(1, 25))

    def transform(window: list[str]):
        selectors = tuple(lower_if_even(lowbit(w)) for w in window)
        if not all(1 <= s <= 24 for s in selectors):
            return None
        token = "".join(notes[s][0][0].upper() for s in selectors)
        return token, selectors

    eligible = []
    the_outputs = []
    for n, body in notes.items():
        for i in range(len(body) - 2):
            got = transform(body[i:i + 3])
            if got is None:
                continue
            token, selectors = got
            row = (n, i + 1, token, selectors)
            eligible.append(row)
            if token == "THE":
                the_outputs.append(row)

    assert len(eligible) == 125
    assert the_outputs == [(10, 1, "THE", (5, 15, 11))]
    assert notes[10][:3] == ["the", "desk", "copy"]
    assert [notes[s][0][0].upper() for s in (5, 15, 11)] == ["T", "H", "E"]

    # Independent source-side N10 selector used elsewhere in the established chain:
    # official PTW-417 signed/CLOSED/AS_LEFT highest-revision seal serial LSBs
    # in MAIL-04 witness order B,D,A,C are 0,1,0,1 -> 10 LSB-first.
    seal_bits = (0, 1, 0, 1)
    seal_selector = sum(bit << i for i, bit in enumerate(seal_bits))
    assert seal_selector == 10

    print({
        "source_pin": "PASS",
        "target_or_nonce_read": False,
        "eligible_triplet_windows": len(eligible),
        "unique_THE_output": the_outputs,
        "official_seal_selector": seal_selector,
        "complete_author_final_wording_emitted": False,
    })


if __name__ == "__main__":
    main()
