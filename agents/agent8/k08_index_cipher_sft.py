"""Read-only H-17 K08 indexed-note word-picking hypothesis, with positive controls."""
import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTES = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
ACCEPTANCE = ROOT / "acceptance.json"
ROUTING = ROOT / "evidence/recovery-routing.json"
NOTES_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def normalize(text):
    return " ".join(re.sub(r"[^a-z0-9\\s]", " ", text.lower()).split())


def reduction(text, nonce):
    return hmac.new(nonce, normalize(text).encode("utf-8"), hashlib.sha256).digest()[:16]


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def main():
    assert hashlib.sha256(NOTES.read_bytes()).hexdigest() == NOTES_SHA256
    raw = NOTES.read_text(encoding="utf-8")
    matches = re.findall(r"(?m)^N(\\d\\d) / (.+)\\n([^\\n]+)$", raw)
    assert len(matches) == 24
    notes = []
    for index, byline, line in matches:
        idx = int(index)
        assert idx == len(notes) + 1
        notes.append((idx, byline.split()[0], line))

    nonce = bytes.fromhex(json.loads(ROUTING.read_text())["K08"]["desk_nonce"])
    wanted = bytes.fromhex(json.loads(ACCEPTANCE.read_text())["slot_sha256"]["K08"])
    n02 = notes[1][2].split(":", 1)[1].strip()
    assert reduction(n02, nonce).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    named = {
        "all24": notes,
        "emily8": [n for n in notes if n[1] == "Emily"],
        "late8": notes[-8:],
        "first12": notes[:12],
        "last12": notes[12:],
        "scene10": [notes[i - 1] for i in (1, 4, 8, 9, 10, 11, 13, 19, 20, 23)],
    }
    tested = set()
    pergroup = {}
    positive = None
    planted_group, planted_field, planted_direction, planted_a, planted_b = "emily8", "body", 0, 5, 13

    def phrase(group, field, direction, a, b):
        selected = []
        for index, _byline, line in named[group]:
            words = tokenize(line if field == "body" else line.split(":", 1)[-1])
            position = (a * index + b) % len(words)
            selected.append(words[position if direction == 0 else -1 - position])
        return " ".join(selected)

    synthetic = reduction(phrase(planted_group, planted_field, planted_direction, planted_a, planted_b), nonce)
    synthetic_commitment = hashlib.sha256(synthetic).digest()
    synthetic_hits = 0
    seen = set()
    for group in named:
        count = 0
        for field in ("body", "after_colon"):
            for direction in (0, 1):
                for a in range(25):
                    for b in range(25):
                        candidate = phrase(group, field, direction, a, b)
                        out = reduction(candidate, nonce)
                        digest = hashlib.sha256(out).digest()
                        if digest == wanted:
                            tested.add((group, field, direction, a, b))
                            print("ORIGINAL_HIT", group, field, direction, a, b, candidate, out.hex().upper())
                        if digest == synthetic_commitment:
                            synthetic_hits += 1
                            if group == planted_group and field == planted_field and direction == planted_direction and a == planted_a and b == planted_b:
                                positive = True
                        seen.add(candidate)
                        count += 1
        pergroup[group] = count
    assert positive and synthetic_hits >= 1
    assert sum(pergroup.values()) == 6 * 2 * 2 * 25 * 25
    print(json.dumps({
        "notes": len(notes), "source_sha256": NOTES_SHA256,
        "assignments": sum(pergroup.values()), "distinct_phrases": len(seen),
        "per_group": pergroup, "original_hits": len(tested),
        "synthetic_positive_hits": synthetic_hits, "synthetic_selected_positive": bool(positive)}, indent=2))


if __name__ == "__main__":
    main()
