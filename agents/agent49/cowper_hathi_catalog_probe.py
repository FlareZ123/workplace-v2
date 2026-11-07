"""Read-only retrieval of the public HathiTrust catalog record for Cowper Part I."""
from __future__ import annotations

import hashlib
import json
from urllib.request import Request, urlopen

URL = "https://catalog.hathitrust.org/api/volumes/brief/htid/hvd.hn5w2p.json"

request = Request(URL, headers={"User-Agent": "H17-records-research/1.0"})
with urlopen(request, timeout=30) as response:
    raw = response.read()
    status = response.status
    content_type = response.headers.get("Content-Type", "")

print(f"HTTP_STATUS={status}")
print(f"CONTENT_TYPE={content_type}")
print(f"BYTES={len(raw)}")
print(f"SHA256={hashlib.sha256(raw).hexdigest()}")
print("BEGIN_JSON")
print(json.dumps(json.loads(raw.decode("utf-8")), ensure_ascii=False, indent=2))
print("END_JSON")
