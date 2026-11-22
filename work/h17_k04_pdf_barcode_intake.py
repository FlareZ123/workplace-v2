"""Read-only raster extraction of QR/barcode image carriers from native PDF coupons.

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

_MAX_PAGES = 24
_MAX_RENDER_PIXELS = 20_000_000
_MAX_PDF_IMAGE_BYTES = 32 * 1024 * 1024
_MAX_TOTAL_IMAGE_BYTES = 128 * 1024 * 1024


def iter_pdf_barcode_images(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Yield bounded original embedded images and rendered PDF pages.

    An encrypted PDF produces no images. Any missing optional backend is
    visible as the absence of outputs; the caller owns coverage diagnostics.
    """
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
