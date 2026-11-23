"""Recover native author text and tracked Word revision views from OOXML/OPC documents.

An original DOCX/PPTX/XLSX is a ZIP package. A printed coupon or author-final
caption may span adjacent styling runs with XML tags in between. WordprocessingML
revision markup also preserves insertions, deletions, moves, author IDs and dates;
the final and original paragraph views must not be conflated.

WordprocessingML w:p/w:r/w:t:
https://learn.microsoft.com/en-us/office/open-xml/word/structure-of-a-wordprocessingml-document
"""
from __future__ import annotations

import io
import re
from collections.abc import Iterator
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DRAW_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
SHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
W = f"{{{WORD_NS}}}"
MAX_PART_BYTES = 4 * 1024 * 1024
MAX_PARTS = 1000
MAX_TEXT = 1_000_000
REVISION_TAGS = {W + "ins", W + "del", W + "moveFrom", W + "moveTo"}


def _word_element_text(node, view: str = "final") -> str:
    """Reconstruct a Word subtree as final, original, or all revision text."""
    if view not in {"final", "original", "all"}:
        raise ValueError("view must be final, original, or all")
    pieces: list[str] = []

    def visit(current) -> None:
        tag = current.tag
        if view == "final" and tag in {W + "del", W + "moveFrom"}:
            return
        if view == "original" and tag in {W + "ins", W + "moveTo"}:
            return
        if tag == W + "t":
            pieces.append(current.text or "")
            return
        if tag == W + "delText":
            if view in {"original", "all"}:
                pieces.append(current.text or "")
            return
        if tag == W + "tab":
            pieces.append("\t")
            return
        if tag in {W + "br", W + "cr"}:
            pieces.append("\n")
            return
        for child in list(current):
            visit(child)

    visit(node)
    return "".join(pieces)


def _label_value(value: str, limit: int = 40) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return (value or "unknown")[:limit]


def iter_ooxml_text_units(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Yield source-authored paragraph/shared-string text in visible final view."""
    try:
        with ZipFile(io.BytesIO(data)) as package:
            if "[Content_Types].xml" not in package.namelist():
                return
            processed = 0
            for member in package.infolist():
                name = member.filename
                if not name.endswith(".xml"):
                    continue
                if name == "word/comments.xml":
                    parent_tag = f"{W}comment"
                    text_tags = None
                elif name.startswith("word/"):
                    parent_tag = f"{W}p"
                    text_tags = None
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
                    if name == "word/comments.xml":
                        text = "\n".join(
                            _word_element_text(paragraph, "final")
                            for paragraph in parent.iter(W + "p")
                        )
                        comment_id = _label_value(parent.attrib.get(W + "id", ""))
                        author = _label_value(parent.attrib.get(W + "author", ""))
                        date = _label_value(parent.attrib.get(W + "date", ""))
                        label = (
                            f"{name}#comment-id-{comment_id}"
                            f"-author-{author}-date-{date}"
                        )
                    elif name.startswith("word/"):
                        text = _word_element_text(parent, "final")
                        label = f"{name}#authored-unit-{index}"
                    else:
                        text = "".join(
                            child.text or "" for child in parent.iter()
                            if child.tag in text_tags
                        )
                        label = f"{name}#authored-unit-{index}"
                    if 0 < len(text) <= MAX_TEXT:
                        yield label, text.encode("utf-8")
    except (BadZipFile, OSError, ValueError, ElementTree.ParseError):
        return


def iter_ooxml_revision_units(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Yield Word original-view paragraphs and attributed tracked-change text.

    The normal OOXML text iterator already yields visible final-view paragraphs.
    This companion stream adds the pre-revision view and each retained insert,
    delete, move-from and move-to event, with author/date/id in the source label.
    A match in an original/deleted stream is not a final-version assertion.
    """
    try:
        with ZipFile(io.BytesIO(data)) as package:
            names = set(package.namelist())
            if "[Content_Types].xml" not in names:
                return
            if "word/document.xml" in names:
                info = package.getinfo("word/document.xml")
                if 0 < info.file_size <= MAX_PART_BYTES:
                    root = ElementTree.fromstring(package.read("word/document.xml"))
                    for index, paragraph in enumerate(root.iter(W + "p")):
                        original = _word_element_text(paragraph, "original")
                        final = _word_element_text(paragraph, "final")
                        if original and original != final and len(original) <= MAX_TEXT:
                            yield (
                                f"word/document.xml#original-unit-{index}",
                                original.encode("utf-8"),
                            )
                        for event_index, event in enumerate(paragraph.iter()):
                            if event.tag not in REVISION_TAGS:
                                continue
                            text = _word_element_text(event, "all")
                            if not text or len(text) > MAX_TEXT:
                                continue
                            kind = event.tag.rsplit("}", 1)[-1]
                            author = _label_value(event.attrib.get(W + "author", ""))
                            date = _label_value(event.attrib.get(W + "date", ""))
                            revision_id = _label_value(event.attrib.get(W + "id", ""))
                            label = (
                                f"word/document.xml#revision-{kind}"
                                f"-id-{revision_id}-author-{author}-date-{date}"
                                f"-event-{event_index}"
                            )
                            yield label, text.encode("utf-8")

    except (BadZipFile, OSError, ValueError, ElementTree.ParseError):
        return
