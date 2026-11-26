#!/usr/bin/env python3
"""Fetch public-domain OCR text for a narrowly targeted K08 source check.

Only corpus metadata is logged. No candidate phrase, recovery component, nonce,
or acceptance digest is emitted.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "irish-poetry-1915.txt"
IDENTIFIERS = ("bookofirishpoetr01grav", "cu31924013512482")
UA = "H17-archive-research/1.0 (public-domain text retrieval)"


def get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    last = None
    for n in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            last = exc
            if n < 2:
                time.sleep((2, 5)[n])
    raise RuntimeError(f"metadata retrieval failed: {last}")


def download(url: str, path: pathlib.Path) -> bool:
    cmd = [
        "curl", "--fail", "--location", "--silent", "--show-error",
        "--http1.1", "--retry", "2", "--retry-all-errors",
        "--connect-timeout", "30", "--max-time", "180",
        "-A", UA, "-o", str(path), url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and path.exists() and path.stat().st_size >= 50_000:
        return True
    if path.exists():
        path.unlink()
    print(json.dumps({
        "url_host": url.split("/", 3)[2],
        "curl_returncode": result.returncode,
        "stderr_tail": result.stderr[-300:],
    }, sort_keys=True))
    return False


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    chosen = None
    for identifier in IDENTIFIERS:
        meta = get_json(f"https://archive.org/metadata/{identifier}")
        files = [
            f for f in meta.get("files", [])
            if f.get("name", "").endswith("_djvu.txt") and not f.get("private")
        ]
        if not files:
            continue
        files.sort(key=lambda f: (
            not f["name"].startswith(identifier),
            int(f.get("size", 0) or 0),
        ))
        chosen = (identifier, files[0]["name"], meta)
        break
    if chosen is None:
        raise RuntimeError("No public DjVu OCR text file found in the candidate IA records")

    identifier, filename, meta = chosen
    directory = meta.get("dir", "")
    hosts = [meta.get("d1"), meta.get("server"), "archive.org"]
    urls = []
    for host in hosts:
        if host:
            urls.extend([
                f"https://{host}{directory}/{filename}",
                f"http://{host}{directory}/{filename}",
            ])
    urls.append(f"https://archive.org/download/{identifier}/{filename}")

    success = False
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp) / "corpus.txt"
        for url in urls:
            if download(url, tmp_path):
                data = tmp_path.read_bytes()
                OUT.write_bytes(data)
                success = True
                break
    if not success:
        raise RuntimeError(
            f"Unable to download public OCR file from IA mirrors; "
            f"identifier={identifier}, filename={filename}, "
            f"d1={meta.get('d1')}, server={meta.get('server')}, dir={directory}"
        )

    text = OUT.read_text(encoding="utf-8", errors="replace")
    words = len(text.split())
    if words < 5_000:
        raise RuntimeError(f"OCR word count unexpectedly small: {words}")
    data = OUT.read_bytes()
    print(json.dumps({
        "identifier": identifier,
        "filename": filename,
        "bytes": len(data),
        "words": words,
        "sha256": hashlib.sha256(data).hexdigest(),
        "output": str(OUT.relative_to(ROOT)),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
