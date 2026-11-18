#!/usr/bin/env python3
"""Recover text from XPS Glyphs elements that omit UnicodeString.

This is a conservative fallback for XPS/OXPS packages whose FixedPage XML
contains Glyphs/Indices but no UnicodeString. It deobfuscates embedded .odttf
fonts using the GUID-derived OpenXPS key, reads their cmap tables with
fontTools, and maps glyph IDs back to Unicode only when the mapping is unique.

It does not rasterize pages, infer text from outlines, or guess ambiguous
ligatures/clusters. Install fontTools to enable font parsing.
"""
from __future__ import annotations

import io
import posixpath
import uuid
import zipfile
from urllib.parse import unquote
from collections import defaultdict
from pathlib import PurePosixPath
from typing import Any
from xml.etree import ElementTree as ET

try:
    from fontTools.ttLib import TTFont
except ImportError:  # optional dependency
    TTFont = None

MAX_PACKAGE_ENTRIES = 10000
MAX_PART_BYTES = 32 * 1024 * 1024
MAX_FONT_BYTES = 16 * 1024 * 1024
MAX_TOTAL_FONT_BYTES = 64 * 1024 * 1024
MAX_TOTAL_XML_BYTES = 128 * 1024 * 1024
CONTENT_TYPES_LIMIT = 1024 * 1024
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
FIXED_PAGE_MIME = "application/vnd.ms-package.xps-fixedpage+xml"
MAX_GLYPHS_PER_RUN = 100000


def _safe_part_name(name: str) -> str:
    name = name.replace("\\", "/").lstrip("/")
    norm = posixpath.normpath(name)
    if norm in ("", ".") or norm == ".." or norm.startswith("../"):
        raise ValueError(f"unsafe package part name: {name!r}")
    return norm


def _resolve_font_part(page_part: str, font_uri: str) -> str:
    uri = unquote(font_uri.split("#", 1)[0].split("?", 1)[0])
    if uri.startswith("/"):
        return _safe_part_name(uri)
    return _safe_part_name(posixpath.join(posixpath.dirname(page_part), uri))


def _declared_fixed_pages(package: zipfile.ZipFile) -> tuple[set[str], set[str]]:
    """Read OPC FixedPage part declarations, including arbitrary part names."""
    try:
        info = package.getinfo("[Content_Types].xml")
        if info.file_size > CONTENT_TYPES_LIMIT:
            return set(), set()
        raw = package.read(info)
        if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
            return set(), set()
        root = ET.fromstring(raw)
    except (KeyError, ET.ParseError, OSError, RuntimeError):
        return set(), set()
    if root.tag != f"{{{CONTENT_TYPES_NS}}}Types":
        return set(), set()
    explicit: set[str] = set()
    extensions: set[str] = set()
    for element in root:
        if element.get("ContentType") != FIXED_PAGE_MIME:
            continue
        if element.tag == f"{{{CONTENT_TYPES_NS}}}Override":
            name = element.get("PartName", "")
            if name.startswith("/"):
                explicit.add(_safe_part_name(name[1:]))
        elif element.tag == f"{{{CONTENT_TYPES_NS}}}Default":
            extension = element.get("Extension", "").lower().lstrip(".")
            if extension:
                extensions.add(extension)
    return explicit, extensions


def deobfuscate_odttf(data: bytes, part_name: str) -> bytes:
    """Undo the OpenXPS .odttf first-32-byte XOR obfuscation.

    The GUID byte order follows MS-VGSFF 2.1.6.2 (the same OpenXPS
    obfuscation rule): reverse Guid.ToByteArray(), then repeat the 16-byte
    key over the first 32 font bytes.
    """
    if not part_name.lower().endswith(".odttf"):
        return data
    stem = PurePosixPath(part_name).stem.strip("{}")
    guid = uuid.UUID(stem)
    # GUID.ToByteArray() order, reversed, as specified for the XPS font key.
    key = guid.bytes_le[::-1]
    if len(data) < 32:
        raise ValueError("obfuscated font shorter than 32 bytes")
    out = bytearray(data)
    for i in range(32):
        out[i] ^= key[i % 16]
    return bytes(out)


