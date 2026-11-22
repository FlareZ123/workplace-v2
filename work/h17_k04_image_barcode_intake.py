"""Read-only K04 coupon extraction from original raster barcode media.

Decoded symbols are untrusted until compared against the unchanged original
K04 slot commitment and route mask. Pillow is required; pyzbar (zbar) and
OpenCV are optional independent symbol detectors.
"""
from __future__ import annotations

import io

MAX_BARCODE_PIXELS = 24_000_000
MAX_BARCODE_FRAMES = 32


def read_image_barcodes(data: bytes) -> tuple[list[tuple[str, bytes]], list[str]]:
    """Return distinct (symbology/frame, bytes) and decoder diagnostics."""
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        return [], ["Pillow unavailable: image coupon not decoded"]
    try:
        with Image.open(io.BytesIO(data)) as image:
            results: list[tuple[str, bytes]] = []
            failures: list[str] = []
            total_pixels = 0
            frames = getattr(image, "n_frames", 1)
            if frames > MAX_BARCODE_FRAMES:
                failures.append("Only the first 32 image frames are decoded")
            for frame in range(min(frames, MAX_BARCODE_FRAMES)):
                image.seek(frame)
                width, height = image.size
                total_pixels += width * height
                if width <= 0 or height <= 0 or total_pixels > MAX_BARCODE_PIXELS:
                    failures.append("24-million-pixel cumulative frame bound reached")
                    break
                image.load()
                before = len(results)
                try:
                    from pyzbar.pyzbar import decode
                    for code in decode(image):
                        if not code.data:
                            continue
                        payload = bytes(code.data)
                        results.append((f"{code.type}-frame{frame}", payload))
                        if code.type == "QRCODE":
                            try:
                                latin1 = payload.decode("utf-8").encode("latin-1")
                            except (UnicodeDecodeError, UnicodeEncodeError):
                                pass
                            else:
                                if latin1 != payload:
                                    results.append((f"QRCODE-latin1-frame{frame}", latin1))
                except (ImportError, OSError) as exc:
                    failures.append(f"pyzbar unavailable: {type(exc).__name__}")
                if len(results) == before:
                    try:
                        import cv2
                        import numpy as np
                    except (ImportError, OSError) as exc:
                        failures.append(f"OpenCV QR fallback unavailable: {type(exc).__name__}")
                    else:
                        try:
                            detector = cv2.QRCodeDetector()
                            gray = np.asarray(image.convert("L"))
                            success, values, _, _ = detector.detectAndDecodeMulti(gray)
                            if success:
                                results.extend(
                                    (f"QRCODE-cv2-frame{frame}", s.encode("utf-8"))
                                    for s in values if s
                                )
                            if len(results) == before:
                                s, _, _ = detector.detectAndDecode(gray)
                                if s:
                                    results.append((f"QRCODE-cv2-frame{frame}", s.encode("utf-8")))
                        except cv2.error as exc:
                            failures.append(f"OpenCV QR fallback failed: {type(exc).__name__}")
            return list(dict.fromkeys(results)), list(dict.fromkeys(failures))
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        return [], [f"Image could not be decoded: {type(exc).__name__}"]
