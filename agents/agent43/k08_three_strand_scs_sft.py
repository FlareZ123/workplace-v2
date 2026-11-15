"""K08: 3-strand shortest-common-supersequence source-caption test.

Usage: python agents/agent43/k08_three_strand_scs_sft.py [--max-words 15]

This model combines N01 (sea), N13 (end of night), and either
N20 (editorial voices at table) or N09 (galley cup alone) through
minimum-length order-preserving interleavings, coalescing identical
next words from any available strands. It is exploratory and does not imply
that the source attests Emily's actual final wording.
"""
import argparse
import hashlib
import hmac
import itertools
import json
import re
from functools import lru_cache
from pathlib import Path

NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
K08_TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
KNOWN_N02 = "BF889359B0303F2B2B2FD96AE841210B"


def words(line):
    return tuple(re.findall(r"[a-z0-9]+", line.lower()))


def notes_by_id(raw):
    text = raw.decode("utf-8")
    out = {}
    for found in re.finditer(r"(?ms)^N(\d\d) /[^\n]*\n(.*?)(?=\n\nN\d\d /|\Z)", text):
        n = int(found.group(1))
        line = found.group(2).strip()
        if n in (1, 9):
            expected = ("For the photograph of the empty bench:" if n == 1
                        else "Caption for the galley board:")
            assert line.startswith(expected)
            line = line.split(":", 1)[1]
        out[n] = words(line)
    assert set(out) == set(range(1, 25))
    return out


def source_spans(seq, motif, min_words, max_words):
    found = set()
    for start in range(len(seq)):
        for stop in range(start + min_words, min(start + max_words, len(seq)) + 1):
            fragment = seq[start:stop]
            if any(fragment[pos:pos + len(motif)] == motif for pos in range(len(fragment) - len(motif) + 1)):
                found.add(fragment)
    return sorted(found)


def scs_walk(a, b, c, limit):
    lengths = len(a), len(b), len(c)

    @lru_cache(None)
    def shortest(i, j, k):
        if (i, j, k) == lengths:
            return 0
        next_words = {s[pos] for s, pos in ((a, i), (b, j), (c, k)) if pos < len(s)}
        return 1 + min(shortest(
            i + int(i < len(a) and a[i] == token),
            j + int(j < len(b) and b[j] == token),
            k + int(k < len(c) and c[k] == token)
        ) for token in next_words)

    min_len = shortest(0, 0, 0)
    if min_len > limit:
        return

    def walk(i, j, k, prefix):
        if (i, j, k) == lengths:
            yield " ".join(prefix)
            return
        next_words = sorted({s[pos] for s, pos in ((a, i), (b, j), (c, k)) if pos < len(s)})
        remaining = shortest(i, j, k)
        for token in next_words:
            ni = i + int(i < len(a) and a[i] == token)
            nj = j + int(j < len(b) and b[j] == token)
            nk = k + int(k < len(c) and c[k] == token)
            if shortest(ni, nj, nk) == remaining - 1:
                yield from walk(ni, nj, nk, prefix + (token,))
    yield from walk(0, 0, 0, ())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--resources", type=Path, default=Path(__file__).resolve().parents[2] / "resources")
    p.add_argument("--max-words", type=int, default=15)
    p.add_argument("--human-role", choices=("editorial", "galley"), default="editorial")
    args = p.parse_args()

    files = (
        (args.resources / "evidence/crew/noticeboard-and-desk-notes.txt", NOTES_SHA),
        (args.resources / "evidence/recovery-routing.json", ROUTE_SHA),
        (args.resources / "acceptance.json", ACCEPT_SHA),
    )
    for path, expected in files:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
    notes = notes_by_id(files[0][0].read_bytes())
    assert notes[1][:2] == ("the", "sea")
    assert notes[13][:6] == ("at", "the", "end", "of", "the", "night")
    assert ("voices", "at", "the", "table") in [notes[20][i:i+4] for i in range(len(notes[20])-3)]
    if args.human_role == "editorial":
        social_spans = source_spans(notes[20], ("voices", "at", "the", "table"), 4, 8)
        expected_spans = (10, 12, 15)
    else:
        social_spans = source_spans(notes[9], ("cup", "alone"), 3, 7)
        expected_spans = (10, 12, 19)
    spans = (
        source_spans(notes[1], ("sea",), 2, 6),
        source_spans(notes[13], ("end", "of", "the", "night"), 4, 8),
        social_spans,
    )
    assert tuple(map(len, spans)) == expected_spans
    route = json.loads(files[1][0].read_text())
    acceptance = json.loads(files[2][0].read_text())
    assert acceptance["slot_sha256"]["K08"] == K08_TARGET
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    known = "a good watch leaves the room ready for the next pair of hands"
    assert hmac.new(nonce, known.encode(), hashlib.sha256).digest()[:16].hex().upper() == KNOWN_N02

    # A genuinely in-family phrase, used only for an independent planted positive.
    chosen = next(iter(scs_walk(spans[0][0], spans[1][0], spans[2][0], 30)))
    planted = hashlib.sha256(hmac.new(nonce, chosen.encode(), hashlib.sha256).digest()[:16]).digest()
    planted_count = 0
    checked = 0
    hits = []
    for a, b, c in itertools.product(*spans):
        for phrase in scs_walk(a, b, c, args.max_words):
            check = hashlib.sha256(hmac.new(nonce, phrase.encode(), hashlib.sha256).digest()[:16]).digest()
            checked += 1
            if check == planted:
                planted_count += 1
            if check.hex() == K08_TARGET:
                hits.append(phrase)
    assert planted_count > 0 if args.max_words >= len(chosen.split()) else planted_count == 0
    if args.human_role == "editorial" and args.max_words == 15:
        assert checked == 21_743_888, checked
    if args.human_role == "galley" and args.max_words == 14:
        assert checked == 35_071_612, checked
    print(json.dumps({
        "source_spans": list(map(len, spans)),
        "triples": len(spans[0])*len(spans[1])*len(spans[2]),
        "max_caption_words": args.max_words,
        "human_role": args.human_role,
        "tested_complete_scs_assignments": checked,
        "planted_in_family_positive": planted_count,
        "original_K08_acceptance_hits": hits,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
