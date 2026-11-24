#!/usr/bin/env python3
"""Bounded K08 hypothesis test against the 1887 Land of the Broads scan.

Tests both accepted 16-byte components as (page,word) pairs, searches source-
selected pages and the full OCR text for the exact K08 commitment, and samples
the back-of-book colour map at K07 byte-pair coordinates. This is exploratory:
a match must still be checked against the source context and edition.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "resources" / "candidate.json"
ACCEPTANCE = ROOT / "resources" / "acceptance.json"
ROUTING = ROOT / "resources" / "evidence" / "recovery-routing.json"

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*")


def normalize(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return " ".join(value.split())


def words(value: str) -> list[str]:
    # Apostrophized words count as one token; punctuation is removed only after
    # boundaries have been established.
    return [re.sub(r"[^a-z0-9]", "", token.lower().replace("’", "'"))
            for token in WORD_RE.findall(value)]


def k08(phrase: str, nonce: bytes, target: str) -> tuple[bool, str, str]:
    normalized = normalize(phrase)
    mac = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    digest = hashlib.sha256(mac).hexdigest()
    return digest == target, mac.hex().upper(), digest


def page_lines(page: fitz.Page) -> list[tuple[float, float, str]]:
    result = []
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text = "".join(s.get("text", "") for s in spans).strip()
            if text:
                result.append((min(s["bbox"][1] for s in spans),
                               max(s["bbox"][3] for s in spans), text))
    return sorted(result, key=lambda x: (x[0], x[1]))


def locate_pages(doc: fitz.Document, target_pages: list[int]) -> dict[int, dict]:
    found = {p: [] for p in target_pages}
    for page_index, page in enumerate(doc):
        height = page.rect.height
        lines = page_lines(page)
        for p in target_pages:
            for y0, y1, text in lines:
                if text.strip() == str(p) and (y0 < height * 0.15 or y1 > height * 0.85):
                    # Prefer margin folios; the page-index heuristic is used
                    # only to disambiguate duplicate OCR numbers.
                    margin_distance = min(y0, height - y1)
                    found[p].append((page_index, margin_distance, lines))
    selected = {}
    for p, hits in found.items():
        hits = sorted(hits, key=lambda x: (abs(x[0] - (p + 19)), x[1]))
        selected[p] = {
            "all_pdf_page_indices": [h[0] for h in hits],
            "selected_pdf_page_index": hits[0][0] if hits else (p + 19 if p + 19 < len(doc) else None),
            "lines": hits[0][2] if hits else None,
        }
    return selected


def page_modes(lines, page_height: float, page_no: int) -> dict[str, list[str]]:
    all_lines = [t for _, _, t in lines if t.strip() != str(page_no)]
    body = [t for y0, y1, t in lines
            if y0 >= 34 and y1 <= page_height - 34
            and t.strip() != str(page_no)
            and "THE LAND OF THE BROADS" not in t.upper()]
    no_header = [t for t in all_lines if "THE LAND OF THE BROADS" not in t.upper()]
    return {
        "all_except_folio": words(" ".join(all_lines)),
        "body_blocks": words(" ".join(body)),
        "no_running_header": words(" ".join(no_header)),
    }


def spans(tokens: list[str], nonce: bytes, target: str, min_width=2, max_width=20):
    for start in range(len(tokens)):
        for width in range(min_width, min(max_width, len(tokens) - start) + 1):
            phrase = " ".join(tokens[start:start + width])
            match, mac, digest = k08(phrase, nonce, target)
            if match:
                yield {"start_1based": start + 1, "width": width,
                       "phrase": phrase, "hmac16": mac, "sha256": digest}


def teal_stats(im: Image.Image) -> tuple[float, float]:
    pixels = list(im.getdata())
    n = len(pixels)
    colored = sum(1 for r, g, b in pixels if max(r, g, b) - min(r, g, b) > 24)
    teal = sum(1 for r, g, b in pixels
               if g > 65 and b > 65 and r < 190 and min(g, b) - r > 18)
    return colored / n, teal / n


def pixel_probe(im: Image.Image, points: list[tuple[int, int]]) -> dict:
    # Normalize candidate map to a 256-square coordinate plane. Also test the
    # transposed coordinate convention and common scan rotations/reflections.
    variants = {
        "xy": im,
        "yx": im.transpose(Image.Transpose.TRANSPOSE),
        "rot90": im.rotate(90, expand=False),
        "rot180": im.rotate(180, expand=False),
        "rot270": im.rotate(270, expand=False),
        "flip_x": ImageOps.mirror(im),
        "flip_y": ImageOps.flip(im),
        "transpose_rot90": im.transpose(Image.Transpose.TRANSPOSE).rotate(90, expand=False),
    }
    result = {}
    for name, image in variants.items():
        image = image.resize((256, 256))
        samples = []
        for x, y in points:
            r, g, b = image.getpixel((x, y))
            samples.append([r, g, b])
        g_bytes = bytes(p[1] for p in samples)
        b_bytes = bytes(p[2] for p in samples)
        min_bytes = bytes(min(p[1], p[2]) for p in samples)
        bits = {
            "green_lsb": "".join(str(p[1] & 1) for p in samples),
            "blue_lsb": "".join(str(p[2] & 1) for p in samples),
            "green_msb": "".join(str((p[1] >> 7) & 1) for p in samples),
            "blue_msb": "".join(str((p[2] >> 7) & 1) for p in samples),
            "G_LSB_even_B_MSB_odd": "".join(str((p[1] & 1) if i % 2 == 0 else ((p[2] >> 7) & 1))
                                               for i, p in enumerate(samples)),
            "B_LSB_even_G_MSB_odd": "".join(str((p[2] & 1) if i % 2 == 0 else ((p[1] >> 7) & 1))
                                               for i, p in enumerate(samples)),
        }
        result[name] = {
            "rgb_samples": samples,
            "green_hex": g_bytes.hex(), "green_ascii": g_bytes.decode("ascii", "replace"),
            "blue_hex": b_bytes.hex(), "blue_ascii": b_bytes.decode("ascii", "replace"),
            "teal_min_hex": min_bytes.hex(), "teal_min_ascii": min_bytes.decode("ascii", "replace"),
            "bit_reads": bits,
        }
    return result


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: k08_broads_pageword_probe.py BOOK.pdf", file=sys.stderr)
        return 2

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    k01 = bytes.fromhex(candidate["K01"])
    k07 = bytes.fromhex(candidate["K07"])
    k01_coords = [(k01[i], k01[i + 1]) for i in range(0, 16, 2)]
    k07_coords = [(k07[i], k07[i + 1]) for i in range(0, 16, 2)]
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    pdf_path = Path(sys.argv[1])
    doc = fitz.open(pdf_path)
    pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()

    target_pages = sorted(set([p for p, _ in k01_coords] +
                              [p for p, _ in k07_coords] + [212]))
    located = locate_pages(doc, target_pages)
    report = {
        "book_hypothesis": "The Land of the Broads (Ernest R. Suffling, 1887)",
        "pdf_sha256": pdf_hash,
        "pdf_pages": len(doc),
        "k08_target_sha256": target,
        "K01_page_word_pairs": k01_coords,
        "K07_page_word_pairs": k07_coords,
        "pages": {},
        "page_word_sequences": {},
        "selected_page_span_hits": [],
        "full_book_span_hits": [],
        "k07_map_pixel_probe": {},
    }

    modes_by_page = {}
    for p in target_pages:
        loc = located[p]
        idx = loc["selected_pdf_page_index"]
        page_report = {"all_pdf_page_indices": loc["all_pdf_page_indices"],
                       "selected_pdf_page_index": idx}
        if idx is not None:
            lines = loc["lines"] or page_lines(doc[idx])
            modes = page_modes(lines, doc[idx].rect.height, p)
            modes_by_page[p] = modes
            page_report["modes"] = {
                mode: {"word_count": len(tokens),
                       "first_20": tokens[:20]}
                for mode, tokens in modes.items()
            }
        report["pages"][str(p)] = page_report

    for component_name, coords in (("K01", k01_coords), ("K07", k07_coords)):
        for mode in ("all_except_folio", "body_blocks", "no_running_header"):
            for base in (0, 1):
                selected = []
                complete = True
                for p, word_no in coords:
                    modes = modes_by_page.get(p)
                    if not modes:
                        complete = False
                        break
                    tokens = modes[mode]
                    index = word_no - base
                    if index < 0 or index >= len(tokens):
                        complete = False
                        break
                    selected.append(tokens[index])
                if complete:
                    phrase = " ".join(selected)
                    match, mac, digest = k08(phrase, nonce, target)
                    report["page_word_sequences"][f"{component_name}|{mode}|base={base}"] = {
                        "words": selected, "phrase": phrase,
                        "normalized": normalize(phrase),
                        "hmac16": mac, "sha256": digest, "match": match,
                    }

    # Search spans on all coordinate pages plus P212.
    for p in target_pages:
        modes = modes_by_page.get(p)
        if modes:
            for hit in spans(modes["body_blocks"], nonce, target):
                report["selected_page_span_hits"].append({"page": p, **hit})

    # Search all OCR text, including phrases crossing page boundaries. Headers
    # and isolated folios are stripped; the source remains a single bounded book.
    all_tokens = []
    for page in doc:
        raw_lines = page.get_text("text").splitlines()
        body_lines = [line for line in raw_lines
                      if line.strip() and "THE LAND OF THE BROADS" not in line.upper()
                      and not re.fullmatch(r"\s*\d{1,4}\s*", line)]
        all_tokens.extend(words(" ".join(body_lines)))
    for hit in spans(all_tokens, nonce, target):
        report["full_book_span_hits"].append(hit)

    # The map is explicitly described as being at the back. Restrict image
    # scoring to the last 80 scans rather than rasterizing the whole book.
    map_scores = []
    start_index = max(0, len(doc) - 80)
    for page_index in range(start_index, len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.12, 0.12),
                              colorspace=fitz.csRGB, alpha=False)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        im = im.resize((256, 256))
        color_fraction, teal_fraction = teal_stats(im)
        map_scores.append({
            "pdf_page_index": page_index,
            "page_width": round(page.rect.width, 1),
            "page_height": round(page.rect.height, 1),
            "landscape": page.rect.width > page.rect.height,
            "color_fraction": round(color_fraction, 5),
            "teal_fraction": round(teal_fraction, 5),
            "text_excerpt": normalize(page.get_text("text"))[:180],
            "image": im,
        })
    top = sorted(map_scores, key=lambda x: (x["teal_fraction"], x["color_fraction"]), reverse=True)[:12]
    points = k07_coords
    map_report = []
    for item in top:
        im = item["image"]
        # Crop to non-white map content as well as testing the full page.
        gray = ImageOps.grayscale(im)
        bbox = gray.point(lambda p: 255 if p < 245 else 0).getbbox()
        cropped = im.crop(bbox) if bbox else im
        cropped = cropped.resize((256, 256))
        out = {k: v for k, v in item.items() if k != "image"}
        out["full_page_samples"] = pixel_probe(im, points)
        out["content_crop_samples"] = pixel_probe(cropped, points)
        map_report.append(out)
    report["k07_map_pixel_probe"] = {
        "coordinate_pairs": points,
        "scanned_pdf_page_range": [start_index, len(doc) - 1],
        "top_color_pages": map_report,
    }

    matched = any(x["match"] for x in report["page_word_sequences"].values())
    matched = matched or bool(report["selected_page_span_hits"]) or bool(report["full_book_span_hits"])

    # This probe reads accepted component bytes and a K08 nonce locally. Never
    # publish their coordinate pairs, candidate phrases, MACs, or target values.
    # Preserve only an aggregate, reproducible outcome summary.
    safe_report = {
        "status": "candidate_match_requires_private_review" if matched else "bounded_negative",
        "book_hypothesis": report["book_hypothesis"],
        "pdf_sha256": pdf_hash,
        "pdf_pages": len(doc),
        "tested": {
            "coordinate_page_count": len(target_pages),
            "page_word_sequence_tests": len(report["page_word_sequences"]),
            "selected_page_span_hits": len(report["selected_page_span_hits"]),
            "full_book_span_hits": len(report["full_book_span_hits"]),
            "map_scan_page_range": [start_index, len(doc) - 1],
        },
        "outcome": {
            "candidate_match": matched,
            "exact_phrase_recovered": False,
            "map_probe": {
                "top_ranked_color_scan_pages": [item["pdf_page_index"] for item in map_report],
                "max_teal_fraction": max(
                    (item["teal_fraction"] for item in map_report), default=0.0
                ),
            },
        },
        "limitations": [
            "The title is not named in the surviving H-17 evidence; this remains an unverified candidate.",
            "The map may be omitted from this scan or the physical copy/edition may differ.",
            "No candidate, acceptance, routing, or verifier data was changed.",
            "Accepted-component coordinates, candidate wording, and nonce-derived values are intentionally omitted.",
        ],
    }
    out_path = ROOT / "agents" / "agent21" / "broads-pageword-results.json"
    out_path.write_text(json.dumps(safe_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(safe_report, indent=2, ensure_ascii=False))
    print("K08_MATCH", matched)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
