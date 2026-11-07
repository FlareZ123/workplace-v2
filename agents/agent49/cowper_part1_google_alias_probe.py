"""Bounded probe for a Google Books mirror/alias of Cowper Sailing Tours Part I."""
from __future__ import annotations

import base64
import hashlib
import json
import re
import struct
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINTS = {
    "google_com_hathi_id": "https://books.google.com/books?id=hvd.hn5w2p",
    "google_es_hathi_id": "https://books.google.es/books?id=hvd.hn5w2p",
    "google_com_hathi_image_p94": "https://books.google.com/books/content?id=hvd.hn5w2p&pg=PA94&img=1&zoom=2",
    "google_es_hathi_image_p94": "https://books.google.es/books/content?id=hvd.hn5w2p&pg=PA94&img=1&zoom=2",
    "google_oclc_p94": "https://books.google.com/books?vid=OCLC7504145&pg=PA94&output=html_text",
}

for name, url in ENDPOINTS.items():
    print(f"PROBE_START name={name} url={url}")
    request = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; H17-Archive-Preservation/1.0)",
        "Accept": "text/html,image/*,*/*;q=0.8",
    })
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read(5_000_001)
            content_type = response.headers.get("Content-Type", "")
            record = {
                "name": name,
                "status": response.status,
                "final_url": response.geturl(),
                "content_type": content_type,
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
            }
            if "html" in content_type:
                text = body.decode("utf-8", "replace")
                title = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
                record["title"] = re.sub(r"\\s+", " ", title.group(1)).strip() if title else None
                record["contains_cowper"] = "Cowper" in text
                record["contains_coasts_essex"] = "Coasts of Essex" in text
            if content_type.startswith("image/png") and len(body) >= 24:
                record["dimensions"] = struct.unpack(">II", body[16:24])
                print("IMAGE_BASE64 " + base64.b64encode(body).decode("ascii"))
            print("PROBE_RESULT " + json.dumps(record, sort_keys=True))
    except HTTPError as exc:
        print("PROBE_RESULT " + json.dumps({"name": name, "status": exc.code, "error": str(exc)}))
    except (URLError, TimeoutError, OSError) as exc:
        print("PROBE_RESULT " + json.dumps({"name": name, "error": f"{type(exc).__name__}: {exc}"}))
