"""Read-only October 2026 Common Crawl public-host metadata triage.

Queries only the archived public correspondence hostname's CDX index.
No authentication, corporate portal, live site, or WARC fetching.
"""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

ARCHIVE = "CC-MAIN-2026-43"
BASE = f"https://index.commoncrawl.org/{ARCHIVE}-index"
HOST = "noyes-energy-group.pages.dev"
query = urlencode({"url": f"{HOST}/*", "output": "json"})
req = Request(f"{BASE}?{query}", headers={"User-Agent": "H17-offline-records-public-index/1.0"})
print("QUERY", ARCHIVE, HOST, "2026-10-05..2026-10-18 UTC", flush=True)
try:
    with urlopen(req, timeout=20) as response:
        status = response.status
        body = response.read(1500000)
except HTTPError as error:
    print("HTTP", error.code, "MESSAGE", error.read(160).decode("utf-8", "replace"))
    print("NO_HISTORICAL_SOURCE_ACQUIRED; 404 means no captures returned, 5xx is inconclusive")
except (URLError, TimeoutError) as error:
    print("TRANSPORT_UNKNOWN", str(error)[:300])
    print("NO_HISTORICAL_SOURCE_ACQUIRED")
else:
    print("HTTP", status, "BODY_BYTES", len(body))
    count = 0
    public = 0
    for ln in body.splitlines():
        count += 1
        item = json.loads(ln)
        u = item.get("url", "")
        parsed = urlsplit(u)
        if parsed.netloc.lower() != HOST or any(parsed.path.lower().startswith(p) for p in ("/admin", "/api")):
            continue
        public += 1
        print("PUBLIC_CAPTURE", item.get("timestamp"), item.get("status"), item.get("mime"), u)
    print("CAPTURES_RETURNED", count, "PUBLIC_ELIGIBLE", public)
    print("CAPTURE_METADATA_IS_NOT_ACTUAL_SOURCE_CONTENT")
