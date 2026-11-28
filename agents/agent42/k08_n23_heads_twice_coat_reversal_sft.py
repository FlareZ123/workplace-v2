#!/usr/bin/env python3
"""N23 landmark gaps -> HEAD twice -> N01; COAT -> N07 reversal complete editor."""
from __future__ import annotations

import hashlib
import hmac
import itertools
import json
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s.lower())


def pack(bits) -> int:
    return sum((b & 1) << i for i, b in enumerate(bits))


def head_low(ws: list[str]) -> int:
    return pack((ord(w[0].upper()) - ord("A") + 1) & 1 for w in ws)


def lowbit(s: str) -> int:
    return pack(ord(c.lower()) & 1 for c in s)


def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def reduce_phrase(s: str, key: bytes) -> tuple[bytes, str]:
    component = hmac.new(key, normalize(s).encode(), hashlib.sha256).digest()[:16]
    return component, hashlib.sha256(component).hexdigest().lower()


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CREW_SHA256

    labels = {}
    bodies = {}
    raw_bodies = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw.decode(),
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3)
        if ": " in line:
            label, body = line.split(": ", 1)
        else:
            label, body = "", line
        labels[n] = label
        raw_bodies[n] = body
        bodies[n] = words(body)

    # Reproduce the N23 landmark-gap selector.
    landmarks = ["wording", "margin", "envelope", "words", "it"]
    n23 = bodies[23]
    positions = [n23.index(x) + 1 for x in landmarks]
    assert positions == [2, 5, 12, 16, 21]
    selected = [positions[i + 1] - positions[i] - 1 for i in range(4)]
    assert selected == [2, 6, 3, 4]

    # N04 says "Count the heads twice". Reproduce the two HEAD passes.
    heading_heads = [words(labels[n])[0] for n in selected]
    assert heading_heads == ["first", "second", "kitchen", "under"]
    first = head_low(heading_heads)
    assert first == 14 and labels[first] == "Sunrise photograph"
    second = head_low(words(labels[first]))
    assert second == 1 and labels[second] == "For the photograph of the empty bench"

    # Continue N04 literally: its terminal noun COAT has LOW BIT 7, selecting
    # the already-calibrated N07 "Put it back" reversal operation.
    assert bodies[4][-1] == "coat"
    reversal_note = lowbit("coat")
    assert reversal_note == 7
    assert bodies[7][:3] == ["put", "it", "back"]

    # Apply the reversal to the complete selected N01 caption. The operator's
    # short-token calibrations reverse character/token sequences; at phrase
    # width the only two natural granularities are whole-word order and the
    # entire normalized character stream. Test both, no other edit choices.
    n01 = bodies[1]
    normalized_n01 = " ".join(n01)
    candidates = [
        " ".join(reversed(n01)),
        normalized_n01[::-1],
    ]
    assert candidates[0] != candidates[1]

    route = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "resources/acceptance.json").read_text())
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    component, _ = reduce_phrase(" ".join(bodies[2]), key)
    assert component.hex().upper() == N02_HMAC16

    hits = [reduce_phrase(c, key)[1] == target for c in candidates]
    assert hits == [False, False]

    planted = reduce_phrase(candidates[0], key)[1]
    planted_hits = sum(reduce_phrase(c, key)[1] == planted for c in candidates)
    assert planted_hits == 1

    print({
        "source_pin": "PASS",
        "landmark_between_notes": selected,
        "HEAD_pass1": first,
        "HEAD_pass2": second,
        "selected_complete_source": "N01",
        "coat_LOWBIT": reversal_note,
        "reversal_instruction": "N07 first three post-label words",
        "complete_reversal_granularities": 2,
        "original_hits": sum(hits),
        "historical_n02_control": "PASS",
        "planted_complete_output_hits": planted_hits,
        "candidate_wording_printed": False,
    })


if __name__ == "__main__":
    main()
