"""K08 exact-word one-bridge version model, read-only H-17 source test."""
from __future__ import annotations

import hashlib
import hmac
import json
import pathlib
import re
from collections import Counter

CASE = pathlib.Path(__file__).resolve().parents[2] / "resources"
route = json.loads((CASE / "evidence/recovery-routing.json").read_text())
accept = json.loads((CASE / "acceptance.json").read_text())
raw_notes = (CASE / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(raw_notes).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
notes = raw_notes.decode()
mail = (CASE / "evidence/mail/11.eml").read_text().split("\n\n", 1)[-1].rsplit("\nEmily", 1)[0]
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
target = accept["slot_sha256"]["K08"]
entries = {
    number: re.findall(r"[a-z0-9]+", body.lower())
    for number, body in re.findall(
        r"(?m)^N(\d\d) / [^\n]+\n(.+?)(?=\n\n|\Z)", notes, re.S
    )
}
assert sorted(entries) == [f"{i:02d}" for i in range(1, 25)]

bases = {n: entries[n].copy() for n in ("02", "06", "13")}
bases["02"] = bases["02"][6:]  # Remove six-word first-draft label.
bases["06"] = bases["06"][3:]  # Remove three-word second-draft label.
sources = {
    f"N{n}": bases[n] if n in ("02", "06") else entries[n]
    for n in ("02", "06", "10", "13", "20")
}
sources["MAIL11"] = re.findall(r"[a-z0-9]+", mail.lower())
anchors = {"sea", "water", "voices", "table", "room", "watch",
           "night", "lamp", "window", "mugs", "hands", "cup"}
bridges = {}
for source, words in sources.items():
    for i in range(len(words)):
        for j in range(i + 2, min(len(words), i + 10) + 1):
            span = tuple(words[i:j])
            if not anchors.isdisjoint(span):
                bridges.setdefault(span, set()).add(source)


def digest(words):
    message = " ".join(words).encode("utf-8")
    slot = hmac.new(nonce, message, hashlib.sha256).digest()[:16]
    return hashlib.sha256(slot).hexdigest(), slot.hex().upper()


assert digest(tuple(bases["02"]))[1] == "BF889359B0303F2B2B2FD96AE841210B"
planted = (
    tuple(bases["13"][:5]) + ("and", "the", "voices", "at", "the", "table", "while")
    + tuple(bases["13"][10:])
)
control = digest(planted)[0]
matches = []
control_seen = False
counts = Counter()
joiners = ((), ("and",), ("while",), ("with",))
for base, words in bases.items():
    for i in range(2, len(words) - 1):
        for j in range(i, min(len(words) - 1, i + 13)):
            left, right = tuple(words[:i]), tuple(words[j:])
            if len(left) + len(right) < 8:
                continue
            for bridge, origins in bridges.items():
                if origins == {f"N{base}"}:
                    continue
                for leading in joiners:
                    for trailing in joiners:
                        candidate = left + leading + bridge + trailing + right
                        actual, component = digest(candidate)
                        counts[base] += 1
                        control_seen |= actual == control
                        if actual == target:
                            matches.append({"base": base, "component": component,
                                            "words": " ".join(candidate)})

assert control_seen, "Synthetic exact-phrase witness not reconstructed"
assert sum(counts.values()) == 1780048, "Candidate-family drift"
print(json.dumps({"bridge_spans": len(bridges), "candidate_assignments": dict(counts),
                  "positive_control": control_seen, "accepted_matches": matches}, indent=2))
