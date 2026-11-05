"""H-17 folio-linked public historical archive lookup, Arquivo.pt (no login).

Queries an independently maintained archival metadata API, not the company
site. It never requests authenticated or restricted corporate endpoints.
"""
import json
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

HOST = "noyes-energy-group.pages.dev"
QUERIES = (
    {"versionHistory": f"https://{HOST}/", "maxItems": 50},
    {"versionHistory": HOST, "maxItems": 50},
    {"q": '"Noyes Energy Group" "H-17"', "maxItems": 30},
)


def permitted(url: str) -> bool:
    parts = urlsplit(url)
    path = parts.path.lower()
    return parts.hostname == HOST and not any(
        path == p or path.startswith(p + "/") for p in ("/admin", "/api")
    )


def main() -> None:
    assert permitted("https://" + HOST + "/projects/")
    assert not permitted("https://" + HOST + "/admin")
    assert not permitted("https://" + HOST + "/api/login")
    print("PUBLIC ARCHIVE METADATA ONLY; NO CORPORATE SITE AUTHENTICATION OR API REQUESTS")
    for query in QUERIES:
        url = "https://arquivo.pt/textsearch?" + urlencode(query)
        request = Request(url, headers={
            "User-Agent": "H17-records-preservation-public-archive/1.0"
        })
        try:
            with urlopen(request, timeout=35) as response:
                data = json.loads(response.read(750000))
            rows = data.get("response_items", [])
            matches = [
                row for row in rows
                if permitted(row.get("originalURL", ""))
            ]
            print("PUBLIC_ARCHIVE_QUERY", json.dumps(query, sort_keys=True),
                  "estimated", data.get("estimated_nr_results"),
                  "returned", len(rows), "permitted", len(matches))
            for row in matches[:35]:
                print("ARCHIVED_PUBLIC_PAGE", json.dumps({
                    "url": row.get("originalURL"),
                    "timestamp": row.get("tstamp"),
                    "digest": row.get("digest"),
                    "mime": row.get("mimeType"),
                    "archive": row.get("linkToArchive"),
                }, sort_keys=True))
        except (HTTPError, URLError, TimeoutError, ValueError) as e:
            print("QUERY_UNAVAILABLE", json.dumps(query),
                  type(e).__name__, str(e)[:150])
    print("PUBLIC_ARCHIVE_LOOKUP_COMPLETE")


if __name__ == "__main__":
    main()
