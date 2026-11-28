#!/usr/bin/env python3
"""Fixed MHI-continuation editor over the equal-width P20/N02 rows."""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
P20_SHA256 = "4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c"


def pack(bits):
    return sum((b & 1) << i for i, b in enumerate(bits))


def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def slot(phrase: str, key: bytes):
    component = hmac.new(key, normalize(phrase).encode(), hashlib.sha256).digest()[:16]
    return component, hashlib.sha256(component).hexdigest().lower()


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CREW_SHA256

    notes = {}
    raw_lines = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw.decode("utf-8"),
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3)
        body = line.split(": ", 1)[1] if ": " in line else line
        notes[n] = re.findall(r"[A-Za-z0-9]+", body.lower())
        raw_lines[n] = body
    assert set(notes) == set(range(1, 25))

    p20 = notes[20][6:19]
    n02 = notes[2]
    assert len(p20) == len(n02) == 13
    assert hashlib.sha256(" ".join(p20).encode()).hexdigest() == P20_SHA256

    # First 24 raw N20 body LOW BIT values are the already fixed MHI emitter.
    all_bits = [ord(c) & 1 for c in raw_lines[20]]
    head = bytes(pack(all_bits[i:i + 8]) for i in (0, 8, 16))
    assert head == b"MHI"

    # No window search: consume the next 13 bits immediately.
    mask = all_bits[24:37]
    assert mask == [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0]

    route = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "resources/acceptance.json").read_text())
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    # Historical reducer fixture.
    component, _ = slot(" ".join(n02), key)
    assert component.hex().upper() == N02_HMAC16

    candidates = []
    for polarity in (0, 1):
        tokens = [
            (n02 if (bit ^ polarity) else p20)[i]
            for i, bit in enumerate(mask)
        ]
        candidates.append(" ".join(tokens))

    hits = [slot(c, key)[1] == target for c in candidates]
    assert hits == [False, False]

    planted = slot(candidates[0], key)[1]
    planted_hits = sum(slot(c, key)[1] == planted for c in candidates)
    assert planted_hits == 1

    print({
        "source_pin": "PASS",
        "mhi_head": head.decode(),
        "row_width": 13,
        "selector_bits": len(mask),
        "free_choices": "bit-to-row polarity only",
        "assignments": 2,
        "original_hits": sum(hits),
        "n02_historical_control": "PASS",
        "planted_complete_output_hits": planted_hits,
        "candidate_wording_printed": False,
    })


if __name__ == "__main__":
    main()
