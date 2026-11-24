#!/usr/bin/env python3
"""Test the source-selected K01 page/word coordinates against a public map-back book.

This is a bounded hypothesis test, not an assertion that this is the authenticated
book. It reads the accepted K01 bytes and K08 commitment from the repository,
locates printed page numbers in the supplied PDF, and tests the eight (page,word)
pairs in signed A/B/C/D order. It also searches contiguous spans on those eight
pages. No candidate or acceptance file is modified.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "resources" / "candidate.json"
ACCEPTANCE = ROOT / "resources" / "acceptance.json"
ROUTING = ROOT / "resources" / "evidence" / "recovery-routing.json"

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*")
TARGET_PAGES = (4, 171, 28, 122, 205, 96, 67, 201)


def normalize(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return " ".join(value.split())


def words(value: str) -> list[str]:
    # Count apostrophized words as one token; remove punctuation only after
    # token boundaries have been established.
    return [re.sub(r"[^a-z0-9]", "", token.lower().replace("’", "'"))
            for token in WORD_RE.findall(value)]


def k08_matches(phrase: str, nonce: bytes, target: str) -> tuple[bool, str, str]:
    normalized = normalize(phrase)
    mac = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    digest = hashlib.sha256(mac).hexdigest()
    return digest == target, mac.hex().upper(), digest


def line_texts(page: fitz.Page) -> list[tuple[float, float, str]]:
    result: list[tuple[float, float, str]] = []
    data = page.get_text("dict")
    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text = "".join(span.get("text", "") for span in spans).strip()
            if text:
                y0 = min(span["bbox"][1] for span in spans)
                y1 = max(span["bbox"][3] for span in spans)
                result.append((y0, y1, text))
    return sorted(result, key=lambda item: (item[0], item[1]))


def locate_printed_pages(doc: fitz.Document) -> dict[int, list[tuple[int, list[tuple[float, float, str]]]]]:
    located: dict[int, list[tuple[int, list[tuple[float, float, str]]]]] = {
        p: [] for p in TARGET_PAGES
    }
    for page_index, page in enumerate(doc):
        lines = line_texts(page)
        for target in TARGET_PAGES:
            marker = str(target)
            # Printed folios are isolated numeric lines in this scan. Keep all
            # hits so the report exposes ambiguous page-number matches.
            # Printed folios are at the top or bottom margin. This avoids
            # mistaking table-of-contents entries (e.g. "205") for folios.
            height = page.rect.height
            if any(text.strip() == marker and (y0 < height * 0.12 or y1 > height * 0.88)
                   for y0, y1, text in lines):
                located[target].append((page_index, lines))
    return located


def extract_modes(lines: list[tuple[float, float, str]], page_height: float, page_no: int) -> dict[str, list[str]]:
    all_lines = [text for _, _, text in lines if text.strip() != str(page_no)]
    # Running headers/folios are outside the main text block. The PDF has
    # variable top/bottom placement, so retain a second full-page mode.
    body_lines = [
        text for y0, y1, text in lines
        if y0 >= 34 and y1 <= page_height - 34 and text.strip() != str(page_no)
        and "THE LAND OF THE BROADS" not in text.upper()
    ]
    # A conservative mode strips only the book-title running header and folio.
    no_running_header = [
        text for text in all_lines
        if "THE LAND OF THE BROADS" not in text.upper()
    ]
    return {
        "all_except_folio": words(" ".join(all_lines)),
        "body_blocks": words(" ".join(body_lines)),
        "no_running_header": words(" ".join(no_running_header)),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: k08_broads_pageword_probe.py BOOK.pdf", file=sys.stderr)
        return 2

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    k01 = bytes.fromhex(candidate["K01"])
    coords = [(k01[i], k01[i + 1]) for i in range(0, 16, 2)]
    assert tuple(page for page, _ in coords) == TARGET_PAGES
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    pdf_path = Path(sys.argv[1])
    pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    doc = fitz.open(pdf_path)
    located = locate_printed_pages(doc)

    report: dict[str, object] = {
        "book_hypothesis": "The Land of the Broads (Ernest R. Suffling, 1887)",
        "pdf_sha256": pdf_hash,
        "pdf_pages": len(doc),
        "k01_page_word_pairs": coords,
        "k08_target_sha256": target,
        "pages": {},
        "candidate_sequences": {},
        "contiguous_span_hits": [],
    }

    page_modes: dict[int, dict[str, list[str]]] = {}
    page_candidates: dict[int, list[int]] = {}
    for page_no in TARGET_PAGES:
        hits = located[page_no]
        page_candidates[page_no] = [idx for idx, _ in hits]
        page_report: dict[str, object] = {"pdf_page_indices": page_candidates[page_no], "modes": {}}
        if hits:
            # If the scan has duplicate folios, report each, but use the first
            # exact folio hit for the canonical extraction.
            page_index, lines = hits[0]
            modes = extract_modes(lines, doc[page_index].rect.height, page_no)
            page_modes[page_no] = modes
            for mode, tokens in modes.items():
                page_report["modes"][mode] = {
                    "word_count": len(tokens),
                    "selected_1based": tokens[coords[TARGET_PAGES.index(page_no)][1] - 1]
                    if len(tokens) >= coords[TARGET_PAGES.index(page_no)][1] else None,
                    "selected_0based": tokens[coords[TARGET_PAGES.index(page_no)][1]]
                    if len(tokens) > coords[TARGET_PAGES.index(page_no)][1] else None,
                    "excerpt_first_24": tokens[:24],
                }
        else:
            page_report["missing"] = True
        report["pages"][str(page_no)] = page_report

    orderings = {
        "signed_ABCD_order": list(TARGET_PAGES),
        "reverse_signed_order": list(reversed(TARGET_PAGES)),
        "ascending_page_order": sorted(TARGET_PAGES),
    }
    for mode in ("all_except_folio", "body_blocks", "no_running_header"):
        for index_base in (0, 1):
            for ordering_name, page_order in orderings.items():
                selected: list[str] = []
                complete = True
                for page_no in page_order:
                    modes = page_modes.get(page_no)
                    if not modes:
                        complete = False
                        break
                    word_index = coords[TARGET_PAGES.index(page_no)][1] - index_base
                    tokens = modes[mode]
                    if word_index < 0 or word_index >= len(tokens):
                        complete = False
                        break
                    selected.append(tokens[word_index])
                if not complete:
                    continue
                phrase = " ".join(selected)
                match, mac_hex, digest = k08_matches(phrase, nonce, target)
                key = f"{mode}|index_base={index_base}|{ordering_name}"
                report["candidate_sequences"][key] = {
                    "words": selected,
                    "phrase": phrase,
                    "normalized": normalize(phrase),
                    "hmac16": mac_hex,
                    "sha256": digest,
                    "match": match,
                }

    # The source-selected pages are also a bounded text corpus. Search all
    # contiguous spans of 2..20 words on those pages for the exact K08 commitment.
    for page_no in TARGET_PAGES:
        modes = page_modes.get(page_no)
        if not modes:
            continue
        tokens = modes["body_blocks"]
        for start in range(len(tokens)):
            for width in range(2, min(20, len(tokens) - start) + 1):
                phrase = " ".join(tokens[start:start + width])
                match, mac_hex, digest = k08_matches(phrase, nonce, target)
                if match:
                    report["contiguous_span_hits"].append({
                        "page": page_no, "start_1based": start + 1,
                        "width": width, "phrase": phrase,
                        "hmac16": mac_hex, "sha256": digest,
                    })


    # Map-back hypothesis: scan all pages at low resolution and rank color pages
    # by a conservative teal score. This does not assume that any one page is
    # the map; the top candidates and pixel samples are preserved for review.
    try:
        from PIL import Image
        import io

        k07 = bytes.fromhex(candidate["K07"])
        k07_points = [(k07[i], k07[i + 1]) for i in range(0, 16, 2)]
        map_scores = []
        for page_index, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(0.12, 0.12),
                                  colorspace=fitz.csRGB, alpha=False)
            im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            im = im.resize((256, 256))
            data = list(im.getdata())
            colored = sum(1 for r, g, b in data if max(r, g, b) - min(r, g, b) > 24)
            teal = sum(1 for r, g, b in data
                       if g > 65 and b > 65 and r < 190 and abs(g - b) < 110)
            map_scores.append({
                "pdf_page_index": page_index,
                "page_width": round(page.rect.width, 1),
                "page_height": round(page.rect.height, 1),
                "landscape": page.rect.width > page.rect.height,
                "color_fraction": round(colored / len(data), 5),
                "teal_fraction": round(teal / len(data), 5),
                "text_excerpt": normalize(page.get_text("text"))[:180],
                "image": im,
            })
        top = sorted(map_scores, key=lambda x: (x["teal_fraction"], x["color_fraction"]), reverse=True)[:12]
        map_report = []
        for item in top:
            im = item["image"]
            samples = []
            for x, y in k07_points:
                r, g, b = im.getpixel((x, y))
                samples.append({"xy": [x, y], "rgb": [r, g, b],
                                "teal_min": min(g, b), "teal_max": max(g, b)})
            # Try the two byte channels most naturally associated with teal,
            # plus a parity-gated low/high bit read.
            g_bytes = bytes(s["rgb"][1] for s in samples)
            b_bytes = bytes(s["rgb"][2] for s in samples)
            min_bytes = bytes(s["teal_min"] for s in samples)
            max_bytes = bytes(s["teal_max"] for s in samples)
            low_even_high_odd_gb = []
            low_even_high_odd_bg = []
            for i, s in enumerate(samples):
                g, b = s["rgb"][1], s["rgb"][2]
                low_even_high_odd_gb.append((g & 1) if i % 2 == 0 else ((b >> 7) & 1))
                low_even_high_odd_bg.append((b & 1) if i % 2 == 0 else ((g >> 7) & 1))
            item_out = {k: v for k, v in item.items() if k != "image"}
            item_out["samples"] = samples
            item_out["channel_bytes"] = {
                "green_hex": g_bytes.hex(), "green_ascii": g_bytes.decode("ascii", "replace"),
                "blue_hex": b_bytes.hex(), "blue_ascii": b_bytes.decode("ascii", "replace"),
                "teal_min_hex": min_bytes.hex(), "teal_min_ascii": min_bytes.decode("ascii", "replace"),
                "teal_max_hex": max_bytes.hex(), "teal_max_ascii": max_bytes.decode("ascii", "replace"),
            }
            item_out["parity_bit_reads"] = {
                "G_LSB_even_B_MSB_odd": "".join(str(x) for x in low_even_high_odd_gb),
                "B_LSB_even_G_MSB_odd": "".join(str(x) for x in low_even_high_odd_bg),
            }
            map_report.append(item_out)
        report["k07_map_pixel_probe"] = {
            "coordinate_pairs": k07_points,
            "top_color_pages": map_report,
        }
    except Exception as exc:
        report["k07_map_pixel_probe_error"] = repr(exc)

    out = ROOT / "agents" / "agent21" / "broads-pageword-results.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    any_match = any(x["match"] for x in report["candidate_sequences"].values())
    any_match = any_match or bool(report["contiguous_span_hits"])
    print("K08_MATCH", any_match)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
