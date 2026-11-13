#!/usr/bin/env python3
"""Bounded K08 source-span join: N01 sea + N13 end-of-night + N09 social.

The operation is frozen to exact contiguous source spans, N20's semantic order,
and its comma/and list structure. No paraphrase, synonym, reordering, or
candidate text is inferred from the commitment.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def note_body(notes: str, number: int) -> str:
    match = re.search(rf"^N{number:02d} /[^\n]*\n([^\n]+)", notes, re.MULTILINE)
    if not match:
        raise ValueError(f"N{number:02d} not found")
    body = match.group(1).strip()
    prefixes = {
        1: "For the photograph of the empty bench: ",
        9: "Caption for the galley board: ",
    }
    prefix = prefixes.get(number)
    if prefix:
        if not body.startswith(prefix):
            raise ValueError(f"N{number:02d} source label changed: {body!r}")
        body = body[len(prefix):]
    return body


def contiguous_spans(words: list[str], predicate) -> list[str]:
    found = []
    for start in range(len(words)):
        for end in range(start + 1, len(words) + 1):
            part = words[start:end]
            if predicate([word.lower() for word in part]):
                found.append(" ".join(part))
    return found


def normalize(phrase: str) -> str:
    phrase = phrase.lower()
    phrase = re.sub(r"[^a-z0-9\s]", " ", phrase)
    return " ".join(phrase.split())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    data_root = args.data_root
    if data_root is None:
        data_root = repo_root / "resources"
        if not (data_root / "evidence").is_dir():
            data_root = repo_root

    notes_path = data_root / "evidence/crew/noticeboard-and-desk-notes.txt"
    route_path = data_root / "evidence/recovery-routing.json"
    acceptance_path = data_root / "acceptance.json"
    notes_bytes = notes_path.read_bytes()
    route_bytes = route_path.read_bytes()
    acceptance_bytes = acceptance_path.read_bytes()

    notes = notes_bytes.decode("utf-8")
    route = json.loads(route_bytes)
    acceptance = json.loads(acceptance_bytes)

    n01 = tokens(note_body(notes, 1))
    n13 = tokens(note_body(notes, 13))
    n09 = tokens(note_body(notes, 9))

    sea_spans = contiguous_spans(n01, lambda w: "sea" in w)
    night_spans = contiguous_spans(
        n13,
        lambda w: any(w[i:i + 4] == ["end", "of", "the", "night"]
                      for i in range(len(w) - 3)),
    )
    social_spans = contiguous_spans(
        n09,
        lambda w: ("cup" in w and "alone" in w)
        or ("alone" in w and "bad" in w and "night" in w),
    )

    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    checked = 0
    hits = []
    for sea in sea_spans:
        for night in night_spans:
            for social in social_spans:
                # N20: sea, end-of-night, and social/table motif.
                # Punctuation is removed by the prescribed normalization.
                phrase = f"{sea}, {night} and {social}"
                normalized = normalize(phrase)
                mac16 = hmac.new(key, normalized.encode("utf-8"),
                                 hashlib.sha256).digest()[:16]
                commitment = hashlib.sha256(mac16).hexdigest()
                checked += 1
                if commitment == target:
                    hits.append({
                        "phrase": phrase,
                        "normalized": normalized,
                        "mac16": mac16.hex(),
                    })

    print(json.dumps({
        "method": "N01 sea-span + N13 end-of-night-span + N09 social-span",
        "join": "N20 comma/and order; exact source spans only",
        "normalization": route["K08"]["rule"],
        "span_counts": {
            "N01_sea": len(sea_spans),
            "N13_end_of_night": len(night_spans),
            "N09_social": len(social_spans),
        },
        "candidate_count": checked,
        "hits": hits,
        "input_sha256": {
            "notes": hashlib.sha256(notes_bytes).hexdigest(),
            "routing": hashlib.sha256(route_bytes).hexdigest(),
            "acceptance": hashlib.sha256(acceptance_bytes).hexdigest(),
        },
        "target_sha256": target,
    }, indent=2))


if __name__ == "__main__":
    main()
