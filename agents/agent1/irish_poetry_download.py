#!/usr/bin/env python3
"""Fetch the public-domain OCR text for a narrowly targeted K08 literary-source check.

No candidate phrase, recovery component, nonce, or acceptance digest is emitted.
The fetched text is an Internet Archive public OCR derivative of the 1915 anthology.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "irish-poetry-1915.txt"
IDENTIFIERS = ("bookofirishpoetr01grav", "cu31924013512482")
UA = "H17-archive-research/1.0 (public-domain text retrieval)"


def get(url: str, attempts: int = 3) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json,text/plain,*/*",
        },
    )
    last = None
    for n in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status} for {url}")
                return response.read()
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            last = exc
            if n + 1 < attempts:
                time.sleep((2, 5)[n])
    raise RuntimeError(f"retrieval failed for {url}: {last}")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    chosen = None
    for identifier in IDENTIFIERS:
        meta = json.loads(get(f"https://archive.org/metadata/{identifier}"))
        files = meta.get("files", [])
        candidates = [
            f for f in files
            if f.get("name", "").endswith("_djvu.txt")
            and not f.get("private")
        ]
        if candidates:
            # Prefer the identifier's canonical OCR file, then the smallest public candidate.
            candidates.sort(key=lambda f: (not f["name"].startswith(identifier), int(f.get("size", 0) or 0)))
            chosen = (identifier, candidates[0]["name"])
            break
    if chosen is None:
        raise RuntimeError("No public DjVu OCR text file found in the candidate IA records")

    identifier, filename = chosen
    url = f"https://archive.org/download/{identifier}/{filename}"
    data = get(url)
    if len(data) < 50_000:
        raise RuntimeError(f"OCR text unexpectedly small: {len(data)} bytes")
    text = data.decode("utf-8", errors="replace")
    if len(text.split()) < 5_000:
        raise RuntimeError(f"OCR word count unexpectedly small: {len(text.split())}")
    OUT.write_text(text, encoding="utf-8")
    print(json.dumps({
        "identifier": identifier,
        "filename": filename,
        "bytes": len(data),
        "words": len(text.split()),
        "sha256": hashlib.sha256(data).hexdigest(),
        "output": str(OUT.relative_to(ROOT)),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
