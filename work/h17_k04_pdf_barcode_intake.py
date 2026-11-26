"""Read-only raster extraction of QR/barcode image carriers from native PDF coupons.

Temporarily quarantined: public entry points deny access before hashing or parsing.
This is not OCR. Existing image and QR decoders inspect original embedded
raster images and the preserved PDF page rendering. Do not decrypt protected
PDFs, infer missing words, or accept a symbol without the original K04
SHA256 and route-mask comparison.

PyMuPDF official API:
https://pymupdf.readthedocs.io/en/latest/document.html
https://pymupdf.readthedocs.io/en/latest/page.html
"""
from __future__ import annotations

from collections.abc import Iterator
import hashlib
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
if str(WORK) not in sys.path:
    sys.path.insert(0, str(WORK))
from h17_ax7782_object_intake import OPAQUE_PDF_SHA256

_MAX_PAGES = 24
_MAX_RENDER_PIXELS = 20_000_000
_MAX_PDF_IMAGE_BYTES = 32 * 1024 * 1024
_MAX_TOTAL_IMAGE_BYTES = 128 * 1024 * 1024


def _is_hash_only_pdf(data: bytes) -> bool:
    """Identify the quarantined PDF using SHA-256 only; never parse its bytes."""
    return hashlib.sha256(data).hexdigest() == OPAQUE_PDF_SHA256


def iter_pdf_embedded_files(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Extract actual PDF portfolio /EmbeddedFiles attachments, read-only."""
    # No independently authenticated PDF or derivative is admitted at present.
    # Fail before hashing, importing a parser, or opening an in-memory document.
    raise PermissionError("PDF intake quarantined pending independent source authorization")
    if _is_hash_only_pdf(data):
        return
    try:
        import pymupdf
    except ImportError:
        return
    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            if doc.needs_pass:
                return
            for name in doc.embfile_names()[:32]:
                info = doc.embfile_info(name)
                if not 0 < int(info.get("size", 0)) <= _MAX_PDF_IMAGE_BYTES:
                    continue
                raw = doc.embfile_get(name)
                if len(raw) <= _MAX_PDF_IMAGE_BYTES:
                    filename = str(info.get("filename") or name)
                    filename = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
                    yield filename, raw
            for page_index in range(min(doc.page_count, _MAX_PAGES)):
                page = doc.load_page(page_index)
                for index, annotation in enumerate(
                    page.annots(types=(pymupdf.PDF_ANNOT_FILE_ATTACHMENT,)) or ()
                ):
                    if index >= 32:
                        break
                    info = annotation.file_info
                    if not 0 < int(info.get("size", 0)) <= _MAX_PDF_IMAGE_BYTES:
                        continue
                    raw = annotation.get_file()
                    if len(raw) <= _MAX_PDF_IMAGE_BYTES:
                        filename = str(info.get("filename") or f"page-{page_index+1}-file-{index}")
                        filename = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
                        yield filename, raw
    except (RuntimeError, ValueError, OSError):
        return


def iter_pdf_coupon_text(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Extract native PDF text before considering bitmap-only symbol carriers.

    Native text is checked exactly as transcribed and once without whitespace
    or punctuation separators to support multi-run hexadecimal labels.
    The original 16-byte hash determines acceptance, not a text guess.
    """
    # No independently authenticated PDF or derivative is admitted at present.
    # Fail before hashing, importing a parser, or opening an in-memory document.
    raise PermissionError("PDF intake quarantined pending independent source authorization")
    if _is_hash_only_pdf(data):
        return
    try:
        import pymupdf
    except ImportError:
        return
    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            if doc.needs_pass:
                return
            for page_index in range(min(doc.page_count, _MAX_PAGES)):
                source = f"pdf-page-{page_index+1}"
                page = doc.load_page(page_index)
                for index, annotation in enumerate(page.annots() or ()):
                    if index >= 512:
                        break
                    for field in ("content", "subject", "title"):
                        value = annotation.info.get(field)
                        if isinstance(value, str) and 0 < len(value) <= 1_000_000:
                            yield f"{source}-annotation-{index}-{field}", value.encode("utf-8")
                for index, widget in enumerate(page.widgets() or ()):
                    if index >= 512:
                        break
                    value = widget.field_value
                    if isinstance(value, str) and 0 < len(value) <= 1_000_000:
                        yield f"{source}-form-field-{index}", value.encode("utf-8")
                text = page.get_text("text", sort=True)
                if not text or len(text) > 1_000_000:
                    continue
                yield f"{source}-native-text", text.encode("utf-8")
                condensed = "".join(
                    ch for ch in text if ch not in " \t\r\n:.-"
                )
                if condensed != text:
                    yield f"{source}-condensed-text", condensed.encode("utf-8")
    except (RuntimeError, ValueError, OSError):
        return


def iter_pdf_barcode_images(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Yield bounded original embedded images and rendered PDF pages.

    An encrypted PDF produces no images. Any missing optional backend is
    visible as the absence of outputs; the caller owns coverage diagnostics.
    """
    # No independently authenticated PDF or derivative is admitted at present.
    # Fail before hashing, importing a parser, or opening an in-memory document.
    raise PermissionError("PDF intake quarantined pending independent source authorization")
    if _is_hash_only_pdf(data):
        return
    try:
        import pymupdf
    except ImportError:
        return
    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            if doc.needs_pass:
                return
            budget = 0
            seen_xrefs: set[int] = set()
            for page_index in range(min(doc.page_count, _MAX_PAGES)):
                page = doc.load_page(page_index)
                for image_info in page.get_images(full=True):
                    xref = int(image_info[0])
                    if xref in seen_xrefs:
                        continue
                    seen_xrefs.add(xref)
                    image = doc.extract_image(xref)
                    if image is None:
                        continue
                    raw = image["image"]
                    if (not raw or len(raw) > _MAX_PDF_IMAGE_BYTES
                            or budget + len(raw) > _MAX_TOTAL_IMAGE_BYTES):
                        continue
                    budget += len(raw)
                    yield f"pdf-page-{page_index+1}-embedded-image-xref-{xref}", raw
                width = int(page.rect.width * 200 / 72) + 2
                height = int(page.rect.height * 200 / 72) + 2
                if (width <= 0 or height <= 0
                        or width * height > _MAX_RENDER_PIXELS):
                    continue
                pix = page.get_pixmap(dpi=200, alpha=False)
                if pix.width * pix.height > _MAX_RENDER_PIXELS:
                    continue
                raw = pix.tobytes("png")
                if budget + len(raw) > _MAX_TOTAL_IMAGE_BYTES:
                    return
                budget += len(raw)
                yield f"pdf-page-{page_index+1}-rendered-200dpi", raw
    except (RuntimeError, ValueError, OSError):
        return
