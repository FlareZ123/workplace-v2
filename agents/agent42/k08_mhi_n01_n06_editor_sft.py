#!/usr/bin/env python3
"""Target-blind MHI -> N06/N01 carrier convergence and two-polarity full editor."""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import re
import sys

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s.lower())


def pack_lsb(bits: list[int]) -> int:
    return sum((b & 1) << i for i, b in enumerate(bits))


def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def k08_component(phrase: str, key: bytes) -> bytes:
    return hmac.new(key, normalize(phrase).encode("utf-8"), hashlib.sha256).digest()[:16]


def slot_hash(component: bytes) -> str:
    return hashlib.sha256(component).hexdigest().lower()


def body_lsb_bytes(body: str) -> bytes:
    bits = [ord(c) & 1 for c in body]
    return bytes(pack_lsb(bits[i:i + 8]) for i in range(0, len(bits) - 7, 8))


def main(root_arg: str) -> None:
    root = Path(root_arg)
    crew_path = root / "evidence/crew/noticeboard-and-desk-notes.txt"
    raw = crew_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CREW_SHA256

    notes: dict[int, str] = {}
    lines: dict[int, str] = {}
    for m in re.finditer(
        rb"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw,
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3).decode("utf-8")
        body = line.split(": ", 1)[1] if ": " in line else line
        notes[n] = body
        lines[n] = line
    assert set(notes) == set(range(1, 25))

    # Reproduce the already-established MHI selector from N20 exactly.
    packed = body_lsb_bytes(notes[20])
    assert packed[:3] == b"MHI"
    uppercase_heads = []
    for n in range(1, 25):
        p = body_lsb_bytes(notes[n])
        if len(p) >= 3 and all(ord("A") <= b <= ord("Z") for b in p[:3]):
            uppercase_heads.append((n, p[:3]))
    assert uppercase_heads == [(20, b"MHI")]

    selected = [ord(c) - ord("A") + 1 for c in "MHI"]
    assert selected == [13, 8, 9]

    # New convergence 1: fixed selected-note word-count LOW BIT -> N06.
    counts = [len(words(notes[n])) for n in selected]
    assert counts == [22, 13, 13]
    count_bits = [n & 1 for n in counts]
    count_selector = pack_lsb(count_bits)
    assert count_bits == [0, 1, 1] and count_selector == 6
    assert lines[count_selector].lower().startswith("second desk draft:")

    # New convergence 2: fixed selected-note first-word HEAD low bits -> N01.
    head_letters = [words(notes[n])[0][0] for n in selected]
    head_bits = [((ord(c.upper()) - ord("A") + 1) & 1) for c in head_letters]
    head_selector = pack_lsb(head_bits)
    assert head_letters == ["a", "b", "n"]
    assert head_bits == [1, 0, 0] and head_selector == 1
    assert lines[head_selector].lower().startswith("for the photograph of the empty bench:")

    # Independent local reselection: N06's source label is "Second desk draft".
    heading6 = lines[6].split(":", 1)[0]
    heading_words = words(heading6)
    heading_bits = [((ord(w[0].upper()) - ord("A") + 1) & 1) for w in heading_words]
    heading_selector = pack_lsb(heading_bits)
    assert heading_words == ["second", "desk", "draft"]
    assert heading_bits == [1, 0, 0] and heading_selector == 1

    # The two selected provenance carriers have the same 11-token width.
    photo = words(notes[1])
    desk = words(notes[6])
    assert len(photo) == len(desk) == 11

    # Deterministic terminal-editor falsifier: continue the exact N20 raw LOW BIT
    # stream immediately after the 24 MHI bits. The next 11 source bits decide
    # aligned N01/N06 token origin. Only bit-to-row polarity remains ambiguous,
    # so test both polarities and no other row/word/edit choices.
    all_bits = [ord(c) & 1 for c in notes[20]]
    mask = all_bits[24:35]
    assert len(mask) == 11

    routing = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    key = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    # Historical reducer fixture, independent of the new editor.
    n02 = notes[2]
    assert k08_component(n02, key).hex().upper() == N02_HMAC16

    candidates = []
    for polarity in (0, 1):
        tokens = []
        for i, bit in enumerate(mask):
            use_desk = bit ^ polarity
            tokens.append((desk if use_desk else photo)[i])
        phrase = " ".join(tokens)
        candidates.append(phrase)

    assert candidates[0] != candidates[1]
    hits = [slot_hash(k08_component(c, key)) == target for c in candidates]
    assert hits == [False, False]

    # Planted complete-output positive proves the fixed two-branch enumeration.
    planted_target = slot_hash(k08_component(candidates[0], key))
    planted_hits = sum(slot_hash(k08_component(c, key)) == planted_target for c in candidates)
    assert planted_hits == 1

    print(json.dumps({
        "source_pin": "PASS",
        "mhi_unique_uppercase_head": True,
        "mhi_note_ids": selected,
        "mhi_word_counts": counts,
        "count_low_bits": count_bits,
        "count_selector": count_selector,
        "head_low_bits": head_bits,
        "head_selector": head_selector,
        "n06_heading_low_bits": heading_bits,
        "n06_heading_reselects": heading_selector,
        "selected_carrier_width": len(photo),
        "editor_free_choices": "bit-to-row polarity only",
        "editor_assignments": 2,
        "original_hits": sum(hits),
        "historical_n02_control": "PASS",
        "planted_complete_output_hits": planted_hits,
        "candidate_wording_printed": False,
    }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: k08_mhi_n01_n06_editor_sft.py ROOT")
    main(sys.argv[1])
