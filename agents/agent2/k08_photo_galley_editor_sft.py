"""H-17 K08 three-voice collage SFT. Read-only, source-pinned.

Hypothetical photo + galley + Emily editing mechanism, not attested final words.
Usage: python k08_photo_galley_editor_sft.py PATH_TO_ORIGINAL_RESOURCES
"""
from __future__ import annotations

import hashlib
import hmac
import itertools
import json
import re
import sys
import time
from pathlib import Path

SOURCE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ANCHORS = {
    "N01": ("sea", "tea", "finished"),
    "N08": ("water", "daylight", "overnight"),
    "N09": ("cup", "alone", "night"),
    "N11": ("mug", "chipped", "blue"),
    "N19": ("mugs", "bed", "down"),
    "N02": ("watch", "room", "hands"),
    "N06": ("lamp", "quiet"),
    "N13": ("night", "mugs", "window", "lamp"),
    "N20": ("sea", "night", "voices", "table"),
}
GROUPS = {
    "P": ("N01", "N08"),
    "G": ("N09", "N11", "N19"),
    "E": ("N02", "N06", "N13", "N20"),
}
COUNTS = {
    "N01": 34, "N08": 35, "N09": 39, "N11": 27, "N19": 73,
    "N02": 46, "N06": 27, "N13": 85, "N20": 104,
}
JOINERS = (b" ", b" and ")


def fragments(notes: str, note_id: str, anchors: tuple[str, ...]) -> list[bytes]:
    match = re.search(r"^" + note_id + r" / [^\n]+\n([^\n]+)", notes, re.M)
    assert match is not None, note_id
    body = match.group(1)
    if ": " in body:
        body = body.split(": ", 1)[1]
    words = re.findall(r"[a-z0-9]+", body.lower())
    pieces = set()
    for first in range(len(words)):
        for end in range(first + 2, min(len(words), first + 8) + 1):
            span = words[first:end]
            if any(word in span for word in anchors):
                pieces.add(" ".join(span).encode("ascii"))
    return sorted(pieces)


def run(root: Path) -> None:
    raw = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    assert len(nonce) == 16 and len(target) == 32

    first_draft = b"a good watch leaves the room ready for the next pair of hands"
    assert hmac.digest(nonce, first_draft, "sha256")[:16].hex().upper() == (
        "BF889359B0303F2B2B2FD96AE841210B"
    )
    assert hashlib.sha256(hmac.digest(nonce, first_draft, "sha256")[:16]).hexdigest() == (
        "47e787785ff25082b4b960ad415f1e030ae0edc89c38b2f61c48f9331282ea55"
    )

    source = {name: fragments(raw.decode("utf-8"), name, terms)
              for name, terms in ANCHORS.items()}
    assert {name: len(spans) for name, spans in source.items()} == COUNTS
    grouped = {kind: sorted(set(itertools.chain.from_iterable(source[n] for n in notes)))
               for kind, notes in GROUPS.items()}
    assert {name: len(spans) for name, spans in grouped.items()} == {
        "P": 69, "G": 139, "E": 256,
    }
    expected = 69 * 139 * 256 * 6 * 4

    padded = nonce.ljust(64, b"\x00")
    inner_base = hashlib.sha256(bytes(x ^ 0x36 for x in padded))
    outer_base = hashlib.sha256(bytes(x ^ 0x5c for x in padded))
    planted = grouped["P"][8] + b" and " + grouped["G"][11] + b" " + grouped["E"][17]
    planted_target = hashlib.sha256(hmac.digest(nonce, planted, "sha256")[:16]).digest()

    count = matched = controls = 0
    start = time.monotonic()
    for order in itertools.permutations("PGE"):
        a_spans, b_spans, c_spans = (grouped[k] for k in order)
        for join_a, join_b in itertools.product(JOINERS, repeat=2):
            for a in a_spans:
                for b in b_spans:
                    prefix = inner_base.copy()
                    prefix.update(a + join_a + b + join_b)
                    for c in c_spans:
                        inner = prefix.copy()
                        inner.update(c)
                        outer = outer_base.copy()
                        outer.update(inner.digest())
                        slot = outer.digest()[:16]
                        digest = hashlib.sha256(slot).digest()
                        count += 1
                        if digest == target:
                            matched += 1
                            print("ORIGINAL_K08_PASS", (a + join_a + b + join_b + c).decode(),
                                  slot.hex().upper(), flush=True)
                        if digest == planted_target:
                            controls += 1
    assert count == expected and controls == 1
    print(json.dumps({
        "result": "PASS" if matched else "NO_MATCH",
        "crew_sha256": SOURCE_SHA,
        "source_span_counts": COUNTS,
        "group_counts": {k: len(v) for k, v in grouped.items()},
        "complete_assignments": count,
        "original_hits": matched,
        "planted_positive_hits": controls,
        "seconds": round(time.monotonic() - start, 2),
    }, indent=2))


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else (
        Path(__file__).resolve().parents[2] / "resources"
    )
    run(root)
