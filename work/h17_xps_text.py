"""Read text-bearing XPS/OXPS FixedPage Glyphs from a preserved package.

This is a bounded, read-only ZIP/OPC extractor for XPS text attributes.
It cannot recover text rendered solely as outlines, glyph indices, or images.
"""
from __future__ import annotations

import io
import math
import zipfile
from collections.abc import Iterator
from xml.etree import ElementTree

PAGE_LIMIT = 4 * 1024 * 1024
TOTAL_LIMIT = 32 * 1024 * 1024
MAX_PAGES = 4096
CONTENT_TYPES_LIMIT = 1024 * 1024
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
FIXED_PAGE_MIME = "application/vnd.ms-package.xps-fixedpage+xml"
XPS_NAMESPACES = {
    "http://schemas.microsoft.com/xps/2005/06",
    "http://schemas.openxps.org/oxps/v1.0",
}


def _local_name(tag: str) -> tuple[str, str]:
    if tag.startswith("{"):
        ns, name = tag[1:].split("}", 1)
        return ns, name
    return "", tag


def _texts(page: bytes) -> list[str]:
    if len(page) > PAGE_LIMIT or b"<!DOCTYPE" in page.upper() or b"<!ENTITY" in page.upper():
        return []
    try:
        root = ElementTree.fromstring(page)
    except ElementTree.ParseError:
        return []
    namespace, name = _local_name(root.tag)
    if namespace not in XPS_NAMESPACES or name != "FixedPage":
        return []
    texts: list[str] = []
    for element in root.iter():
        child_namespace, child_name = _local_name(element.tag)
        if child_namespace == namespace and child_name == "Glyphs":
            value = element.get("UnicodeString")
            if value and value.strip():
                texts.append(value)
    return texts


def _declared_fixed_pages(package: zipfile.ZipFile) -> tuple[set[str], set[str]]:
    """Read OPC FixedPage overrides and extension defaults within a small limit."""
    info = package.getinfo("[Content_Types].xml")
    if info.file_size > CONTENT_TYPES_LIMIT:
        return set(), set()
    with package.open(info) as stream:
        data = stream.read(CONTENT_TYPES_LIMIT + 1)
    if len(data) > CONTENT_TYPES_LIMIT or b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        return set(), set()
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError:
        return set(), set()
    if root.tag != f"{{{CONTENT_TYPES_NS}}}Types":
        return set(), set()
    explicit, extensions = set(), set()
    for element in root:
        if element.get("ContentType") != FIXED_PAGE_MIME:
            continue
        if element.tag == f"{{{CONTENT_TYPES_NS}}}Override":
            name = element.get("PartName", "")
            if name.startswith("/"):
                explicit.add(name[1:])
        elif element.tag == f"{{{CONTENT_TYPES_NS}}}Default":
            extension = element.get("Extension", "").lower().lstrip(".")
            if extension:
                extensions.add(extension)
    return explicit, extensions


def _spatial_texts(page: bytes) -> list[str]:
    """Optional left-to-right, top-to-bottom candidate for positioned glyph runs.

    It supplements the original XML-order streams. It is intentionally only
    an approximation for simple non-transformed single-column pages.
    """
    if len(page) > PAGE_LIMIT or b"<!DOCTYPE" in page.upper() or b"<!ENTITY" in page.upper():
        return []
    try:
        root = ElementTree.fromstring(page)
    except ElementTree.ParseError:
        return []
    namespace, name = _local_name(root.tag)
    if namespace not in XPS_NAMESPACES or name != "FixedPage":
        return []
    positioned = []
    for element in root.iter():
        elem_ns, elem_name = _local_name(element.tag)
        if (elem_ns, elem_name) != (namespace, "Glyphs"):
            continue
        value = element.get("UnicodeString")
        if not value or not value.strip():
            continue
        try:
            x = float(element.attrib["OriginX"])
            y = float(element.attrib["OriginY"])
        except (KeyError, ValueError):
            return []
        if not (math.isfinite(x) and math.isfinite(y)):
            return []
        positioned.append((round(y, 1), x, len(positioned), value))
    return [value for _, _, _, value in sorted(positioned)]


def could_contain_xps(data: bytes) -> bool:
    """Recognize an OPC ZIP header with an optional short spool preamble."""
    return data.find(b"PK\x03\x04", 0, 4096) >= 0


def extract_xps_text(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Yield page-local line/spaced/joined UTF-8 texts from an OPC XPS ZIP.

    FixedPage order uses the package member order. Consumers must not assume
    this represents the final printed order across different pages.
    """
    if not could_contain_xps(data):
        return
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as package:
            items = package.infolist()
            names = {item.filename for item in items}
            if "[Content_Types].xml" not in names:
                return
            explicit, extensions = _declared_fixed_pages(package)
            budget = 0
            page_count = 0
            for item in items:
                suffix = item.filename.rsplit(".", 1)[-1].lower()
                is_page = (item.filename.lower().endswith(".fpage")
                           or item.filename in explicit or suffix in extensions)
                if item.is_dir() or item.filename == "[Content_Types].xml" or not is_page:
                    continue
                page_count += 1
                if page_count > MAX_PAGES or item.file_size > PAGE_LIMIT:
                    return
                budget += item.file_size
                if budget > TOTAL_LIMIT:
                    return
                with package.open(item) as stream:
                    page = stream.read(PAGE_LIMIT + 1)
                if len(page) > PAGE_LIMIT:
                    return
                strings = _texts(page)
                if not strings:
                    continue
                spatial = _spatial_texts(page)
                variants = [
                    ("lines", "\n".join(strings)),
                    ("spaced", " ".join(strings)),
                    ("joined", "".join(strings)),
                ]
                if spatial and spatial != strings:
                    variants.extend((
                        ("spatial-spaced", " ".join(spatial)),
                        ("spatial-joined", "".join(spatial)),
                    ))
                for label, value in variants:
                    if value:
                        yield f"xps-page-{page_count}-{label}", value.encode("utf-8")
    except (zipfile.BadZipFile, RuntimeError, OSError, EOFError, ValueError):
        return
