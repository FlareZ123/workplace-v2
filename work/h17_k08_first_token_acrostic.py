#!/usr/bin/env python3
"""Reproduce the bounded K08 first-token selector check.

This is a note-order/locator analysis only. It does not derive a phrase,
inspect images, or access K08 key material or acceptance commitments.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

NOTE_RE = re.compile(
    r"(?m)^(N\d{2}) / ([^\n]+)\n(.*?)(?=\n\nN\d{2} / |\Z)", re.S
)
BASE_IDS = (2, 6, 10, 13, 17, 18, 20, 23)


def first_prose_token(body: str) -> str:
    # A leading label such as "Mug shelf:" or "Standby label:" precedes
    # the actual note prose. Strip only that first label delimiter.
    prose = body.split(":", 1)[1] if ":" in body else body
    match = re.match(r"\s*([A-Za-z0-9]+)", prose)
    if not match:
        raise ValueError("note has no first prose token")
    return match.group(1)


def load_notes(path: Path) -> dict[int, tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    notes: dict[int, tuple[str, str]] = {}
    for note_id, author, body in NOTE_RE.findall(text):
        notes[int(note_id[1:])] = (author.strip(), first_prose_token(body.strip()))
    return notes


def initials(ids: tuple[int, ...] | list[int], notes: dict[int, tuple[str, str]]) -> str:
    return "".join(notes[n][1][0].upper() for n in ids)


def analyze(notes: dict[int, tuple[str, str]]) -> dict[str, object]:
    missing = [n for n in BASE_IDS if n not in notes]
    if missing:
        raise ValueError(f"selected note IDs missing: {missing}")
    base = initials(BASE_IDS, notes)
    variants: list[dict[str, object]] = []
    for position, note_id in enumerate(BASE_IDS):
        for adjacent in (note_id - 1, note_id + 1):
            if adjacent not in notes:
                continue
            candidate = list(BASE_IDS)
            candidate[position] = adjacent
            variants.append({
                "replace": f"N{note_id:02d}->N{adjacent:02d}",
                "initials": initials(candidate, notes),
            })
    hits = [v for v in variants if v["initials"] == "ATEALBIT"]
    if len(hits) != 1 or hits[0]["replace"] != "N10->N11":
        raise AssertionError(f"expected one N10->N11 ATEALBIT selector, found {hits}")
    return {
        "base_note_ids": [f"N{n:02d}" for n in BASE_IDS],
        "base_initials": base,
        "adjacent_variant_count": len(variants),
        "atealbit_variant": hits[0],
        "variants": variants,
        "interpretation": "source locator only; not a recovered K08 phrase or image-source authentication",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", type=Path, default=Path("resources"))
    args = parser.parse_args()
    path = args.resources / "evidence" / "crew" / "noticeboard-and-desk-notes.txt"
    result = analyze(load_notes(path))
    print(f"base={result['base_initials']}")
    print(f"adjacent_variants={result['adjacent_variant_count']}")
    print(f"selector={result['atealbit_variant']['replace']}:{result['atealbit_variant']['initials']}")
    print(result["interpretation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
