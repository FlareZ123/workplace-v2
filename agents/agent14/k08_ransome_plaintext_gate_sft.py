#!/usr/bin/env python3
"""K08 edition-identified Ransome plain-text source gate, with no book quotations.

The historical author-final H17 phrase is not known to quote Ransome. This
bounded experiment tests only verbatim contiguous normalized spans of one
particular source candidate. No source text is retained in public output.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

SOURCE_URL = "https://www.fadedpage.com/link.php?file=20180428.txt"
SOURCE_EDITION = "Arthur Ransome, We Didn't Mean to Go to Sea, FadedPage 20180428 (Jonathan Cape, 1937)"
MIN_WORDS = 5
MAX_WORDS = 60

def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower(), flags=re.ASCII)

def main(route_path: str, acceptance_path: str, output_path: str) -> None:
    route_bytes = Path(route_path).read_bytes()
    acceptance_bytes = Path(acceptance_path).read_bytes()
    assert hashlib.sha256(route_bytes).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
    assert hashlib.sha256(acceptance_bytes).hexdigest() == "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
    route = json.loads(route_bytes)
    acceptance = json.loads(acceptance_bytes)
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    goal = acceptance["slot_sha256"]["K08"]
    known = "a good watch leaves the room ready for the next pair of hands"
    assert hmac.new(key, known.encode(), hashlib.sha256).digest()[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    request = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0 (compatible; H17-source-gate/1.0)"})
    with urlopen(request, timeout=60) as response:
        raw = response.read()
        content_type = response.headers.get("Content-Type", "")
        fetched_url = response.url
    text = raw.decode("utf-8-sig", errors="replace")
    tokens = words(text)
    if len(raw) < 100000 or len(tokens) < 20000:
        raise SystemExit(
            f"INCOMPLETE_SOURCE bytes={len(raw)} words={len(tokens)} "
            f"content_type={content_type!r} final_url={fetched_url!r}; "
            "zero candidate comparisons executed"
        )
    if "<html" in text[:2000].lower() or "<!doctype" in text[:2000].lower():
        raise SystemExit("INCOMPLETE_SOURCE HTML response; zero candidate comparisons")
    phrase_buffer: list[str]
    found = []
    count = 0
    for start in range(len(tokens)):
        limit = min(MAX_WORDS, len(tokens) - start)
        if limit < MIN_WORDS:
            break
        phrase_buffer = tokens[start : start + MIN_WORDS - 1]
        for length in range(MIN_WORDS, limit + 1):
            phrase_buffer.append(tokens[start + length - 1])
            candidate = " ".join(phrase_buffer)
            result = hmac.new(key, candidate.encode("utf-8"), hashlib.sha256).digest()[:16]
            count += 1
            if hashlib.sha256(result).hexdigest() == goal:
                found.append({
                    "start_word": start,
                    "length_words": length,
                    "component_hex": result.hex().upper(),
                    "phrase_sha256": hashlib.sha256(candidate.encode("utf-8")).hexdigest()
                })
    payload = {
        "edition": SOURCE_EDITION,
        "source_url": SOURCE_URL,
        "fetched_url": fetched_url,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_bytes": len(raw),
        "source_words": len(tokens),
        "span_min": MIN_WORDS,
        "span_max": MAX_WORDS,
        "tested": count,
        "matches": found,
        "limitation": "Unverified source attribution; one exact-edition contiguous-span gate only."
    }
    Path(output_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: script.py ROUTING_JSON ACCEPTANCE_JSON OUTPUT_JSON")
    main(*sys.argv[1:])
