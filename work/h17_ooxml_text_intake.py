"""Recover native author text across style runs in OOXML/OPC documents.

An original DOCX/PPTX/XLSX is a ZIP package. A printed coupon or author-final
caption may span adjacent styling runs with XML tags in between. Reconstruct
source-defined paragraph/shared-string units without inventing wording.

WordprocessingML w:p/w:r/w:t:
https://learn.microsoft.com/en-us/office/open-xml/word/structure-of-a-wordprocessingml-document
"""
from __future__ import annotations

import io
from collections.abc import Iterator
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DRAW_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
SHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
MAX_PART_BYTES = 4 * 1024 * 1024
MAX_PARTS = 1000
MAX_TEXT = 1_000_000


def iter_ooxml_text_units(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Yield source-authored paragraph/shared-string text from native OOXML."""
    try:
        with ZipFile(io.BytesIO(data)) as package:
            if "[Content_Types].xml" not in package.namelist():
                return
            processed = 0
            for member in package.infolist():
                name = member.filename
                if not name.endswith(".xml"):
                    continue
                if name.startswith("word/"):
                    parent_tag = f"{{{WORD_NS}}}p"
                    text_tags = {f"{{{WORD_NS}}}t"}
                elif (name.startswith("ppt/slides/") or
                      name.startswith("ppt/notesSlides/")):
                    parent_tag = f"{{{DRAW_NS}}}p"
                    text_tags = {f"{{{DRAW_NS}}}t"}
                elif name == "xl/sharedStrings.xml":
                    parent_tag = f"{{{SHEET_NS}}}si"
                    text_tags = {f"{{{SHEET_NS}}}t"}
                else:
                    continue
                if (member.file_size > MAX_PART_BYTES or member.file_size <= 0
                        or processed >= MAX_PARTS):
                    continue
                processed += 1
                root = ElementTree.fromstring(package.read(member))
                for index, parent in enumerate(root.iter(parent_tag)):
                    text = "".join(
                        node.text or "" for node in parent.iter()
                        if node.tag in text_tags
                    )
                    if 0 < len(text) <= MAX_TEXT:
                        yield f"{name}#authored-unit-{index}", text.encode("utf-8")
    except (BadZipFile, OSError, ValueError, ElementTree.ParseError):
        return
