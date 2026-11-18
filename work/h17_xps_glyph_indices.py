#!/usr/bin/env python3
"""Recover text from XPS Glyphs elements that omit UnicodeString.

This is a conservative fallback for XPS/OXPS packages whose FixedPage XML
contains Glyphs/Indices but no UnicodeString. It deobfuscates embedded .odttf
fonts using the GUID-derived OpenXPS key, reads their cmap tables with
fontTools, and maps glyph IDs back to Unicode only when the mapping is unique.
It emits per-page lines/spaced/joined variants and a coordinate-sorted variant
when every run has OriginX/OriginY, so existing K04/K08 scanners can consume it.

It does not rasterize pages, infer text from outlines, or guess ambiguous
ligatures/clusters. Install fontTools to enable font parsing.
"""
from __future__ import annotations

import io
import math
import posixpath
import uuid
import zipfile
import unicodedata
from urllib.parse import unquote
from collections import defaultdict
from pathlib import PurePosixPath
from typing import Any
from xml.etree import ElementTree as ET

try:
    from fontTools.ttLib import TTFont
except ImportError:  # optional dependency
    TTFont = None

try:
    from fontTools import agl
except ImportError:  # optional glyph-name fallback
    agl = None

MAX_PACKAGE_ENTRIES = 10000
MAX_PART_BYTES = 32 * 1024 * 1024
MAX_FONT_BYTES = 16 * 1024 * 1024
MAX_TOTAL_FONT_BYTES = 64 * 1024 * 1024
MAX_TOTAL_XML_BYTES = 128 * 1024 * 1024
CONTENT_TYPES_LIMIT = 1024 * 1024
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
FIXED_PAGE_MIME = "application/vnd.ms-package.xps-fixedpage+xml"
MAX_GLYPHS_PER_RUN = 100000
MAX_RUNS_PER_PACKAGE = 10000
MAX_TOTAL_GLYPHS = 2000000
XPS_NAMESPACES = {
    "http://schemas.microsoft.com/xps/2005/06",
    "http://schemas.openxps.org/oxps/v1.0",
}


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
                if cluster_units < 1 or cluster_glyphs < 1:
                    out.append({"position": position, "glyph_id": None, "error": "cluster counts must be positive"})
                    continue
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
        if "cmap" in font:
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
        # Some subset fonts omit cmap but retain Adobe/uni-style glyph names.
        # Use that fallback only when cmap supplied no mapping for the glyph.
        if agl is not None:
            for gid, glyph_name in enumerate(glyph_order):
                if reverse.get(gid):
                    continue
                text = agl.toUnicode(glyph_name)
                if text and all(unicodedata.category(ch)[0] not in ("C",) for ch in text):
                    reverse[gid].append(text)
        return dict(reverse), len(glyph_order)
    finally:
        font.close()


def _split_tag(tag: str) -> tuple[str, str]:
    if tag.startswith("{"):
        namespace, local = tag[1:].split("}", 1)
        return namespace, local
    return "", tag


def _page_has_transform(root: ET.Element, namespace: str) -> bool:
    """Conservatively reject spatial ordering if any page transform is present."""
    transform_names = {
        "MatrixTransform", "TranslateTransform", "ScaleTransform",
        "RotateTransform", "SkewTransform",
    }
    for element in root.iter():
        element_namespace, local = _split_tag(element.tag)
        if element_namespace != namespace:
            continue
        if ("RenderTransform" in element.attrib
                or "RenderTransformOrigin" in element.attrib
                or local in transform_names
                or local.endswith(".RenderTransform")):
            return True
    return False


def _coordinate(element: ET.Element, name: str) -> float | None:
    try:
        value = float(element.attrib[name])
    except (KeyError, ValueError):
        return None
    return value if math.isfinite(value) else None


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
    try:
        parsed = parse_indices(indices)
    except ValueError as exc:
        return {
            "page": page_part,
            "font_uri": font_uri,
            "font_part": font_part,
            "status": "malformed-indices",
            "error": str(exc),
            "text": "",
            "unresolved": [],
        }
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
            unresolved.append({**item, "reason": "glyph has no Unicode cmap or AGL mapping"})
        else:
            unresolved.append({**item, "reason": "ambiguous cmap entry", "unicode_options": options})
    return {
        "page": page_part,
        "font_uri": font_uri,
        "font_part": font_part,
        "origin_x": _coordinate(element, "OriginX"),
        "origin_y": _coordinate(element, "OriginY"),
        "status": "decoded" if not unresolved else "partial",
        "glyph_count": glyph_count,
        "glyphs": len(parsed),
        "text": "".join(chars),
        "unresolved": unresolved,
    }


