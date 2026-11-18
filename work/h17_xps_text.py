"""Read text-bearing XPS/OXPS FixedPage Glyphs from a preserved package.

This is a bounded, read-only ZIP/OPC extractor for XPS text attributes.
It cannot recover text rendered solely as outlines, glyph indices, or images.
"""
from __future__ import annotations

import io
import zipfile
from collections.abc import Iterator
from xml.etree import ElementTree

PAGE_LIMIT = 4 * 1024 * 1024
TOTAL_LIMIT = 32 * 1024 * 1024
MAX_PAGES = 4096
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
            budget = 0
            page_count = 0
            for item in items:
                if not item.filename.lower().endswith(".fpage") or item.is_dir():
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
                for label, value in (
                    ("lines", "\n".join(strings)),
                    ("spaced", " ".join(strings)),
                    ("joined", "".join(strings)),
                ):
                    if value:
                        yield f"xps-page-{page_count}-{label}", value.encode("utf-8")
    except (zipfile.BadZipFile, RuntimeError, OSError, EOFError, ValueError):
        return
