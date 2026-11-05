"""Original-source K08 literal-label-to-printer transport calibration.
Tests whether two known old caption HMAC16 outputs appear as whole printer
payloads under a single shared XOR/add mask, fixed word layout, or arbitrary
byte permutation. No original K08 target digest or unknown final text is used.
"""
import hashlib
import hmac
import json
import re
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTES = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
assert hashlib.sha256(NOTES.read_bytes()).hexdigest() == (
    "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
)
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
nonce = bytes.fromhex(json.loads((ROOT / "evidence/recovery-routing.json").read_text())["K08"]["desk_nonce"])
notes = {
    int(i): line.split(":", 1)[-1].strip()
    for i, line in re.findall(
        r"^N(\d\d) / Emily \[censored\]\n([^\n]+)",
        NOTES.read_text(encoding="utf8"),
        re.MULTILINE,
    )
}

def h16(s):
    normalized = " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())
    return hmac.digest(nonce, normalized.encode("utf8"), "sha256")[:16]

known = {i: h16(notes[i]) for i in (2, 6, 17, 18)}
assert known[2].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
assert notes[17] == "Leave the light on for the next watch."
assert notes[18] == "Back before the first boat."
rows = []
for line in SPOOL.read_text(encoding="utf8").splitlines():
    if line.startswith("#"):
        continue
    fields = dict(re.findall(r"(\w+)=(\S+)", line))
    rows.append((fields["CLASS"], bytes.fromhex(fields["PAYLOAD"])))
assert len(rows) == 133 and sum(cls == "LABEL" for cls, _ in rows) == 52

def layouts(packet):
    words = [packet[i:i + 4] for i in range(0, 16, 4)]
    return [
        b"".join(w[::-1] if byte_reverse else w for w in (words[::-1] if word_reverse else words))
        for word_reverse in (False, True)
        for byte_reverse in (False, True)
    ]

def diff(a, b, kind):
    if kind == "xor":
        return bytes(x ^ y for x, y in zip(a, b))
    if kind == "byteadd":
        return bytes((x - y) & 255 for x, y in zip(a, b))
    if kind == "add128be":
        return ((int.from_bytes(a, "big") - int.from_bytes(b, "big")) % (1 << 128)).to_bytes(16, "big")
    if kind == "add128le":
        return ((int.from_bytes(a, "little") - int.from_bytes(b, "little")) % (1 << 128)).to_bytes(16, "little")
    raise ValueError(kind)

# Check the entire calibration path with two synthetic, independently known
# literal labels transported through the same nonzero fixed 16byte XOR pad.
pad = bytes.fromhex("D14C05A9027819F32CAF0750BE083761")
a = bytes(x ^ y for x, y in zip(known[17], pad))
b = bytes(x ^ y for x, y in zip(known[18], pad))
assert diff(a, b, "xor") == diff(known[17], known[18], "xor")
assert Counter(diff(a[::-1], b[::-1], "xor")) == Counter(diff(known[17], known[18], "xor"))

for poolname, pool in (
    ("LABEL", [b for cls, b in rows if cls == "LABEL"]),
    ("ALL", [b for _, b in rows]),
):
    ordered = len(pool) * (len(pool) - 1)
    for kind in ("xor", "add128be", "add128le"):
        wanted = diff(known[17], known[18], kind)
        matches = []
        for layout in range(4):
            rendered = [layouts(packet)[layout] for packet in pool]
            for i, first in enumerate(rendered):
                for j, second in enumerate(rendered):
                    if i != j and diff(first, second, kind) == wanted:
                        matches.append((layout, i, j))
        print("FIXED_LAYOUT", poolname, kind, "ordered_pairs", ordered,
              "views", 4, "matches", matches[:10])
        assert not matches, "Unexpected original calibration: investigate"
    for kind in ("xor", "byteadd"):
        targets = {
            pair: Counter(diff(known[pair[0]], known[pair[1]], kind))
            for pair in combinations(sorted(known), 2)
        }
        matches = []
        best = 0
        for i, first in enumerate(pool):
            for j, second in enumerate(pool):
                if i == j:
                    continue
                observed = Counter(diff(first, second, kind))
                for pair, target in targets.items():
                    best = max(best, sum((observed & target).values()))
                    if observed == target:
                        matches.append((pair, i, j))
        print("ANY_BYTE_PERMUTATION", poolname, kind,
              "ordered_pairs", ordered, "known_label_pairs", len(targets),
              "matches", matches[:10], "max_overlap", best)
        assert not matches, "Unexpected original calibration: investigate"
print("PLANTED_LABEL_PAIR_POSITIVE=PASS ORIGINAL_SOURCE_CALIBRATION=NO_MATCH")
