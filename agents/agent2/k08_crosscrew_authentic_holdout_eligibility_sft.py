"""Source-pinned K08 editorial-graph authentic whole-caption eligibility audit.

Historic N02, N06, N17, N18 are genuine complete captions/labels. Withhold
each entire note body when building the source-author graph; do not expose
held-out words or edges. This tests the candidate-family *representability*,
without improperly promoting drafts or old labels to the final envelope.
"""
import hashlib
import re
from pathlib import Path

PIN = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
SCENES = ({"sea", "water"}, {"night", "watch", "morning"}, {"room", "voices", "table", "people"})
HELDOUT = ("N02", "N06", "N17", "N18")


def body_tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.lower())


def main() -> None:
    path = Path(__file__).resolve().parents[2] / "resources/evidence/crew/noticeboard-and-desk-notes.txt"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    records = dict(re.findall(r"(?m)^(N\d\d) / [^\n]+\n([^\n]+)", raw.decode()))
    assert set(records) == {f"N{i:02d}" for i in range(1, 25)}
    for name in HELDOUT:
        # Original header is a source/editorial designation, not caption words.
        title = records[name].split(": ", 1)[1]
        target = body_tokens(title)
        source = [body_tokens(line) for n, line in records.items() if n != name]
        source_words = {w for row in source for w in row}
        edges = {(a, b) for row in source for a, b in zip(row, row[1:])}
        oov = [w for w in target if w not in source_words]
        unseen = [f"{a} {b}" for a, b in zip(target, target[1:]) if (a, b) not in edges]
        motifs = [bool(SCENES[i].intersection(target)) for i in range(3)]
        eligible_one = 6 <= len(target) <= 12 and all(motifs) and not oov and len(unseen) == 1
        eligible_two = 6 <= len(target) <= 9 and all(motifs) and not oov and len(unseen) == 2
        assert not eligible_one and not eligible_two
        print(f"{name}: words={len(target)} scene_flags={''.join('1' if b else '0' for b in motifs)} "
              f"oov={len(oov)} original_unknown_edges={len(unseen)} "
              f"one_new_edge_eligible={eligible_one} two_new_edges_eligible={eligible_two}")
        print(f"  unseen_word_types={','.join(sorted(set(oov))) or 'none'}")
    print("Original source pin confirmed; four complete authentic captions excluded by source/motif eligibility before hash.")


if __name__ == "__main__":
    main()
