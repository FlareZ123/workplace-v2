#!/usr/bin/env python3
"""Bounded K08 phrase screen from the eight most relevant desk/crew notes.

Tests two fixed eight-word initial patterns suggested by the selected notes'
first-word initials: source order ATEALBIT and its anagram ABITLATE. It also
tests the exact one-word-per-note mapping implied by ABITLATE.
"""
from __future__ import annotations
import hashlib, hmac, itertools, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resources"
NOTE_IDS = ("N02", "N06", "N11", "N13", "N17", "N18", "N20", "N23")
NOTE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
EXPECTED_TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"

def sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())

def read(rel: str) -> bytes:
    return (RES / rel).read_bytes()

def parse_notes(text: str) -> dict[str, str]:
    found = {}
    for match in re.finditer(r"(N\d{2}) /[^\n]+\n(.*?)(?=\n\nN\d{2} /|\Z)", text, re.S):
        found[match.group(1)] = match.group(2).strip()
    return found

def body_words(body: str) -> list[str]:
    if ":" in body:
        body = body.split(":", 1)[1].strip()
    return re.findall(r"[a-z0-9]+", body.lower())

def scan_phrases(pattern: str, vocab: list[str], nonce: bytes, target: str):
    buckets = [[word for word in vocab if word.startswith(letter.lower())] for letter in pattern]
    count = 1
    for bucket in buckets:
        count *= len(bucket)
    hits = []
    for words in itertools.product(*buckets):
        phrase = " ".join(words)
        component = hmac.digest(nonce, normalize(phrase).encode(), "sha256")[:16]
        if sha(component).hex() == target:
            hits.append((phrase, component.hex().upper()))
    return count, hits, buckets

def main():
    note_bytes = read("evidence/crew/noticeboard-and-desk-notes.txt")
    route_bytes = read("evidence/recovery-routing.json")
    acceptance_bytes = read("acceptance.json")
    assert hashlib.sha256(note_bytes).hexdigest() == NOTE_SHA
    assert hashlib.sha256(route_bytes).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(acceptance_bytes).hexdigest() == ACCEPTANCE_SHA
    route = json.loads(route_bytes)
    acceptance = json.loads(acceptance_bytes)
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    assert target == EXPECTED_TARGET

    notes = parse_notes(note_bytes.decode())
    assert all(note in notes for note in NOTE_IDS)
    words_by_note = {note: body_words(notes[note]) for note in NOTE_IDS}
    first_initials = "".join(words[0][0].upper() for words in words_by_note.values())
    assert first_initials == "ATEALBIT"
    assert sorted(first_initials) == sorted("ABITLATE")

    vocab = sorted(set(word for words in words_by_note.values() for word in words))
    assert len(vocab) == 81
    totals, pattern_hits = {}, {}
    synthetic_controls = {}
    for pattern in ("ATEALBIT", "ABITLATE"):
        count, hits, buckets = scan_phrases(pattern, vocab, nonce, target)
        totals[pattern] = count
        pattern_hits[pattern] = hits
        planted_words = [bucket[0] for bucket in buckets]
        planted_phrase = " ".join(planted_words)
        planted_component = hmac.digest(nonce, normalize(planted_phrase).encode(), "sha256")[:16]
        planted_target = sha(planted_component).hex()
        planted_count, planted_hits, _ = scan_phrases(pattern, vocab, nonce, planted_target)
        synthetic_controls[pattern] = any(hit[0] == planted_phrase for hit in planted_hits)
        assert synthetic_controls[pattern] and planted_count == count

    note_order = ("N02", "N18", "N20", "N06", "N17", "N13", "N23", "N11")
    per_note_choices = []
    for note, initial in zip(note_order, "ABITLATE"):
        per_note_choices.append(list(dict.fromkeys(
            word for word in words_by_note[note] if word.startswith(initial.lower())
        )))
    per_note_count = 1
    for bucket in per_note_choices:
        per_note_count *= len(bucket)
    per_note_hits = []
    for words in itertools.product(*per_note_choices):
        phrase = " ".join(words)
        component = hmac.digest(nonce, normalize(phrase).encode(), "sha256")[:16]
        if sha(component).hex() == target:
            per_note_hits.append((phrase, component.hex().upper()))

    direct = {}
    for phrase in ("a bit late", "facts its a bit late"):
        component = hmac.digest(nonce, normalize(phrase).encode(), "sha256")[:16]
        direct[phrase] = sha(component).hex() == target

    report = {
        "selected_notes": list(NOTE_IDS),
        "source_order_initials": first_initials,
        "anagram_initials": "ABITLATE",
        "distinct_note_vocabulary": len(vocab),
        "pattern_candidate_counts": totals,
        "pattern_hits": pattern_hits,
        "per_note_order": list(note_order),
        "per_note_candidate_count": per_note_count,
        "per_note_hits": per_note_hits,
        "direct_phrase_checks": direct,
        "synthetic_positive_controls": synthetic_controls,
        "status": "NO_MATCH" if not any(pattern_hits.values()) and not per_note_hits and not any(direct.values()) else "HIT",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] == "HIT":
        raise SystemExit(10)

if __name__ == "__main__":
    main()
