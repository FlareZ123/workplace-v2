"""Publicly indexed historical copies of the exact original BX25/08 correspondence host.

Independent of Internet Archive, urlscan and Common Crawl. Public archival
index metadata only; no company-site requests, credentials or bypasses.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

HOST = "https://noyes-energy-group.pages.dev/"
QUERIES = {
    "arquivo-url-history": "https://arquivo.pt/textsearch?" + urllib.parse.urlencode({
        "versionHistory": HOST, "maxItems": "30", "prettyPrint": "false"
    }),
    "arquivo-cdx-root": "https://arquivo.pt/wayback/cdx?" + urllib.parse.urlencode({
        "url": HOST, "output": "json"
    }),
}


def run():
    for name, url in QUERIES.items():
        request = urllib.request.Request(url, headers={"User-Agent": "H17HistoricalRecords/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=24) as response:
                body = response.read(90000)
                status = response.status
        except urllib.error.HTTPError as error:
            print(json.dumps({"query": name, "status": error.code, "hits": "unknown"}))
            continue
        except (urllib.error.URLError, TimeoutError) as error:
            print(json.dumps({"query": name, "error": str(error)[:180]}))
            continue
        decoded = body.decode("utf-8", errors="replace")
        if name == "arquivo-url-history":
            obj = json.loads(decoded)
            data = obj.get("response_items", [])
            entries = [{"url": x.get("originalURL"), "at": x.get("date"),
                        "archive": x.get("linkToArchive")} for x in data[:30]]
        else:
            lines = [x for x in decoded.splitlines() if x.strip()]
            entries = []
            for line in lines[:30]:
                obj = json.loads(line)
                entries.append({"url": obj.get("url"), "at": obj.get("timestamp")})
        print(json.dumps({"query": name, "status": status, "hits": len(entries),
                          "items": entries, "truncated": len(body) == 90000}, sort_keys=True))


if __name__ == "__main__":
    run()
