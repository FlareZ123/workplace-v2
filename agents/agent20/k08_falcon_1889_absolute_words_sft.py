"""Test WN-14 signed K01 as absolute word offsets into a full Falcon transcription.

This is a restricted, exploratory complete-candidate construction. It does
not claim that David's map-back book was Falcon or that any website text is a
source-authenticated physical copy. Source acquisition is tested separately
from exact H-17 K08 acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

SOURCE_URL = "https://soul-trade.com/sailing/falcon/falcon_frames.htm"
# Freeze after source-only acquisition and source-text inspection.
SOURCE_SHA256 = None
K01_HEX = "049AAB2E1CDE7A82CD7C60234303C91A"
NONCE_HEX = "5F933DA6A1BD03C32DA5CBC25344F497"
K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
N02_EXPECTED = "BF889359B0303F2B2B2FD96AE841210B"
N02_PHRASE = "a good watch leaves the room ready for the next pair of hands"


class PlainText(HTMLParser):
    """Extract visible paragraph and heading text, omitting script/style."""
    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self.skip_depth += 1
        if tag in ("p", "div", "h1", "h2", "h3", "h4", "br"):
            self.blocks.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self.skip_depth -= 1
        if tag in ("p", "div", "h1", "h2", "h3", "h4"):
            self.blocks.append(" ")

    def handle_data(self, data: str) -> None:
        if self.skip_depth == 0:
            self.blocks.append(data)


def hmac_component(phrase: str) -> bytes:
    raw = hmac.digest(bytes.fromhex(NONCE_HEX), phrase.encode("utf-8"), "sha256")
    return raw[:16]


def load_source() -> tuple[bytes, list[str]]:
    req = Request(SOURCE_URL, headers={"User-Agent": "H17-local-history-research/1.0"})
    with urlopen(req, timeout=30) as handle:
        raw = handle.read()
    parser = PlainText()
    parser.feed(raw.decode("utf-8"))
    text = " ".join(parser.blocks)
    match_start = re.search(r"\bIN\s+the\s+summer\s+of\s+['’]86", text)
    match_end = re.search(r"October\s+2nd,\s+1888\.", text)
    assert match_start and match_end and match_end.end() > match_start.start()
    book_text = text[match_start.start():match_end.end()]
    assert re.search(r"CHAPTER\s+XV\s+COPENHAGEN\s+AND\s+HOME", book_text, re.I)
    assert "Falcon" in book_text and "Kronborg" in book_text
    words = re.findall(r"[a-z0-9]+", book_text.lower())
    assert len(words) > 56861, len(words)
    return raw, words


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acquire-only", action="store_true")
    args = parser.parse_args()
    raw, words = load_source()
    source_hash = hashlib.sha256(raw).hexdigest()
    word_hash = hashlib.sha256(" ".join(words).encode("ascii")).hexdigest()
    meta = {
        "url": SOURCE_URL,
        "raw_bytes": len(raw),
        "source_sha256": source_hash,
        "word_count": len(words),
        "word_stream_sha256": word_hash,
        "first_20": words[:20],
        "last_20": words[-20:],
    }
    print("SOURCE", json.dumps(meta, sort_keys=True))
    if args.acquire_only:
        print("SOURCE_ONLY_NO_TARGET_CHECK")
        return
    assert SOURCE_SHA256 and source_hash == SOURCE_SHA256, "Original source digest changed"
    assert hmac_component(N02_PHRASE).hex().upper() == N02_EXPECTED
    signed = bytes.fromhex(K01_HEX)
    checks = 0
    for byte_order in ("big", "little"):
        offsets = [int.from_bytes(signed[i:i + 2], byte_order) for i in range(0, 16, 2)]
        for base in (0, 1):
            positions = [x - base for x in offsets]
            assert min(positions) >= 0 and max(positions) < len(words)
            phrase = " ".join(words[x] for x in positions)
            component = hmac_component(phrase)
            digest = hashlib.sha256(component).hexdigest()
            check = digest == K08_SHA256
            checks += 1
            print("CANDIDATE", json.dumps({
                "byte_order": byte_order, "index_base": base,
                "positions": positions, "phrase": phrase,
                "component": component.hex().upper(),
                "slot_sha256": digest, "accepted": check,
            }, sort_keys=True))
            if check:
                print("ORIGINAL_K08_PASS", component.hex().upper())
    assert checks == 4
    print("COMPLETE", json.dumps({
        "complete_candidates": checks,
        "source_sha256": source_hash,
        "original_commitment": K08_SHA256,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
