"""REC8 K08: test all literal 1..28-word spans of an identified public-domain book.

Only an original HMAC→16B→SHA256 commitment hit counts as a recovery.
The source text is a weak, independent book hypothesis; no historical
attribution to Emily's final margin is assumed.
"""
from __future__ import annotations

import hashlib
import hmac
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import time
from urllib.request import Request, urlopen

URL = "https://www.gutenberg.org/files/2360/2360-h/2360-h.htm"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
MAX_WORDS = 28


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.blocked: int = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.blocked += 1
        if tag in {"p", "h1", "h2", "h3", "h4", "li"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.blocked -= 1
        if tag in {"p", "h1", "h2", "h3", "h4", "li"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.blocked:
            self.parts.append(data)


def tokens_from_html(data: bytes) -> list[str]:
    parser = VisibleText()
    parser.feed(data.decode("utf-8-sig"))
    text = " ".join(parser.parts)
    normalized = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", normalized).split()


def component(phrase: str) -> bytes:
    return hmac.digest(NONCE, phrase.encode("utf-8"), "sha256")[:16]


def run(data: bytes, target: str = TARGET) -> tuple[int, str | None]:
    words = tokens_from_html(data)
    assert len(words) > 10000, len(words)
    print("SOURCE", URL, "sha256", hashlib.sha256(data).hexdigest(),
          "tokens", len(words), "max_words", MAX_WORDS, flush=True)
    checked = 0
    t0 = time.monotonic()
    for i, first in enumerate(words):
        caption = first
        for j in range(i, min(i + MAX_WORDS, len(words))):
            if j > i:
                caption += " " + words[j]
            candidate = component(caption)
            checked += 1
            if hashlib.sha256(candidate).hexdigest() == target:
                print("ORIGINAL K08 HIT", repr(caption), "component", candidate.hex().upper(), flush=True)
                return checked, caption
        if i and i % 30000 == 0:
            print("PROGRESS", i, "/", len(words), "attempts", checked,
                  "elapsed_seconds", round(time.monotonic() - t0, 2), flush=True)
    print("ORIGINAL hits=0 assignments=", checked,
          "elapsed_seconds=", round(time.monotonic() - t0, 2), flush=True)
    return checked, None


def main() -> None:
    phrase = "a good watch leaves the room ready for the next pair of hands"
    assert component(phrase).hex().upper() == N02_HMAC16
    print("N02_HMAC_POSITIVE PASS", flush=True)
    if len(sys.argv) == 2:
        data = Path(sys.argv[1]).read_bytes()
    else:
        req = Request(URL, headers={"User-Agent": "H17-archival-research/1.0"})
        with urlopen(req, timeout=60) as response:
            data = response.read()
    attempts, hit = run(data)
    if hit is not None:
        raise SystemExit(0)
    assert attempts > 10000


if __name__ == "__main__":
    main()
