"""Read-only H-17 K08 PV-decimal literal-carrier falsifier with planted caption.

The source has 112 PV rows seq100..211, each with three fractional digits.
A copying layer might encode one byte per PV sample, with an optional global
one-byte XOR pad. Scan eight plain byte projections and three source orderings,
then require a real three-word lowercase ASCII run before contacting K08 HMAC.
The hypothesis is exploratory; the route sheet does not assign PV to K08.
"""
import hashlib
import hmac
import json
import re
from pathlib import Path

SOURCE_SHA256 = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
NOTE_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
PHRASE_RE = re.compile(rb"[a-z]{2,}(?: [a-z]{2,}){2,}")
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"


def word_bytes(row, mode):
    integer = round(row["value"] * 1000)
    fraction = integer % 1000
    values = (
        integer,
        fraction,
        integer // 1000,
        fraction // 4,
        fraction ^ row["seq"],
        integer >> 8,
        fraction // 10,
        (fraction % 10) * 26 + row["seq"] % 26,
    )
    return values[mode] & 255


def ordered(rows, order):
    if order == "seq":
        return sorted(rows, key=lambda row: row["seq"])
    if order == "timestamp":
        # All PV timestamps have +00:00 in this source.
        return sorted(rows, key=lambda row: row["ts"])
    return rows


def k08_component(phrase):
    return hmac.digest(NONCE, phrase, "sha256")[:16]


def carriers(rows):
    for order in ("seq", "timestamp", "retrieval"):
        group = ordered(rows, order)
        for mode in range(8):
            symbols = bytes(word_bytes(row, mode) for row in group)
            for key in range(256):
                output = bytes(x ^ key for x in symbols).lower()
                yield order, mode, key, output


def main(root):
    source = root / "evidence/telemetry/freeze-export.jsonl"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_SHA256
    note = root / "evidence/crew/noticeboard-and-desk-notes.txt"
    assert hashlib.sha256(note.read_bytes()).hexdigest() == NOTE_SHA256
    rows = [json.loads(line) for line in source.read_text().splitlines()]
    pv = [row for row in rows if row["field"] == "PV"]
    assert len(pv) == 112
    assert {row["seq"] for row in pv} == set(range(100, 212))
    assert k08_component(b"a good watch leaves the room ready for the next pair of hands").hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    # Independent whole-original-label positive. Alter a separate synthetic
    # PV copy only, and preserve source integer parts and the same 112 IDs.
    old_caption = b"leave the light on for the next watch"
    synthetic = [dict(row) for row in ordered(pv, "seq")]
    for row, character in zip(synthetic, old_caption):
        row["value"] = (int(row["value"]) * 1000 + (character ^ 0x5A)) / 1000
    planted = hashlib.sha256(k08_component(old_caption)).hexdigest()
    positive = [match.group() for order, mode, key, output in carriers(synthetic)
                if order == "seq" and mode == 1 and key == 0x5A
                for match in PHRASE_RE.finditer(output)]
    assert old_caption in positive
    assert any(hashlib.sha256(k08_component(text)).hexdigest() == planted for text in positive)

    hits = []
    qualifying = 0
    for order, mode, key, output in carriers(pv):
        for match in PHRASE_RE.finditer(output):
            qualifying += 1
            phrase = match.group()
            if hashlib.sha256(k08_component(phrase)).hexdigest() == K08_SHA256:
                hits.append((order, mode, key, phrase.decode("ascii")))
    assert not hits
    print(json.dumps({"decoded_streams": 6144, "three_word_spans": qualifying,
                      "original_k08_hits": hits,
                      "synthetic_whole_caption": "PASS"}, sort_keys=True))


if __name__ == "__main__":
    main(Path(__file__).resolve().parents[2] / "resources")
