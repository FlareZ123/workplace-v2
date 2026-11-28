#!/usr/bin/env python3
"""Target-blind First draft -> Second draft -> final-margin carrier program."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s.lower())


def pack(bits) -> int:
    return sum((b & 1) << i for i, b in enumerate(bits))


def lowbit(s: str) -> int:
    return pack(ord(c.lower()) & 1 for c in s)


def low_if_even(v: int) -> int:
    return v + 1 if v % 2 == 0 else v


def count_letter(v: int) -> str:
    assert 0 <= v < 26
    return chr(ord("A") + v)


def heading_channels(label: str) -> tuple[int, int, int]:
    ws = words(label)
    head = pack((ord(w[0].upper()) - ord("A") + 1) & 1 for w in ws)
    tail = pack(ord(w[-1]) & 1 for w in ws)
    length = pack(len(w) & 1 for w in ws)
    return head, low_if_even(tail), low_if_even(length)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256

    notes = {}
    labels = {}
    bodies = {}
    authors = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw.decode("utf-8"),
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

    # Stage 1: source-selected STOW14 -> LEN -> N02 First draft.
    chosen = {"Simon", "Emily", "Gabriel"}
    author_bits = [1 if authors[n] in chosen else 0 for n in range(1, 25)]
    stow = "".join(chr(ord("A") + pack(author_bits[i:i + 5])) for i in (0, 5, 10, 15))
    suffix = pack(author_bits[20:24])
    assert (stow, suffix) == ("STOW", 14)
    stow_ids = [ord(c) - ord("A") + 1 for c in stow]
    assert stow_ids == [19, 20, 15, 23]
    len_token = "".join(bodies[n][suffix - 1] for n in stow_ids).strip().upper()
    assert len_token == "LEN"
    first = lowbit(len_token)
    assert first == 2
    assert labels[first].lower().startswith("first draft")

    # Stage 2a: N20 raw LOW BIT emits MHI. MHI itself generates AME.
    n20_bits = [ord(c) & 1 for c in bodies[20]]
    mhi = bytes(pack(n20_bits[i:i + 8]) for i in (0, 8, 16)).decode("ascii")
    assert mhi == "MHI"
    mhi_ids = [ord(c) - ord("A") + 1 for c in mhi]
    assert mhi_ids == [13, 8, 9]
    mhi_head_bits = [
        (ord(notes[n][0][0].upper()) - ord("A") + 1) & 1
        for n in mhi_ids
    ]
    a = chr(ord("A") + pack(mhi_head_bits) - 1)
    m = mhi[0]
    e = chr(ord("A") + lowbit(mhi) - 1)
    assert (a, m, e) == ("A", "M", "E")

    # Stage 2b: the independently selected First-draft heading emits P.
    first_head, _, _ = heading_channels(labels[first])
    assert first_head == 16
    p = chr(ord("A") + first_head - 1)
    assert p == "P"
    amep = a + m + e + p
    assert amep == "AMEP"

    # Stage 2c: the pre-existing AMEP/N07 count+reverse program predicts N06.
    reversal_note = lowbit(amep)
    assert reversal_note == 7
    amep_ids = [ord(c) - ord("A") + 1 for c in amep]
    assert amep_ids == [1, 13, 5, 16]
    amep_counts = [len(notes[n]) for n in amep_ids]
    assert amep_counts == [11, 22, 14, 11]
    count_token = "".join(count_letter(v) for v in amep_counts)
    assert count_token == "LWOL"
    reversed_token = count_token[::-1]
    assert reversed_token == "LOWL"
    second = lowbit(reversed_token)
    assert second == 6
    assert labels[second].lower().startswith("second desk draft")

    # Stage 3: the selected Second-draft heading emits ACE under the frozen
    # HEAD/TAILBIT/LEN channels; its count/reversal path reaches a photograph.
    second_channels = heading_channels(labels[second])
    assert second_channels == (1, 3, 5)
    ace = "".join(chr(ord("A") + v - 1) for v in second_channels)
    assert ace == "ACE"
    ace_ids = [ord(c) - ord("A") + 1 for c in ace]
    ace_counts = [len(notes[n]) for n in ace_ids]
    assert (ace_ids, ace_counts) == ([1, 3, 5], [11, 12, 14])
    ace_count_token = "".join(count_letter(v) for v in ace_counts)
    assert ace_count_token == "LMO"
    photo = lowbit(ace_count_token[::-1])
    assert photo == 3
    assert labels[photo].lower().startswith("kitchen photograph")

    # Stage 4: existing COUNT/LOW-IF-EVEN transitions reach N13 then N23.
    n13 = low_if_even(len(notes[photo]))
    final_carrier = low_if_even(len(notes[n13]))
    assert (len(notes[photo]), n13, len(notes[n13]), final_carrier) == (12, 13, 22, 23)
    assert "margin" in notes[final_carrier]
    assert "finally" in notes[final_carrier]

    # Matched heading controls for the two version transitions.
    head16 = []
    ace_matches = []
    eligible = 0
    for n in range(1, 25):
        if not labels[n]:
            continue
        channels = heading_channels(labels[n])
        if channels[0] == 16:
            head16.append(n)
        if all(1 <= x <= 24 for x in channels):
            eligible += 1
            token = "".join(chr(ord("A") + x - 1) for x in channels)
            if token == "ACE":
                ace_matches.append(n)
    assert head16 == [2]
    assert ace_matches == [6]

    print({
        "source_pin": "PASS",
        "target_or_nonce_read": False,
        "stage1": "STOW14 -> LEN -> N02 First draft",
        "mhi": mhi,
        "generated_address_heads": amep,
        "first_heading_HEAD": first_head,
        "stage2": "AMEP -> N07 -> LWOL -> LOWL -> N06 Second desk draft",
        "second_heading_channels": second_channels,
        "stage3": "ACE -> LMO -> OML -> N03 Kitchen photograph",
        "stage4": "N03(12) -> N13(22) -> N23 final-margin witness",
        "HEAD16_heading_matches": head16,
        "eligible_heading_triples": eligible,
        "ACE_heading_matches": ace_matches,
        "complete_author_final_wording_emitted": False,
    })


if __name__ == "__main__":
    main()
