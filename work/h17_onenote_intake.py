"""Read-only OneNote page and revision extraction for H-17 K08 profile scans.

Optional dependency: aspose-note==26.3.2. The upstream source repository
provides a PageHistory API and a history fixture/test. This adapter deliberately
emits every historical revision and the current page separately; it never
chooses a final version or modifies the source file.

Only individual .one section files are handled here. .onepkg/CAB extraction and
OneNoteOfflineCache.onecache decoding are not implemented; the profile scanner
retains its generic fallback for those files.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


class OneNoteDependencyUnavailable(RuntimeError):
    """Raised when the optional aspose-note package is not installed."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _iso(value: Any) -> str:
    if value is None:
        return ""
    method = getattr(value, "isoformat", None)
    return method() if callable(method) else str(value)


def _page_title(page: Any) -> str:
    title = getattr(page, "Title", None)
    title_text = getattr(title, "TitleText", None)
    return _text(getattr(title_text, "Text", None))


def _child_nodes(page: Any, node_type: Any) -> list[Any]:
    if node_type is None:
        return []
    try:
        return list(page.GetChildNodes(node_type))
    except Exception:
        return []


def _tags_text(node: Any) -> str:
    values: list[str] = []
    try:
        tags = list(getattr(node, "Tags", None) or [])
    except Exception:
        tags = []
    for tag in tags:
        for attribute in ("Label", "Status"):
            value = _text(getattr(tag, attribute, None))
            if value and value not in values:
                values.append(value)
    return " ".join(values)


def _page_streams(
    page: Any,
    source_label: str,
    page_index: int,
    revision_index: int,
    revision_kind: str,
    rich_text_type: Any,
    image_type: Any,
    attachment_type: Any,
) -> list[dict[str, str]]:
    title = _page_title(page)
    author = _text(getattr(page, "Author", None))
    created = _iso(getattr(page, "CreationTime", None))
    modified = _iso(getattr(page, "LastModifiedTime", None))
    metadata = [
        f"title={title}" if title else "",
        f"author={author}" if author else "",
        f"created={created}" if created else "",
        f"modified={modified}" if modified else "",
    ]
    metadata_suffix = "!".join(value for value in metadata if value)
    prefix = (
        f"{source_label}!onenote-page={page_index}"
        f"!revision={revision_index}:{revision_kind}"
    )
    if metadata_suffix:
        prefix += "!" + metadata_suffix

    streams: list[dict[str, str]] = []
    if title:
        streams.append({"source": prefix + "!title", "text": title})

    rich_nodes = _child_nodes(page, rich_text_type)
    rich_parts: list[str] = []
    for node in rich_nodes:
        value = getattr(node, "Text", None)
        if value is not None and str(value):
            rich_parts.append(str(value))
    body = "\n".join(rich_parts)
    if body:
        streams.append({"source": prefix + "!body", "text": body})

    for image_index, image in enumerate(_child_nodes(page, image_type), 1):
        values = [
            _text(getattr(image, "AlternativeTextTitle", None)),
            _text(getattr(image, "AlternativeTextDescription", None)),
            _text(getattr(image, "FileName", None)),
            _text(getattr(image, "HyperlinkUrl", None)),
            _tags_text(image),
        ]
        caption = " | ".join(value for value in values if value)
        if caption:
            streams.append(
                {
                    "source": prefix + f"!image={image_index}",
                    "text": caption,
                }
            )

    for attachment_index, attachment in enumerate(
        _child_nodes(page, attachment_type), 1
    ):
        values = [
            _text(getattr(attachment, "FileName", None)),
            _tags_text(attachment),
        ]
        attachment_text = " | ".join(value for value in values if value)
        if attachment_text:
            streams.append(
                {
                    "source": prefix + f"!attachment={attachment_index}",
                    "text": attachment_text,
                }
            )
    return streams


def extract_onenote_document(path: str | Path, source_label: str | None = None) -> dict[str, Any]:
    """Extract current and historical page text without modifying the .one file.

    The result keeps parser iteration order for history and labels the current
    page separately. Consumers must make any final-version decision from
    source-authored evidence rather than assuming that the newest revision is
    the envelope wording.
    """
    source_path = Path(path)
    before_hash = _sha256_file(source_path)
    try:
        from aspose.note import Document, LoadOptions, Page, RichText
    except Exception as exc:
        raise OneNoteDependencyUnavailable(
            "Install the optional aspose-note package to decode OneNote .one files"
        ) from exc

    try:
        from aspose.note import Image
    except Exception:
        Image = None
    try:
        from aspose.note import AttachedFile
    except Exception:
        AttachedFile = None

    label = source_label or source_path.name
    load_options = LoadOptions(LoadHistory=True)
    document = Document(str(source_path), load_options)
    pages = list(document.GetChildNodes(Page))

    result: dict[str, Any] = {
        "format": "onenote",
        "source": label,
        "source_sha256": before_hash,
        "pages": len(pages),
        "historical_revisions": 0,
        "streams": [],
        "warnings": [],
    }

    for page_index, page in enumerate(pages, 1):
        try:
            history = document.GetPageHistory(page)
            historical_pages = list(history) if history is not None else []
            current_page = getattr(history, "Current", None) if history is not None else None
            if current_page is None:
                current_page = page
        except Exception as exc:
            historical_pages = []
            current_page = page
            result["warnings"].append(
                f"page {page_index}: page history unavailable ({type(exc).__name__}: {exc})"
            )

        for revision_index, revision in enumerate(historical_pages):
            result["streams"].extend(
                _page_streams(
                    revision,
                    label,
                    page_index,
                    revision_index,
                    "historical",
                    RichText,
                    Image,
                    AttachedFile,
                )
            )
            result["historical_revisions"] += 1

        result["streams"].extend(
            _page_streams(
                current_page,
                label,
                page_index,
                len(historical_pages),
                "current",
                RichText,
                Image,
                AttachedFile,
            )
        )

    after_hash = _sha256_file(source_path)
    if before_hash != after_hash:
        raise RuntimeError("OneNote source changed during read-only extraction")
    return result
