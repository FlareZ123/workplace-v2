"""K08 source-role photo/desk word-interweave search, original-source pinned.

Usage: python k08_photo_desk_word_interweave_sft.py [archive_root] [photo_id]
photo_id is optionally one of 1, 8, 9, 14; shard runs avoid long single jobs.
"""
import hashlib
import hmac
import re
import sys
from pathlib import Path

CREW_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")
KNOWN_DRAFT = "a good watch leaves the room ready for the next pair of hands"
KNOWN_HMAC = "BF889359B0303F2B2B2FD96AE841210B"
PHOTO_IDS = (1, 8, 9, 14)
EMILY_IDS = (2, 6, 10, 13, 20)
PHOTO_WORDS = set("sea water night boat tea cup rain horizon daylight window colors morning first last".split())
EMILY_WORDS = set("room watch hands lamp window night mugs voices table sea cup people morning tea corridor".split())
GROUPS = ({"sea", "water"}, {"night", "watch", "morning"}, {"room", "voices", "table", "people"})
EXPECTED = {1: (511, 3267571), 8: (994, 7490106), 9: (43, 526475), 14: (59, 833280)}


def hmac16(text):
    return hmac.digest(NONCE, text.encode("utf-8"), "sha256")[:16]


def spans(notes, ids, anchors):
    out = []
    for ident in ids:
        text = notes[ident]
        if ":" in text:
            text = text.split(":", 1)[1]
        words = re.findall(r"[a-z0-9]+", text.lower())
        for width in range(3, 10):
            for start in range(len(words) - width + 1):
                fragment = tuple(words[start : start + width])
                if any(word in anchors for word in fragment):
                    out.append((ident, fragment))
    return out


def main(root, photo_id=None):
    raw = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CREW_SHA
    notes = {
        int(ident): body.strip()
        for ident, body in re.findall(
            r"(?ms)^N(\d\d) / [^\n]+\n(.*?)(?=^N\d\d /|\Z)",
            raw.decode("utf-8"),
        )
    }
    assert len(notes) == 24
    assert hmac16(KNOWN_DRAFT).hex().upper() == KNOWN_HMAC
    photos = spans(notes, PHOTO_IDS, PHOTO_WORDS)
    emilys = spans(notes, EMILY_IDS, EMILY_WORDS)
    assert len(photos) == 172 and len(emilys) == 297
    all_pairs = [
        (photo, emily)
        for photo in photos
        for emily in emilys
        if all(group.intersection(photo[1] + emily[1]) for group in GROUPS)
    ]
    assert len(all_pairs) == 1607
    if photo_id is None:
        pairs = all_pairs
    else:
        assert photo_id in PHOTO_IDS
        pairs = [pair for pair in all_pairs if pair[0][0] == photo_id]
        assert len(pairs) == EXPECTED[photo_id][0]

    planted_text = " ".join(pairs[0][0][1] + pairs[0][1][1])
    planted_hash = hashlib.sha256(hmac16(planted_text)).digest()
    assignments = matches = planted = 0
    found = None
    for (p_id, photo), (e_id, emily) in pairs:
        result_words = []

        def visit(i, j):
            nonlocal assignments, matches, planted, found
            if i == len(photo) and j == len(emily):
                phrase = " ".join(result_words)
                digest = hashlib.sha256(hmac16(phrase)).digest()
                assignments += 1
                if digest == TARGET:
                    matches += 1
                    found = (p_id, e_id, phrase)
                if digest == planted_hash:
                    planted += 1
                return
            if i < len(photo):
                result_words.append(photo[i])
                visit(i + 1, j)
                result_words.pop()
            if j < len(emily):
                result_words.append(emily[j])
                visit(i, j + 1)
                result_words.pop()
            if i < len(photo) and j < len(emily) and photo[i] == emily[j]:
                result_words.append(photo[i])
                visit(i + 1, j + 1)
                result_words.pop()

        visit(0, 0)

    assert assignments == (
        12117432 if photo_id is None else EXPECTED[photo_id][1]
    ), assignments
    assert planted > 0
    print({
        "photo_id": photo_id,
        "photo_spans": len(photos),
        "emily_spans": len(emilys),
        "motif_qualified_pairs": len(pairs),
        "complete_assignments": assignments,
        "original_matches": matches,
        "planted_positive_assignments": planted,
        "found": found,
    })


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("."),
         int(sys.argv[2]) if len(sys.argv) > 2 else None)
