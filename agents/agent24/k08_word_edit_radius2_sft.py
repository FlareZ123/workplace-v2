"""Reproducible K08 word-edit radius <=2 candidate family.

From the repository root: python agents/agent24/k08_word_edit_radius2_sft.py --note 2 --mode substitute
For longer batches, shard --mode insert-substitute by --gap-start/--gap-stop.
All source and acceptance files are read-only.
"""
import argparse
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTES = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
raw = NOTES.read_bytes()
assert hashlib.sha256(raw).hexdigest() == NOTES_SHA
lines = raw.decode("utf-8").splitlines()
tokens = lambda s: re.findall(r"[a-z0-9]+", s.lower())
vocab_text = "\n".join(line for line in lines if not line.startswith("N"))
for n in (11, 20):
    mail = (ROOT / f"evidence/mail/{n:02d}.eml").read_text()
    vocab_text += "\n" + mail.split("\n\n", 1)[1]
vocab = tuple(sorted(x for x in set(tokens(vocab_text)) if len(x) > 1))
assert len(vocab) == 355
sources = {}
for n in (2, 6, 13):
    start = next(i for i, s in enumerate(lines) if s.startswith(f"N{n:02d} /"))
    text = lines[start + 1].split(": ", 1)[-1]
    sources[n] = tokens(text)
assert tuple(map(len, sources.values())) == (13, 11, 22)
routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
target = bytes.fromhex(acceptance["slot_sha256"]["K08"])


def component(candidate: str) -> bytes:
    return hmac.digest(nonce, candidate.encode("utf-8"), "sha256")[:16]


assert component(" ".join(sources[2])).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
plant = sources[13].copy()
plant[0], plant[-1] = "sea", "table"
plant_sha = hashlib.sha256(component(" ".join(plant))).digest()


def candidates(base: list[str], mode: str, gap_start: int, gap_stop: int):
    n = len(base)
    if mode == "substitute":
        for i in range(n):
            for a in vocab:
                if a != base[i]:
                    words = base.copy()
                    words[i] = a
                    yield words
        for i in range(n):
            for j in range(i + 1, n):
                for a in vocab:
                    if a == base[i]:
                        continue
                    for b in vocab:
                        if b != base[j]:
                            words = base.copy()
                            words[i], words[j] = a, b
                            yield words
    elif mode == "insert-two":
        for i in range(n + 1):
            for j in range(i, n + 1):
                for a in vocab:
                    for b in vocab:
                        words = base.copy()
                        words.insert(i, a)
                        words.insert(j + 1, b)
                        yield words
    elif mode == "insert-substitute":
        for gap in range(max(0, gap_start), min(n + 1, gap_stop)):
            for repl in range(n):
                for a in vocab:
                    for b in vocab:
                        if b == base[repl]:
                            continue
                        words = base.copy()
                        words.insert(gap, a)
                        words[repl + (gap <= repl)] = b
                        yield words
    elif mode == "deletion":
        for i in range(n):
            deleted = base[:i] + base[i + 1:]
            for gap in range(n):
                for a in vocab:
                    words = deleted.copy()
                    words.insert(gap, a)
                    yield words
            for j in range(i + 1, n):
                yield base[:i] + base[i + 1:j] + base[j + 1:]
            for j in range(n - 1):
                for a in vocab:
                    if a != deleted[j]:
                        words = deleted.copy()
                        words[j] = a
                        yield words
    else:
        raise ValueError("Unknown edit family")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--note", type=int, choices=[2, 6, 13], required=True)
    p.add_argument("--mode", choices=["substitute", "insert-two", "insert-substitute", "deletion"], required=True)
    p.add_argument("--gap-start", type=int, default=0)
    p.add_argument("--gap-stop", type=int, default=100000)
    args = p.parse_args()
    checks = planted = original_hits = 0
    for words in candidates(sources[args.note], args.mode, args.gap_start, args.gap_stop):
        normalized = " ".join(words)
        digest = hashlib.sha256(component(normalized)).digest()
        checks += 1
        if digest == plant_sha:
            planted += 1
        if digest == target:
            original_hits += 1
            print("ORIGINAL_HIT", normalized, component(normalized).hex().upper(), flush=True)
    if args.note == 13 and args.mode == "substitute":
        assert planted == 1, planted
    print(json.dumps({"note": args.note, "mode": args.mode,
        "gap_start": args.gap_start, "gap_stop": args.gap_stop,
        "source_sha256": NOTES_SHA, "vocabulary": len(vocab),
        "complete_assignments": checks, "planted_positive_hits": planted,
        "original_k08_hits": original_hits}, indent=2))


if __name__ == "__main__":
    main()
