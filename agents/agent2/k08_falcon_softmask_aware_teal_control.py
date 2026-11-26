#!/usr/bin/env python3
"""Mask-aware control for the public Falcon rear-map JPX images.

The source-literal teal-bit layouts match work/h17_k08_teal_bit_image_scan.py:
- teal HSV gate H=110..150, S>=64, V>=32;
- green or blue channel;
- selected bit is pixel-index parity (even -> bit 0, odd -> bit 1);
- offsets 0..7, MSB/LSB packing, and normal/complemented streams.

This control additionally intersects the teal gate with the PDF image soft mask.
It prints no candidate phrase or recovery component.
"""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

ASCII_RUN = re.compile(r"[\x20-\x7e]{4,}")
WORD = re.compile(r"[a-z0-9]+")
EXPECTED_JPX = {
    343: "72579cdc18d555fb43cfbb46897b724f1b0c3d79bbb06a9137755bad63883c21",
    344: "8ce15ec1d5c56b1472464a642d10d17ba36270337c20fb05a071e9b5ba6b1053",
}
EXPECTED_MASK_SAMPLES = {
    343: "85655151941ce3948a96b3b8d558a287a250788bdfdb63235e64bce0ea717a59",
    344: "304e523db23c0f30f7eda1b0143e2a8fd15b77bd6379a22e783c86d905af3b1b",
}


def normalize_phrase(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return " ".join(value.split())


def candidate_runs(payload: bytes):
    decoded = payload.decode("latin1", errors="ignore")
    for match in ASCII_RUN.finditer(decoded):
        yield match.group(0)
    for encoding in ("utf-16le", "utf-16be"):
        text = payload.decode(encoding, errors="ignore")
        for match in ASCII_RUN.finditer(text):
            yield match.group(0)


def ngrams(run: str):
    words = WORD.findall(run.lower())
    for start in range(len(words)):
        phrase_words = []
        for end in range(start, min(len(words), start + 48)):
            phrase_words.append(words[end])
            phrase = " ".join(phrase_words)
            if len(phrase) > 96:
                break
            if len(phrase) >= 8:
                yield phrase


def image_records(doc: fitz.Document):
    for page_number in (343, 344):
        page = doc.load_page(page_number - 1)
        matches = []
        for item in page.get_images(full=True):
            xref, smask, width, height = item[:4]
            if smask and (width, height) in ((3626, 2167), (3595, 2119)):
                raw = doc.xref_stream(xref)
                digest = hashlib.sha256(raw).hexdigest()
                if digest == EXPECTED_JPX[page_number]:
                    matches.append((xref, smask, digest))
        if len(matches) != 1:
            raise RuntimeError(
                f"expected one pinned JPX+softmask image on page {page_number}; found {len(matches)}"
            )
        yield page_number, matches[0]


def scan_rgb(rgb: np.ndarray, alpha: np.ndarray | None, nonce: bytes, target: str):
    hsv = np.asarray(Image.fromarray(rgb, mode="RGB").convert("HSV"), dtype=np.uint8)
    teal = (
        (hsv[:, :, 0] >= 110)
        & (hsv[:, :, 0] <= 150)
        & (hsv[:, :, 1] >= 64)
        & (hsv[:, :, 2] >= 32)
    )
    raw_count = int(teal.sum())
    if alpha is not None:
        teal &= alpha > 0
    visible_count = int(teal.sum())
    indices = np.flatnonzero(teal.ravel(order="C"))
    matches = []
    windows = 0
    for channel_name, channel_index in (("green", 1), ("blue", 2)):
        values = rgb[:, :, channel_index].ravel(order="C")[indices]
        parity = (indices & 1).astype(np.uint8)
        bits = ((values >> parity) & 1).astype(np.uint8)
        for offset in range(8):
            aligned = bits[offset:]
            for bit_order in ("big", "little"):
                packed = np.packbits(aligned, bitorder=bit_order).tobytes()
                for complemented, payload in (
                    (False, packed),
                    (True, bytes(x ^ 0xFF for x in packed)),
                ):
                    for run in candidate_runs(payload):
                        for candidate in ngrams(run):
                            windows += 1
                            normalized = normalize_phrase(candidate)
                            component = hmac.new(
                                nonce, normalized.encode("utf-8"), hashlib.sha256
                            ).digest()[:16]
                            if hashlib.sha256(component).hexdigest().lower() == target.lower():
                                matches.append(
                                    {
                                        "channel": channel_name,
                                        "offset": offset,
                                        "bit_order": bit_order,
                                        "complemented": complemented,
                                        "phrase_sha256": hashlib.sha256(
                                            normalized.encode("utf-8")
                                        ).hexdigest(),
                                    }
                                )
    return raw_count, visible_count, windows, matches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--resource-root", type=Path, default=Path("resources"))
    args = parser.parse_args()
    evidence = args.resource_root / "evidence"
    routing = json.loads((evidence / "recovery-routing.json").read_text())
    acceptance = json.loads((args.resource_root / "acceptance.json").read_text())
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    pdf_sha = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
    print("pdf_sha256", pdf_sha)
    doc = fitz.open(args.pdf)
    for page_number, (xref, smask, image_sha) in image_records(doc):
        pix = fitz.Pixmap(doc, xref)
        mask = fitz.Pixmap(doc, smask)
        rgb = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )[:, :, :3].copy()
        alpha = np.frombuffer(mask.samples, dtype=np.uint8).reshape(
            mask.height, mask.width
        ).copy()
        raw_count, _, raw_windows, raw_hits = scan_rgb(rgb, None, nonce, target)
        _, visible_count, visible_windows, visible_hits = scan_rgb(
            rgb, alpha, nonce, target
        )
        mask_sha = hashlib.sha256(mask.samples).hexdigest()
        if mask_sha != EXPECTED_MASK_SAMPLES[page_number]:
            raise RuntimeError(
                f"soft-mask pixel hash mismatch on page {page_number}: {mask_sha}"
            )
        print(
            json.dumps(
                {
                    "page": page_number,
                    "jpx_sha256": image_sha,
                    "softmask_samples_sha256": mask_sha,
                    "dimensions": [pix.width, pix.height],
                    "softmask_nonzero_pixels": int((alpha > 0).sum()),
                    "raw_teal_pixels": raw_count,
                    "visible_teal_pixels": visible_count,
                    "raw_candidate_windows": raw_windows,
                    "visible_candidate_windows": visible_windows,
                    "raw_hmac_matches": len(raw_hits),
                    "visible_hmac_matches": len(visible_hits),
                    "match_layouts": raw_hits + visible_hits,
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
