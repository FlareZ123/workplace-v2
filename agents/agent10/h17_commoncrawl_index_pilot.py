"""Bounded read-only Common Crawl public index lookup for source-cited H-17 host.

This reads Common Crawl index metadata only. It never visits the corporate host,
authenticates, or requests protected /admin or /api paths.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

HOST = "noyes-energy-group.pages.dev"
INDEXES = ("CC-MAIN-2026-43", "CC-MAIN-2026-39", "CC-MAIN-2025-43")


def run():
    for index in INDEXES:
        query = urllib.parse.urlencode({"url": HOST + "/*", "output": "json"})
        url = f"https://index.commoncrawl.org/{index}-index?{query}"
        request = urllib.request.Request(url, headers={"User-Agent": "H17HistoricalRecords/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                raw = response.read(150000)
                status = response.status
        except urllib.error.HTTPError as error:
            print(json.dumps({"index": index, "status": error.code, "public_captures": 0}))
            continue
        except (urllib.error.URLError, TimeoutError) as error:
            print(json.dumps({"index": index, "error": str(error)[:200]}))
            continue
        rows = []
        for line in raw.splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            path = urllib.parse.urlparse(obj.get("url", "")).path
            if path.startswith(("/admin", "/api")):
                continue
            rows.append({"url": obj.get("url"), "timestamp": obj.get("timestamp"),
                         "status": obj.get("status"), "mime": obj.get("mime")})
        print(json.dumps({"index": index, "status": status, "public_captures": len(rows),
                          "truncated": len(raw) == 150000, "results": rows[:30]}, sort_keys=True))


if __name__ == "__main__":
    run()
