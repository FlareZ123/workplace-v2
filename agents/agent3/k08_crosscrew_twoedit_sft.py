"""K08 cross-crew source-literal two-interior-edit reconstruction.

Original notes from six non-Emily galley/photo/mug captions are possible
ancestors. Replace two disjoint interior spans with 2-5 exact contiguous
words from Emily N20 and N02/N06/N13 in either order. No made-up words.
Use unchanged K08 nonce, normalizer and original commitment.
"""
import hashlib
import hmac
import json
import re
from pathlib import Path

NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
BASES = (1, 4, 8, 9, 11, 19)
EXPECTED = {1: 287000, 4: 287000, 8: 951200, 9: 951200,
            11: 1476000, 19: 10397600}


def normalize(value):
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def spans(notes, ids, anchors):
    result = set()
    for note_id in ids:
        words = normalize(notes[note_id]).split()
        for start in range(len(words)):
            for end in range(start + 2, min(len(words), start + 5) + 1):
                block = tuple(words[start:end])
                if any(word in anchors for word in block):
                    result.add(block)
    return sorted(result)


def cuts(words):
    length = len(words)
    for a in range(2, length - 5):
        for left_count in range(1, 5):
            for b in range(a + left_count + 2, length - 2):
                for right_count in range(1, 5):
                    if b + right_count <= length - 2:
                        yield a, a + left_count, b, b + right_count


def main(root=None):
    if root is None:
        root = Path(__file__).resolve().parents[2] / "resources"
    source = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(source).hexdigest() == NOTES_SHA
    notes = {
        int(number): line.split(":", 1)[-1].strip()
        for number, _, line in re.findall(
            r"(?m)^N(\d{2}) / ([^\n]+)\n([^\n]+)$",
            source.decode("utf-8"),
        )
    }
    assert len(notes) == 24
    routing = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])

    def slot(sentence):
        return hmac.digest(nonce, normalize(sentence).encode("ascii"), "sha256")[:16]

    assert slot(notes[2]).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    n20 = spans(notes, (20,), {"sea", "night", "voices", "table"})
    other = spans(notes, (2, 6, 13),
                  {"watch", "room", "hands", "lamp", "window", "mugs",
                   "night", "quiet"})
    assert (len(n20), len(other)) == (50, 82)
    ninth = normalize(notes[9]).split()
    a, ae, b, be = next(cuts(ninth))
    planted = " ".join(ninth[:a] + list(n20[0]) + ninth[ae:b] +
                       list(other[0]) + ninth[be:])
    planted_hash = hashlib.sha256(slot(planted)).digest()

    matches = []
    planted_hits = 0
    tested = 0
    for note_id in BASES:
        words = normalize(notes[note_id]).split()
        count = 0
        for a, ae, b, be in cuts(words):
            left = " ".join(words[:a]) + " "
            mid = " " + " ".join(words[ae:b]) + " "
            right = " " + " ".join(words[be:])
            for first, second in ((n20, other), (other, n20)):
                suffixes = [" ".join(x) for x in second]
                for x in first:
                    front = left + " ".join(x) + mid
                    for suffix in suffixes:
                        phrase = front + suffix + right
                        candidate = hmac.digest(
                            nonce, phrase.encode("ascii"), "sha256"
                        )[:16]
                        digest = hashlib.sha256(candidate).digest()
                        if digest == target:
                            matches.append((note_id, phrase, candidate.hex().upper()))
                        if digest == planted_hash and phrase == planted:
                            planted_hits += 1
                        count += 1
        assert count == EXPECTED[note_id], (note_id, count)
        tested += count
    assert tested == 14350000
    assert planted_hits == 1
    print("Synthetic planted two-edit positive: PASS")
    print("N20 donor spans:", len(n20), "Emily other donor spans:", len(other))
    print("Original K08 complete assignments:", tested)
    print("Original K08 acceptance matches:", matches)
    return matches


if __name__ == "__main__":
    main()
