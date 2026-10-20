"""Check existing 2025–26 Wayback captures for the source-cited public folio host.

Read-only and bounded: two published Internet Archive APIs, 150 capture
metadata rows maximum, no direct company website navigation or sign-in.
"""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

HOST = "noyes-energy-group.pages.dev"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, url):
        return None


def public_url(value: str) -> bool:
    p = urlparse(value)
    return p.scheme in {"http", "https"} and p.hostname == HOST and (
        p.username is None and p.password is None and p.port is None
    ) and not p.path.lower().startswith(("/admin", "/api"))


def fetch_index(url: str):
    assert urlparse(url).hostname in {"archive.org", "web.archive.org"}
    try:
        with build_opener(NoRedirect).open(
            Request(url, headers={"User-Agent": "H17-public-historic-index/1.0"}), timeout=16
        ) as response:
            body = response.read(400001)
            if len(body) > 400000:
                raise ValueError("Index body exceeded 400KB cap")
            print("PUBLIC_INDEX_HTTP", response.status, "BYTES", len(body))
            return json.loads(body)
    except (HTTPError, URLError, ValueError, json.JSONDecodeError) as exc:
        print("PUBLIC_INDEX_UNAVAILABLE", type(exc).__name__, str(exc)[:200])
        return None


def records(rows):
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], list):
        return []
    header = rows[0]
    if "original" not in header or "timestamp" not in header:
        return []
    indices = {col: i for i, col in enumerate(header)}
    found = []
    for row in rows[1:]:
        if not isinstance(row, list) or len(row) != len(header):
            continue
        url = str(row[indices["original"]])
        ts = str(row[indices["timestamp"]])
        if public_url(url) and len(ts) == 14 and ts.isdigit():
            found.append({"original": url, "timestamp": ts,
                          "mimetype": row[indices["mimetype"]] if "mimetype" in indices else "",
                          "digest": row[indices["digest"]] if "digest" in indices else ""})
    return found


def main() -> None:
    sample = [["original", "timestamp"], [f"https://{HOST}/about", "20261003000100"],
              [f"https://{HOST}/admin", "20261003000101"]]
    assert [r["original"] for r in records(sample)] == [f"https://{HOST}/about"]
    print("PASS synthetic public-only capture selector")

    params = urlencode({"url": HOST + "/*", "output": "json",
                        "filter": "statuscode:200", "collapse": "urlkey",
                        "from": "2025", "to": "2026", "limit": "150"})
    data = fetch_index("https://web.archive.org/cdx/search/cdx?" + params)
    found = records(data)
    print("CAPTURE_COUNT", len(found) if data is not None else "UNOBSERVED_INDEX_UNAVAILABLE")
    for item in found:
        print("PUBLIC_CAPTURE", json.dumps(item, sort_keys=True))

    available = fetch_index("https://archive.org/wayback/available?" +
                            urlencode({"url": "https://" + HOST + "/"}))
    if isinstance(available, dict):
        latest = (available.get("archived_snapshots") or {}).get("closest") or {}
        if latest:
            print("NEAREST_CAPTURE_TIMESTAMP", latest.get("timestamp"),
                  "STATUS", latest.get("status"))
    print("H17_WAYBACK_INDEX_CHECK_COMPLETE")


if __name__ == "__main__":
    main()
