#!/usr/bin/env python3
"""Bounded K08 N08-to-N20 metaphor-transfer candidate construction.

This is a source-motivated, complete-phrase test, not a claim that Emily used
this edit. It transfers N08's "water gives back ... colors ... borrowed
overnight" predicate frame to N20's sea/voices/table motifs, then varies only
source-attested temporal, subject, verb, object, relative-clause and social
tail phrases. It never changes the route, nonce, acceptance commitment or
normalization rule.
"""
from __future__ import annotations
import argparse, hashlib, hmac, itertools, json, re, zipfile
from pathlib import Path

NOTES_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
EXPECTED_CANDIDATES = 162_666

TEMPORALS = [
    "", "by daylight", "at daylight", "at the end of the night",
    "after a long watch", "after the last cup", "when the night is over",
    "at daybreak",
]
SUBJECTS = ["the water", "the sea", "the sea outside", "the water outside"]
VERBS = ["gives back", "returns", "brings back", "gives", "keeps", "leaves"]
OBJECTS = [
    "the colors", "the light", "the voices", "the voices at the table",
    "the words", "the warmth", "the room", "a place",
    "the next pair of hands", "the quiet", "the mugs",
]
RELATIVES = [
    "it borrowed overnight", "it borrowed through the night",
    "it held overnight", "it kept through the night",
    "we shared overnight", "we left at the table",
    "it took from the room", "the night had borrowed",
    "from the table", "from the room", "from the long watch",
]
TAILS = [
    "", "and leaves room for one more",
    "and makes room for the next pair of hands",
    "while the voices gather at the table", "for the next watch",
    "at the table", "for one another",
]
EXPLICIT = [
    "The sea gives back the voices it borrowed overnight.",
    "The sea gives back the light it borrowed overnight.",
    "The sea gives back the voices it borrowed from the table.",
    "The sea gives back the room it borrowed overnight.",
    "The sea gives back what the night borrowed from the table.",
    "The sea returns the voices to the table at the end of the night.",
    "The water gives back the colors it borrowed overnight, and the room is ready for the next pair of hands.",
    "At the end of the night, the sea gives back the light it borrowed, and leaves room for one more.",
    "At the end of the night, the sea gives back the voices it borrowed, and leaves room for one more.",
    "After the last cup, the sea gives back the light it borrowed overnight.",
    "After a long watch, the sea gives back the voices it borrowed overnight.",
    "The sea gives back the light it borrowed overnight, and the table is ready for the next watch.",
    "The sea gives back the voices it borrowed overnight, and there is room at the table for one more.",
    "The sea gives back the night to the people at the table.",
    "The night gives back the sea to the people at the table.",
    "The water gives back the light to the room after a long watch.",
    "The sea keeps the light on until the corridor has gone quiet.",
    "The little lamp gives back the light the sea borrowed overnight.",
    "The sea gives back what it borrowed, and the table has room for one more.",
    "The sea outside gives back the voices inside.",
    "By daylight the sea gives back most of the voices it borrowed overnight.",
    "At the end of the night the sea gives back most of the voices it borrowed overnight.",
    "By daylight the water gives back the voices it borrowed overnight.",
    "At the end of the night the water gives back the voices it borrowed overnight.",
    "The sea gives back the voices it borrowed overnight.",
    "The sea gives back the voices it borrowed from the table.",
    "The sea gives back the voices that the night borrowed.",
    "The sea gives back what it borrowed from the table.",
    "The sea returns the voices to the table after a long watch.",
    "The sea returns the light to the room at the end of the night.",
    "The sea gives back the light that it borrowed overnight.",
    "The sea gives back the warmth that it borrowed overnight.",
    "The sea gives back the room that it borrowed overnight.",
    "The sea gives back the words that it borrowed overnight.",
    "The sea gives back the colors of the night to the voices at the table.",
    "The sea gives back the colors it borrowed from the voices at the table.",
    "The sea gives back the voices and the table gives back the room.",
    "The water gives back the colors of the night and the room is ready for the next watch.",
    "At the end of the night the sea gives back the voices at the table.",
    "After the last cup the sea gives back the voices at the table.",
    "After a long watch the sea gives back the voices at the table.",
    "By daylight the sea gives back the voices at the table.",
    "The voices at the table give the sea back its colors.",
    "The voices at the table give back what the sea borrowed overnight.",
    "The sea keeps the voices of the table until daylight.",
    "The sea keeps the voices at the table until the night is over.",
    "The table keeps the voices while the sea gives back the light.",
    "The table gives back the voices the sea borrowed overnight.",
    "The sea gives back the night to the people at the table.",
    "The sea gives back the room to the next pair of hands.",
    "The sea leaves room for the next pair of hands after the last cup.",
    "The sea leaves a place at the table for one more after a long watch.",
]

