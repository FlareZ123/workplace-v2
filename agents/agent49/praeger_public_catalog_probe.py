"""Read-only public catalog/access check for the Praeger map-back-book hypothesis.

This probe retrieves bibliographic metadata only. It does not download book text,
page images, restricted material, or use credentials.
"""
from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

UA = "H17-public-book-catalog-probe/1.0 (+read-only metadata)"


def get_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urlopen(req, timeout=18) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        body = response.read(500_001)
        if len(body) > 500_000:
            raise RuntimeError("response exceeded 500 KB cap")
        return json.loads(body)


def archive_query(query: str) -> dict:
    params = {
        "q": query,
        "fl[]": ["identifier", "title", "creator", "year", "mediatype", "collection", "downloads"],
        "rows": 20,
        "page": 1,
        "output": "json",
    }
    # urlencode with doseq is required for the repeated fl[] fields.
    return get_json("https://archive.org/advancedsearch.php?" + urlencode(params, doseq=True))


def google_volume(volume_id: str) -> dict:
    fields = (
        "id,volumeInfo(title,authors,publishedDate,pageCount,industryIdentifiers),"
        "accessInfo(viewability,embeddable,publicDomain,accessViewStatus,webReaderLink,"
        "pdf(isAvailable),epub(isAvailable))"
    )
    return get_json(
        "https://www.googleapis.com/books/v1/volumes/"
        + volume_id + "?" + urlencode({"fields": fields})
    )


def main() -> None:
    print("PROBE", "Praeger / The Way That I Went", "metadata-only")
    for label, query in (
        ("title-and-author", 'title:"The Way That I Went" AND creator:Praeger AND mediatype:texts'),
        ("title-texts", 'title:"The Way That I Went" AND mediatype:texts'),
    ):
        try:
            result = archive_query(query)
            response = result.get("response") or {}
            docs = response.get("docs") or []
            print("ARCHIVE", label, "numFound", response.get("numFound"), "docs",
                  json.dumps(docs[:20], sort_keys=True))
        except Exception as exc:
            print("ARCHIVE_UNAVAILABLE", label, type(exc).__name__, str(exc)[:240])

    for label, volume_id in (
        ("1947-third-edition-candidate", "uT5RAQAAIAAJ"),
        ("1997-reprint-control", "Fo0iAQAAIAAJ"),
    ):
        try:
            result = google_volume(volume_id)
            print("GOOGLE_BOOKS", label, json.dumps({
                "id": result.get("id"),
                "volumeInfo": result.get("volumeInfo"),
                "accessInfo": result.get("accessInfo"),
            }, sort_keys=True))
        except Exception as exc:
            print("GOOGLE_BOOKS_UNAVAILABLE", label, type(exc).__name__, str(exc)[:240])

    print("PRAEGER_PUBLIC_CATALOG_PROBE_COMPLETE")


if __name__ == "__main__":
    main()
