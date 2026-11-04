"""Read-only Common Crawl CDX index inventory for the original 2025 BX25 PDF host.
Never fetches the live site, its /admin or /api endpoints, nor archives of them.
Only archived index metadata for public paths is listed. Windows compatible.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

HOST = "noyes-energy-group.pages.dev"
INDEXES = (
    "CC-MAIN-2026-43", "CC-MAIN-2026-39", "CC-MAIN-2026-34",
    "CC-MAIN-2026-30", "CC-MAIN-2026-25", "CC-MAIN-2026-21",
    "CC-MAIN-2025-51", "CC-MAIN-2025-47", "CC-MAIN-2025-43",
    "CC-MAIN-2025-38",
)
EXCLUDE = ("/api", "/admin")
MAX_READ = 2000000

def run():
    found = {}
    counted = 0
    for index in INDEXES:
        params = urllib.parse.urlencode({
            "url": f"{HOST}/*", "output": "json", "filter": "status:200",
        })
        url = f"https://index.commoncrawl.org/{index}-index?{params}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "H17ArchivedPublicIndexReadOnly/1.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=22) as resp:
                body = resp.read(MAX_READ + 1)
            assert len(body) <= MAX_READ, "unexpected large archived index"
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                print(f"{index} SOURCE_INDEX_NO_CAPTURES (HTTP404)")
                continue
            print(f"{index} INDEX_HTTP_ERROR status={exc.code}")
            continue
        except (TimeoutError, urllib.error.URLError) as exc:
            print(f"{index} NETWORK_ERROR {type(exc).__name__}: {exc}")
            continue
        rows = [json.loads(line) for line in body.splitlines() if line.strip()]
        public = []
        protected = 0
        for row in rows:
            u = urllib.parse.urlsplit(row["url"])
            if u.hostname != HOST:
                continue
            path = u.path or "/"
            if any(path == prefix or path.startswith(prefix + "/")
                   for prefix in EXCLUDE):
                protected += 1
                continue
            public.append(row)
        print(f"{index} total_returned={len(rows)} public={len(public)} protected_omitted={protected}")
        for row in public[:30]:
            link = row["url"]
            timestamp = row.get("timestamp", "?")
            mime = row.get("mime", "?")
            print(f" PUBLIC {index} at={timestamp} mime={mime} url={link}")
            found.setdefault(link, []).append((index, timestamp))
        if len(public) > 30:
            print(f" PUBLIC_SKIPPED_OUT_OF_OUTPUT {len(public)-30}")
        counted += len(rows)
    print(f"SUMMARY count_index_records={counted} unique_public_paths={len(found)}")
    if not found:
        print("NO_PUBLIC_HISTORICAL_SNAPSHOT_IN_THESE_INDEXES; other archives remain untested")
    print("ZERO protected portal/API requests; index metadata only")

if __name__ == "__main__":
    run()
