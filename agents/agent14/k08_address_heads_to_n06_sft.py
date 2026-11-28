#!/usr/bin/env python3
"""Target-blind AT/MT/ET/PT address-head selector to Emily N06."""

from hashlib import sha256
from pathlib import Path
import re
import sys

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ADDRESSES = ("AT", "MT", "ET", "PT")

def words(s):
    return re.findall(r"[A-Za-z0-9]+", s.lower())

def lowbit(s):
    return sum((ord(c.lower()) & 1) << i for i, c in enumerate(s))

def count_letter(n):
    assert 0 <= n < 26
    return chr(ord("A") + n)

def main(root):
    root = Path(root)
    raw = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256

    notes = {}
    raw_lines = {}
    for m in re.finditer(
        rb"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw,
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3).decode()
        body = line.split(": ", 1)[1] if ": " in line else line
        notes[n] = words(body)
        raw_lines[n] = line
    assert set(notes) == set(range(1, 25))

    heads = "".join(a[0] for a in ADDRESSES)
    tails = "".join(a[1] for a in ADDRESSES)
    assert heads == "AMEP"
    assert tails == "TTTT"

    # The changing address coordinate selects the calibrated reversal note.
    assert lowbit(heads) == 7
    assert lowbit(tails) == 0
    assert 7 in notes and 0 not in notes

    # Address heads -> note counts -> A=0 count token.
    head_note_ids = [ord(c) - 64 for c in heads]
    assert head_note_ids == [1, 13, 5, 16]
    counts = [len(notes[n]) for n in head_note_ids]
    assert counts == [11, 22, 14, 11]
    count_token = "".join(count_letter(n) for n in counts)
    assert count_token == "LWOL"

    # N07's independently calibrated operation reverses LWOL.
    reversed_token = count_token[::-1]
    assert reversed_token == "LOWL"

    # Apply the already-established whole-token LOW BIT reduction, as in
    # the prior VLOWL -> N12 route-field construction.
    selector = lowbit(reversed_token)
    assert selector == 6
    assert raw_lines[selector].lower().startswith("second desk draft:")
    assert len(notes[selector]) == 11

    print({
        "source_pin": "PASS",
        "addresses": ADDRESSES,
        "heads": heads,
        "tails": tails,
        "heads_lowbit": 7,
        "tails_lowbit": 0,
        "selected_reversal_note": 7,
        "head_note_ids": head_note_ids,
        "head_note_counts": counts,
        "count_token": count_token,
        "reversed_count_token": reversed_token,
        "whole_token_lowbit": selector,
        "selected_note": selector,
        "selected_role": "second desk draft",
        "selected_note_word_count": len(notes[selector]),
        "target_or_nonce_read": False,
    })

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: k08_address_heads_to_n06_sft.py ROOT")
    main(sys.argv[1])
