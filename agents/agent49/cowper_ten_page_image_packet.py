"""Fetch the ten frozen Cowper page images for the K08 page/word test."""
from __future__ import annotations

import base64
import hashlib
import json
import struct
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

VOLUMES = (
    ("part1_1892", "hvd.hn5w2p", (81, 94, 99, 106, 112)),
    ("part2_1893", "o7P-qis2u9IC", (121, 130, 135, 142, 151)),
)
OUT = Path("cowper-pages")
OUT.mkdir(exist_ok=True)
PLACEHOLDER_SHA256 = {
    "3efa8c43e5b4348f303a528c81adf435f0111ea752fe9f0f6241478b60987fa6",
    "12557f8948b8bdc6af436e3a8b3adddd45f7f7d2b67c5832e799cdf4686f72bb",
}
manifest = []

for volume, volume_id, pages in VOLUMES:
    folder = OUT / volume
    folder.mkdir(exist_ok=True)
    for page in pages:
        url = (
            f"https://books.google.com/books/content?id={volume_id}"
            f"&pg=PA{page}&img=1&zoom=2&edge=curl&source=gbs_api"
        )
        request = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/png,image/*,*/*;q=0.8",
            "Referer": f"https://books.google.com/books?id={volume_id}&pg=PA{page}",
        })
        try:
            with urlopen(request, timeout=45) as response:
                body = response.read(5_000_001)
                content_type = response.headers.get("Content-Type", "")
                status = response.status
                if status != 200 or not content_type.startswith("image/png"):
                    raise RuntimeError(f"Unexpected response {status} {content_type}")
            if len(body) < 24 or body[:8] != b"\x89PNG\r\n\x1a\n":
                raise RuntimeError("Response is not a valid PNG")
            width, height = struct.unpack(">II", body[16:24])
            digest = hashlib.sha256(body).hexdigest()
            if digest in PLACEHOLDER_SHA256:
                item = {
                    "volume": volume,
                    "volume_id": volume_id,
                    "printed_page": page,
                    "url": url,
                    "http_status": status,
                    "content_type": content_type,
                    "bytes": len(body),
                    "width": width,
                    "height": height,
                    "sha256": digest,
                    "status": "placeholder",
                    "is_page_content": False,
                    "error": "Google Books returned the generic image-not-available placeholder",
                }
                manifest.append(item)
                print("PAGE_PLACEHOLDER " + json.dumps(item, sort_keys=True))
                continue
            filename = f"p{page}.png"
            target = folder / filename
            target.write_bytes(body)
            item = {
                "volume": volume,
                "volume_id": volume_id,
                "printed_page": page,
                "url": url,
                "http_status": status,
                "content_type": content_type,
                "bytes": len(body),
                "width": width,
                "height": height,
                "sha256": digest,
                "status": "candidate_image_requires_visual_check",
                "is_page_content": False,
                "artifact_file": str(target).replace("\\", "/"),
            }
            manifest.append(item)
            print("PAGE_RESULT " + json.dumps(item, sort_keys=True))
            print(f"PAGE_IMAGE_BASE64 volume={volume} page={page} data={base64.b64encode(body).decode('ascii')}")
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            item = {
                "volume": volume,
                "volume_id": volume_id,
                "printed_page": page,
                "url": url,
                "error": f"{type(exc).__name__}: {exc}",
            }
            manifest.append(item)
            print("PAGE_ERROR " + json.dumps(item, sort_keys=True))

manifest_path = OUT / "manifest.json"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
successes = sum(1 for item in manifest if item.get("is_page_content") is True)
print(f"PAGE_BATCH_COMPLETE visually_unverified={successes} total={len(manifest)}")
