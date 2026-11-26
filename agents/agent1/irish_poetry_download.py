#!/usr/bin/env python3
"""Fetch public-domain OCR and page-structure assets for a targeted K08 check.

Only metadata is logged. No candidate phrase, recovery component, nonce,
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
WORK = ROOT / "work"
OUT = WORK / "irish-poetry-1915.txt"
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


def download(url: str, path: pathlib.Path, minimum: int = 50_000) -> bool:
    cmd = [
        "curl", "--fail", "--location", "--silent", "--show-error",
        "--http1.1", "--retry", "2", "--retry-all-errors",
        "--connect-timeout", "30", "--max-time", "180",
        "-A", UA, "-o", str(path), url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and path.exists() and path.stat().st_size >= minimum:
        return True
    if path.exists():
        path.unlink()
    print(json.dumps({
        "url_host": url.split("/", 3)[2],
        "curl_returncode": result.returncode,
        "stderr_tail": result.stderr[-300:],
    }, sort_keys=True))
    return False


def urls_for(meta: dict, identifier: str, filename: str) -> list[str]:
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
    return urls


def fetch_asset(meta: dict, identifier: str, filename: str, output: pathlib.Path,
                minimum: int = 50_000) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp) / "asset"
        for url in urls_for(meta, identifier, filename):
            if download(url, tmp_path, minimum):
                output.write_bytes(tmp_path.read_bytes())
                return True
    return False


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    chosen = None
    for identifier in IDENTIFIERS:
        meta = get_json(f"https://archive.org/metadata/{identifier}")
        files = [
            f for f in meta.get("files", [])
            if f.get("name", "").endswith("_djvu.txt") and not f.get("private")
        ]
        if files:
            files.sort(key=lambda f: (
                not f["name"].startswith(identifier),
                int(f.get("size", 0) or 0),
            ))
            chosen = (identifier, files[0]["name"], meta)
            break
    if chosen is None:
        raise RuntimeError("No public DjVu OCR text file found in candidate IA records")

    identifier, filename, meta = chosen
    if not fetch_asset(meta, identifier, filename, OUT):
        raise RuntimeError(f"Unable to download OCR text: {identifier}/{filename}")

    public_assets = [
        f for f in meta.get("files", [])
        if not f.get("private")
        and (
            f.get("name", "").endswith("_djvu.xml")
            or f.get("name", "").endswith("_text.pdf")
            or f.get("name", "").endswith(".pdf")
        )
    ]
    public_assets.sort(key=lambda f: (
        0 if f["name"].endswith("_djvu.xml") else
        1 if f["name"].endswith("_text.pdf") else 2,
        int(f.get("size", 0) or 0),
    ))
    (WORK / "irish-poetry-1915-files.json").write_text(json.dumps({
        "identifier": identifier,
        "d1": meta.get("d1"),
        "server": meta.get("server"),
        "dir": meta.get("dir"),
        "public_assets": [
            {"name": f["name"], "size": f.get("size")} for f in public_assets
        ],
    }, indent=2), encoding="utf-8")

    asset_saved = None
    for item in public_assets:
        suffix = ".xml" if item["name"].endswith("_djvu.xml") else ".pdf"
        output = WORK / ("irish-poetry-1915-pages" + suffix)
        if fetch_asset(meta, identifier, item["name"], output, minimum=100_000):
            asset_saved = {"name": item["name"], "bytes": output.stat().st_size,
                           "output": str(output.relative_to(ROOT))}
            break

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
        "page_asset": asset_saved,
        "public_asset_count": len(public_assets),
        "output": str(OUT.relative_to(ROOT)),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
