"""H17 K08 source-conditioned literary quotation hypothesis, read-only SFT.

The MAIL-09 map-bearing book is unidentified. This program tests only the
speculative candidate Treasure Island, Project Gutenberg ebook 120, as
a literal contiguous 5..16-token quotation. No prose synthesis or
source-hidden author-final claim is made.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import time
import urllib.request

PUBLIC_TEXT = "https://www.gutenberg.org/cache/epub/120/pg120.txt"
DESK_NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
K08_SHA256 = bytes.fromhex(
    "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
)
FIRST_LENGTH = 5
LAST_LENGTH = 16


def normalize(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(cleaned.split())


def component(phrase: str) -> bytes:
    return hmac.digest(DESK_NONCE, phrase.encode("utf-8"), "sha256")[:16]


def scan(words: list[str], expected: bytes, first: int, last: int) -> tuple[int, list[str]]:
    tested = 0
    hits = []
    for length in range(first, last + 1):
        for offset in range(len(words) - length + 1):
            phrase = " ".join(words[offset:offset + length])
            digest = hashlib.sha256(component(phrase)).digest()
            tested += 1
            if digest == expected:
                hits.append(phrase)
    return tested, hits


def strip_gutenberg_envelope(raw_text: str) -> str:
    start = re.search(r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK[^\n]*\n", raw_text)
    end = re.search(r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK", raw_text)
    if start is None or end is None or start.end() >= end.start():
        raise ValueError("Unexpected Gutenberg source boundaries")
    return raw_text[start.end():end.start()]


def main() -> None:
    assert component(
        "A good watch leaves the room ready for the next pair of hands."
    ).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    synthetic = normalize("Outside! The sea outside the room and the table inside. Home")
    planted = "the sea outside the room and the table inside"
    checked, synthetic_hits = scan(
        synthetic.split(), hashlib.sha256(component(planted)).digest(), 5, 16
    )
    assert checked > 0 and planted in synthetic_hits
    print("controls: original N02 component PASS; independent whole-phrase synthetic PASS", flush=True)

    request = urllib.request.Request(
        PUBLIC_TEXT,
        headers={"User-Agent": "H17-records-research/1.0 (public-domain text audit)"},
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        raw = response.read()
    raw_hash = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8-sig")
    words = normalize(strip_gutenberg_envelope(text)).split()
    assert len(words) > 40000, "Downloaded source unexpectedly short"
    t0 = time.perf_counter()
    count, hits = scan(words, K08_SHA256, FIRST_LENGTH, LAST_LENGTH)
    elapsed = time.perf_counter() - t0
    print(
        f"source={PUBLIC_TEXT} raw_sha256={raw_hash} "
        f"tokens={len(words)} lengths={FIRST_LENGTH}..{LAST_LENGTH} "
        f"complete_candidate_assignments={count} "
        f"original_K08_hits={len(hits)} seconds={elapsed:.3f}",
        flush=True,
    )
    for hit in hits:
        print("K08 MATCH normalized_phrase=" + repr(hit))
        print("K08 component=" + component(hit).hex().upper())


if __name__ == "__main__":
    main()
