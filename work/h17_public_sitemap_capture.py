"""Capture the bounded, anonymous public sitemap result as a short-lived CI artifact.

This deliberately repeats only the previously authorized robots.txt and explicitly
named sitemap.xml check. It does not guess routes, follow redirects, or fetch page
content. The report contains public URL inventory metadata only.
"""
from __future__ import annotations

import hashlib
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

HOST = "noyes-energy-group.pages.dev"
ROOT = f"https://{HOST}"
PATTERN = re.compile(r"H[- ]?17|261003|ESC[- ]?N|BX25|coupon|keeper|preserv|record|correspond", re.I)
REPORT = "h17-public-sitemap-report.json"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, url):
        return None


OPENER = build_opener(NoRedirect)


def allowed(url: str) -> bool:
    parsed = urlparse(url)
    return (
        parsed.scheme == "https"
        and parsed.hostname == HOST
        and parsed.username is None
        and parsed.password is None
        and parsed.port is None
        and not parsed.path.startswith(("/admin", "/api/", "/api"))
    )


def get(url: str) -> tuple[bytes | None, dict]:
    if not allowed(url):
        raise ValueError(f"Excluded non-public host/path: {url}")
    try:
        with OPENER.open(
            Request(url, headers={"User-Agent": "H17-public-sitemap-source-inventory/1.0"}),
            timeout=15,
        ) as response:
            actual = response.geturl()
            if not allowed(actual):
                raise ValueError(f"Unsafe response URL: {actual}")
            data = response.read(1_000_001)
            if len(data) > 1_000_000:
                return None, {"url": url, "status": response.status, "oversize": True, "size": len(data)}
            return data, {
                "url": url,
                "status": response.status,
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "content_type": response.headers.get("Content-Type"),
            }
    except HTTPError as exc:
        return None, {"url": url, "status": exc.code}
    except URLError as exc:
        return None, {"url": url, "error": str(exc.reason)[:200]}


def main() -> None:
    robots, robots_meta = get(ROOT + "/robots.txt")
    indexes = [ROOT + "/sitemap.xml"]
    if robots:
        for line in robots.decode("utf-8", "replace").splitlines():
            if line.lower().startswith("sitemap:"):
                candidate = line.partition(":")[2].strip()
                if allowed(candidate):
                    indexes.append(candidate)
    index_reports = []
    all_urls = set()
    for index in dict.fromkeys(indexes[:3]):
        raw, meta = get(index)
        report = {"fetch": meta, "urls": [], "parse_error": None}
        if raw:
            try:
                xml = ElementTree.fromstring(raw)
                for element in xml.iter():
                    if element.tag.rsplit("}", 1)[-1] == "loc" and element.text:
                        url = element.text.strip()
                        if allowed(url):
                            all_urls.add(url)
                            report["urls"].append({
                                "url": url,
                                "matches_h17_terms": bool(PATTERN.search(url)),
                            })
            except ElementTree.ParseError as exc:
                report["parse_error"] = str(exc)[:200]
        index_reports.append(report)
    result = {
        "host": HOST,
        "robots": robots_meta,
        "indexes": index_reports,
        "total_public_index_urls": len(all_urls),
        "matching_urls": sorted(url for url in all_urls if PATTERN.search(url)),
        "scope": "robots.txt and explicitly declared or /sitemap.xml only; no route guessing or page fetches",
    }
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print("PUBLIC_SITEMAP_CAPTURE", json.dumps({
        "robots": robots_meta,
        "total_public_index_urls": len(all_urls),
        "matching_urls": result["matching_urls"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