def extract_xps_glyph_indices(data: bytes) -> dict[str, Any]:
    """Extract complete glyph-index-only text runs from an XPS/OXPS ZIP package.

    Partial runs remain diagnostic-only: they are never compacted into candidate
    text streams. The returned coverage object distinguishes a complete scan
    from pages/runs skipped because of malformed data or resource limits.
    """
    if len(data) > 256 * 1024 * 1024:
        raise ValueError("XPS package exceeds size limit")
    coverage: dict[str, Any] = {
        "complete": True,
        "reasons": [],
        "pages_seen": 0,
        "pages_processed": 0,
        "runs_seen": 0,
        "glyphs_seen": 0,
    }

    def mark_incomplete(reason: str) -> None:
        coverage["complete"] = False
        if reason not in coverage["reasons"]:
            coverage["reasons"].append(reason)

    if TTFont is None:
        mark_incomplete("fontTools-unavailable")
        return {
            "status": "fontTools-unavailable",
            "runs": [],
            "streams": [],
            "text": "",
            "coverage": coverage,
        }

    runs: list[dict[str, Any]] = []
    by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    font_cache: dict[str, tuple[dict[int, list[str]], int] | Exception] = {}
    font_budget = [0]
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        infos = package.infolist()
        if len(infos) > MAX_PACKAGE_ENTRIES:
            raise ValueError("too many XPS package entries")
        names = {item.filename for item in infos}
        if "[Content_Types].xml" not in names:
            return {
                "status": "no-opc-content-types",
                "runs": [],
                "streams": [],
                "text": "",
                "coverage": coverage,
            }
        explicit, extensions = _declared_fixed_pages(package)
        total_xml_bytes = 0
        for info in infos:
            suffix = info.filename.rsplit(".", 1)[-1].lower()
            is_page = (info.filename.lower().endswith(".fpage")
                       or info.filename in explicit or suffix in extensions)
            if info.is_dir() or info.filename == "[Content_Types].xml" or not is_page:
                continue

            coverage["pages_seen"] += 1
            name = _safe_part_name(info.filename)
            if info.file_size > MAX_PART_BYTES:
                mark_incomplete("page-size-limit")
                continue
            if total_xml_bytes + info.file_size > MAX_TOTAL_XML_BYTES:
                mark_incomplete("total-xml-budget")
                break
            total_xml_bytes += info.file_size
            raw = package.read(info)
            if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
                mark_incomplete("page-xml-entity-declaration")
                continue
            try:
                root = ET.fromstring(raw)
            except ET.ParseError:
                mark_incomplete("page-xml-parse-error")
                continue

            namespace, local = _split_tag(root.tag)
            if namespace not in XPS_NAMESPACES or local != "FixedPage":
                continue
            coverage["pages_processed"] += 1
            transformed = _page_has_transform(root, namespace)
            page_runs: list[dict[str, Any]] = []
            page_overflow = False
            for element in root.iter():
                element_namespace, element_local = _split_tag(element.tag)
                if element_namespace != namespace or element_local != "Glyphs":
                    continue
                unicode_string = element.attrib.get("UnicodeString", "")
                if unicode_string not in ("", "{}"):
                    continue
                if "Indices" not in element.attrib:
                    continue
                if coverage["runs_seen"] >= MAX_RUNS_PER_PACKAGE:
                    mark_incomplete("run-count-limit")
                    page_overflow = True
                    break

                coverage["runs_seen"] += 1
                try:
                    run = _decode_glyph_run(name, element, package, font_cache, font_budget)
                except Exception as exc:
                    run = {
                        "page": name,
                        "status": "malformed-run",
                        "error": str(exc),
                        "text": "",
                        "unresolved": [],
                    }
                run["spatial_allowed"] = not transformed
                glyph_count = int(run.get("glyphs", 0) or 0)
                if coverage["glyphs_seen"] + glyph_count > MAX_TOTAL_GLYPHS:
                    mark_incomplete("total-glyph-limit")
                    page_overflow = True
                    break
                coverage["glyphs_seen"] += glyph_count

                if run.get("status") != "decoded":
                    mark_incomplete("run-" + str(run.get("status", "unknown")))
                page_runs.append(run)
                runs.append(run)

            if page_runs and not page_overflow:
                by_page[name] = page_runs

    streams: list[dict[str, str]] = []
    complete_text: list[str] = []
    for page, page_runs in sorted(by_page.items()):
        # Never join around an unresolved/partial run: that would invent adjacency.
        if not page_runs or any(run.get("status") != "decoded" or not run.get("text")
                                for run in page_runs):
            continue
        texts = [run["text"] for run in page_runs]
        streams.extend((
            {"page": page, "label": "lines", "text": "\n".join(texts)},
            {"page": page, "label": "spaced", "text": " ".join(texts)},
            {"page": page, "label": "joined", "text": "".join(texts)},
        ))
        complete_text.append("\n".join(texts))
        spatial_allowed = all(run.get("spatial_allowed", False) for run in page_runs)
        if (spatial_allowed
                and all(run.get("origin_x") is not None and run.get("origin_y") is not None
                        for run in page_runs)):
            spatial = sorted(page_runs, key=lambda run: (run["origin_y"], run["origin_x"]))
            spatial_texts = [run["text"] for run in spatial]
            if spatial_texts != texts:
                streams.extend((
                    {"page": page, "label": "spatial-spaced", "text": " ".join(spatial_texts)},
                    {"page": page, "label": "spatial-joined", "text": "".join(spatial_texts)},
                ))

    if coverage["reasons"]:
        if any(reason in coverage["reasons"] for reason in
               ("page-size-limit", "total-xml-budget", "run-count-limit", "total-glyph-limit")):
            status = "truncated"
        elif streams:
            status = "partial"
        else:
            status = "glyph-runs-found"
    elif not runs:
        status = "no-glyph-index-only-runs"
    elif all(run.get("status") == "decoded" for run in runs):
        status = "decoded"
    elif streams:
        status = "partial"
    else:
        status = "glyph-runs-found"

    return {
        "status": status,
        "runs": runs,
        "streams": streams,
        "text": "\n".join(complete_text),
        "coverage": coverage,
    }

def extract_xps_glyph_streams(data: bytes) -> list[tuple[str, bytes]]:
    """Return only complete-page (label, UTF-8 bytes) candidate variants.

    Call extract_xps_glyph_indices() as well when a caller needs the coverage
    object; an empty stream list is not proof of a complete negative scan.
    """
    result = extract_xps_glyph_indices(data)
    return [
        (f"xps-glyph:{stream['page']}:{stream['label']}", stream["text"].encode("utf-8"))
        for stream in result.get("streams", [])
    ]


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
