"""Source-pinned A BIT LATE plus three-strand complete K08 caption test."""
from __future__ import annotations
import hashlib
import hmac
import itertools
import json
from pathlib import Path
import re
import sys

NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
N02_HMAC = "BF889359B0303F2B2B2FD96AE841210B"
CONNECTORS = ("", "and", "but", "when", "with", "after", "as", "until")

def source(path: Path, digest: str) -> bytes:
    value = path.read_bytes()
    assert hashlib.sha256(value).hexdigest() == digest, path
    return value

def normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))

def spans(text: str, motif: str, min_size: int, max_size: int) -> tuple[str, ...]:
    tokens = normalize(text).split()
    needle = motif.split()
    found = []
    for size in range(min_size, max_size + 1):
        for start in range(len(tokens) - size + 1):
            sub = tokens[start : start + size]
            if any(sub[i : i + len(needle)] == needle for i in range(len(sub) - len(needle) + 1)):
                found.append(" ".join(sub))
    return tuple(dict.fromkeys(found))

def extract_notes(blob: bytes) -> dict[int, str]:
    return {
        int(identifier): body.split(": ", 1)[-1]
        for identifier, body in re.findall(r"(?m)^N(\d+) / [^\n]+\n([^\n]+)", blob.decode())
    }

def commitment(nonce: bytes, phrase: str) -> bytes:
    key = hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]
    return hashlib.sha256(key).digest()

def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    notes = extract_notes(source(root / "evidence/crew/noticeboard-and-desk-notes.txt", NOTES_SHA))
    route = json.loads(source(root / "evidence/recovery-routing.json", ROUTE_SHA))
    accept = json.loads(source(root / "acceptance.json", ACCEPT_SHA))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(accept["slot_sha256"]["K08"])
    first = normalize(notes[2])
    assert hmac.digest(nonce, first.encode(), "sha256")[:16].hex().upper() == N02_HMAC
    sea = spans(notes[1], "sea", 2, 6)
    night = spans(notes[13], "end of the night", 4, 8)
    voices = spans(notes[20], "voices at the table", 4, 8)
    assert (len(sea), len(night), len(voices)) == (10, 12, 15)
    total = 0
    matches = []
    anchor = "a bit late"
    planted = normalize(" ".join((anchor, sea[0], "and", night[0], "and", voices[0])))
    planted_commitment = commitment(nonce, planted)
    planted_hits = 0
    for pieces in itertools.product(sea, night, voices):
        for at in range(4):
            ordered = list(pieces)
            ordered.insert(at, anchor)
            for connect in itertools.product(CONNECTORS, repeat=3):
                phrase = ordered[0] + "".join(
                    f" {link} {piece}" if link else f" {piece}"
                    for link, piece in zip(connect, ordered[1:])
                )
                total += 1
                digest = commitment(nonce, phrase)
                if digest == target:
                    matches.append((phrase, hmac.digest(nonce, phrase.encode(), "sha256")[:16].hex().upper()))
                if digest == planted_commitment:
                    planted_hits += 1
    assert total == 10 * 12 * 15 * 4 * 8**3
    assert planted_hits > 0, "Planted complete-caption control failed"
    print(json.dumps({
        "source_sha256": NOTES_SHA,
        "model": "A BIT LATE anchor in any of four positions; three source spans in N20 order; three source-literal connectors",
        "spans": {"N01": len(sea), "N13": len(night), "N20": len(voices)},
        "connectors": list(CONNECTORS),
        "complete_assignments": total,
        "planted_hits": planted_hits,
        "k08_matches": matches,
    }, indent=2))

if __name__ == "__main__":
    main()
