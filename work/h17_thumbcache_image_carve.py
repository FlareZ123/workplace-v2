#!/usr/bin/env python3
"""Read-only image carving for Windows Explorer thumbnail-cache files.

This is a bounded byte-carver, not a forensic parser for the thumbnail-cache
index. It extracts intact JPEG, PNG, GIF, BMP and WebP payloads embedded in
thumbcache_*.db / Thumbs.db files, preserving their original bytes so that
lossless-channel analysis remains possible. It never modifies source files.

Use only on an authorized, read-only copy of a retired profile. Output must be
outside the source tree. Extracted images can be passed to
work/h17_k08_teal_bit_image_scan.py, for example:

  python work/h17_thumbcache_image_carve.py /mnt/read-only-profile \
      --out-dir /tmp/h17-thumbcache-images
  python work/h17_k08_teal_bit_image_scan.py --images /tmp/h17-thumbcache-images/images \
      --resources /path/to/extracted-h17-resources
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mmap
import struct
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable

from PIL import Image

SIGNATURES = (
    (b"\xff\xd8\xff", "jpeg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"BM", "bmp"),
    (b"RIFF", "webp"),
)
DEFAULT_MAX_IMAGE_BYTES = 32 * 1024 * 1024
DEFAULT_MAX_PIXELS = 100_000_000


@dataclass(frozen=True)
class CarvedImage:
    source: str
    offset: int
    length: int
    format: str
    width: int
    height: int
    sha256: str
    output: str | None = None
    duplicate: bool = False


def _png_end(data: bytes | mmap.mmap, start: int, limit: int) -> int | None:
    pos = start + 8
    while pos + 12 <= limit:
        length = struct.unpack_from(">I", data, pos)[0]
        kind = bytes(data[pos + 4 : pos + 8])
        end = pos + 12 + length
        if length > limit - pos - 12 or end > limit:
            return None
        if kind == b"IEND":
            return end
        pos = end
    return None


def _jpeg_end(data: bytes | mmap.mmap, start: int, limit: int) -> int | None:
    """Find the JPEG EOI marker while respecting stuffed bytes and segments."""
    pos = start + 2
    in_scan = False
    while pos < limit:
        if in_scan:
            marker_at = data.find(b"\xff", pos, limit)
            if marker_at < 0:
                return None
            pos = marker_at + 1
            while pos < limit and data[pos] == 0xFF:
                pos += 1
            if pos >= limit:
                return None
            marker = data[pos]
            pos += 1
            if marker == 0x00 or 0xD0 <= marker <= 0xD7:
                continue
            if marker == 0xD9:
                return pos
            in_scan = False
            # A marker other than a stuffed byte/restart/EOI ends the current
            # entropy-coded segment. Process it as a normal marker below.
            pos -= 2
            continue

        marker_at = data.find(b"\xff", pos, limit)
        if marker_at < 0:
            return None
        pos = marker_at + 1
        while pos < limit and data[pos] == 0xFF:
            pos += 1
        if pos >= limit:
            return None
        marker = data[pos]
        pos += 1
        if marker == 0xD9:
            return pos
        if marker == 0x00:
            continue
        if marker == 0xD8 or 0xD0 <= marker <= 0xD7 or marker == 0x01:
            continue
        if pos + 2 > limit:
            return None
        segment_length = struct.unpack_from(">H", data, pos)[0]
        if segment_length < 2 or pos + segment_length > limit:
            return None
        pos += segment_length
        if marker == 0xDA:  # Start of Scan; entropy-coded bytes follow.
            in_scan = True
    return None


def _gif_end(data: bytes | mmap.mmap, start: int, limit: int) -> int | None:
    """Parse GIF sub-blocks to avoid mistaking compressed 0x3b bytes for EOF."""
    if start + 13 > limit:
        return None
    packed = data[start + 10]
    pos = start + 13
    if packed & 0x80:
        pos += 3 * (1 << ((packed & 0x07) + 1))
    if pos > limit:
        return None
    while pos < limit:
        marker = data[pos]
        pos += 1
        if marker == 0x3B:
            return pos
        if marker == 0x21:  # Extension: label followed by data sub-blocks.
            if pos >= limit:
                return None
            pos += 1
            while pos < limit:
                size = data[pos]
                pos += 1
                if size == 0:
                    break
                pos += size
                if pos > limit:
                    return None
            continue
        if marker == 0x2C:  # Image descriptor.
            if pos + 9 > limit:
                return None
            image_packed = data[pos + 8]
            pos += 9
            if image_packed & 0x80:
                pos += 3 * (1 << ((image_packed & 0x07) + 1))
            if pos >= limit:
                return None
            pos += 1  # LZW minimum code size.
            while pos < limit:
                size = data[pos]
                pos += 1
                if size == 0:
                    break
                pos += size
                if pos > limit:
                    return None
            continue
        return None
    return None


def _bmp_end(data: bytes | mmap.mmap, start: int, limit: int) -> int | None:
    if start + 26 > limit or data[start : start + 2] != b"BM":
        return None
    size = struct.unpack_from("<I", data, start + 2)[0]
    dib_size = struct.unpack_from("<I", data, start + 14)[0]
    if size < 26 or size > limit - start or dib_size not in {12, 40, 52, 56, 64, 108, 124}:
        return None
    planes_offset = start + (22 if dib_size == 12 else 26)
    if planes_offset + 2 > limit:
        return None
    planes = struct.unpack_from("<H", data, planes_offset)[0]
    if planes != 1:
        return None
    return start + size


def _webp_end(data: bytes | mmap.mmap, start: int, limit: int) -> int | None:
    if start + 12 > limit or data[start + 8 : start + 12] != b"WEBP":
        return None
    size = struct.unpack_from("<I", data, start + 4)[0] + 8
    if size < 12 or size > limit - start:
        return None
    return start + size


END_FNS = {
    "jpeg": _jpeg_end,
    "png": _png_end,
    "gif": _gif_end,
    "bmp": _bmp_end,
    "webp": _webp_end,
}
EXTENSIONS = {"jpeg": ".jpg", "png": ".png", "gif": ".gif", "bmp": ".bmp", "webp": ".webp"}


def _next_signature(data: bytes | mmap.mmap, cursor: int, limit: int) -> tuple[int, str] | None:
    best: tuple[int, str] | None = None
    for signature, kind in SIGNATURES:
        offset = data.find(signature, cursor, limit)
        while offset >= 0:
            if kind != "webp" or (offset + 12 <= limit and data[offset + 8 : offset + 12] == b"WEBP"):
                if best is None or offset < best[0]:
                    best = (offset, kind)
                break
            offset = data.find(signature, offset + 1, limit)
    return best


def _validate_image(blob: bytes, expected_kind: str, max_pixels: int) -> tuple[str, int, int] | None:
    try:
        with Image.open(BytesIO(blob)) as image:
            fmt = (image.format or "").lower()
            width, height = image.size
            if width < 1 or height < 1 or width * height > max_pixels:
                return None
            image.verify()
        with Image.open(BytesIO(blob)) as image:
            image.load()
        aliases = {"jpg": "jpeg"}
        fmt = aliases.get(fmt, fmt)
        if fmt != expected_kind:
            return None
        return fmt, width, height
    except Exception:
        return None


def carve_bytes(
    data: bytes | mmap.mmap,
    source: str,
    max_image_bytes: int = DEFAULT_MAX_IMAGE_BYTES,
    max_pixels: int = DEFAULT_MAX_PIXELS,
) -> list[CarvedImage]:
    """Carve intact supported image payloads from one cache file's bytes."""
    if max_image_bytes < 64 or max_pixels < 1:
        raise ValueError("image and pixel limits must be positive")
    results: list[CarvedImage] = []
    cursor = 0
    limit = len(data)
    while cursor < limit:
        found = _next_signature(data, cursor, limit)
        if found is None:
            break
        start, kind = found
        bounded_limit = min(limit, start + max_image_bytes)
        end = END_FNS[kind](data, start, bounded_limit)
        if end is None or end <= start:
            cursor = start + 1
            continue
        blob = bytes(data[start:end])
        valid = _validate_image(blob, kind, max_pixels)
        if valid is None:
            cursor = start + 1
            continue
        fmt, width, height = valid
        results.append(
            CarvedImage(
                source=source,
                offset=start,
                length=len(blob),
                format=fmt,
                width=width,
                height=height,
                sha256=hashlib.sha256(blob).hexdigest(),
            )
        )
        cursor = end
    return results