def parse_indices(indices: str) -> list[dict[str, Any]]:
    """Parse ECMA-388 12.1.3 Glyphs/Indices IDs and cluster annotations.

    Glyph metrics are intentionally ignored. Cluster sizes are retained for
    audit, but do not supply missing Unicode characters.
    """
    if len(indices) > 2_000_000:
        raise ValueError("Indices attribute too large")
    out: list[dict[str, Any]] = []
    for position, raw in enumerate(indices.split(";")):
        token = raw.strip()
        if not token:
            continue
        cluster_units = cluster_glyphs = None
        if token.startswith("("):
            close = token.find(")")
            if close < 0:
                out.append({"position": position, "glyph_id": None, "error": "unterminated cluster"})
                continue
            cluster = token[1:close]
            if cluster == "":
                cluster_units = cluster_glyphs = 1
            else:
                parts = cluster.split(":", 1)
                if not parts[0].isdigit() or (len(parts) == 2 and not parts[1].isdigit()):
                    out.append({"position": position, "glyph_id": None, "error": "invalid cluster"})
                    continue
                cluster_units = int(parts[0])
                cluster_glyphs = int(parts[1]) if len(parts) == 2 else 1
            token = token[close + 1:]
        # The first field is GlyphIndex; following comma fields are metrics.
        glyph_field = token.split(",", 1)[0].strip()
        if glyph_field == "":
            gid = None
        elif glyph_field.isdigit():
            gid = int(glyph_field)
        else:
            out.append({"position": position, "glyph_id": None, "error": "invalid glyph index"})
            continue
        out.append({
            "position": position,
            "glyph_id": gid,
            "cluster_code_units": cluster_units,
            "cluster_glyph_count": cluster_glyphs,
        })
        if len(out) > MAX_GLYPHS_PER_RUN:
            raise ValueError("too many glyphs in one run")
    return out


def _font_glyph_map(font_data: bytes) -> tuple[dict[int, list[str]], int]:
    if TTFont is None:
        raise RuntimeError("fontTools is required for Glyphs/Indices decoding")
    font = TTFont(io.BytesIO(font_data), lazy=True, recalcBBoxes=False, recalcTimestamp=False)
    try:
        glyph_order = font.getGlyphOrder()
        reverse: dict[int, list[str]] = defaultdict(list)
        for table in font["cmap"].tables:
            if not table.isUnicode():
                continue
            for codepoint, glyph_name in table.cmap.items():
                if not isinstance(codepoint, int) or not (0 <= codepoint <= 0x10FFFF):
                    continue
                gid = font.getGlyphID(glyph_name)
                char = chr(codepoint)
                if char not in reverse[gid]:
                    reverse[gid].append(char)
        return dict(reverse), len(glyph_order)
    finally:
        font.close()


