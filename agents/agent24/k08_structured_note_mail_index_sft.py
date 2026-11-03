"""Source-masked K08 indexed-word carrier pilot with chronology/author controls.

Reads immutable official resources in the shared repo and prints exact original
K08 match count plus source-order ID-shuffle placebo.
"""
import hashlib
import hmac
import itertools
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
CREW = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
EXPECTED = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
assert hashlib.sha256(CREW.read_bytes()).hexdigest() == EXPECTED
TOKEN = re.compile(r"[a-z0-9]+")
norm = lambda s: " ".join(TOKEN.findall(s.lower()))
notes = {}
for no, author, body in re.findall(r"(?m)^N(\d\d) / (.+)\n([^\n]+)", CREW.read_text(encoding="utf-8")):
    notes[int(no)] = (author.split()[0], body)
assert len(notes) == 24
controls = {
    "standby": norm(notes[17][1].split(": ", 1)[1]),
    "commissioning": norm(notes[18][1].split(": ", 1)[1]),
}
assert controls == {
    "standby": "leave the light on for the next watch",
    "commissioning": "back before the first boat",
}
source = {}
for i, (author, body) in notes.items():
    if i in (17, 18):
        continue
    source[("N", i)] = (author, TOKEN.findall(body.lower()))
for i in range(1, 21):
    mail = (ROOT / f"evidence/mail/{i:02d}.eml").read_text(encoding="utf-8")
    body = mail.split("\n\n", 1)[1]
    for phrase in controls.values():
        body = re.sub(r"\b" + re.escape(phrase) + r"\.?", " ", body, flags=re.I)
    source[("M", i)] = ("MAIL", TOKEN.findall(body.lower()))
assert len(source) == 42
vocab = {w for _, words in source.values() for w in words}
assert "light" not in vocab and "lights" in vocab

routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
target = bytes.fromhex(acceptance["slot_sha256"]["K08"])

def digest(s):
    return hashlib.sha256(hmac.digest(nonce, norm(s).encode(), "sha256")[:16]).digest()

assert hmac.digest(nonce, norm(notes[2][1].split(": ", 1)[1]).encode(), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

A = (-2, -1, 0, 1, 2)
B = (-1, 0, 1)
C = tuple(range(24))
LENGTHS = tuple(range(5, 17))

def source_groups(anchor):
    return {
        "all_note_preceding": [k for k in source if k[0] == "N" and k[1] < anchor],
        "emily_note_preceding": [k for k in source if k[0] == "N" and k[1] < anchor and source[k][0] == "Emily"],
        "mail_original_order": [k for k in source if k[0] == "M"],
        "all_notes": [k for k in source if k[0] == "N"],
    }

def generate(anchor, replace_ids=None):
    for group, all_keys in source_groups(anchor).items():
        for size in LENGTHS:
            if len(all_keys) < size:
                continue
            keys = all_keys[-size:]
            for a, b, c, reversed_index in itertools.product(A, B, C, (False, True)):
                words = []
                for k in keys:
                    identifier = replace_ids[k] if replace_ids is not None else k[1]
                    body = source[k][1]
                    pos = (a * identifier + b * anchor + c) % len(body)
                    words.append(body[-1 - pos] if reversed_index else body[pos])
                yield group, size, a, b, c, reversed_index, " ".join(words)

synthetic_phrase = next(generate(23))[-1]
synthetic_commitment = digest(synthetic_phrase)
assert any(digest(r[-1]) == synthetic_commitment for r in generate(23))

results = {}
for anchor, label in ((17, "standby"), (18, "commissioning"), (23, "keeper")):
    phrases = [r[-1] for r in generate(anchor)]
    hits = [s for s in phrases if digest(s) == target]
    assert not hits
    results[label] = {
        "anchor": anchor,
        "assignments": len(phrases),
        "distinct_texts": len(set(phrases)),
        "exact_label_recovered": None if label == "keeper" else sum(s == controls[label] for s in phrases),
        "original_k08_matches": len(hits),
    }

bigrams = set(itertools.chain.from_iterable(zip(w, w[1:]) for _, w in source.values()))

def coherence(phrase):
    words = phrase.split()
    return sum(pair in bigrams for pair in zip(words, words[1:]))

def best_score(idmap):
    return max(coherence(r[-1]) for r in generate(23, idmap))

original = best_score(None)
rng = random.Random(20261103)
placebos = []
for _ in range(16):
    perm = {}
    for source_type in ("N", "M"):
        keys = [k for k in source if k[0] == source_type]
        ids = [k[1] for k in keys]
        rng.shuffle(ids)
        perm.update(zip(keys, ids))
    placebos.append(best_score(perm))
assert original == 5
assert placebos == [6, 6, 6, 7, 6, 6, 6, 5, 6, 5, 6, 6, 6, 6, 6, 5]
assert [results[x]["assignments"] for x in ("standby", "commissioning", "keeper")] == [25920, 25920, 26640]
print(json.dumps({
    "cases": results,
    "synthetic_control": "PASS",
    "notes_sha256": EXPECTED,
    "original_max_in_source_bigram_hits": original,
    "shuffled_ID_max_in_source_bigram_hits": placebos,
}, indent=2))
