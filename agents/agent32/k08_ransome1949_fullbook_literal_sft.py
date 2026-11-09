"""Read-only K08 exact literal source test, Faded Page 20180428 HTML.

Process a privately fetched text in memory, reporting only SHA/counts/hits.
Do not write or republish the source text.
"""

import hashlib
import hmac
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

URL = "https://www.fadedpage.com/books/20180428/html.php"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
N02_REFERENCE = "BF889359B0303F2B2B2FD96AE841210B"
MAX_WORDS = 28


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignore = 0
        self.words = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "svg"}:
            self.ignore += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg"}:
            self.ignore -= 1

    def handle_data(self, data):
        if not self.ignore:
            self.words.extend(re.findall(r"[a-z0-9]+", data.lower()))


def main():
    repo = Path(__file__).resolve().parents[2]
    base = repo / "resources"
    pinned = {
        base / "evidence/crew/noticeboard-and-desk-notes.txt": NOTES_SHA,
        base / "evidence/recovery-routing.json": ROUTE_SHA,
        base / "acceptance.json": ACCEPTANCE_SHA,
    }
    for path, digest in pinned.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path
    route = json.loads((base / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((base / "acceptance.json").read_text())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])

    def reduce(phrase):
        return hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]

    ref = "a good watch leaves the room ready for the next pair of hands"
    assert reduce(ref).hex().upper() == N02_REFERENCE
    assert hashlib.sha256(reduce(ref)).digest() != target

    request = Request(URL, headers={"User-Agent": "H17-historical-readonly-source-check/1.0"})
    with urlopen(request, timeout=40) as response:
        assert response.status == 200
        source = response.read()
    source_sha = hashlib.sha256(source).hexdigest()
    text = TextExtractor()
    text.feed(source.decode("utf-8"))
    words = text.words
    assert 50000 <= len(words) <= 200000, f"Unexpected full-text length: {len(words)}"

    checks = 0
    hits = []
    for start in range(len(words)):
        end = min(len(words), start + MAX_WORDS)
        phrase = ""
        for stop in range(start, end):
            phrase = phrase + (" " if phrase else "") + words[stop]
            component = reduce(phrase)
            if hashlib.sha256(component).digest() == target:
                hits.append((start, stop + 1, phrase, component.hex().upper()))
            checks += 1
    print(json.dumps({
        "source_url": URL, "source_sha256": source_sha,
        "word_count": len(words), "max_span_words": MAX_WORDS,
        "complete_phrases_checked": checks, "original_k08_hits": len(hits),
        "hits": hits,
        "historical_n02_hmac_fixture": "PASS",
    }, separators=(",", ":")))
    if hits:
        sys.exit(2)


if __name__ == "__main__":
    main()
