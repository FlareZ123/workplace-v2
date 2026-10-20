"""Bounded public sitemap check for the BX25/08 original correspondence host.

Anonymous read-only requests for robots.txt and explicitly named sitemap.xml only.
No route guessing, login attempts, portal/API requests, or external redirects.
"""

from __future__ import annotations

import hashlib
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

HOST = "noyes-energy-group.pages.dev"
ROOT = f"https://{HOST}"
PATTERN = re.compile(r"H[- ]?17|261003|ESC[- ]?N|BX25|coupon|keeper|preserv|record|correspond", re.I)


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


def get(url: str) -> bytes | None:
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
                print("OVERSIZE", url, len(data), flush=True)
                return None
            print("GET", response.status, url, len(data), hashlib.sha256(data).hexdigest(), flush=True)
            return data
    except HTTPError as exc:
        print("HTTP_STATUS", exc.code, url, flush=True)
    except URLError as exc:
        print("NETWORK_ERROR", url, str(exc.reason), flush=True)
    return None


def main() -> None:
    robots = get(ROOT + "/robots.txt")
    indexes = [ROOT + "/sitemap.xml"]
    if robots:
        for line in robots.decode("utf-8", "replace").splitlines():
            if line.lower().startswith("sitemap:"):
                index = line.partition(":")[2].strip()
                if allowed(index):
                    indexes.append(index)
    found = set()
    for index in dict.fromkeys(indexes[:3]):
        raw = get(index)
        if not raw:
            continue
        try:
            xml = ElementTree.fromstring(raw)
        except ElementTree.ParseError:
            print("NOT_XML", index, flush=True)
            continue
        for element in xml.iter():
            if element.tag.rsplit("}", 1)[-1] != "loc" or not element.text:
                continue
            url = element.text.strip()
            if allowed(url):
                found.add(url)
                print("PUBLIC_INDEX_LOC", url, bool(PATTERN.search(url)), flush=True)
    print("TOTAL_PUBLIC_INDEX_LOC", len(found), flush=True)
    print("H17_PUBLIC_SITEMAP_CHECK_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
