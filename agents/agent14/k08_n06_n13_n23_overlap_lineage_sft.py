#!/usr/bin/env python3
"""Source-only AT/MT/ET/PT -> N06 interlock with independently selected N13/N23."""

from hashlib import sha256
from pathlib import Path
import re
import sys

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
N06_N13_SPAN_SHA256 = "2ab57327d0317a1f28546095fb2cccbafc190fd90d4bbff5f19a64637d6a3e8f"
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

def maximal_common_spans(a, b):
    best_len = 0
    best = set()
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i+k] == b[j+k]:
                k += 1
            if k > best_len:
                best_len = k
                best = {tuple(a[i:i+k])} if k else set()
            elif k == best_len and k:
                best.add(tuple(a[i:i+k]))
    return best_len, best

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

    # Fixed address-chain continuation to N06.
    heads = "".join(a[0] for a in ADDRESSES)
    tails = "".join(a[1] for a in ADDRESSES)
    assert heads == "AMEP" and tails == "TTTT"
    assert lowbit(heads) == 7 and lowbit(tails) == 0
    head_ids = [ord(c) - 64 for c in heads]
    assert head_ids == [1, 13, 5, 16]
    counts = [len(notes[n]) for n in head_ids]
    assert counts == [11, 22, 14, 11]
    token = "".join(count_letter(n) for n in counts)
    assert token == "LWOL"
    reversed_token = token[::-1]
    assert reversed_token == "LOWL"
    selected = lowbit(reversed_token)
    assert selected == 6
    assert raw_lines[selected].lower().startswith("second desk draft:")

    # Specificity control: compare selected N06 with all possible note partners.\n    # N13 is independently selected by the existing N09 heading route; this scan\n    # measures the N06/N13 relation rather than authorizing partner choice.\n    partner_rows = []
    for n in range(1, 25):
        if n == selected:
            continue
        length, spans = maximal_common_spans(notes[selected], notes[n])
        partner_rows.append((length, n, spans))
    max_len = max(x[0] for x in partner_rows)
    winners = [x for x in partner_rows if x[0] == max_len]
    assert max_len == 3
    assert len(winners) == 1 and winners[0][1] == 13
    assert len(winners[0][2]) == 1
    span = next(iter(winners[0][2]))
    assert sha256(" ".join(span).encode()).hexdigest() == N06_N13_SPAN_SHA256

    # Corpus control over all 276 unordered note pairs.
    pair_hist = {}
    for i in range(1, 25):
        for j in range(i + 1, 25):
            length, _ = maximal_common_spans(notes[i], notes[j])
            pair_hist[length] = pair_hist.get(length, 0) + 1
    assert sum(pair_hist.values()) == 276
    assert pair_hist.get(5, 0) == 1
    assert pair_hist.get(4, 0) == 0
    assert pair_hist.get(3, 0) == 2

    # Existing LEN applied to the independently selected N06/N13 common span\n    # points to N03, a photograph; its count transition returns to N13.\n    photo_note = len(span)\n    assert photo_note == 3\n    assert raw_lines[photo_note].lower().startswith("kitchen photograph:")\n    assert len(notes[photo_note]) == 12\n    assert low_if_even(len(notes[photo_note])) == 13\n\n    # Existing count/LOW-IF-EVEN transition from independently selected N13 reaches N23.\n    n13_count = len(notes[13])\n    assert n13_count == 22\n    terminal = low_if_even(n13_count)\n    assert terminal == 23\n    assert "margin" in notes[terminal]
    assert "words" in notes[terminal]
    assert "finally" in notes[terminal]

    print({
        "source_pin": "PASS",
        "address_heads": heads,
        "address_heads_lowbit": 7,
        "count_token": token,
        "reversed_count_token": reversed_token,
        "whole_token_lowbit_selected_note": selected,
        "selected_role": "second desk draft",
        "selected_note_partner_denominator": 23,
        "unique_max_overlap_partner": 13,
        "unique_max_overlap_words": max_len,
        "overlap_fingerprint": "PASS",
        "all_note_pairs": 276,
        "pairs_with_len5": pair_hist.get(5, 0),
        "pairs_with_len3": pair_hist.get(3, 0),
        "overlap_len_selects_photo_note": photo_note,\n        "photo_note_word_count": len(notes[photo_note]),\n        "photo_count_low_if_even_returns": low_if_even(len(notes[photo_note])),\n        "n13_count": n13_count,\n        "low_if_even_n13_count": terminal,
        "terminal_role": "final-margin witness",
        "target_or_nonce_read": False,
    })

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: k08_n06_n13_n23_overlap_lineage_sft.py ROOT")
    main(sys.argv[1])
