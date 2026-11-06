"""Source-masked K08 author-order ranker with same-word controls.

SFT: python agents/agent41/k08_masked_author_rank_sft.py
Optional positional argument: original extracted evidence/ directory.
This scores existing genuine texts; it does not guess K08 or mutate sources.
"""
from collections import Counter
from itertools import permutations
from pathlib import Path
import hashlib
import math
import random
import re
import sys

PIN = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
HELD = (2, 6, 10, 13, 17, 18, 20, 23)
NGRAM, SMOOTH, SHUFFLES = 4, 1.0, 1000


def norm(value):
    return " ".join(re.findall(r"[a-z]+", value.lower()))


def gramcounts(value):
    s = "^" + norm(value) + "$"
    return Counter(s[i:i + NGRAM] for i in range(max(0, len(s) - NGRAM + 1)))


def load(root):
    data = (root / "crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(data).hexdigest() == PIN
    matches = list(re.finditer(
        r"(?m)^N(\d\d) / ([A-Za-z]+) \[censored\]\n(.+?)(?=\n\nN\d\d /|\Z)",
        data.decode("utf-8"), re.S))
    notes = {int(m[1]): (m[2], m[3].strip().split(": ", 1)[-1])
             for m in matches}
    assert len(notes) == 24
    mails = []
    for p in sorted((root / "mail").glob("??.eml")):
        text = p.read_text(encoding="utf-8")
        sender = re.search(r"(?m)^From: (\w+)", text)
        assert sender is not None
        body = text.split("\n\n", 1)[1]
        body = re.sub(
            r"(?m)^(Hi|Morning|Thanks,|Emily|David|Zoey|Gabriel|Simon|Jason)\s*,?\s*$",
            "", body)
        body = body.replace("Back before the first boat", "")
        body = body.replace("Leave the light on for the next watch", "")
        mails.append((sender[1], body))
    assert len(mails) == 20
    return notes, mails


def ranker(notes, mails, held):
    # Remove every exact heldout word from remaining source documents,
    # including quoted occurrences, before training.
    forbidden = set(norm(notes[held][1]).split())
    emily, other = Counter(), Counter()
    for k, (author, body) in notes.items():
        if k != held:
            clean = " ".join(w for w in norm(body).split() if w not in forbidden)
            (emily if author == "Emily" else other).update(gramcounts(clean))
    for author, body in mails:
        clean = " ".join(w for w in norm(body).split() if w not in forbidden)
        (emily if author == "Emily" else other).update(gramcounts(clean))
    vocab = len(set(emily) | set(other))
    ne, no = sum(emily.values()), sum(other.values())

    def score(sentence):
        grams = gramcounts(sentence)
        return sum(count * (
            math.log((emily[g] + SMOOTH) / (ne + SMOOTH * vocab))
            - math.log((other[g] + SMOOTH) / (no + SMOOTH * vocab)))
            for g, count in grams.items()) / max(1, sum(grams.values()))

    return score


def decoys(words, note_id):
    rng = random.Random(1700 + note_id)
    original = " ".join(words)
    if len(words) == 5:
        return [" ".join(p) for p in sorted(set(permutations(words)))
                if " ".join(p) != original]
    seen = set()
    while len(seen) < SHUFFLES:
        shuffled = words[:]
        rng.shuffle(shuffled)
        text = " ".join(shuffled)
        if text != original:
            seen.add(text)
    return sorted(seen)


def main(root):
    notes, mails = load(root)
    print("SOURCE_SHA", PIN, "NOTES", len(notes), "MAIL", len(mails))
    print("SCORER", "character 4-gram Emily/non-Emily likelihood ratio",
          "alpha", SMOOTH, "mask", "all exact heldout words")
    print("CONTROL", "all shuffled decoys retain the original word multiset")
    results = {}
    for held in HELD:
        words = norm(notes[held][1]).split()
        score = ranker(notes, mails, held)
        true_score = score(" ".join(words))
        decoy_scores = [score(text) for text in decoys(words, held)]
        rank = 1 + sum(value > true_score for value in decoy_scores)
        results[held] = (rank, len(decoy_scores) + 1)
        print(f"N{held:02}: words={len(words)}, rank={rank}/{len(decoy_scores)+1}, "
              f"real={true_score:.6f}, nullmean={sum(decoy_scores)/len(decoy_scores):.6f}")
    assert results == {
        2: (394, 1001), 6: (79, 1001), 10: (483, 1001),
        13: (794, 1001), 17: (97, 1001), 18: (114, 120),
        20: (880, 1001), 23: (200, 1001)}
    print("PASS: source-masked historical rank calibration; no K08 target asserted")


if __name__ == "__main__":
    evidence = (Path(sys.argv[1]) if len(sys.argv) > 1 else
                Path(__file__).resolve().parents[2] / "resources/evidence")
    main(evidence)