def normalize(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(text.split())

def read_inputs(root: Path | None, zip_path: Path | None):
    if zip_path:
        with zipfile.ZipFile(zip_path) as zf:
            notes = zf.read("evidence/crew/noticeboard-and-desk-notes.txt")
            routing = json.loads(zf.read("evidence/recovery-routing.json"))
            acceptance = json.loads(zf.read("acceptance.json"))
    else:
        root = root or Path("resources")
        base = root / "evidence" if (root / "evidence").is_dir() else root
        notes = (base / "crew/noticeboard-and-desk-notes.txt").read_bytes()
        routing = json.loads((base / "recovery-routing.json").read_text())
        acceptance_path = root / "acceptance.json"
        if not acceptance_path.exists():
            acceptance_path = base.parent / "acceptance.json"
        acceptance = json.loads(acceptance_path.read_text())
    return notes, routing, acceptance

def parse_note(notes_text: str, note_id: str) -> str:
    lines = notes_text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(note_id + " / "):
            return lines[i + 1].strip()
    raise ValueError(f"missing {note_id}")

def candidates() -> set[str]:
    out = set()
    for fields in itertools.product(TEMPORALS, SUBJECTS, VERBS, OBJECTS, RELATIVES, TAILS):
        out.add(" ".join(x for x in fields if x))
    out.update(EXPLICIT)
    return {normalize(x) for x in out}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("resources"))
    ap.add_argument("--zip", type=Path)
    args = ap.parse_args()
    notes_raw, routing, acceptance = read_inputs(args.root, args.zip)
    assert hashlib.sha256(notes_raw).hexdigest() == NOTES_SHA256
    notes_text = notes_raw.decode("utf-8")
    n08 = parse_note(notes_text, "N08")
    n20 = parse_note(notes_text, "N20")
    n02 = parse_note(notes_text, "N02")
    assert "water gives back most of the colors it borrowed overnight" in n08
    assert "sea, the end of the night and the voices at the table" in n20
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    assert target == K08_SHA256
    n02_caption = n02.split(": ", 1)[1]
    assert hmac.new(nonce, normalize(n02_caption).encode(), hashlib.sha256).digest()[:16].hex().upper() == N02_HMAC16
    pool = candidates()
    assert len(pool) == EXPECTED_CANDIDATES, len(pool)

    def commitment(phrase: str):
        component = hmac.new(nonce, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
        return hashlib.sha256(component).hexdigest(), component.hex().upper()

    original_hits = []
    synthetic = normalize("By daylight the sea gives back most of the voices it borrowed overnight.")
    assert synthetic in pool
    synthetic_digest, synthetic_mac = commitment(synthetic)
    synthetic_hits = [s for s in pool if commitment(s)[0] == synthetic_digest]
    assert synthetic_hits == [synthetic], synthetic_hits
    for phrase in sorted(pool):
        digest, component = commitment(phrase)
        if digest == target:
            original_hits.append({"phrase": phrase, "component": component})
    print(json.dumps({
        "source_sha256": NOTES_SHA256,
        "n08": n08, "n20": n20,
        "normalization": "lowercase; non-ASCII-alphanumeric/non-whitespace to space; collapse whitespace",
        "candidate_model": "N08 borrowed-colors predicate frame transferred to N20 sea/voices/table motifs",
        "candidate_count_unique_normalized": len(pool),
        "original_k08_hits": original_hits,
        "synthetic_control_phrase": synthetic,
        "synthetic_control_hmac16": synthetic_mac,
        "synthetic_control_commitment": synthetic_digest,
        "synthetic_control_hits": len(synthetic_hits),
        "n02_hmac16_control": N02_HMAC16,
        "target_commitment": target,
    }, indent=2, ensure_ascii=False))
    print("K08 N08-to-N20 metaphor-transfer SFT: PASS (source pins, original control, synthetic positive)")
    print(f"Original K08 hits: {len(original_hits)}")

if __name__ == "__main__":
    main()
