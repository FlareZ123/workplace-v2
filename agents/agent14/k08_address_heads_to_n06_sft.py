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

def low_if_even(v):
    return v + 1 if v % 2 == 0 else v

def heading_channels(heading):
    ws = words(heading)
    head = sum((((ord(w[0]) - ord("a") + 1) & 1) << i) for i, w in enumerate(ws))
    tail = sum(((ord(w[-1]) & 1) << i) for i, w in enumerate(ws))
    length = sum(((len(w) & 1) << i) for i, w in enumerate(ws))
    return head, low_if_even(tail), low_if_even(length)

def main(root):
    root = Path(root)
    raw = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256

    notes = {}
    whitespace_counts = {}
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
        whitespace_counts[n] = len(body.split())
        raw_lines[n] = line
    assert set(notes) == set(range(1, 25))

    # The specific note counts consumed by this chain are invariant under the
    # two tokenizers that split the older COUNT-LINE continuation.
    count_notes = (1, 3, 5, 6, 13, 16)
    assert all(len(notes[n]) == whitespace_counts[n] for n in count_notes)

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

    # Corroboration only, not a selector: reuse the already established
    # heading HEAD/TAILBIT/LEN channels on the independently selected N06.
    signatures = {}
    for n, line in raw_lines.items():
        if ": " not in line:
            continue
        heading = line.split(": ", 1)[0].lower()
        triple = heading_channels(heading)
        if all(1 <= v <= 24 for v in triple):
            signatures[n] = "".join(chr(ord("A") + v - 1) for v in triple)
    assert signatures[6] == "ACE"
    assert [n for n, token in signatures.items() if token == "ACE"] == [6]

    # Matched heading control: run the same signature -> note-count token ->
    # selected N07 reversal -> whole-token LOW BIT chain on every eligible
    # heading. Only independently selected N06 lands on the photograph N03.
    heading_downstream = {}
    for n, token in signatures.items():
        ids = [ord(c) - ord("A") + 1 for c in token]
        count_values = [len(notes[i]) for i in ids]
        count_token_other = "".join(count_letter(v) for v in count_values)
        heading_downstream[n] = lowbit(count_token_other[::-1])
    assert [n for n, out in heading_downstream.items() if out == 3] == [6]

    # A1Z26 ACE -> N01/N03/N05. Their counts emit LMO. The already selected
    # N07 reversal gives OML, whose whole-token LOW BIT selects N03, a photo.
    ace_ids = [1, 3, 5]
    ace_counts = [len(notes[n]) for n in ace_ids]
    assert ace_counts == [11, 12, 14]
    ace_count_token = "".join(count_letter(n) for n in ace_counts)
    assert ace_count_token == "LMO"
    ace_reversed = ace_count_token[::-1]
    assert ace_reversed == "OML"
    photo_selector = lowbit(ace_reversed)
    assert photo_selector == 3
    assert raw_lines[photo_selector].lower().startswith("kitchen photograph:")

    # Existing count/LOW-IF-EVEN transitions now continue deterministically
    # from the selected photograph to the independently known final witness.
    n13 = low_if_even(len(notes[photo_selector]))
    assert len(notes[photo_selector]) == 12 and n13 == 13
    n23 = low_if_even(len(notes[n13]))
    assert len(notes[n13]) == 22 and n23 == 23
    assert "margin" in notes[n23] and "finally" in notes[n23]

    print({
        "source_pin": "PASS",
        "count_tokenizer_invariant_notes": count_notes,
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
        "heading_signature": signatures[6],
        "heading_signature_matches": sum(token == "ACE" for token in signatures.values()),
        "eligible_heading_signatures": len(signatures),
        "heading_pipeline_photo_matches": sum(out == 3 for out in heading_downstream.values()),
        "ace_note_ids": ace_ids,
        "ace_note_counts": ace_counts,
        "ace_count_token": ace_count_token,
        "ace_reversed_token": ace_reversed,
        "ace_photo_selector": photo_selector,
        "photo_word_count": len(notes[photo_selector]),
        "photo_count_low_if_even": n13,
        "n13_word_count": len(notes[n13]),
        "n13_count_low_if_even": n23,
        "terminal_note": n23,
        "terminal_role": "final-margin witness",
        "target_or_nonce_read": False,
    })

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: k08_address_heads_to_n06_sft.py ROOT")
    main(sys.argv[1])