def _decode_glyph_run(
    page_part: str,
    element: ET.Element,
    package: zipfile.ZipFile,
    font_cache: dict[str, tuple[dict[int, list[str]], int] | Exception],
    font_budget: list[int],
) -> dict[str, Any]:
    font_uri = element.attrib.get("FontUri", "")
    indices = element.attrib.get("Indices", "")
    if not font_uri:
        return {"page": page_part, "status": "missing-font-uri"}
    try:
        font_part = _resolve_font_part(page_part, font_uri)
    except Exception as exc:
        return {"page": page_part, "font_uri": font_uri, "status": "bad-font-uri", "error": str(exc)}
    if font_part not in font_cache:
        try:
            info = package.getinfo(font_part)
            if info.file_size > MAX_FONT_BYTES:
                raise ValueError("font part exceeds size limit")
            if font_budget[0] + info.file_size > MAX_TOTAL_FONT_BYTES:
                raise ValueError("total embedded-font budget exceeded")
            raw = package.read(font_part)
            font_budget[0] += info.file_size
            decoded = deobfuscate_odttf(raw, font_part)
            font_cache[font_part] = _font_glyph_map(decoded)
        except Exception as exc:
            font_cache[font_part] = exc
    font_entry = font_cache[font_part]
    if isinstance(font_entry, Exception):
        return {"page": page_part, "font_uri": font_uri, "font_part": font_part,
                "status": "font-unavailable", "error": str(font_entry)}
    gid_map, glyph_count = font_entry
    parsed = parse_indices(indices)
    chars: list[str] = []
    unresolved: list[dict[str, Any]] = []
    skip_cluster_glyphs = 0
    for item in parsed:
        if skip_cluster_glyphs:
            skip_cluster_glyphs -= 1
            unresolved.append({**item, "reason": "part of unresolved multi-glyph cluster"})
            continue
        cluster_units = item.get("cluster_code_units")
        cluster_glyphs = item.get("cluster_glyph_count")
        if cluster_units is not None and cluster_glyphs is not None and cluster_units != cluster_glyphs:
            skip_cluster_glyphs = max(0, cluster_glyphs - 1)
            unresolved.append({**item, "reason": "non-one-to-one cluster requires UnicodeString"})
            continue
        gid = item["glyph_id"]
        if gid is None:
            unresolved.append({**item, "reason": "empty glyph index"})
            continue
        if gid < 0 or gid >= glyph_count:
            unresolved.append({**item, "reason": "glyph index out of range"})
            continue
        options = gid_map.get(gid, [])
        if len(options) == 1:
            chars.append(options[0])
        elif len(options) == 0:
            unresolved.append({**item, "reason": "glyph has no Unicode cmap entry"})
        else:
            unresolved.append({**item, "reason": "ambiguous cmap entry", "unicode_options": options})
    return {
        "page": page_part,
        "font_uri": font_uri,
        "font_part": font_part,
        "status": "decoded" if not unresolved else "partial",
        "glyph_count": glyph_count,
        "glyphs": len(parsed),
        "text": "".join(chars),
        "unresolved": unresolved,
    }


def extract_xps_glyph_indices(data: bytes) -> dict[str, Any]:
    """Extract glyph-index-only text runs from an XPS/OXPS ZIP package."""
    if len(data) > 256 * 1024 * 1024:
        raise ValueError("XPS package exceeds size limit")
    if TTFont is None:
        return {"status": "fontTools-unavailable", "runs": []}
    runs: list[dict[str, Any]] = []
    font_cache: dict[str, tuple[dict[int, list[str]], int] | Exception] = {}
    font_budget = [0]
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        infos = package.infolist()
        if len(infos) > MAX_PACKAGE_ENTRIES:
            raise ValueError("too many XPS package entries")
        names = {item.filename for item in infos}
        if "[Content_Types].xml" not in names:
            return {"status": "no-opc-content-types", "runs": [], "text": ""}
        explicit, extensions = _declared_fixed_pages(package)
        total_xml_bytes = 0
        for info in infos:
            name = _safe_part_name(info.filename)
            suffix = info.filename.rsplit(".", 1)[-1].lower()
            is_page = (info.filename.lower().endswith(".fpage")
                       or info.filename in explicit or suffix in extensions)
            if info.is_dir() or info.filename == "[Content_Types].xml" or not is_page:
                continue
            if info.file_size > MAX_PART_BYTES:
                continue
            total_xml_bytes += info.file_size
            if total_xml_bytes > MAX_TOTAL_XML_BYTES:
                break
            raw = package.read(info)
            if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
                continue
            try:
                root = ET.fromstring(raw)
            except ET.ParseError:
                continue
            for element in root.iter():
                if element.tag.rsplit("}", 1)[-1] != "Glyphs":
                    continue
                unicode_string = element.attrib.get("UnicodeString", "")
                if unicode_string not in ("", "{}"):
                    continue
                if "Indices" not in element.attrib:
                    continue
                runs.append(_decode_glyph_run(name, element, package, font_cache, font_budget))
    decoded = [r for r in runs if r.get("text")]
    if not runs:
        status = "no-glyph-index-only-runs"
    elif all(r.get("status") == "decoded" for r in runs):
        status = "decoded"
    elif decoded:
        status = "partial"
    else:
        status = "glyph-runs-found"
    return {
        "status": status,
        "runs": runs,
        "text": "\n".join(r["text"] for r in decoded),
    }


def main() -> int:
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xps", type=Path, help="local XPS/OXPS package")
    args = parser.parse_args()
    result = extract_xps_glyph_indices(args.xps.read_bytes())
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "decoded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
