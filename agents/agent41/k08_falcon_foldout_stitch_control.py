#!/usr/bin/env python3
"""Reconstruct a two-page Falcon foldout and run the frozen six-slot image control.

Inputs are the two landscape page renders from Agent41's exact 1889 Internet
Archive acquisition. The stitch is source-image geometry only: no K08
commitment, phrase text, nonce, or target value enters feature matching,
homography estimation, or pixel sampling.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from k08_multislot_teal_coordinate_control import KNOWN_SLOTS, coordinates, sample_byte


def stitch(left_path: Path, right_path: Path) -> tuple[np.ndarray, dict[str, object]]:
    left = cv2.imread(str(left_path), cv2.IMREAD_GRAYSCALE)
    right = cv2.imread(str(right_path), cv2.IMREAD_GRAYSCALE)
    if left is None or right is None:
        raise ValueError("both page renders must be readable grayscale images")

    cv2.setRNGSeed(417)
    sift = cv2.SIFT_create(nfeatures=8000)

    left_start = int(round(left.shape[1] * 0.40))
    right_end = int(round(right.shape[1] * 0.60))
    left_crop = left[:, left_start:]
    right_crop = right[:, :right_end]

    kp_left, des_left = sift.detectAndCompute(left_crop, None)
    kp_right, des_right = sift.detectAndCompute(right_crop, None)
    if des_left is None or des_right is None:
        raise ValueError("insufficient foldout features for stitching")

    matcher = cv2.BFMatcher(cv2.NORM_L2)
    pairs = matcher.knnMatch(des_right, des_left, k=2)
    good = [m for m, n in pairs if m.distance < 0.70 * n.distance]
    if len(good) < 20:
        raise ValueError("insufficient ratio-test matches for foldout homography")

    src = np.float32([kp_right[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([
        (kp_left[m.trainIdx].pt[0] + left_start, kp_left[m.trainIdx].pt[1])
        for m in good
    ]).reshape(-1, 1, 2)

    homography, mask = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
    if homography is None or mask is None:
        raise ValueError("foldout homography could not be estimated")

    right_corners = np.float32([
        [0, 0],
        [right.shape[1], 0],
        [right.shape[1], right.shape[0]],
        [0, right.shape[0]],
    ]).reshape(-1, 1, 2)
    warped_corners = cv2.perspectiveTransform(right_corners, homography).reshape(-1, 2)
    left_corners = np.float32([
        [0, 0],
        [left.shape[1], 0],
        [left.shape[1], left.shape[0]],
        [0, left.shape[0]],
    ])
    all_corners = np.vstack([left_corners, warped_corners])
    x0, y0 = np.floor(all_corners.min(axis=0)).astype(int)
    x1, y1 = np.ceil(all_corners.max(axis=0)).astype(int)
    translate = np.array([[1.0, 0.0, -x0], [0.0, 1.0, -y0], [0.0, 0.0, 1.0]])
    width, height = int(x1 - x0), int(y1 - y0)

    warped = cv2.warpPerspective(
        right,
        translate @ homography,
        (width, height),
        borderValue=255,
    )
    canvas = np.full((height, width), 255, dtype=np.uint8)
    ly, lx = -y0, -x0
    canvas[ly:ly + left.shape[0], lx:lx + left.shape[1]] = left
    stitched = np.minimum(canvas, warped)

    info = {
        "ratio_test_matches": len(good),
        "ransac_inliers": int(mask.ravel().sum()),
        "canvas_width": width,
        "canvas_height": height,
        "right_to_left_homography": homography.tolist(),
        "warped_right_corners": warped_corners.tolist(),
    }
    return stitched, info


def scan(image: np.ndarray, candidate: dict[str, str]) -> dict[str, object]:
    slot_coords = {slot: coordinates(candidate[slot]) for slot in KNOWN_SLOTS}
    pil = Image.fromarray(image, mode="L")

    rows: list[dict[str, object]] = []
    for mapping in ("direct", "scaled"):
        for orientation in range(8):
            for bitplane in range(8):
                for bitorder in ("msb", "lsb"):
                    raw = bytes(
                        sample_byte(
                            pil,
                            slot_coords[slot],
                            mapping,
                            orientation,
                            bitplane,
                            bitorder,
                        )
                        for slot in KNOWN_SLOTS
                    )
                    printable = sum(0x20 <= value <= 0x7E for value in raw)
                    letters = sum(
                        0x41 <= value <= 0x5A or 0x61 <= value <= 0x7A
                        for value in raw
                    )
                    rows.append({
                        "mapping": mapping,
                        "orientation": orientation,
                        "bitplane": bitplane,
                        "bitorder": bitorder,
                        "hex": raw.hex().upper(),
                        "ascii": "".join(
                            chr(value) if 0x20 <= value <= 0x7E else "."
                            for value in raw
                        ),
                        "printable_bytes": printable,
                        "ascii_letters": letters,
                    })

    rows.sort(
        key=lambda row: (
            int(row["printable_bytes"]),
            int(row["ascii_letters"]),
            str(row["hex"]),
        ),
        reverse=True,
    )
    return {
        "configurations_tested": len(rows),
        "six_printable_count": sum(int(row["printable_bytes"]) == 6 for row in rows),
        "five_or_more_printable_count": sum(int(row["printable_bytes"]) >= 5 for row in rows),
        "best": rows[:32],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    stitched, stitch_info = stitch(args.left, args.right)
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    scan_info = scan(stitched, candidate)

    args.out.mkdir(parents=True, exist_ok=True)
    image_path = args.out / "falcon-1889-foldout-stitched.png"
    cv2.imwrite(str(image_path), stitched)
    result = {"stitch": stitch_info, "scan": scan_info}
    (args.out / "foldout-control.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
