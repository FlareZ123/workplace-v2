#!/usr/bin/env python3
"""Apply the frozen teal-mask / LOW-IF-EVEN K08 decoder to the 1889 Falcon rear foldout.

This is a new carrier test, distinct from the prior grayscale six-slot coordinate
and water/land topology controls. The title-to-David physical-copy relationship
remains unproven. No candidate text is emitted unless the unchanged K08 HMAC
and component commitment both match.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path("work").resolve()))
import h17_k08_teal_bit_image_scan as teal_scanner

PDF = Path("agent41-k08-falcon-map-control/falcononbalticc00knig.pdf")
OUT = Path("agent41-k08-falcon-map-control/teal-bit-test")
EXPECTED_PDF_SHA256 = "071e2f16f2a172478e82e7172cabac21960d4b5bc9bd96a7ba90a1152f200167"
PAGE_INDICES = (342, 343)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render_color_pages() -> dict[int, Path]:
    if not PDF.is_file():
        raise FileNotFoundError(f"the existing Falcon map-control run did not leave {PDF}")
    actual_pdf_sha = sha256(PDF)
    if actual_pdf_sha != EXPECTED_PDF_SHA256:
        raise ValueError(f"unexpected Falcon PDF SHA-256: {actual_pdf_sha}")
    OUT.mkdir(parents=True, exist_ok=True)
    document = fitz.open(PDF)
    if document.page_count != 350:
        raise ValueError(f"unexpected PDF page count: {document.page_count}")

    paths: dict[int, Path] = {}
    for index in PAGE_INDICES:
        page = document.load_page(index)
        if page.rect.width <= page.rect.height:
            raise ValueError(f"expected landscape foldout page at index {index}")
        pix = page.get_pixmap(
            matrix=fitz.Matrix(2.0, 2.0),
            colorspace=fitz.csRGB,
            alpha=False,
        )
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        path = OUT / f"page-{index:04d}-color.png"
        image.save(path)
        paths[index] = path
    document.close()
    return paths


def stitch_color_foldout(left_path: Path, right_path: Path) -> tuple[Path, dict]:
    left_bgr = cv2.imread(str(left_path), cv2.IMREAD_COLOR)
    right_bgr = cv2.imread(str(right_path), cv2.IMREAD_COLOR)
    if left_bgr is None or right_bgr is None:
        raise ValueError("both color foldout halves must be readable")
    left_gray = cv2.cvtColor(left_bgr, cv2.COLOR_BGR2GRAY)
    right_gray = cv2.cvtColor(right_bgr, cv2.COLOR_BGR2GRAY)

    cv2.setRNGSeed(417)
    sift = cv2.SIFT_create(nfeatures=8000)
    left_start = int(round(left_gray.shape[1] * 0.40))
    right_end = int(round(right_gray.shape[1] * 0.60))
    kp_left, des_left = sift.detectAndCompute(left_gray[:, left_start:], None)
    kp_right, des_right = sift.detectAndCompute(right_gray[:, :right_end], None)
    if des_left is None or des_right is None:
        raise ValueError("insufficient SIFT descriptors for the rear foldout")
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    pairs = matcher.knnMatch(des_right, des_left, k=2)
    good = [m for m, n in pairs if m.distance < 0.70 * n.distance]
    if len(good) < 20:
        raise ValueError(f"insufficient foldout matches: {len(good)}")

    src = np.float32([kp_right[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([
        (kp_left[m.trainIdx].pt[0] + left_start, kp_left[m.trainIdx].pt[1])
        for m in good
    ]).reshape(-1, 1, 2)
    homography, inlier_mask = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
    if homography is None or inlier_mask is None:
        raise ValueError("foldout homography could not be estimated")

    right_corners = np.float32([
        [0, 0], [right_bgr.shape[1], 0],
        [right_bgr.shape[1], right_bgr.shape[0]], [0, right_bgr.shape[0]],
    ]).reshape(-1, 1, 2)
    warped_corners = cv2.perspectiveTransform(right_corners, homography).reshape(-1, 2)
    left_corners = np.float32([
        [0, 0], [left_bgr.shape[1], 0],
        [left_bgr.shape[1], left_bgr.shape[0]], [0, left_bgr.shape[0]],
    ])
    all_corners = np.vstack([left_corners, warped_corners])
    x0, y0 = np.floor(all_corners.min(axis=0)).astype(int)
    x1, y1 = np.ceil(all_corners.max(axis=0)).astype(int)
    translate = np.array([
        [1.0, 0.0, -x0],
        [0.0, 1.0, -y0],
        [0.0, 0.0, 1.0],
    ])
    width, height = int(x1 - x0), int(y1 - y0)

    warped = cv2.warpPerspective(
        right_bgr, translate @ homography, (width, height),
        borderValue=(255, 255, 255),
    )
    canvas = np.full((height, width, 3), 255, dtype=np.uint8)
    lx, ly = -x0, -y0
    canvas[ly:ly + left_bgr.shape[0], lx:lx + left_bgr.shape[1]] = left_bgr
    stitched = np.minimum(canvas, warped)

    path = OUT / "falcon-1889-rear-map-color-stitched.png"
    Image.fromarray(cv2.cvtColor(stitched, cv2.COLOR_BGR2RGB)).save(path)
    info = {
        "ratio_test_matches": len(good),
        "ransac_inliers": int(inlier_mask.ravel().sum()),
        "canvas_width": width,
        "canvas_height": height,
        "right_to_left_homography": homography.tolist(),
        "source_pages_zero_based": list(PAGE_INDICES),
    }
    return path, info


def teal_pixel_count(path: Path) -> tuple[int, tuple[int, int]]:
    with Image.open(path) as opened:
        image = opened.convert("RGB")
        hsv = np.asarray(image.convert("HSV"), dtype=np.uint8)
        mask = (
            (hsv[:, :, 0] >= 110) & (hsv[:, :, 0] <= 150)
            & (hsv[:, :, 1] >= 64) & (hsv[:, :, 2] >= 32)
        )
        return int(mask.sum()), image.size


def main() -> int:
    pages = render_color_pages()
    stitched_path, stitch_info = stitch_color_foldout(pages[342], pages[343])
    nonce, commitment = teal_scanner.load_commitment(Path("resources"))

    image_paths = [pages[342], pages[343], stitched_path]
    image_results = []
    all_matches = []
    for path in image_paths:
        count, size = teal_pixel_count(path)
        matches = teal_scanner.scan_image(path, nonce, commitment)
        all_matches.extend(matches)
        image_results.append({
            "file": str(path),
            "sha256": sha256(path),
            "size_pixels": list(size),
            "teal_mask_pixel_count": count,
            "exact_k08_matches": len(matches),
            "matches": matches,
        })

    summary = {
        "status": "MATCH" if all_matches else "NO_EXACT_K08_MATCH",
        "source": {
            "internet_archive_identifier": "falcononbalticc00knig",
            "edition": "1889",
            "pdf_sha256": EXPECTED_PDF_SHA256,
            "pdf_page_count": 350,
            "rear_foldout_page_indices_zero_based": list(PAGE_INDICES),
            "physical_identity_caveat": (
                "The surviving MAIL-09 identifies only an unnamed David-owned "
                "map-back book; this public Falcon edition is not authenticated "
                "as his physical copy."
            ),
        },
        "decoder": {
            "implementation": "work/h17_k08_teal_bit_image_scan.py",
            "pre_registered_layouts": [
                "teal-mask-green-low-if-even",
                "teal-mask-blue-low-if-even",
            ],
            "controls": "the scanner's unchanged bounded channel/bit-order controls",
            "teal_mask": "PIL HSV H=110..150, S>=64, V>=32",
            "pixel_order": "row-major",
            "parity": "absolute pixel index even -> bit 0; odd -> bit 1",
            "acceptance": "unchanged K08 normalization, HMAC, and component commitment",
            "candidate_texts_emitted_only_on_exact_match": True,
        },
        "stitch": stitch_info,
        "images": image_results,
        "exact_k08_matches": all_matches,
        "interpretation": (
            "A hit would be a candidate requiring an independent source join. "
            "A no-hit applies only to this public 1889 edition and these frozen "
            "decoder layouts; it does not identify or falsify David's physical copy."
        ),
    }
    report_path = OUT / "teal-bit-scan.json"
    report_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
