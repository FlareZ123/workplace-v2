"""N10->N01 photographic K08 caption splice, original-source complete candidates.

Run: python agents/agent45/k08_n01_photo_scene_sft.py resources --mode both
Or pass the unchanged incident ZIP. Read-only; no original modification.
"""
import argparse
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path
from zipfile import ZipFile

NOTE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ANCHORS = {
    1: {"sea", "tea"},
    2: {"watch", "room", "hands"},
    13: {"night", "mugs", "window", "lamp"},
    20: {"sea", "night", "voices", "table"},
}
JOINS = (" ", " and ")


def normalized(s):
    return " ".join(re.findall(r"[a-z0-9]+", s.lower()))


def spans_for(notes, n):
    body = notes[n].split(": ", 1)[1] if n in (1, 2) else notes[n]
    if n == 20:
        body = body.split(".", 1)[0]
    words = normalized(body).split()
    return sorted({
        " ".join(words[i:j])
        for i in range(len(words))
        for j in range(i + 2, min(len(words), i + 10) + 1)
        if ANCHORS[n].intersection(words[i:j])
    })


def phrases(spans, ids):
    for order in itertools.permutations(ids):
        for a, b, c in itertools.product(*(spans[n] for n in order)):
            for left, right in itertools.product(JOINS, repeat=2):
                yield order, a + left + b + right + c


def pairs(spans, ids):
    for pair in itertools.combinations(ids, 2):
        for order in (pair, pair[::-1]):
            for a, b in itertools.product(*(spans[n] for n in order)):
                for sep in JOINS:
                    yield order, a + sep + b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="Unmodified archive ZIP or unpacked resources")
    ap.add_argument("--mode", choices=("photo", "scene", "both"), default="both")
    args = ap.parse_args()
    source = Path(args.source)
    z = ZipFile(source) if source.is_file() else None

    def read(path):
        return z.read(path).decode() if z else (source / path).read_text()

    note_text = read("evidence/crew/noticeboard-and-desk-notes.txt")
    assert hashlib.sha256(note_text.encode()).hexdigest() == NOTE_SHA
    notes = {
        int(n): body
        for n, body in re.findall(
            r"N(\d\d) / .*?\n(.*?)(?=\n\nN\d\d /|\Z)", note_text, re.S
        )
    }
    assert len(notes) == 24
    route = json.loads(read("evidence/recovery-routing.json"))
    commitment = json.loads(read("acceptance.json"))["slot_sha256"]["K08"]
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(commitment)

    def component(s):
        return hmac.new(nonce, s.encode(), hashlib.sha256).digest()[:16]

    def matches(s, wanted):
        return hashlib.sha256(component(s)).digest() == wanted

    # Independently known reduction fixture from original N02.
    assert component(normalized(notes[2].split(": ", 1)[1])).hex().upper() == (
        "BF889359B0303F2B2B2FD96AE841210B"
    )
    spans = {n: spans_for(notes, n) for n in ANCHORS}
    assert tuple(len(spans[n]) for n in (1, 2, 13, 20)) == (26, 55, 112, 97)
    print("SOURCE-SPANS", {n: len(v) for n, v in spans.items()}, flush=True)
    total = 0
    modes = ("photo", "scene") if args.mode == "both" else (args.mode,)
    for mode in modes:
        ids = (1, 2, 13) if mode == "photo" else (1, 13, 20)
        # An in-class planted synthetic target is recovered as the first candidate.
        synthetic = next(phrases(spans, ids))[1]
        assert next(phrases(spans, ids))[1] == synthetic
        assert matches(synthetic, hashlib.sha256(component(synthetic)).digest())
        family = itertools.chain(
            pairs(spans, ids) if mode == "scene" else (),
            phrases(spans, ids),
        )
        mode_count = 0
        for order, caption in family:
            mode_count += 1
            if matches(caption, target):
                print("K08_ACCEPTED", mode, order, repr(caption),
                      component(caption).hex().upper())
                return 0
        expected = 3843840 if mode == "photo" else 6844328
        assert mode_count == expected, (mode_count, expected)
        total += mode_count
        print(mode.upper(), "NO_MATCH", mode_count, flush=True)
    print("ALL_NO_MATCH", total, flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
