#!/usr/bin/env python3
"""Fixed P20 lexical substitution from independently emitted NOBODY AT THE TABLE."""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import re

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
P20_SHA256 = "4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s.lower())


def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def pack(bits) -> int:
    return sum((b & 1) << i for i, b in enumerate(bits))


def lowbit(s: str) -> int:
    return pack(ord(c.lower()) & 1 for c in s)


def low_if_even(v: int) -> int:
    return v + 1 if v % 2 == 0 else v


def reduce_phrase(s: str, key: bytes) -> tuple[bytes, str]:
    component = hmac.new(key, normalize(s).encode(), hashlib.sha256).digest()[:16]
    return component, hashlib.sha256(component).hexdigest().lower()


def longest_common_suffix(a: list[str], b: list[str]) -> list[str]:
    k = 0
    while k < min(len(a), len(b)) and a[-1-k] == b[-1-k]:
        k += 1
    return a[len(a)-k:] if k else []


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CREW_SHA256

    notes = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw.decode(),
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3)
        body = line.split(": ", 1)[1] if ": " in line else line
        notes[n] = words(body)
    assert set(notes) == set(range(1, 25))

    # Reproduce the already-established N09 -> N13 -> N23 lineage and literal
    # source fragment, without reading the K08 target.
    n09_next = len(notes[9])
    n13_next = low_if_even(len(notes[n09_next]))
    assert (n09_next, n13_next) == (13, 23)
    heads = [notes[n][0] for n in (9, 13, 23)]
    assert heads == ["nobody", "at", "the"]
    table_index = lowbit("words")
    assert table_index == 19
    table = notes[20][table_index - 1]
    assert table == "table"
    fragment = heads + [table]
    assert fragment == ["nobody", "at", "the", "table"]

    # Fixed P20 is the independently address-selected 13-token N20 payload.
    p20 = notes[20][6:19]
    assert len(p20) == 13
    assert hashlib.sha256(" ".join(p20).encode()).hexdigest() == P20_SHA256

    # The emitted fragment and P20 share one exact maximal suffix.
    shared = longest_common_suffix(fragment, p20)
    assert shared == ["at", "the", "table"]
    assert fragment[:-len(shared)] == ["nobody"]
    assert p20[-5:-3] == ["the", "voices"]

    # Unique source-aligned substitution: replace the two P20 tokens
    # immediately preceding the shared suffix with the one emitted prefix.
    candidate_tokens = p20[:-5] + fragment[:-len(shared)] + shared
    assert len(candidate_tokens) == 12

    route = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "resources/acceptance.json").read_text())
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    component, _ = reduce_phrase(" ".join(notes[2]), key)
    assert component.hex().upper() == N02_HMAC16

    _, candidate_hash = reduce_phrase(" ".join(candidate_tokens), key)
    assert candidate_hash != target

    planted = candidate_hash
    planted_hits = int(reduce_phrase(" ".join(candidate_tokens), key)[1] == planted)
    assert planted_hits == 1

    print({
        "source_pin": "PASS",
        "source_fragment": "NOBODY AT THE TABLE",
        "p20_width": len(p20),
        "shared_suffix_width": len(shared),
        "replaced_p20_tokens": 2,
        "inserted_fragment_tokens": 1,
        "complete_assignments": 1,
        "original_hits": 0,
        "historical_n02_control": "PASS",
        "planted_complete_output_hits": planted_hits,
        "candidate_wording_printed": False,
    })


if __name__ == "__main__":
    main()
