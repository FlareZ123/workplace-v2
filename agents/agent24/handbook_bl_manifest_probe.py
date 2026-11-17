#!/usr/bin/env python3
"""Bounded public-source probe for the Davies Handbook BL scan.

This only retrieves metadata and a small set of candidate page images. It does
not search phrases or use the K08 acceptance digest as an oracle.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

OUT = Path("handbook-bl-probe")
OUT.mkdir(exist_ok=True)
UA = "H17-Davies-Handbook-BL-Probe/1.0"
MANIFESTS = [
    "https://api.bl.uk/metadata/iiif/ark:/81055/vdc_000000003A2C.0x000001/manifest.json",
    "https://api.bl.uk/metadata/iiif/ark:/81055/vdc_000000003A2C/manifest.json",
    "https://bl.digirati.io/iiif/ark:/81055/vdc_000000003A2C.0x000001/manifest.json",
    "https://bl.digirati.io/iiif/ark:/81055/vdc_000000003A2C.0x000001",
]
OCR = "https://data.bl.uk/19cbooks/json/0008/000875916_01_text.json"
# K01 candidate page numbers converted to zero-based canvas indexes.
K01_CANVASES = [3, 170, 27, 121, 204, 95, 66, 200]


def fetch(url: str, limit: int = 20_000_000) -> tuple[int, str, str, bytes]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json,application/ld+json,image/jpeg,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        body = response.read(limit + 1)
        if len(body) > limit:
            raise RuntimeError(f"response exceeded {limit} bytes: {url}")
        return response.status, response.headers.get("Content-Type", ""), response.geturl(), body


def label_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if "en" in value and isinstance(value["en"], list):
            return " ".join(map(str, value["en"]))
        if "@value" in value:
            return str(value["@value"])
        return json.dumps(value, ensure_ascii=False)
    return str(value or "")


def service_for(canvas: dict) -> tuple[str | None, int | None, int | None]:
    width, height = canvas.get("width"), canvas.get("height")
    # Presentation API 2
    images = canvas.get("images") or []
    if images:
        resource = images[0].get("resource") or {}
        width = width or resource.get("width")
        height = height or resource.get("height")
        services = resource.get("service") or []
        if isinstance(services, dict):
            services = [services]
        if services:
            return services[0].get("@id") or services[0].get("id"), width, height
        rid = resource.get("@id") or resource.get("id")
        if rid:
            return rid.rsplit("/", 1)[0], width, height
    # Presentation API 3
    items = canvas.get("items") or []
    for page in items:
        for annopage in page.get("items") or []:
            body = annopage.get("body") or {}
            if isinstance(body, list):
                body = body[0] if body else {}
            width = width or body.get("width")
            height = height or body.get("height")
            services = body.get("service") or []
            if isinstance(services, dict):
                services = [services]
            if services:
                return services[0].get("id") or services[0].get("@id"), width, height
            rid = body.get("id") or body.get("@id")
            if rid:
                return rid.rsplit("/", 1)[0], width, height
    return None, width, height


def main() -> int:
    report = {"manifest_attempts": [], "ocr": None, "canvas_count": None, "selected": []}
    manifest = None
    for url in MANIFESTS:
        print("MANIFEST", url, flush=True)
        try:
            status, ctype, final, body = fetch(url)
            print("HTTP", status, ctype, final, "bytes", len(body), flush=True)
            (OUT / "manifest.json").write_bytes(body)
            report["manifest_attempts"].append({"url": url, "status": status, "content_type": ctype, "final_url": final, "bytes": len(body)})
            manifest = json.loads(body.decode("utf-8-sig"))
            break
        except Exception as exc:
            print("FETCH_ERROR", type(exc).__name__, str(exc)[:500], flush=True)
            report["manifest_attempts"].append({"url": url, "error": f"{type(exc).__name__}: {str(exc)[:500]}"})
    try:
        status, ctype, final, body = fetch(OCR, limit=30_000_000)
        print("OCR", status, ctype, final, "bytes", len(body), flush=True)
        (OUT / "ocr.json").write_bytes(body)
        try:
            obj = json.loads(body.decode("utf-8-sig"))
            print("OCR_TOP_KEYS", list(obj)[:40] if isinstance(obj, dict) else type(obj).__name__, flush=True)
            report["ocr"] = {"status": status, "content_type": ctype, "final_url": final, "bytes": len(body), "top_keys": list(obj)[:40] if isinstance(obj, dict) else type(obj).__name__}
        except Exception as exc:
            report["ocr"] = {"status": status, "content_type": ctype, "final_url": final, "bytes": len(body), "parse_error": str(exc)[:300]}
    except Exception as exc:
        print("OCR_ERROR", type(exc).__name__, str(exc)[:500], flush=True)
        report["ocr"] = {"error": f"{type(exc).__name__}: {str(exc)[:500]}"}

    if manifest is not None:
        canvases = []
        if manifest.get("sequences"):
            canvases = manifest["sequences"][0].get("canvases") or []
        if not canvases:
            canvases = manifest.get("items") or []
        report["canvas_count"] = len(canvases)
        print("MANIFEST_LABEL", label_text(manifest.get("label")), "CANVASES", len(canvases), flush=True)
        selected = set(i for i in K01_CANVASES if 0 <= i < len(canvases))
        selected.add(len(canvases) - 1) if canvases else None
        for i, canvas in enumerate(canvases):
            lab = label_text(canvas.get("label"))
            if re.search(r"map|sound asleep|frontispiece|wroxham broad", lab, re.I):
                selected.add(i)
        for i in sorted(selected):
            canvas = canvases[i]
            lab = label_text(canvas.get("label"))
            service, width, height = service_for(canvas)
            row = {"index_zero_based": i, "label": lab, "width": width, "height": height, "service": service}
            print("CANVAS", json.dumps(row, ensure_ascii=False), flush=True)
            if service:
                base = service.rstrip("/")
                if base.endswith("/info.json"):
                    base = base[:-10]
                image_url = base + "/full/1024,/0/default.jpg"
                try:
                    status, ctype, final, img = fetch(image_url, limit=12_000_000)
                    name = f"canvas_{i:03d}.jpg"
                    (OUT / name).write_bytes(img)
                    row.update({"image_status": status, "image_type": ctype, "image_url": final, "image_bytes": len(img), "file": name})
                    print("IMAGE", i, status, ctype, len(img), final, flush=True)
                except Exception as exc:
                    row["image_error"] = f"{type(exc).__name__}: {str(exc)[:400]}"
                    print("IMAGE_ERROR", i, row["image_error"], flush=True)
            report["selected"].append(row)

    (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("REPORT", json.dumps(report, ensure_ascii=False)[:10000], flush=True)
    return 0 if manifest is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
