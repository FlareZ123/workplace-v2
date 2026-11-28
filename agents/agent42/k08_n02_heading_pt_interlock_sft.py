#!/usr/bin/env python3
"""Target-blind STOW14/LEN/N02 heading -> P, independently reproducing PT."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

PINS = {
    "crew": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "audit": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s.lower())


def pack(bits) -> int:
    return sum((b & 1) << i for i, b in enumerate(bits))


def lowbit(s: str) -> int:
    return pack(ord(c.lower()) & 1 for c in s)


def main() -> None:
    root = Path(__file__).resolve().parents[2] / "resources"
    crew = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    audit = (root / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert sha256(crew).hexdigest() == PINS["crew"]
    assert sha256(audit).hexdigest() == PINS["audit"]

    notes = {}
    labels = {}
    bodies = {}
    authors = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        crew.decode("utf-8"),
        re.M,
    ):
        n = int(m.group(1))
        authors[n] = m.group(2)
        line = m.group(3)
        if ": " in line:
            label, body = line.split(": ", 1)
        else:
            label, body = "", line
        labels[n] = label
        bodies[n] = body
        notes[n] = words(body)
    assert set(notes) == set(range(1, 25))

    # Reproduce STOW14 -> column14 LEN -> LOW BIT 2 -> N02.
    chosen = {"Simon", "Emily", "Gabriel"}
    bits = [1 if authors[n] in chosen else 0 for n in range(1, 25)]
    stow = "".join(chr(ord("A") + pack(bits[i:i + 5])) for i in (0, 5, 10, 15))
    suffix = pack(bits[20:24])
    assert (stow, suffix) == ("STOW", 14)
    ids = [ord(c) - ord("A") + 1 for c in stow]
    assert ids == [19, 20, 15, 23]
    len_token = "".join(bodies[n][suffix - 1] for n in ids).strip().upper()
    assert len_token == "LEN"
    first_draft = lowbit(len_token)
    assert first_draft == 2
    assert labels[first_draft] == "First draft for the crew board"

    # Apply the already established heading HEAD low-bit channel.
    heading_words = words(labels[first_draft])
    head_bits = [
        (ord(w[0].upper()) - ord("A") + 1) & 1
        for w in heading_words
    ]
    p_value = pack(head_bits)
    assert heading_words == ["first", "draft", "for", "the", "crew", "board"]
    assert head_bits == [0, 0, 0, 0, 1, 0]
    assert p_value == 16
    p = chr(ord("A") + p_value - 1)
    assert p == "P"

    # Matched heading control: N02 is the only colon heading with HEAD=16.
    head16 = []
    heading_count = 0
    for n in range(1, 25):
        if not labels[n]:
            continue
        heading_count += 1
        ws = words(labels[n])
        value = pack(
            (ord(w[0].upper()) - ord("A") + 1) & 1
            for w in ws
        )
        if value == 16:
            head16.append(n)
    assert heading_count == 19
    assert head16 == [2]

    # N20 is T in the fixed A1Z26 note namespace.
    t = chr(ord("A") + 20 - 1)
    assert t == "T"
    address = p + t
    assert address == "PT"

    # Independent transfer-side PT control.
    rows = [json.loads(x) for x in audit.decode().splitlines() if x.strip()]
    d = {
        (r["seq"], r["attempt"]): bytes.fromhex(r["checkpoint"])
        for r in rows
        if r.get("kind") == "CHUNK" and r["transfer"] == "AX-7782"
    }
    mixed = b"".join(d[(seq, 1 if seq % 2 == 0 else 2)] for seq in range(8))
    low = [b & 1 for b in mixed]
    packed = bytes(pack(low[o:o + 8]) for o in (0, 8))
    assert packed.hex().upper() == "50D4"
    assert all(b.bit_count() % 2 == 0 for b in packed)
    transfer_pt = "".join(chr(b & 0x7f) for b in packed)
    assert transfer_pt == address

    # PT's existing A1Z26 address points to the fixed prohibition boundary.
    assert [ord(c) - ord("A") + 1 for c in address] == [16, 20]
    a, b = notes[16], notes[20]
    overlaps = []
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            if k:
                overlaps.append((k, i, j, tuple(a[i:i + k])))
    best = max(k for k, *_ in overlaps)
    runs = [(i, j, run) for k, i, j, run in overlaps if k == best]
    assert best == 2 and runs == [(1, 19, ("do", "not"))]

    print({
        "source_pins": "PASS",
        "target_or_nonce_read": False,
        "stow": stow,
        "suffix": suffix,
        "column_token": len_token,
        "selected_first_draft": first_draft,
        "n02_heading_head_bits": head_bits,
        "n02_heading_HEAD": p_value,
        "heading_denominator": heading_count,
        "HEAD16_matches": head16,
        "note20_coordinate": t,
        "draft_address": address,
        "transfer_address": transfer_pt,
        "addresses_agree": address == transfer_pt,
        "PT_overlap_length": best,
        "PT_n20_zero_based_start": runs[0][1],
        "complete_author_final_wording_emitted": False,
    })


if __name__ == "__main__":
    main()
