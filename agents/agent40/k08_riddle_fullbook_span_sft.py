#!/usr/bin/env python3
"""K08 exact-span scan of the map-back book candidate, The Riddle of the Sands.

The script emits no book quotation. A hit is recorded only by source token
position, normalized-text SHA-256, and the resulting K08 component bytes.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://www.gutenberg.org/cache/epub/2360/pg2360.txt"
MIN_WORDS = 5  # 1-4 word sequences have already had a separate exhaustive gate.
MAX_WORDS = 60


def normalize_words(text: str) -> list[str]:
    # REC8/1 K08 normalization: lowercase, retain ASCII a-z and digits,
    # replace other characters with separators, and collapse whitespace.
    return re.findall(r"[a-z0-9]+", text.lower(), flags=re.ASCII)


def main() -> int:
    if len(sys.argv) not in (3, 4):
        raise SystemExit(
            "usage: k08_riddle_fullbook_span_sft.py ROUTING_JSON ACCEPTANCE_JSON [OUTPUT_JSON]"
        )

    routing = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    acceptance = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    key = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "H17-archive-research/1.0 (K08 exact-span source test)"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        raw_text = response.read().decode("utf-8", errors="replace")
    source_sha = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
    if start_marker in raw_text:
        raw_text = raw_text.split(start_marker, 1)[1]
    if end_marker in raw_text:
        raw_text = raw_text.split(end_marker, 1)[0]

    words = normalize_words(raw_text)
    if len(words) < 50_000:
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
        "hypothesis": "K08 is a verbatim contiguous span in The Riddle of the Sands",
        "source_url": SOURCE_URL,
        "source_text_sha256": source_sha,
        "normalized_word_count": len(words),
        "min_span_words": MIN_WORDS,
        "max_span_words": max_len,
        "windows_tested": windows,
        "acceptance_sha256": target,
        "matches": matches,
        "limitation": "A no-hit rejects only this exact-span/book hypothesis; it does not reject other wording or other source texts.",
    }
    out = Path(sys.argv[3]) if len(sys.argv) == 4 else Path("k08-riddle-fullbook-span-result.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "matches"}, indent=2))
    print(f"matches={len(matches)} result_file={out}")
    if matches:
        print(json.dumps(matches, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
