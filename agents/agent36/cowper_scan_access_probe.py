"""Read-only retrieval of exact Cowper scan pages for the frozen K08 test.

Use target=part1-search to resolve an accessible Google Books Part I ID and
verify HathiTrust catalog metadata. Use target=pNNN to fetch one exact Part II
page image. No word extraction or candidate construction occurs here.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import struct
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OUT = Path("cowper-probe")
OUT.mkdir(exist_ok=True)
MAX_BYTES = 5_000_000
PART2_ID = "o7P-qis2u9IC"
PART2_PAGES = {130, 151, 121, 135, 142}


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current_href: str | None = None
        self.current_text: list[str] = []
        self.anchors: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            self.current_href = dict(attrs).get("href")
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self.current_href is not None:
            text = re.sub(r"\s+", " ", " ".join(self.current_text)).strip()
            self.anchors.append((text, self.current_href))
            self.current_href = None
            self.current_text = []


def fetch(name: str, url: str) -> tuple[bytes | None, dict[str, object]]:
    print(f"PROBE_START name={name} url={url}")
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; H17-Archive-Preservation/1.0)",
            "Accept": "text/html,application/json,application/xml,image/*,*/*;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "")
            body = response.read(MAX_BYTES + 1)
            truncated = len(body) > MAX_BYTES
            if truncated:
                body = body[:MAX_BYTES]
            record: dict[str, object] = {
                "status": response.status,
                "final_url": response.geturl(),
                "content_type": content_type,
                "bytes_saved": len(body),
                "truncated": truncated,
                "sha256": hashlib.sha256(body).hexdigest(),
            }
            if "html" in content_type:
                text = body.decode("utf-8", "replace")
                title = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
                record["title"] = html.unescape(re.sub(r"\s+", " ", title.group(1)).strip()) if title else None
                parser = AnchorParser()
                parser.feed(text)
                record["book_links"] = [
                    {"text": label, "href": href}
                    for label, href in parser.anchors
                    if ("books?id=" in href or "/books?" in href)
                    and (re.search(r"cowper|sailing|coasts|part", label, re.I) or "id=" in href)
                ][:50]
                record["has_part1_terms"] = {
                    term: bool(re.search(term, text, re.I))
                    for term in ("Coasts of Essex", "Part I", "Cowper")
                }
            if "json" in content_type:
                try:
                    parsed = json.loads(body.decode("utf-8"))
                    info = parsed.get("volumeInfo", {}) if isinstance(parsed, dict) else {}
                    record["volume_info"] = {
                        "title": info.get("title"),
                        "authors": info.get("authors"),
                        "publishedDate": info.get("publishedDate"),
                        "pageCount": info.get("pageCount"),
                    }
                    record["top_keys"] = list(parsed)[:20] if isinstance(parsed, dict) else None
                    if name.startswith("hathi_catalog_api") and isinstance(parsed, dict):
                        record["hathi_records"] = parsed.get("records")
                        record["hathi_items"] = parsed.get("items")
                except (UnicodeDecodeError, json.JSONDecodeError):
                    record["json_parse"] = "failed"
            if content_type.startswith("image/png") and len(body) >= 24:
                record["png_dimensions"] = struct.unpack(">II", body[16:24])
            filename = name + (
                ".html" if "html" in content_type else
                ".json" if "json" in content_type else
                ".png" if "image/png" in content_type else
                ".jpg" if "image/jpeg" in content_type else ".bin"
            )
            (OUT / filename).write_bytes(body)
            record["artifact_file"] = filename
            print("PROBE_RESULT " + json.dumps({"name": name, **record}, sort_keys=True))
            return body, record
    except HTTPError as exc:
        record = {"status": exc.code, "error": str(exc), "url": url}
    except (URLError, TimeoutError, OSError) as exc:
        record = {"error": f"{type(exc).__name__}: {exc}", "url": url}
    print("PROBE_RESULT " + json.dumps({"name": name, **record}, sort_keys=True))
    return None, record


def hathi_browser_access() -> dict[str, object]:
    from http.cookiejar import CookieJar
    from urllib.request import HTTPCookieProcessor, build_opener

    cookie_jar = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie_jar))
    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    endpoints = [
        ("hathi_catalog_record", "https://catalog.hathitrust.org/Record/100485750", None),
        ("hathi_viewer_ampersand", "https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p&seq=7&view=1up", "https://catalog.hathitrust.org/Record/100485750"),
        ("hathi_viewer_semicolon", "https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p;seq=7;view=1up", "https://catalog.hathitrust.org/Record/100485750"),
        ("hathi_viewer_http", "http://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p&seq=7&view=1up", "https://catalog.hathitrust.org/Record/100485750"),
        ("hathi_image_browser_headers", "https://babel.hathitrust.org/cgi/imgsrv/image?id=hvd.hn5w2p;seq=7;width=900", "https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p&seq=7&view=1up"),
    ]
    results: dict[str, object] = {}
    for name, url, referer in endpoints:
        print(f"HATHI_BROWSER_START name={name} url={url}")
        headers = dict(base_headers)
        if referer:
            headers["Referer"] = referer
        try:
            with opener.open(Request(url, headers=headers), timeout=30) as response:
                content_type = response.headers.get("Content-Type", "")
                body = response.read(MAX_BYTES + 1)
                truncated = len(body) > MAX_BYTES
                if truncated:
                    body = body[:MAX_BYTES]
                ext = ".html" if "html" in content_type else ".png" if "image/png" in content_type else ".jpg" if "image/jpeg" in content_type else ".bin"
                filename = name + ext
                (OUT / filename).write_bytes(body)
                record: dict[str, object] = {
                    "status": response.status,
                    "final_url": response.geturl(),
                    "content_type": content_type,
                    "bytes_saved": len(body),
                    "truncated": truncated,
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "artifact_file": filename,
                    "cookie_count": len(cookie_jar),
                }
                if "html" in content_type:
                    title = re.search(r"<title[^>]*>(.*?)</title>", body.decode("utf-8", "replace"), re.I | re.S)
                    record["title"] = html.unescape(re.sub(r"\\s+", " ", title.group(1)).strip()) if title else None
                if content_type.startswith("image/"):
                    print(f"HATHI_IMAGE_BASE64 name={name} data={base64.b64encode(body).decode('ascii')}")
                results[name] = record
                print("HATHI_BROWSER_RESULT " + json.dumps({"name": name, **record}, sort_keys=True))
        except HTTPError as exc:
            record = {"status": exc.code, "error": str(exc), "url": url, "cookie_count": len(cookie_jar)}
            results[name] = record
            print("HATHI_BROWSER_RESULT " + json.dumps({"name": name, **record}, sort_keys=True))
        except (URLError, TimeoutError, OSError) as exc:
            record = {"error": f"{type(exc).__name__}: {exc}", "url": url, "cookie_count": len(cookie_jar)}
            results[name] = record
            print("HATHI_BROWSER_RESULT " + json.dumps({"name": name, **record}, sort_keys=True))
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    target = parser.parse_args().target
    results: dict[str, object] = {}

    if target == "hathi-access":
        results = hathi_browser_access()
    elif target == "part1-search":
        endpoints = {
            "hathi_catalog_api_brief": "https://catalog.hathitrust.org/api/volumes/brief/htid/hvd.hn5w2p.json",
            "hathi_catalog_api_full": "https://catalog.hathitrust.org/api/volumes/full/htid/hvd.hn5w2p.json",
            "hathi_handle": "https://hdl.handle.net/2027/hvd.hn5w2p",
            "google_search_part1_es": "https://books.google.es/books?q=%22The+Coasts+of+Essex+and+Suffolk%22+%22Frank+Cowper%22",
            "google_search_part1_com": "https://books.google.com/books?q=Frank+Cowper+Sailing+Tours+Part+1",
            "google_vid_oclc_7504145": "https://books.google.com/books?vid=OCLC7504145",
            "google_vid_oclc_894082875": "https://books.google.com/books?vid=OCLC894082875",
            "google_viewer_part2": f"https://books.google.es/books?hl=en&id={PART2_ID}&pg=PA130",
            "google_part2_about": f"https://books.google.es/books?id={PART2_ID}&source=gbs_navlinks_s",
            "google_part2_plaintext_p130": f"https://books.google.es/books?pg=PA130&id={PART2_ID}&output=text",
        }
        for name, url in endpoints.items():
            _, results[name] = fetch(name, url)
    elif target.startswith("p") and target[1:].isdigit() and int(target[1:]) in PART2_PAGES:
        page = int(target[1:])
        url = (
            f"https://books.google.com/books/content?id={PART2_ID}"
            f"&pg=PA{page}&img=1&zoom=2&edge=curl&source=gbs_api"
        )
        body, record = fetch(f"google_part2_page_{page}", url)
        results[f"google_part2_page_{page}"] = record
        if body is not None and str(record.get("content_type", "")).startswith("image/"):
            encoded = base64.b64encode(body).decode("ascii")
            print(f"IMAGE_BASE64 page={page} data={encoded}")
    else:
        raise SystemExit(f"Unsupported target: {target}")

    (OUT / "summary.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"PROBE_COMPLETE target={target} endpoints={len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
