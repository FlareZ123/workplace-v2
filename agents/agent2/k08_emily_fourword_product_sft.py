"""Single-file original-source K08 four-word author-vocabulary test.

Python 3 standard library. Defaults to all 90 first-word shards; --start and
--end optionally divide the complete run into nonoverlapping half-open shards.
"""
import argparse
import hashlib
import hmac
import itertools
import re
from pathlib import Path

NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
VOCAB_SHA = "a323bd487dce87a6023e813c2e9756e9103df4f2f771f3e5c0455e0f1e11e261"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")
EMILY = {"02", "06", "10", "13", "17", "18", "20", "23"}


def component(phrase: bytes) -> bytes:
    return hmac.digest(NONCE, phrase, "sha256")[:16]


def commitment(phrase: bytes) -> bytes:
    return hashlib.sha256(component(phrase)).digest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notes", type=Path,
                        default=Path(__file__).resolve().parents[2] / "resources/evidence/crew/noticeboard-and-desk-notes.txt")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=90)
    args = parser.parse_args()
    source = args.notes.read_bytes()
    assert hashlib.sha256(source).hexdigest() == NOTES_SHA, "Original notes source changed"
    matches = re.findall(rb"(?m)^N(\d\d) / Emily [^\n]*\n([^\r\n]+)", source)
    found = {note.decode("ascii") for note, _ in matches}
    assert found == EMILY and len(matches) == 8, "Emily note set mismatch"
    vocabulary = sorted({word.lower().decode("ascii")
                         for note, body in matches
                         for word in re.findall(rb"[A-Za-z0-9]+", body)})
    assert len(vocabulary) == 90
    assert hashlib.sha256("\n".join(vocabulary).encode()).hexdigest() == VOCAB_SHA
    assert component(b"a good watch leaves the room ready for the next pair of hands").hex() == "bf889359b0303f2b2b2fd96ae841210b"
    assert 0 <= args.start < args.end <= len(vocabulary)
    planted = (vocabulary[args.start] + " night voices table").encode("ascii")
    planted_hash = commitment(planted)

    words = [w.encode("ascii") for w in vocabulary]
    counts = {"complete": 0, "original": 0, "synthetic": 0}
    for first in words[args.start:args.end]:
        for second, third in itertools.product(words, repeat=2):
            prefix = b" ".join((first, second, third)) + b" "
            for last in words:
                phrase = prefix + last
                digest = commitment(phrase)
                if digest == TARGET:
                    counts["original"] += 1
                    print("ORIGINAL K08 MATCH", phrase.decode(), component(phrase).hex().upper(), flush=True)
                if digest == planted_hash:
                    counts["synthetic"] += 1
                    assert phrase == planted
                counts["complete"] += 1
    assert counts["complete"] == (args.end - args.start) * 90**3
    assert counts["synthetic"] == 1
    print(f"source_sha256={NOTES_SHA} notes={len(matches)} words={len(words)} "
          f"range={args.start}..{args.end} complete={counts['complete']} "
          f"original_hits={counts['original']} planted_hits={counts['synthetic']}")


if __name__ == "__main__":
    main()
