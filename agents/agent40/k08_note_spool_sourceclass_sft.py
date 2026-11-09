"""SFT: source-only note-label role prediction versus H-17 printer CLASS.

Role vocabulary is frozen from visible note text, without looking up
spool CLASS/DEST. A note called a 'label' need not be printed with
CLASS=LABEL. This tests that conditional prediction, not physical identity.

Run: python k08_note_spool_sourceclass_sft.py /path/to/resources
"""
import argparse
import hashlib
import math
import re
from collections import Counter
from pathlib import Path

CREW_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

# All cues are verbatim note-role terms, independent of spool CLASS/DEST.
STRICT = {
    1: "photograph of the empty bench",
    3: "Kitchen photograph",
    4: "old shift photograph",
    8: "Window photograph",
    9: "Caption for the galley board",
    14: "Sunrise photograph",
    15: "Rough draft of a heading",
    16: "Canteen notice",
    17: "Standby envelope label",
    18: "Commissioning envelope label",
    24: "Departure board",
}
# Weaker location-only cues, reported separately from the strict set.
EXTENDED = {**STRICT, 5: "Boat deck", 11: "Mug shelf"}
OFFSETS = tuple(range(-1, 104))


def original_data(root):
    notes_path = root / "evidence/crew/noticeboard-and-desk-notes.txt"
    spool_path = root / "evidence/print/spool-reconstruction.log"
    note_bytes = notes_path.read_bytes()
    spool_bytes = spool_path.read_bytes()
    assert hashlib.sha256(note_bytes).hexdigest() == CREW_SHA
    assert hashlib.sha256(spool_bytes).hexdigest() == SPOOL_SHA
    entries = re.findall(
        r"(?m)^(N\d\d) / [^\n]+\n([^\n]+)", note_bytes.decode("utf-8")
    )
    notes = {int(identifier[1:]): body for identifier, body in entries}
    assert len(notes) == 24 and set(notes) == set(range(1, 25))
    for n, cue in EXTENDED.items():
        assert cue.casefold() in notes[n].casefold(), (n, cue)
    spool = {}
    for line in spool_bytes.decode("ascii").splitlines():
        m = re.search(
            r"JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\w+) "
            r"CLASS=(\w+) .* DEST=(\w+)",
            line,
        )
        if not m:
            continue
        job, attempt, state, kind, dest = m.groups()
        number = int(job)
        if 300 <= number <= 427 and attempt == "1" and state == "ACK":
            assert number not in spool
            spool[number] = (kind, dest)
    assert len(spool) == 128
    return spool


def counts(spool, note_ids):
    return [
        sum(spool[300 + n + offset][0] == "LABEL" for n in note_ids)
        for offset in OFFSETS
    ]


def conditional_tail(spool, note_ids):
    # Exact source-role permutation preserving LABEL count in the proposed
    # 24-job offset-zero window; conditional descriptive reference only.
    successes = sum(spool[300 + n][0] == "LABEL" for n in range(1, 25))
    chosen = len(note_ids)
    observed = sum(spool[300 + n][0] == "LABEL" for n in note_ids)
    tail = sum(
        math.comb(successes, k) * math.comb(24 - successes, chosen - k)
        for k in range(observed, min(successes, chosen) + 1)
        if 0 <= chosen - k <= 24 - successes
    )
    return successes, tail / math.comb(24, chosen)


def report(name, spool, note_ids):
    scores = counts(spool, note_ids)
    at_zero = scores[OFFSETS.index(0)]
    better_or_equal = sum(s >= at_zero for s in scores)
    window_count, tail = conditional_tail(spool, note_ids)
    winners = [offset for offset, score in zip(OFFSETS, scores) if score == max(scores)]
    print(
        f"{name}: n={len(note_ids)} offset0={at_zero}/{len(note_ids)} "
        f"offset_ge={better_or_equal}/105 global_best={max(scores)} "
        f"best_offsets={winners} window_labels={window_count}/24 "
        f"exact_role_permutation_tail={tail:.9f}"
    )
    print(
        "  source-role pair outcomes at offset0:",
        ", ".join(
            f"N{n:02d}=PS-{300+n:04d}:{spool[300+n][0]}"
            for n in note_ids
        ),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path)
    args = parser.parse_args()
    spool = original_data(args.resources)
    print("original source SHA256s match, 24 notes + 128 ordinary printer jobs parsed")
    print("original 128-job CLASS frequencies", dict(Counter(c for c, _ in spool.values())))
    report("strict_source_only", spool, sorted(STRICT))
    report("extended_weaker", spool, sorted(EXTENDED))
    report("out_of_anchor_holdouts_01to16", spool, sorted(n for n in STRICT if n <= 16))
    report("literal_envelope_and_board_anchors", spool, [17, 18, 24])
    for n in (17, 18, 24):
        subset = sorted(set(STRICT) - {n})
        scores = counts(spool, subset)
        current = scores[OFFSETS.index(0)]
        print(
            f"leave_one_out=N{n:02d}: offset0={current}/{len(subset)} "
            f"offset_ge={sum(s >= current for s in scores)}/105 "
            f"best={max(scores)}"
        )
    # Synthetic positive verifies exact offset indexing.
    planted = {n: ("RECOVER", "desk") for n in spool}
    for n in STRICT:
        planted[300+n] = ("LABEL", "desk")
    synthetic = counts(planted, sorted(STRICT))
    assert synthetic[OFFSETS.index(0)] == len(STRICT)
    assert synthetic.count(len(STRICT)) == 1
    print("planted_exact_offset0_control=PASS, one unique full-role match")
    assert spool[317][0] == "LABEL" and spool[318][0] == "RECOVER"
    print("literal N17/N18 envelope-label pair: original CLASS LABEL/RECOVER")
    print("target_status=NO_K08_VALUE_RECOVERED; join and body-to-payload remain unverified")


if __name__ == "__main__":
    main()
