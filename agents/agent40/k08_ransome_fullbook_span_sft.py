#!/usr/bin/env python3
"""Source-specific K08 exact-span test for the identified map-back book candidate.

The script deliberately emits no book quotation. A hit is recorded only as
its source position, normalized-text SHA-256, and the K08 component bytes.
"""
from __future__ import annotations

import hashlib
import hmac
import html.parser
import json
import re
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://www.fadedpage.com/books/20180428/html.php"
MIN_WORDS = 5  # 1-4 word sequences have already had a separate exhaustive gate.
MAX_WORDS = 60


class VisibleText(html.parser.HTMLParser):
    SKIP = {"script", "style", "head", "title", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in self.SKIP:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.SKIP and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)


def normalize_words(text: str) -> list[str]:
    # Equivalent to REC8/1 K08 normalization.
    return re.findall(r"[a-z0-9]+", text.lower(), flags=re.ASCII)


def main() -> int:
    if len(sys.argv) not in (3, 4):
        raise SystemExit(
            "usage: k08_ransome_fullbook_span_sft.py ROUTING_JSON ACCEPTANCE_JSON [OUTPUT_JSON]"
        )

    routing = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    acceptance = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    key = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; H17-archive-research/1.0)"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        raw_html = response.read()
    raw_sha = hashlib.sha256(raw_html).hexdigest()

    parser = VisibleText()
    parser.feed(raw_html.decode("utf-8", errors="replace"))
    words = normalize_words(" ".join(parser.parts))
    if len(words) < 10_000:
        raise SystemExit(f"refusing undersized/non-book response: {len(words)} normalized words")

    windows = 0
    matches = []
    max_len = min(MAX_WORDS, len(words))
    for start in range(len(words)):
        stop = min(max_len, len(words) - start)
        for length in range(MIN_WORDS, stop + 1):
            phrase = " ".join(words[start : start + length])
            component = hmac.new(key, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
            windows += 1
            if hashlib.sha256(component).hexdigest() == target:
                matches.append({
                    "start_token": start,
                    "end_token_exclusive": start + length,
                    "word_count": length,
                    "normalized_phrase_sha256": hashlib.sha256(phrase.encode("utf-8")).hexdigest(),
                    "component_hex": component.hex().upper(),
                    "component_sha256": hashlib.sha256(component).hexdigest(),
                })

    result = {
        "hypothesis": "K08 is a verbatim contiguous span in the map-back book candidate",
        "source_url": SOURCE_URL,
        "source_html_sha256": raw_sha,
        "normalized_word_count": len(words),
        "min_span_words": MIN_WORDS,
        "max_span_words": max_len,
        "windows_tested": windows,
        "acceptance_sha256": target,
        "matches": matches,
        "limitation": "A no-hit rejects only this exact-span/book hypothesis; it does not reject other wording or other books.",
    }
    out = Path(sys.argv[3]) if len(sys.argv) == 4 else Path("k08-ransome-fullbook-span-result.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "matches"}, indent=2))
    print(f"matches={len(matches)} result_file={out}")
    if matches:
        print(json.dumps(matches, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
