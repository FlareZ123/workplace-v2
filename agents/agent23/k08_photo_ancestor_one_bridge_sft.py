"""K08 cross-author photo-caption antecedent with one Emily-sourced replacement.

Source-pinned, read-only standalone Python 3 SFT. Do not modify original evidence.
"""
from pathlib import Path
import hashlib
import hmac
import json
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[2] / "resources"
RAW = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(RAW).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
NOTES = {
    number: re.findall(r"[a-z0-9]+", body.lower())
    for number, body in re.findall(
        r"(?m)^N(\d\d) / [^\n]+\n(.+?)(?=\n\n|\Z)",
        RAW.decode("utf-8"),
        re.S,
    )
}
assert len(NOTES) == 24
PHOTOS = {
    "N01": NOTES["01"][7:],    # Jason's empty-bench sea/tea photo
    "N08": NOTES["08"][2:],    # Jason's window/water photo
    "N09": NOTES["09"][5:],    # Zoey's first-cup galley caption
}
EMILY = {n: NOTES[n] for n in ("02", "06", "10", "13", "20")}
EMILY["02"] = EMILY["02"][6:]
EMILY["06"] = EMILY["06"][3:]
EMILY["20"] = EMILY["20"][:20]
ANCHORS = {
    "sea", "night", "water", "room", "table", "lamp", "watch",
    "window", "voices", "tea", "cup", "hands", "light", "mugs",
}
BRIDGES = {
    tuple(words[i:j])
    for words in EMILY.values()
    for i in range(len(words))
    for j in range(i + 2, min(len(words), i + 10) + 1)
    if ANCHORS.intersection(words[i:j])
}
NONCE = bytes.fromhex(json.loads(
    (ROOT / "evidence/recovery-routing.json").read_text()
)["K08"]["desk_nonce"])
TARGET = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K08"]


def digest(words):
    mac = hmac.new(NONCE, " ".join(words).encode("utf-8"), hashlib.sha256).digest()[:16]
    return hashlib.sha256(mac).hexdigest(), mac.hex().upper()


assert digest("a good watch leaves the room ready for the next pair of hands".split())[1] == "BF889359B0303F2B2B2FD96AE841210B"
JOINS = ((), ("and",), ("while",), ("with",))
base = PHOTOS["N01"]
planted = (
    tuple(base[:3]) + ("and", "the", "voices", "at", "the", "table", "while")
    + tuple(base[6:])
)
planted_digest = digest(planted)[0]

count = Counter()
planted_found = False
matches = []
for photo, words in PHOTOS.items():
    for i in range(2, len(words) - 1):
        for j in range(i, min(len(words) - 1, i + 13)):
            left, right = tuple(words[:i]), tuple(words[j:])
            if len(left) + len(right) < 7:
                continue
            for bridge in BRIDGES:
                for pre in JOINS:
                    for post in JOINS:
                        candidate = left + pre + bridge + post + right
                        found, key = digest(candidate)
                        planted_found |= found == planted_digest
                        count[photo] += 1
                        if found == TARGET:
                            matches.append((photo, " ".join(candidate), key))
assert planted_found
assert dict(count) == {"N01": 144480, "N08": 235984, "N09": 235984}
print(json.dumps({
    "bridge_spans": len(BRIDGES),
    "candidate_assignments": dict(count),
    "synthetic_positive": planted_found,
    "accepted_matches": matches,
}, indent=2))
