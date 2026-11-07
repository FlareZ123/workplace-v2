"""K08 read-only source probe: Alfred Noyes literature, a speculative name-link carrier.

The original corpus is fetched only at execution; no copied book content is
committed. The model tests complete literal poem lines, adjacent printed lines,
and prose sentences. It does not imply that Emily used a literary quotation.
"""
from __future__ import annotations

import hashlib
import hmac
import html
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
NOTE_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
BOOK_IDS = (30501, 30599, 43186)


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower(), flags=re.ASCII))


def reduce_caption(text: str) -> bytes:
    return hmac.new(NONCE, normalize(text).encode("utf-8"), hashlib.sha256).digest()[:16]


def accepted(text: str) -> bool:
    return hashlib.sha256(reduce_caption(text)).hexdigest() == TARGET


class TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.ignored = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("style", "script"):
            self.ignored += 1
        if tag in ("p", "div", "h1", "h2", "h3", "br", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("style", "script"):
            self.ignored -= 1
        if tag in ("p", "div", "h1", "h2", "h3", "li"):
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.ignored:
            self.parts.append(data)


def fetch_book(book_id: int) -> tuple[str, str, str]:
    urls = [
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-8.txt",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}-images.html",
    ]
    for url in urls:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "H17-read-only-archival-source-probe"})
            with urllib.request.urlopen(request, timeout=25) as response:
                raw = response.read(7_000_001)
                is_html = "html" in response.headers.get_content_type()
            if len(raw) >= 7_000_001:
                raise ValueError("source exceeds 7MB cap")
            text = raw.decode("utf-8-sig", errors="replace")
            if is_html or "<html" in text[:500].lower():
                parser = TextHTMLParser()
                parser.feed(text)
                text = html.unescape("".join(parser.parts))
            if len(text) < 20000 or "Noyes" not in text[:16000]:
                raise ValueError("unexpected book text")
            return url, hashlib.sha256(raw).hexdigest(), text
        except (OSError, ValueError) as error:
            print("SOURCE_FAILURE", book_id, url, str(error)[:160], flush=True)
    raise RuntimeError(f"Unable to obtain authentic Gutenberg source for {book_id}")


def candidates(text: str):
    seen: set[str] = set()
    lines = text.splitlines()
    for i in range(len(lines)):
        for span in (1, 2, 3):
            chunk = lines[i:i + span]
            if len(chunk) != span or any(not part.strip() for part in chunk):
                continue
            phrase = normalize(" ".join(chunk))
            if 3 <= len(phrase.split()) <= 42 and phrase not in seen:
                seen.add(phrase)
                yield phrase, f"printed-line:{i + 1}/span:{span}"
    for i, sentence in enumerate(re.split(r"(?<=[.!?])\s+", text)):
        phrase = normalize(sentence)
        if 3 <= len(phrase.split()) <= 42 and phrase not in seen:
            seen.add(phrase)
            yield phrase, f"sentence:{i + 1}"


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    note = (root / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    acceptance = json.loads((root / "resources/acceptance.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(note).hexdigest() == NOTE_SHA256
    assert acceptance["slot_sha256"]["K08"] == TARGET
    n02 = "A good watch leaves the room ready for the next pair of hands."
    assert reduce_caption(n02).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    synthetic = "Mere keepers of the light"
    assert any(normalize(synthetic) == item for item, _ in candidates(synthetic + "\nThe sea beyond the windows"))
    print("PINNED_ORIGINAL_SOURCE=PASS N02_GENUINE_CONTROL=PASS SYNTHETIC_CARRIER=PASS", flush=True)

    total = 0
    all_hits: list[dict[str, str | int]] = []
    for book_id in BOOK_IDS:
        url, source_sha256, text = fetch_book(book_id)
        matches = []
        checked = 0
        for phrase, where in candidates(text):
            checked += 1
            if accepted(phrase):
                matches.append({"phrase": phrase, "locator": where})
                all_hits.append({"book": book_id, "phrase": phrase, "locator": where})
        total += checked
        print("SOURCE_RESULT", json.dumps({"book": book_id, "url": url,
              "source_sha256": source_sha256, "text_characters": len(text),
              "complete_phrases_checked": checked, "K08_hits": matches}), flush=True)
    print("FINAL_RESULT", json.dumps({"complete_phrases_checked": total,
          "exact_original_K08_matches": all_hits, "status": "HIT" if all_hits else "NO_HIT"}), flush=True)


if __name__ == "__main__":
    main()
