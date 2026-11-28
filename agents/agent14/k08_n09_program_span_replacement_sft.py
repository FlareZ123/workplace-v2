#!/usr/bin/env python3
from hashlib import sha256
import hmac, json, re, sys
from pathlib import Path

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
N02_HMAC16 = "bf889359b0303f2b2b2fd96ae841210b"

def lowbit(word):
    return sum((ord(c.lower()) & 1) << i for i, c in enumerate(word))

def lower_if_even(v):
    return v + 1 if v % 2 == 0 else v

def words(s):
    return re.findall(r"[A-Za-z0-9]+", s.lower())

def main(root):
    root = Path(root)
    raw = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest() == CREW_SHA256
    notes = {}
    for m in re.finditer(rb"^N(\\d{2}) / (\\w+) \\[censored\\]\\n([^\\n]+)$", raw, re.M):
        n = int(m.group(1))
        line = m.group(3).decode()
        body = line.split(": ", 1)[1] if ": " in line else line
        notes[n] = words(body)
    assert set(notes) == set(range(1, 25))

    def transform(win):
        sels = [lower_if_even(lowbit(w)) for w in win]
        assert all(1 <= s <= 24 for s in sels)
        return "".join(notes[s][0][0].upper() for s in sels)

    n09 = notes[9]
    assert len(n09) == 13
    assert [transform(n09[i-1:i+2]) for i in (2, 4, 6)] == ["AES", "SHA", "AES"]

    fragment = [notes[9][0], notes[13][0], notes[23][0], notes[20][18]]
    assert len(fragment) == 4

    # Single hypothesized edit edge: replace the N09 body span 2..8 that
    # encodes AES/SHA/AES with the independently emitted lineage fragment.
    # The N09 first token appears only once, at the start of the fragment.
    candidate_words = fragment + n09[8:]
    assert len(candidate_words) == 9

    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    def component(ws):
        return hmac.new(key, " ".join(ws).encode(), sha256).digest()[:16]

    assert component(notes[2]).hex() == N02_HMAC16
    got = sha256(component(candidate_words)).hexdigest()
    hit = got == target
    print({
        "source_pin": "PASS",
        "aes_sha_aes_span": "PASS",
        "emitted_fragment": "PASS",
        "candidate_word_count": len(candidate_words),
        "complete_candidates": 1,
        "historical_n02_control": "PASS",
        "original_k08_hits": int(hit),
    })
    raise SystemExit(3 if hit else 0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: k08_n09_program_span_replacement_sft.py ROOT")
    main(sys.argv[1])
