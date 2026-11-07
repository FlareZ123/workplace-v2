"""Read-only public-scan access probe for the frozen Cowper K08 candidate.

Fetches only viewer/metadata endpoints and one representative image/page per
provider. It does not guess printed-page sequence offsets or create a phrase.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OUT = Path("cowper-probe")
OUT.mkdir(exist_ok=True)
MAX_BYTES = 5_000_000

ENDPOINTS = {
    "hathi_viewer_part1_seq7": (
        "https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p&seq=7&view=1up"
    ),
    "hathi_mets_metadata": (
        "https://babel.hathitrust.org/cgi/htd/volume?id=hvd.hn5w2p"
    ),
    "hathi_catalog_api": (
        "https://catalog.hathitrust.org/api/volumes/brief/json/id/hvd.hn5w2p"
    ),
    "hathi_image_part1_seq7": (
        "https://babel.hathitrust.org/cgi/imgsrv/image?id=hvd.hn5w2p;seq=7;width=900"
    ),
    "google_viewer_part2_p130": (
        "https://books.google.es/books?hl=en&id=o7P-qis2u9IC&pg=PA130"
    ),
    "google_books_api_part2": (
        "https://www.googleapis.com/books/v1/volumes/o7P-qis2u9IC"
    ),
    "google_image_part2_p130": (
        "https://books.google.com/books/content?id=o7P-qis2u9IC&pg=PA130&img=1&zoom=1&edge=curl&source=gbs_api"
    ),
}


def safe_filename(name: str, content_type: str) -> str:
    ext = ".bin"
    if "html" in content_type:
        ext = ".html"
    elif "json" in content_type:
        ext = ".json"
    elif "xml" in content_type:
        ext = ".xml"
    elif "image/jpeg" in content_type:
        ext = ".jpg"
    elif "image/png" in content_type:
        ext = ".png"
    elif "pdf" in content_type:
        ext = ".pdf"
    return name + ext


def extract_html_summary(data: bytes) -> dict[str, object]:
    text = data.decode("utf-8", "replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    tokens = ("seq", "pageLabel", "pageNum", "pageNumber", "page-number", "currentPage")
    excerpts: dict[str, str] = {}
    for token in tokens:
        at = text.find(token)
        if at >= 0:
            excerpts[token] = html.unescape(text[max(0, at - 180):at + 420])
    return {
        "title": html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else None,
        "html_length": len(data),
        "page_metadata_excerpts": excerpts,
    }


def main() -> int:
    results: dict[str, object] = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; H17-Archive-Preservation/1.0)",
        "Accept": "text/html,application/json,application/xml,image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }
    for name, url in ENDPOINTS.items():
        print(f"PROBE_START name={name} url={url}")
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=30) as response:
                content_type = response.headers.get("Content-Type", "")
                body = response.read(MAX_BYTES + 1)
                truncated = len(body) > MAX_BYTES
                if truncated:
                    body = body[:MAX_BYTES]
                filename = safe_filename(name, content_type)
                (OUT / filename).write_bytes(body)
                record: dict[str, object] = {
                    "status": response.status,
                    "final_url": response.geturl(),
                    "content_type": content_type,
                    "bytes_saved": len(body),
                    "truncated": truncated,
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "artifact_file": filename,
                }
                if "html" in content_type:
                    record.update(extract_html_summary(body))
                elif "json" in content_type:
                    try:
                        parsed = json.loads(body.decode("utf-8"))
                        if name == "google_books_api_part2":
                            info = parsed.get("volumeInfo", {})
                            record["volume_info"] = {
                                "title": info.get("title"),
                                "authors": info.get("authors"),
                                "publishedDate": info.get("publishedDate"),
                                "pageCount": info.get("pageCount"),
                                "industryIdentifiers": info.get("industryIdentifiers"),
                            }
                        else:
                            record["json_top_keys"] = list(parsed)[:20] if isinstance(parsed, dict) else None
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        record["json_parse"] = "failed"
                results[name] = record
                print("PROBE_RESULT " + json.dumps({"name": name, **record}, sort_keys=True))
        except HTTPError as exc:
            record = {"status": exc.code, "error": str(exc), "url": url}
            results[name] = record
            print("PROBE_RESULT " + json.dumps({"name": name, **record}, sort_keys=True))
        except (URLError, TimeoutError, OSError) as exc:
            record = {"error": f"{type(exc).__name__}: {exc}", "url": url}
            results[name] = record
            print("PROBE_RESULT " + json.dumps({"name": name, **record}, sort_keys=True))
    summary = OUT / "summary.json"
    summary.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    successes = sum(1 for item in results.values() if isinstance(item, dict) and "status" in item and 200 <= int(item["status"]) < 300)
    print(f"PROBE_COMPLETE endpoints={len(results)} http_successes={successes} artifact_dir={OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
