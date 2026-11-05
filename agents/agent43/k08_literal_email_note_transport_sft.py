"""Exact historic crew-note to email quotation transport test for K08.

The two known old labels serve as full-literal positive controls.
Search independent mail bodies for every 5+ word contiguous phrase
present in any original crew note. No terminal Emily margin is assumed.
Python 3 standard library, source read-only.
"""
from pathlib import Path
import collections
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2] / "resources/evidence"
NOTES = ROOT / "crew/noticeboard-and-desk-notes.txt"
MAIL11 = ROOT / "mail/11.eml"
MAIL20 = ROOT / "mail/20.eml"
assert hashlib.sha256(NOTES.read_bytes()).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
assert hashlib.sha256(MAIL11.read_bytes()).hexdigest() == "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
assert hashlib.sha256(MAIL20.read_bytes()).hexdigest() == "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71"

def normalized_words(s):
    return re.findall(r"[a-z0-9]+", s.lower())

note_text = NOTES.read_text()
notes = dict(re.findall(
    r"(?ms)^N(\d\d) / [^\n]*\n(.*?)(?=\n\nN\d\d /|\Z)", note_text
))
assert len(notes) == 24
mails = {
    path.stem: path.read_text().split("\n\n", 1)[1]
    for path in (ROOT / "mail").glob("[0-9][0-9].eml")
}
assert len(mails) == 20

# Record only exact text shared between *different* source families.
fragments = collections.defaultdict(lambda: [set(), set()])
for group, texts in enumerate((notes, mails)):
    for source, body in texts.items():
        words = normalized_words(body)
        for size in range(5, len(words) + 1):
            for start in range(len(words) - size + 1):
                fragment = tuple(words[start:start + size])
                fragments[fragment][group].add(source)

shared = {
    phrase: refs for phrase, refs in fragments.items()
    if refs[0] and refs[1]
}
assert shared
assert {next(iter(refs[0])) for refs in shared.values()} == {"17", "18"}
assert {next(iter(refs[1])) for refs in shared.values()} == {"11"}
assert max(map(len, shared)) == 8
labels = {
    "17": "leave the light on for the next watch",
    "18": "back before the first boat",
}
mail11_normalized = " ".join(normalized_words(mails["11"]))
for note_id, expected in labels.items():
    source_line = " ".join(normalized_words(notes[note_id]))
    assert expected in source_line
    assert expected in mail11_normalized

print(f"24 exact note texts x 20 mail bodies; shared 5+ word spans={len(shared)}")
print("Full cross-source historic quotations: N17 and N18 in MAIL11, both explicitly superseded.")
print("No N23 or N13 full-phrase overlap and no authenticated final Emily margin text.")
print("Scope: source quotation transport only; K08 exact words remain unrecovered.")
