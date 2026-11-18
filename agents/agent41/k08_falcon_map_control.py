#!/usr/bin/env python3
"""Bounded public-scan control for the six-slot ATEALBIT coordinate decoder.

Downloads the explicitly identified Internet Archive item falcononbalticc00knig,
records item metadata, identifies landscape/foldout-like PDF pages, and applies
the already-frozen Agent41 coordinate decoder without consulting K08 acceptance.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
import sys
import urllib.parse
import urllib.request

import fitz
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k08_multislot_teal_coordinate_control import KNOWN_SLOTS, coordinates, sample_byte

ITEM = "falcononbalticc00knig"
BASE = f"https://archive.org/download/{ITEM}/"
META_URL = f"https://archive.org/metadata/{ITEM}"
OUT = Path("agent41-k08-falcon-map-control")
PDF = OUT / f"{ITEM}.pdf"

HEADERS = {"User-Agent": "H17-records-preservation-research/1.0"}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def download(url: str, path: Path) -> None:
    subprocess.run(
        [
            "curl", "-fL",
            "--retry", "4",
            "--retry-all-errors",
            "--connect-timeout", "30",
            "--max-time", "300",
            "--user-agent", HEADERS["User-Agent"],
            "--output", str(path),
            url,
        ],
        check=True,
    )


def choose_pdf(meta: dict) -> str:
    files = meta.get("files", [])
    exact = f"{ITEM}.pdf"
    names = {entry.get("name", "") for entry in files}
    if exact in names:
        return exact
    pdfs = []
    for entry in files:
        name = entry.get("name", "")
        if not name.lower().endswith(".pdf"):
            continue
        size = int(entry.get("size", 0) or 0)
        pdfs.append((size, name))
    if not pdfs:
        raise RuntimeError("item metadata exposes no PDF")
    pdfs.sort()
    return pdfs[0][1]


def printable_count(raw: bytes) -> int:
    return sum(0x20 <= value <= 0x7E for value in raw)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = fetch_json(META_URL)
    item_meta = meta.get("metadata", {})
    file_name = choose_pdf(meta)
    file_entry = next(entry for entry in meta["files"] if entry.get("name") == file_name)

    summary = {
        "identifier": ITEM,
        "title": item_meta.get("title"),
        "date": item_meta.get("date"),
        "year": item_meta.get("year"),
        "publisher": item_meta.get("publisher"),
        "contributor": item_meta.get("contributor"),
        "scanner": item_meta.get("scanner"),
        "foldoutcount": item_meta.get("foldoutcount"),
        "pdf_file": file_name,
        "pdf_metadata_size": file_entry.get("size"),
        "pdf_metadata_sha1": file_entry.get("sha1"),
        "pdf_metadata_md5": file_entry.get("md5"),
    }

    download(BASE + urllib.parse.quote(file_name), PDF)
    summary["pdf_downloaded_size"] = PDF.stat().st_size
    summary["pdf_sha256"] = hashlib.sha256(PDF.read_bytes()).hexdigest()

    candidate = json.loads(Path("candidate.json").read_text(encoding="utf-8"))
    slot_coords = {slot: coordinates(candidate[slot]) for slot in KNOWN_SLOTS}

    document = fitz.open(PDF)
    page_records = []
    landscape_pages = []
    global_best = -1
    global_rows = []

    for page_index in range(document.page_count):
        page = document.load_page(page_index)
        rect = page.rect
        ratio = rect.width / rect.height if rect.height else 0.0
        is_landscape = ratio > 1.15

        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), colorspace=fitz.csGRAY, alpha=False)
        image = Image.frombytes("L", (pix.width, pix.height), pix.samples)

        page_best = -1
        page_rows = []
        for mapping in ("direct", "scaled"):
            for orientation in range(8):
                for bitplane in range(8):
                    for bitorder in ("msb", "lsb"):
                        try:
                            output = bytes(
                                sample_byte(
                                    image,
                                    slot_coords[slot],
                                    mapping,
                                    orientation,
                                    bitplane,
                                    bitorder,
                                )
                                for slot in KNOWN_SLOTS
                            )
                        except ValueError:
                            continue
                        printable = printable_count(output)
                        row = {
                            "page_index_zero_based": page_index,
                            "mapping": mapping,
                            "orientation": orientation,
                            "bitplane": bitplane,
                            "bitorder": bitorder,
                            "hex": output.hex().upper(),
                            "ascii": "".join(chr(v) if 0x20 <= v <= 0x7E else "." for v in output),
                            "printable_bytes": printable,
                        }
                        if printable > page_best:
                            page_best = printable
                            page_rows = [row]
                        elif printable == page_best:
                            page_rows.append(row)
                        if printable > global_best:
                            global_best = printable
                            global_rows = [row]
                        elif printable == global_best:
                            global_rows.append(row)

        page_record = {
            "page_index_zero_based": page_index,
            "pdf_width": rect.width,
            "pdf_height": rect.height,
            "render_width": pix.width,
            "render_height": pix.height,
            "aspect_ratio": ratio,
            "landscape": is_landscape,
            "best_printable_bytes_of_six": page_best,
            "best": page_rows[:16],
        }
        page_records.append(page_record)
        if is_landscape:
            landscape_pages.append(page_index)
            image.save(OUT / f"page-{page_index:04d}-landscape.png")

    summary.update({
        "pdf_page_count": document.page_count,
        "landscape_page_indices_zero_based": landscape_pages,
        "global_best_printable_bytes_of_six": global_best,
        "global_best": global_rows[:64],
    })
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (OUT / "pages.json").write_text(json.dumps(page_records, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
