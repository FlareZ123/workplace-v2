#!/usr/bin/env python3
"""Target-blind AT/MT/ET/PT address-head lineage to N23."""

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

def low_if_even(v):
    return v + 1 if v % 2 == 0 else v

def count_letter(n):
    assert 0 <= n < 26
    return chr(ord("A") + n)

def main(root):
    root = Path(root)
    raw = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256

    notes = {}
    for m in re.finditer(
        rb"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw,
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3).decode()
        body = line.split(": ", 1)[1] if ": " in line else line
        notes[n] = words(body)
    assert set(notes) == set(range(1, 25))

    heads = "".join(a[0] for a in ADDRESSES)
    tails = "".join(a[1] for a in ADDRESSES)
    assert heads == "AMEP"
    assert tails == "TTTT"

    # The information-bearing coordinate selects the known reversal note.
    assert lowbit(heads) == 7
    assert lowbit(tails) == 0
    assert 7 in notes and 0 not in notes

    # A1Z26-address the four varying heads and read their note-body counts.
    head_note_ids = [ord(c) - 64 for c in heads]
    assert head_note_ids == [1, 13, 5, 16]
    counts = [len(notes[n]) for n in head_note_ids]
    assert counts == [11, 22, 14, 11]
    count_token = "".join(count_letter(n) for n in counts)
    assert count_token == "LWOL"

    # N07's already-calibrated operation reverses the emitted count token.
    reversed_token = count_token[::-1]
    assert reversed_token == "LOWL"
    assert reversed_token.startswith("LOW")
    residual = reversed_token[3:]
    assert residual == "L"

    # Reuse the established LOW IF EVEN rule on the residual A1Z26 symbol.
    residual_value = ord(residual) - 64
    n13 = low_if_even(residual_value)
    assert residual_value == 12 and n13 == 13

    # The same fixed count/LOW-IF-EVEN transition reaches the final-margin note.
    n13_count = len(notes[n13])
    n23 = low_if_even(n13_count)
    assert n13_count == 22 and n23 == 23
    assert "margin" in notes[n23]
    assert "words" in notes[n23]
    assert "finally" in notes[n23]

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
        "operator_prefix": "LOW",
        "residual": residual,
        "low_if_even_residual": n13,
        "n13_count": n13_count,
        "low_if_even_n13_count": n23,
        "final_carrier_note": n23,
        "target_or_nonce_read": False,
    })

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: k08_address_heads_to_n23_sft.py ROOT")
    main(sys.argv[1])
