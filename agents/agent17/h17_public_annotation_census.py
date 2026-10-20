"""Read public original-site HTML annotation surfaces omitted by prior visible-text crawls.

The 2025 BX25/08 original names this exact public host. This test GETs only
public same-origin linked HTML, never /admin, /api/, a login, or guessed paths.
It tests a new carrier class: HTML comments, JSON-LD script blocks, and
accessibility/data-caption attributes. Existing visible text is not re-scanned.
"""
from __future__ import annotations

import hashlib
import re
from collections import deque
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlsplit
from urllib.request import Request, urlopen

BASE = "https://noyes-energy-group.pages.dev"
SITE = urlsplit(BASE)
TARGET = re.compile(
    r"IR[- ]?261003|PS[- ]?261003|H[- ]?17|ESC[- ]?N|"
    r"Emily|keeper|coupon|spool|WN[- ]?14|L[- ]?29",
    re.IGNORECASE,
)


class Annotations(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.carriers: list[tuple[str, str]] = []
        self.script: list[str] | None = None

    def handle_comment(self, text: str) -> None:
        self.carriers.append(("html-comment", text))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self.links.append(d["href"])
        if tag == "script" and d.get("type", "").lower() in (
            "application/ld+json", "application/json"
        ):
            self.script = []
        for key, value in attrs:
            if value is not None and (
                key.startswith("data-") or key in ("aria-label", "title", "aria-description")
            ):
                self.carriers.append((f"attribute:{tag}:{key}", value))

    def handle_data(self, text: str) -> None:
        if self.script is not None:
            self.script.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.script is not None:
            self.carriers.append(("embedded-json", "".join(self.script)))
            self.script = None


def local_positive_control() -> None:
    html = """<a href='/company/'>Company</a>
    <!-- Incident IR-261003-H17 original annotation -->
    <script type='application/ld+json'>{"name":"Emily, keeper"}</script>
    <img data-caption="Coupon PS-261003-0417" />"""
    parser = Annotations()
    parser.feed(html)
    assert parser.links == ["/company/"]
    assert len(parser.carriers) == 3
    assert all(TARGET.search(value) for _, value in parser.carriers)
    print("SYNTHETIC_COMMENT_JSON_ATTRIBUTE_CONTROL PASS", flush=True)


def allowed(href: str) -> str | None:
    full, _fragment = urldefrag(urljoin(BASE + "/", href))
    parsed = urlsplit(full)
    if (parsed.scheme, parsed.netloc) != (SITE.scheme, SITE.netloc):
        return None
    path = parsed.path or "/"
    if path.startswith(("/admin", "/api/")) or parsed.query:
        return None
    return path


def read_public(path: str) -> bytes | None:
    url = urljoin(BASE, path)
    try:
        with urlopen(
            Request(url, headers={"User-Agent": "H17-readonly-public-original/1.0"}),
            timeout=18,
        ) as response:
            raw = response.read(1_000_001)
            mime = response.headers.get("Content-Type", "")
            final = urlsplit(response.url)
            if (final.scheme, final.netloc) != (SITE.scheme, SITE.netloc):
                print("EXTERNAL_REDIRECT_SKIP", path, flush=True)
                return None
            if len(raw) > 1_000_000 or "html" not in mime:
                print("MIME_OR_SIZE_SKIP", path, mime, len(raw), flush=True)
                return None
    except (HTTPError, URLError) as error:
        print("GET_FAIL", path, type(error).__name__, str(error)[:150], flush=True)
        return None
    print("SOURCE", path, len(raw), hashlib.sha256(raw).hexdigest(), flush=True)
    return raw


def main() -> None:
    local_positive_control()
    queue = deque(["/"])
    seen: set[str] = set()
    total = 0
    matches = 0
    while queue and len(seen) < 24:
        path = queue.popleft()
        if path in seen:
            continue
        seen.add(path)
        raw = read_public(path)
        if raw is None:
            continue
        doc = Annotations()
        doc.feed(raw.decode("utf-8", errors="replace"))
        total += len(doc.carriers)
        print("ANNOTATION_COUNT", path, len(doc.carriers), flush=True)
        for kind, value in doc.carriers:
            if TARGET.search(value):
                matches += 1
                print(
                    "ORIGINAL_TARGET_MARKER", path, kind,
                    hashlib.sha256(value.encode()).hexdigest(),
                    repr(value[:2000]), flush=True,
                )
        for href in doc.links:
            linked = allowed(href)
            if linked is not None and linked not in seen and linked not in queue:
                queue.append(linked)
    print("FINISHED", "paths", len(seen), "annotations", total,
          "target_markers", matches, flush=True)
    print("NOTE: Markers alone require independent dating/provenance verification.",
          flush=True)


if __name__ == "__main__":
    main()
