#!/usr/bin/env python3
"""Two complete shared-AT merges of source-selected N01 and fixed P20."""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
AT_SHA256 = "556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0"
P20_SHA256 = "4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s.lower())


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

    notes = {}
    labels = {}
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
        notes[n] = words(body)

    n01 = notes[1]
    p20 = notes[20][6:19]
    n02 = notes[2]
    assert len(n01) == 11 and len(p20) == 13
    assert hashlib.sha256(" ".join(p20).encode()).hexdigest() == P20_SHA256

    # The independently fixed AT span is exactly the shared two-token prefix.
    shared = n01[:2]
    assert p20[:2] == shared
    assert hashlib.sha256(" ".join(shared).encode()).hexdigest() == AT_SHA256

    # Frozen complete editor: expand the common AT prefix to both selected
    # source sequences. Prefix-prefix overlap leaves exactly two whole-sequence
    # orders and no lexical/per-position choices.
    candidates = [
        n01 + p20[2:],
        p20 + n01[2:],
    ]
    assert all(len(c) == 22 for c in candidates)
    assert candidates[0] != candidates[1]

    route = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "resources/acceptance.json").read_text())
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    component, _ = reduce_phrase(" ".join(n02), key)
    assert component.hex().upper() == N02_HMAC16

    hits = [reduce_phrase(" ".join(c), key)[1] == target for c in candidates]
    assert hits == [False, False]

    planted = reduce_phrase(" ".join(candidates[0]), key)[1]
    planted_hits = sum(
        reduce_phrase(" ".join(c), key)[1] == planted
        for c in candidates
    )
    assert planted_hits == 1

    print({
        "source_pin": "PASS",
        "n01_width": len(n01),
        "p20_width": len(p20),
        "shared_AT_width": len(shared),
        "complete_assignments": len(candidates),
        "free_lexical_choices": 0,
        "original_hits": sum(hits),
        "n02_historical_control": "PASS",
        "planted_complete_output_hits": planted_hits,
        "candidate_wording_printed": False,
    })


if __name__ == "__main__":
    main()
