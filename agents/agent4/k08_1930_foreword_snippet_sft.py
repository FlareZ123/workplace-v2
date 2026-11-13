"""Original H-17 K08 checks against exact 1930 Tomlinson foreword OCR search excerpts.

Public Google Books SearchWithinVolume2 snippets, source-filtered to foreword pages.
The experiment neither downloads complete book text nor changes original files.
"""
import hashlib
import hmac
import html
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

VOLUMES = {
    "hHYYAAAAYAAJ": ("PA", 7, 19),   # Duckworth 1930: foreword pages
    "4L8XAAAAIAAJ": ("PR", 6, 17),   # Harper 1930: foreword pages
}
QUERIES = ("foreword", "sea", "night", "table", "voices", "watch")
SNIPPET = re.compile(r'"page_id":"([^"]+)","page_number":"(?:\\.|[^"\\])*","snippet_text":"((?:\\.|[^"\\])*)"')


def fetch_snippets(volume: str, query: str) -> list[tuple[str, str]]:
    arguments = urllib.parse.urlencode({"jscmd": "SearchWithinVolume2", "q": query, "vid": volume})
    request = urllib.request.Request(
        "https://books.google.com/books?" + arguments,
        headers={"User-Agent": "Mozilla/5.0 (compatible; historical-records-source-test/1.0)"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        page = response.read(200_000).decode("utf-8", errors="replace")
        print("FETCH", volume, query, response.status, len(page))
    matches = []
    for match in SNIPPET.finditer(page):
        page_id = match.group(1)
        snippet = json.loads('"' + match.group(2) + '"')
        matches.append((page_id, snippet))
    return matches


def strings_from_excerpt(text: str):
    for segment in re.split(r"\\.{2,}|…+", html.unescape(re.sub(r"<[^>]*>", " ", html.unescape(text)))):
        words = re.findall(r"[a-z0-9]+", segment.lower())
        for start in range(len(words)):
            for end in range(start + 1, min(start + 33, len(words) + 1)):
                yield " ".join(words[start:end])


def main():
    repo = Path(__file__).resolve().parents[2]
    notes = (repo / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(notes).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
    route = json.loads((repo / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((repo / "resources/acceptance.json").read_text(encoding="utf-8"))
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    n02 = "A good watch leaves the room ready for the next pair of hands"
    fixture = hmac.digest(key, n02.lower().encode("ascii"), "sha256")[:16].hex().upper()
    assert fixture == "BF889359B0303F2B2B2FD96AE841210B"

    tested = set()
    page_ids = set()
    original_matches = []
    synthetic_phrase = None
    synthetic_hits = 0
    failures = 0
    for volume, (prefix, first, last) in VOLUMES.items():
        for query in QUERIES:
            try:
                snippets = fetch_snippets(volume, query)
            except Exception as exc:
                print("FETCH_ERROR", volume, query, type(exc).__name__, str(exc)[:120])
                failures += 1
                continue
            retained = 0
            for page_id, snippet in snippets:
                if not page_id.startswith(prefix) or not page_id[len(prefix):].isdigit():
                    continue
                page_number = int(page_id[len(prefix):])
                if not (first <= page_number <= last):
                    continue
                retained += 1
                page_ids.add((volume, page_id))
                for phrase in strings_from_excerpt(snippet):
                    if synthetic_phrase is None and len(phrase.split()) >= 4:
                        synthetic_phrase = phrase
                    if phrase in tested:
                        continue
                    tested.add(phrase)
                    component = hmac.digest(key, phrase.encode("ascii"), "sha256")[:16]
                    digest = hashlib.sha256(component).hexdigest()
                    if digest == target:
                        original_matches.append((volume, page_id, query, phrase, component.hex().upper()))
                    if phrase == synthetic_phrase:
                        synthetic_hits += 1
            print("FOREWORD_PAGES", volume, query, retained)
    assert synthetic_phrase is not None, "No original 1930 foreword OCR available"
    assert synthetic_hits == 1
    print("SUMMARY", json.dumps({
        "queries": len(QUERIES) * len(VOLUMES),
        "failed_requests": failures,
        "distinct_foreword_pages": len(page_ids),
        "distinct_complete_normalized_candidates": len(tested),
        "synthetic_planted_source_phrase_hits": synthetic_hits,
        "original_k08_matches": original_matches,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
