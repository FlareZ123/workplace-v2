"""H-17 K08: exactly one/two extra-word irreducible source supersequences.

Default: independent DP census of the frozen source domain. --scan repeats
all HMAC/SHA256 candidate checks (Python is slower than the executed C++ run).
Read-only. Uses only the original resources and Python standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import itertools
import json
import re
from functools import cache
from pathlib import Path

NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
PLANTED = "9df012e755f08320c21eda41d5d323075097c3437c1ce42ae5ce021575ab3869"
MAX_WORDS = 17


def words(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9]+", text.lower()))


def source(path: Path, sha: str) -> bytes:
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == sha, path
    return data


def notes(raw: bytes) -> dict[int, tuple[str, ...]]:
    found: dict[int, tuple[str, ...]] = {}
    for m in re.finditer(rb"(?ms)^N(\d\d) /[^\n]*\n(.*?)(?=\n\nN\d\d /|\Z)", raw):
        number = int(m[1])
        body = m[2].decode().strip()
        if number in (1, 9):
            body = body.split(":", 1)[1]
        found[number] = words(body)
    assert set(found) == set(range(1, 25))
    return found


def spans(src: tuple[str, ...], motif: tuple[str, ...], lo: int, hi: int) -> list[tuple[str, ...]]:
    return sorted({src[i:j] for i in range(len(src)) for j in range(i + lo, min(len(src), i + hi) + 1)
                   if any(src[t:t + len(motif)] == motif for t in range(i, j - len(motif) + 1))})


def next_words(a: tuple[str, ...], b: tuple[str, ...], c: tuple[str, ...],
               i: int, j: int, k: int) -> list[str]:
    return sorted({seq[pos] for seq, pos in ((a, i), (b, j), (c, k)) if pos < len(seq)})


def adv(a: tuple[str, ...], b: tuple[str, ...], c: tuple[str, ...],
        i: int, j: int, k: int, word: str) -> tuple[int, int, int]:
    return (i + int(i < len(a) and a[i] == word),
            j + int(j < len(b) and b[j] == word),
            k + int(k < len(c) and c[k] == word))


def reduce_phrase(nonce: bytes, phrase: str) -> str:
    mac = hmac.digest(nonce, phrase.encode(), "sha256")
    return hashlib.sha256(mac[:16]).hexdigest()


def family(a: tuple[str, ...], b: tuple[str, ...], c: tuple[str, ...],
           scan: bool, nonce: bytes, totals: list[int], hits: list[str], positive: list[int]) -> None:
    length = (len(a), len(b), len(c))

    @cache
    def count(i: int, j: int, k: int) -> tuple[int, ...]:
        if (i, j, k) == length:
            return (1,) + (0,) * MAX_WORDS
        out = [0] * (MAX_WORDS + 1)
        for word in next_words(a, b, c, i, j, k):
            counts = count(*adv(a, b, c, i, j, k, word))
            for t in range(MAX_WORDS):
                out[t + 1] += counts[t]
        return tuple(out)

    counts = count(0, 0, 0)
    minimum = next((i for i, n in enumerate(counts) if n), None)
    if minimum is None:
        return
    for extra in (1, 2):
        if minimum + extra <= MAX_WORDS:
            totals[extra] += counts[minimum + extra]

    if not scan:
        return

    @cache
    def shortest(i: int, j: int, k: int) -> int:
        if (i, j, k) == length:
            return 0
        return 1 + min(shortest(*adv(a, b, c, i, j, k, w))
                       for w in next_words(a, b, c, i, j, k))

    def walk(i: int, j: int, k: int, left: int, prefix: tuple[str, ...]) -> None:
        if shortest(i, j, k) > left or left > sum(length) - i - j - k:
            return
        if left == 0:
            if (i, j, k) == length:
                phrase = " ".join(prefix)
                digest = reduce_phrase(nonce, phrase)
                if digest == PLANTED:
                    positive[0] += 1
                if digest == TARGET:
                    hits.append(phrase)
            return
        for w in next_words(a, b, c, i, j, k):
            walk(*adv(a, b, c, i, j, k, w), left - 1, prefix + (w,))

    for extra in (1, 2):
        if minimum + extra <= MAX_WORDS:
            walk(0, 0, 0, minimum + extra, ())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--resources", type=Path, default=Path(__file__).resolve().parents[2] / "resources")
    p.add_argument("--scan", action="store_true")
    args = p.parse_args()
    root = args.resources
    n = notes(source(root / "evidence/crew/noticeboard-and-desk-notes.txt", NOTES_SHA))
    route = json.loads(source(root / "evidence/recovery-routing.json", ROUTE_SHA))
    acc = json.loads(source(root / "acceptance.json", ACCEPT_SHA))
    assert acc["slot_sha256"]["K08"] == TARGET
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    assert hmac.digest(nonce, b"a good watch leaves the room ready for the next pair of hands", "sha256")[:16].hex() == "bf889359b0303f2b2b2fd96ae841210b"
    planted = "and at sea looks the end of the night voices at the table"
    assert reduce_phrase(nonce, planted) == PLANTED
    groups = (spans(n[1], ("sea",), 2, 6),
              spans(n[13], ("end", "of", "the", "night"), 4, 8),
              spans(n[20], ("voices", "at", "the", "table"), 4, 8))
    assert tuple(map(len, groups)) == (10, 12, 15)
    totals = [0, 0, 0]
    hits: list[str] = []
    positive = [0]
    for a, b, c in itertools.product(*groups):
        family(a, b, c, args.scan, nonce, totals, hits, positive)
    assert totals == [0, 369357248, 167294491], totals
    if args.scan:
        assert positive[0] >= 1
    print(json.dumps({"source_span_counts": [10, 12, 15],
                      "full_assignment_count_plus1": totals[1],
                      "full_assignment_count_plus2": totals[2],
                      "acceptance_hits": hits if args.scan else "not checked in census",
                      "planted_positive": positive[0] if args.scan else "not checked in census"}, indent=2))


if __name__ == "__main__":
    main()
