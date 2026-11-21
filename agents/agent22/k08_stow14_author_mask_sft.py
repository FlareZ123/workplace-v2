#!/usr/bin/env python3
"""H-17 K08 source-local STOW14 author mask, with exact conditional null.

Reads five SHA-pinned original sources; never submits a final K08 caption.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import re

EVIDENCE = Path("resources/evidence")
PINS = {
    "crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "mail/10.eml": "ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48",
    "mail/11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "mail/13.eml": "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
    "mail/14.eml": "9c86de086a1727ca09b4df6f12cf5c634eaa22a3949424171cc50b4ef9983be5",
}

def load(name):
    raw = (EVIDENCE / name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return raw.decode("utf-8")

def decode(authors, subset):
    bits = [int(a in subset) for a in authors]
    assert len(bits) == 24
    values = [sum(bits[s + j] << j for j in range(5)) for s in (0, 5, 10, 15)]
    word = "".join(chr(65 + x) if x < 26 else "?" for x in values)
    suffix = sum(bits[20 + j] << j for j in range(4))
    return word, suffix, "".join(map(str, bits))

def main():
    note_text = load("crew/noticeboard-and-desk-notes.txt")
    notes = re.findall(r"^N(\d{2}) / (\w+) \[censored\]$", note_text, re.M)
    assert [int(n) for n, _ in notes] == list(range(1, 25))
    authors = [a for _, a in notes]
    assert Counter(authors) == {
        "Jason": 3, "Emily": 8, "Zoey": 4,
        "David": 3, "Gabriel": 3, "Simon": 3,
    }
    order = list(dict.fromkeys(authors))
    assert order == ["Jason", "Emily", "Zoey", "David", "Gabriel", "Simon"]
    crew = decode(authors, {"Emily"})
    assert crew == ("CREW", 4, "010001000100100011010010")
    assert order[crew[1] - 1] == "David"

    slot_mails = {"K05": "mail/10.eml", "K06": "mail/11.eml", "K07": "mail/13.eml"}
    senders = {}
    for slot, path in slot_mails.items():
        match = re.search(r"^From: (\w+) \[censored\]", load(path), re.M)
        assert match is not None
        senders[slot] = match.group(1)
    assert senders == {"K05": "Simon", "K06": "Emily", "K07": "Gabriel"}
    selected = set(senders.values())
    stow = decode(authors, selected)
    assert stow == ("STOW", 14, "010011100101110011010111")
    assert sum(a in selected for a in authors) == 14

    mail14 = load("mail/14.eml")
    assert mail14.startswith("From: David [censored]")
    assert "your\ndesk notes are under it" in mail14
    assert "photographs and galley captions" in mail14
    assert "WN-14 signed" in mail14

    # Conditional exact finite null: preserve Emily's eight source positions,
    # reassign the six Gabriel/Simon positions among the sixteen others.
    emily = {i for i, a in enumerate(authors) if a == "Emily"}
    others = [i for i in range(24) if i not in emily]
    actual = {i for i, a in enumerate(authors) if a in selected}
    assert len(emily) == 8 and len(others) == 16
    total = word_hits = exact_hits = 0
    for extra in combinations(others, 6):
        positions = emily.union(extra)
        bits = [int(i in positions) for i in range(24)]
        values = [sum(bits[s + j] << j for j in range(5)) for s in (0, 5, 10, 15)]
        word = "".join(chr(65 + v) if v < 26 else "?" for v in values)
        suffix = sum(bits[20 + j] << j for j in range(4))
        total += 1
        word_hits += word == "STOW"
        if (word, suffix) == ("STOW", 14):
            exact_hits += 1
            assert positions == actual
    assert (total, word_hits, exact_hits) == (8008, 3, 1)

    print("CREW4", crew[2], "-> David")
    print("K05 K06 K07 author set:", senders)
    print("STOW14", stow[2], "-> MAIL-14 authored by David")
    print("MAIL14: Emily's loose notes are beneath WN-14, not in sleeve")
    print("Conditional null STOW14:", f"{exact_hits}/{total}")
    print("Conditional null STOW-any-suffix:", f"{word_hits}/{total}")
    print("K08: UNRECOVERED (locator, not final caption)")

if __name__ == "__main__":
    main()
