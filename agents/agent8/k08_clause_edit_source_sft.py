"""K08 source-ordered deletion-and-splice hypothesis, self-contained SFT.

The model retains N13's complete end-of-night anchor, removes one or both
scene tails at grammatical edit points, and joins source-literal sea and
voices-at-table spans in N20's declared motif order. This is exploratory;
source evidence does not claim that Emily used this editing operation.
"""

from __future__ import annotations

import hashlib
import hmac
import itertools
import json
from pathlib import Path
import re
import sys

EXPECTED = {
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
CONNECTORS = ("", "and", "as", "when", "after", "with", "while", "until")


def words(s: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9]+", s.lower()))


def source_note(s: str, note: int) -> tuple[str, ...]:
    hit = re.search(rf"^N{note:02d} /[^\n]*\n([^\n]+)", s, re.M)
    assert hit is not None, f"Missing note N{note:02d}"
    text = hit.group(1)
    if note in (1, 2):
        text = text.split(":", 1)[1]
    return words(text)


def spans_containing(tokens: tuple[str, ...], motif: tuple[str, ...], lo: int, hi: int) -> tuple[tuple[str, ...], ...]:
    out = set()
    for size in range(lo, hi + 1):
        for i in range(len(tokens) - size + 1):
            seg = tokens[i:i + size]
            if any(seg[j:j + len(motif)] == motif for j in range(len(seg) - len(motif) + 1)):
                out.add(seg)
    return tuple(sorted(out))


def late_night_variants(n13: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    assert n13[:6] == words("At the end of the night")
    assert n13[6:12] == words("the mugs stood beside the window")
    assert n13[12] == "and"
    assert n13[13:] == words("somebody had remembered to leave the little lamp on")
    base = n13[:6]
    left_choices = ((), n13[6:8], n13[6:10], n13[6:12])
    right = n13[13:]
    right_choices = ((), right, right[3:], right[4:], right[6:])
    out = set()
    for left, tail in itertools.product(left_choices, right_choices):
        out.add(base + left + (("and",) if left and tail else ()) + tail)
    return tuple(sorted(out))


def candidate_phrases(n01: tuple[str, ...], n13: tuple[str, ...], n20: tuple[str, ...]):
    sea = spans_containing(n01, ("sea",), 2, 6)
    night = late_night_variants(n13)
    voices = spans_containing(n20, words("voices at the table"), 4, 8)
    assert len(sea) == 10 and len(night) == 20 and len(voices) == 15
    for a, b, c in itertools.product(sea, night, voices):
        for j1, j2 in itertools.product(CONNECTORS, repeat=2):
            yield " ".join(a + ((j1,) if j1 else ()) + b + ((j2,) if j2 else ()) + c)


def digest(nonce: bytes, phrase: str) -> bytes:
    component = hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]
    return hashlib.sha256(component).digest()


def main(root: Path) -> None:
    for name, digest_hex in EXPECTED.items():
        got = hashlib.sha256((root / name).read_bytes()).hexdigest()
        assert got == digest_hex, (name, got)
    notes = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_text(encoding="utf-8")
    route = json.loads((root / "evidence/recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((root / "acceptance.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    n01, n02, n13, n20 = [source_note(notes, n) for n in (1, 2, 13, 20)]
    n02_component = hmac.digest(nonce, " ".join(n02).encode("utf-8"), "sha256")[:16]
    assert n02_component.hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    planted = "the sea looks different at the end of the night the mugs and leave the little lamp on and voices at the table"
    planted_digest = digest(nonce, planted)
    count = 0
    unique = set()
    planted_hits = 0
    originals = []
    for phrase in candidate_phrases(n01, n13, n20):
        count += 1
        unique.add(phrase)
        d = digest(nonce, phrase)
        if d == planted_digest:
            planted_hits += 1
        if d == target:
            originals.append(phrase)
    assert count == 192000, count
    assert planted_hits > 0, "Planted in-model phrase was not enumerated"
    print(json.dumps({
        "source_n01_sea_spans": 10,
        "source_n13_deletion_variants": 20,
        "source_n20_voices_spans": 15,
        "connectors_per_join": len(CONNECTORS),
        "complete_assignments": count,
        "distinct_phrases": len(unique),
        "independent_n02_hmac_control": "PASS",
        "planted_positives": planted_hits,
        "original_k08_matches": originals,
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
