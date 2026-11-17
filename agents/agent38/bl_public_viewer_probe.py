#!/usr/bin/env python3
"""Bounded public British Library viewer/OCR route probe for the Davies handbook candidate.

This deliberately tests only public catalogue/viewer endpoints and the alternate
OCR URL implied by the Flickr record's digitised-copy identifier. It does not
authenticate, enumerate protected services, or retry blocked hosts indefinitely.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

OUT = Path("probe-out")
OUT.mkdir(exist_ok=True)
UA = "H17-records-preservation-research/1.0 (public catalogue metadata probe)"
TARGETS = [
    ("bl_catalogue_digital", "https://explore.bl.uk/primo_library/libweb/action/search.do?cs=frb&ct=search&doc=BLL01014839753&dscnt=1&dum=true&fn=search&frbg=&indx=1&mode=Basic&scp.scps=scope%3A%28BLCONTENT%29&srt=rank&tab=local_tab&tb=t&vid=BLVU1&vl%28freeText0%29=014839753", 2_000_000),
    ("bl_public_viewer", "https://access.bl.uk/item/viewer/ark:/81055/vdc_000000003A2C", 3_000_000),
    ("bl_ocr_digital_id_candidate", "https://data.bl.uk/19cbooks/json/0148/014839753_01_text.json", 40_000_000),
]

def probe(name: str, url: str, limit: int) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            body = response.read(limit + 1)
            truncated = len(body) > limit
            if truncated:
                body = body[:limit]
            ctype = response.headers.get("Content-Type", "")
            record = {
                "name": name, "status": response.status,
                "requested_url": url, "final_url": response.geturl(),
                "content_type": ctype, "bytes": len(body), "truncated": truncated,
            }
            suffix = ".json" if "json" in ctype.lower() else ".html" if "html" in ctype.lower() else ".bin"
            path = OUT / f"{name}{suffix}"
            path.write_bytes(body)
            record["saved_as"] = str(path)
            if "json" in ctype.lower():
                try:
                    obj = json.loads(body.decode("utf-8-sig"))
                    record["json_top_keys"] = list(obj)[:40] if isinstance(obj, dict) else f"list[{len(obj)}]"
                    if isinstance(obj, dict):
                        record["json_counts"] = {
                            k: len(obj[k]) for k in ("pages", "canvases", "items", "images")
                            if isinstance(obj.get(k), list)
                        }
                except Exception as exc:
                    record["json_parse_error"] = repr(exc)
            else:
                sample = body.decode("utf-8", "replace")
                record["text_preview"] = sample[:1200]
                urls = re.findall(r"""(?:href|src|data-src)=[\"']([^\"']+)[\"']""", sample, re.I)
                record["interesting_links"] = [
                    x for x in urls if re.search(r"manifest|iiif|ocr|json|canvas|image|viewer", x, re.I)
                ][:80]
                record["interesting_tokens"] = [
                    x[:500] for x in re.findall(r"""[^\\"']{0,100}(?:manifest|iiif|ocr|canvas|014839753|vdc_000000003A2C)[^\\"']{0,180}""", sample, re.I)
                ][:40]
            return record
    except urllib.error.HTTPError as exc:
        return {"name": name, "requested_url": url, "status": exc.code, "error": f"HTTPError: {exc.reason}"}
    except Exception as exc:
        return {"name": name, "requested_url": url, "error": repr(exc)}

results = [probe(*target) for target in TARGETS]
(OUT / "report.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2))
# Success means the bounded probes executed and their outcomes were recorded;
# individual endpoint availability is represented explicitly in report.json.
sys.exit(0)
