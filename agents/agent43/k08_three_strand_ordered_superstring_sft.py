"""K08: source-ordered shortest-common-superstring test.

This is a bounded editorial/copy hypothesis distinct from the three-way SCS
interleaving test. It preserves the N20-described order:
N01 sea -> N13 end of the night -> N20 voices at the table.
For each predeclared source-span triple, merge only by maximal suffix/prefix
overlap (or containment), with no arbitrary interleaving or added vocabulary.
It is exploratory and does not imply that Emily used this operation.
"""
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
K08_TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
KNOWN_N02 = "BF889359B0303F2B2B2FD96AE841210B"
MAX_WORDS = 15


def words(line):
    return tuple(re.findall(r"[a-z0-9]+", line.lower()))


def notes_by_id(raw):
    text = raw.decode("utf-8")
    out = {}
    for found in re.finditer(r"(?ms)^N(\\d\\d) /[^\\n]*\\n(.*?)(?=\\n\\nN\\d\\d /|\\Z)", text):
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
            if any(fragment[pos:pos + len(motif)] == motif
                   for pos in range(len(fragment) - len(motif) + 1)):
                found.add(fragment)
    return sorted(found)


def contains(haystack, needle):
    return any(haystack[i:i + len(needle)] == needle
               for i in range(len(haystack) - len(needle) + 1))


def overlap_merge(left, right):
    if contains(left, right):
        return left
    if contains(right, left):
        return right
    for size in range(min(len(left), len(right)), 0, -1):
        if left[-size:] == right[:size]:
            return left + right[size:]
    return left + right


def ordered_superstring(sea_span, night_span, table_span):
    return overlap_merge(overlap_merge(sea_span, night_span), table_span)


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--resources",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "resources",
    )
    args = parser.parse_args()

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
    assert ("voices", "at", "the", "table") in [
        notes[20][i:i + 4] for i in range(len(notes[20]) - 3)
    ]

    spans = (
        source_spans(notes[1], ("sea",), 2, 6),
        source_spans(notes[13], ("end", "of", "the", "night"), 4, 8),
        source_spans(notes[20], ("voices", "at", "the", "table"), 4, 8),
    )
    assert tuple(map(len, spans)) == (10, 12, 15)

    route = json.loads(files[1][0].read_text())
    acceptance = json.loads(files[2][0].read_text())
    assert acceptance["slot_sha256"]["K08"] == K08_TARGET
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    known = "a good watch leaves the room ready for the next pair of hands"
    assert hmac.new(nonce, known.encode(), hashlib.sha256).digest()[:16].hex().upper() == KNOWN_N02

    first = ordered_superstring(spans[0][0], spans[1][0], spans[2][0])
    assert len(first) <= MAX_WORDS
    planted = hashlib.sha256(
        hmac.new(nonce, " ".join(first).encode(), hashlib.sha256).digest()[:16]
    ).digest()

    checked = 0
    unique = set()
    planted_count = 0
    hits = []
    for sea_span, night_span, table_span in itertools.product(*spans):
        phrase = ordered_superstring(sea_span, night_span, table_span)
        if len(phrase) > MAX_WORDS:
            continue
        checked += 1
        unique.add(phrase)
        normalized = " ".join(phrase)
        component = hmac.new(nonce, normalized.encode(), hashlib.sha256).digest()[:16]
        commitment = hashlib.sha256(component).hexdigest()
        if bytes.fromhex(commitment) == planted:
            planted_count += 1
        if commitment == K08_TARGET:
            hits.append(normalized)

    assert checked == 492, checked
    assert len(unique) == 318, len(unique)
    assert planted_count > 0
    assert not hits
    print(json.dumps({
        "source_spans": list(map(len, spans)),
        "span_triples": len(spans[0]) * len(spans[1]) * len(spans[2]),
        "merge_rule": "N01->N13->N20 maximal suffix/prefix overlap",
        "maximum_caption_words": MAX_WORDS,
        "complete_ordered_superstring_assignments": checked,
        "unique_normalized_phrases": len(unique),
        "planted_in_family_positive": planted_count,
        "original_K08_acceptance_hits": hits,
    }, indent=2))


if __name__ == "__main__":
    main()