def _cache_file(path: Path) -> bool:
    name = path.name.casefold()
    return name == "thumbs.db" or name == "ehthumbs.db" or name.startswith("thumbcache")


def discover_cache_files(source: Path) -> list[Path]:
    if source.is_file():
        if source.is_symlink():
            raise ValueError(f"refusing symlink source: {source}")
        return [source]
    if not source.is_dir() or source.is_symlink():
        raise ValueError(f"source must be a regular cache file or directory: {source}")
    return sorted(p for p in source.rglob("*") if p.is_file() and not p.is_symlink() and _cache_file(p))


def carve_file(path: Path, max_image_bytes: int, max_pixels: int) -> list[CarvedImage]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"refusing non-regular or symlink source: {path}")
    size = path.stat().st_size
    if size == 0:
        return []
    with path.open("rb") as handle:
        with mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
            return carve_bytes(data, str(path), max_image_bytes, max_pixels)


def extract(
    sources: Iterable[Path],
    output_dir: Path,
    max_image_bytes: int = DEFAULT_MAX_IMAGE_BYTES,
    max_pixels: int = DEFAULT_MAX_PIXELS,
) -> dict:
    source_paths: list[Path] = []
    source_roots: list[Path] = []
    for source in sources:
        if source.is_symlink():
            raise ValueError(f"refusing symlink source: {source}")
        source_roots.append(source.resolve() if source.is_dir() else source.resolve().parent)
        source_paths.extend(discover_cache_files(source))
    unique_sources = sorted({p.resolve() for p in source_paths})
    output_resolved = output_dir.resolve()
    for root in source_roots:
        if output_resolved == root or root in output_resolved.parents:
            raise ValueError("output_dir must be outside every source file parent and source tree")
    if output_dir.is_symlink():
        raise ValueError("refusing symlink output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    if images_dir.is_symlink():
        raise ValueError("refusing symlink images output directory")
    images_dir.mkdir(exist_ok=True)
    images_resolved = images_dir.resolve()
    if any(root == images_resolved or root in images_resolved.parents for root in source_roots):
        raise ValueError("images output directory must be outside every source tree")

    manifest: list[dict] = []
    seen: dict[str, str] = {}
    errors: list[dict] = []
    for source in unique_sources:
        try:
            if source.stat().st_size == 0:
                continue
            with source.open("rb") as handle:
                with mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
                    carved = carve_bytes(data, str(source), max_image_bytes, max_pixels)
                    for image in carved:
                        duplicate = image.sha256 in seen
                        output_name = seen.get(image.sha256)
                        if not duplicate:
                            output_name = image.sha256 + EXTENSIONS[image.format]
                            output_path = images_dir / output_name
                            output_path.write_bytes(bytes(data[image.offset : image.offset + image.length]))
                            seen[image.sha256] = output_name
                        manifest.append(
                            asdict(
                                CarvedImage(
                                    source=image.source,
                                    offset=image.offset,
                                    length=image.length,
                                    format=image.format,
                                    width=image.width,
                                    height=image.height,
                                    sha256=image.sha256,
                                    output=str(Path("images") / output_name) if output_name else None,
                                    duplicate=duplicate,
                                )
                            )
                        )
        except Exception as exc:
            errors.append({"source": str(source), "error": f"{type(exc).__name__}: {exc}"})

    result = {
        "schema": "h17-thumbcache-image-carve/v1",
        "source_writes_performed": False,
        "source_files_scanned": len(unique_sources),
        "image_occurrences": len(manifest),
        "unique_images_extracted": len(seen),
        "images_directory": str(images_dir),
        "images": manifest,
        "errors": errors,
        "limitations": [
            "This is signature-based image carving, not a full Windows thumbcache or OLE/Thumbs.db parser.",
            "It does not recover cache index metadata, original paths, timestamps, or source associations.",
            "Only intact JPEG, PNG, GIF, BMP and WebP payloads are extracted; TIFF and proprietary formats are not decoded.",
            "Run against an authorized read-only profile copy; never against a live user profile or mounted source in write mode.",
        ],
    }
    (output_dir / "carve_manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path, help="thumbnail-cache file(s) or a profile root")
    parser.add_argument("--out-dir", required=True, type=Path, help="output directory outside all source trees")
    parser.add_argument("--max-image-bytes", type=int, default=DEFAULT_MAX_IMAGE_BYTES)
    parser.add_argument("--max-pixels", type=int, default=DEFAULT_MAX_PIXELS)
    args = parser.parse_args()
    result = extract(args.sources, args.out_dir, args.max_image_bytes, args.max_pixels)
    print(json.dumps(result, indent=2))
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
