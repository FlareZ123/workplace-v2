"""Read-only K04 coupon extraction from original raster barcode media.

Decoded symbols are UNTRUSTED until compared against the unchanged original
K04 slot SHA256 with the unchanged route XOR mask. Pillow is required; pyzbar
(zbar) and OpenCV are optional independent symbol detectors.
"""
from __future__ import annotations

import io

MAX_BARCODE_PIXELS = 24_000_000


def read_image_barcodes(data: bytes) -> tuple[list[tuple[str, bytes]], list[str]]:
    """Return distinct (symbology, bytes) and decoder-coverage diagnostics."""
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        return [], ["Pillow unavailable: image coupon not decoded"]
    try:
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            if width <= 0 or height <= 0 or width * height > MAX_BARCODE_PIXELS:
                return [], ["Image exceeds 24 million pixels; barcode decoding skipped"]
            image.load()
            results: list[tuple[str, bytes]] = []
            failures: list[str] = []
            try:
                from pyzbar.pyzbar import decode
                for code in decode(image):
                    if not code.data:
                        continue
                    payload = bytes(code.data)
                    results.append((str(code.type), payload))
                    # zbar may decode QR ISO-8859-1 data as UTF-8 octets.
                    # The original bytes are preserved as an additional view.
                    if code.type == "QRCODE":
                        try:
                            latin1 = payload.decode("utf-8").encode("latin-1")
                        except (UnicodeDecodeError, UnicodeEncodeError):
                            pass
                        else:
                            if latin1 != payload:
                                results.append(("QRCODE-latin1", latin1))
            except (ImportError, OSError) as exc:
                failures.append(f"pyzbar unavailable: {type(exc).__name__}")
            if not results:
                try:
                    import cv2
                    import numpy as np
                except (ImportError, OSError) as exc:
                    failures.append(f"OpenCV QR fallback unavailable: {type(exc).__name__}")
                else:
                    try:
                        detector = cv2.QRCodeDetector()
                        grayscale = np.asarray(image.convert("L"))
                        success, values, _, _ = detector.detectAndDecodeMulti(grayscale)
                        if success:
                            results.extend(
                                ("QRCODE-cv2", value.encode("utf-8"))
                                for value in values if value
                            )
                        if not results:
                            value, _, _ = detector.detectAndDecode(grayscale)
                            if value:
                                results.append(("QRCODE-cv2", value.encode("utf-8")))
                    except cv2.error as exc:
                        failures.append(f"OpenCV QR fallback failed: {type(exc).__name__}")
            return list(dict.fromkeys(results)), failures
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        return [], [f"Image could not be decoded: {type(exc).__name__}"]
