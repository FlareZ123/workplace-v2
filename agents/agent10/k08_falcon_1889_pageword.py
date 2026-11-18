#!/usr/bin/env python3
"""Bounded K08 test of the exact 1889 Google Books edition of The "Falcon" on the Baltic.

Hypothesis: the MAIL-09 map-back book may be Knight's 1889 Falcon volume, one of
the small-yacht books named in Chapter XX of The Riddle of the Sands. This does
not assert that MAIL-09 identifies Falcon. It tests only the frozen K01 byte
pairs as (printed page, 1-based body word) against the 1889 Google Books copy.

The 1896 PDF is deliberately not used. Source identity is pinned to Google
Books volume fQYN_SZzCFgC (W. H. Allen, Jan 1889, 308 pages).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image
import pytesseract

VOLUME_ID = "fQYN_SZzCFgC"
VOLUME_METADATA_URL = f"https://www.googleapis.com/books/v1/volumes/{VOLUME_ID}"
COORDINATES = [
    (4, 154), (171, 46), (28, 222), (122, 130),
    (205, 124), (96, 35), (67, 3), (201, 26),
]
DESK_NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
EXPECTED_K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
OUT = Path("falcon-1889-pageword-probe")
(OUT / "images").mkdir(parents=True, exist_ok=True)
(OUT / "ocr").mkdir(parents=True, exist_ok=True)

# Count printed words before K08 normalization. Join line-wrap hyphenation and
# retain genuine in-line hyphenated compounds as one printed word.
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[.'’/-][A-Za-z0-9]+)*")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get(url: str, accept: str, timeout: int = 60) -> tuple[bytes, str, str]:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; H17-Archive-Preservation/1.0)",
        "Accept": accept,
    })
    with urlopen(req, timeout=timeout) as response:
        data = response.read()
        return data, response.headers.get("Content-Type", ""), response.geturl()


def fetch_metadata() -> dict:
    raw, content_type, final_url = get(VOLUME_METADATA_URL, "application/json")
    metadata = json.loads(raw.decode("utf-8"))
    info = metadata.get("volumeInfo", {})
    expected = {
        "title": info.get("title", ""),
        "authors": info.get("authors", []),
        "publisher": info.get("publisher", ""),
        "publishedDate": info.get("publishedDate", ""),
        "pageCount": info.get("pageCount"),
        "industryIdentifiers": info.get("industryIdentifiers", []),
        "metadata_url": final_url,
        "metadata_content_type": content_type,
        "metadata_bytes": len(raw),
        "metadata_sha256": sha256(raw),
    }
    if "Falcon" not in expected["title"] or "Knight" not in " ".join(expected["authors"]):
        raise RuntimeError(f"Google Books volume identity mismatch: {expected}")
    if not expected["publishedDate"].startswith("1889"):
        raise RuntimeError(f"Google Books volume is not the 1889 edition: {expected}")
    if expected["pageCount"] != 308:
        raise RuntimeError(f"Unexpected page count; expected 308: {expected}")
    return expected


def fetch_page_image(page: int, zoom: int = 3) -> tuple[bytes, str, str]:
    last_error = None
    for host in ("books.google.com", "books.google.es"):
        url = (
            f"https://{host}/books/content?id={VOLUME_ID}"
            f"&pg=PA{page}&img=1&zoom={zoom}&edge=curl&source=gbs_api"
        )
        try:
            data, content_type, final_url = get(
                url,
                "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                timeout=60,
            )
            if not content_type.startswith("image/"):
                raise RuntimeError(f"scan page {page} returned {content_type}: {data[:160]!r}")
            return data, content_type, final_url
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = f"{host}: {type(exc).__name__}: {exc}"
            print(f"SCAN_FETCH_FAIL scan_index={page} zoom={zoom} {last_error}", flush=True)
    raise RuntimeError(f"Could not fetch Google Books scan page {page}: {last_error}")


def read_margin_folio(image: Image.Image) -> dict[str, dict[str, object]]:
    """OCR only the page margins; a scan index is never assumed to be a printed folio."""
    width, height = image.size
    band_h = max(32, int(height * 0.16))
    band_w = max(32, int(width * 0.12))
    zones = {
        "top": (0, 0, width, band_h),
        "bottom": (0, height - band_h, width, height),
        "left": (0, 0, band_w, height),
        "right": (width - band_w, 0, width, height),
    }
    result: dict[str, dict[str, object]] = {}
    for name, bounds in zones.items():
        crop = image.crop(bounds)
        text = pytesseract.image_to_string(
            crop,
            lang="eng",
            config="--psm 6 -c tessedit_char_whitelist=0123456789",
        )
        tokens = re.findall(r"(?<!\d)\d{1,3}(?!\d)", text)
        result[name] = {"text": text, "tokens": tokens}
    return result


def resolve_printed_page(
    printed_page: int,
    page_count: int,
    window: int = 12,
) -> tuple[int | None, dict[str, object]]:
    """Find exactly one scan image whose margin OCR proves the requested printed folio."""
    first = max(0, printed_page - window)
    last = min(page_count - 1, printed_page + window)
    scanned: list[dict[str, object]] = []
    matches: list[dict[str, object]] = []
    for scan_index in range(first, last + 1):
        try:
            raw, content_type, source_url = fetch_page_image(scan_index, zoom=2)
            image = Image.open(BytesIO(raw)).convert("RGB")
            margin = read_margin_folio(image)
            matched_zones = [
                name for name, row in margin.items()
                if row["tokens"] == [str(printed_page)]
            ]
            row = {
                "scan_index": scan_index,
                "source_url": source_url,
                "content_type": content_type,
                "source_image_bytes": len(raw),
                "source_image_sha256": sha256(raw),
                "image_dimensions": list(image.size),
                "margin_ocr": margin,
                "matched_zones": matched_zones,
                "folio_match": bool(matched_zones),
            }
            scanned.append(row)
            if matched_zones:
                matches.append(row)
        except Exception as exc:
            scanned.append({
                "scan_index": scan_index,
                "error": f"{type(exc).__name__}: {exc}",
            })

    failed_scan_indices = [
        int(row["scan_index"])
        for row in scanned
        if "error" in row
    ]
    mapping: dict[str, object] = {
        "requested_printed_page": printed_page,
        "scan_window": [first, last],
        "scan_window_radius": window,
        "unique_match_count": len(matches),
        "failed_scan_indices": failed_scan_indices,
        "status": (
            "INCOMPLETE" if failed_scan_indices
            else "RESOLVED" if len(matches) == 1
            else "NO_UNIQUE_MATCH"
        ),
        "resolved_scan_index": (
            matches[0]["scan_index"]
            if len(matches) == 1 and not failed_scan_indices
            else None
        ),
        "matches": matches,
        "scanned_candidates": scanned,
    }
    # A single observed folio match is not proof of uniqueness if any other
    # scan index in the requested window failed to fetch or OCR.
    if failed_scan_indices or len(matches) != 1:
        return None, mapping
    return int(matches[0]["scan_index"]), mapping


def join_line_wrap_hyphens(text: str) -> str:
    return re.sub(
        r"(?<=[A-Za-z0-9])-\s*\n\s*(?=[A-Za-z0-9])",
        "",
        text,
    )


def clean_body_lines(text: str, printed_page: int) -> str:
    """Exclude folios, running heads and display headings; preserve body prose."""
    kept = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        upper = line.upper().strip(" .:-—'\"")
        if re.fullmatch(r"\d{1,3}", upper):
            continue
        if upper in {
            "THE FALCON ON THE BALTIC",
            "THE \"FALCON\" ON THE BALTIC",
            "THE 'FALCON' ON THE BALTIC",
            "E. F. KNIGHT",
        }:
            continue
        if re.fullmatch(r"(?:CHAPTER\s+)?[IVXLCDM]+", upper):
            continue
        # Running heads are short all-capital display lines. Exclude only
        # these; the page image and raw OCR are retained for visual audit.
        if len(line) <= 72 and line == line.upper() and re.search(r"[A-Z]", line):
            continue
        kept.append(line)
    return join_line_wrap_hyphens("\n".join(kept))


def normalize_phrase(words: list[str]) -> str:
    phrase = " ".join(words).lower()
    phrase = re.sub(r"[^a-z0-9\s]", " ", phrase)
    return re.sub(r"\s+", " ", phrase).strip()


def verify_phrase(words: list[str]) -> dict[str, object]:
    phrase = normalize_phrase(words)
    slot = hmac.new(DESK_NONCE, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
    return {
        "words_in_K01_byte_order": words,
        "normalized_phrase": phrase,
        "derived_K08_component_hex": slot.hex().upper(),
        "derived_K08_sha256": sha256(slot),
        "acceptance_match": sha256(slot) == EXPECTED_K08_SHA256,
    }


def main() -> int:
    report: dict[str, object] = {
        "candidate": "Knight, The \"Falcon\" on the Baltic, W. H. Allen, 1889",
        "google_books_volume_id": VOLUME_ID,
        "hypothesis": "Independent candidate named in Chapter XX of The Riddle of the Sands; no link to MAIL-09 is established. Test only whether frozen K01 bytes select printed-page / 1-based-body-word coordinates in this exact 1889 edition.",
        "coordinates_page_word_1based": COORDINATES,
        "status": "INCOMPLETE",
        "pages": [],
        "folio_scan_window": 12,
        "folio_resolution": [],
    }
    try:
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        candidate = json.loads((root / "resources/candidate.json").read_text(encoding="utf-8"))
        acceptance = json.loads((root / "resources/acceptance.json").read_text(encoding="utf-8"))
        routing = json.loads((root / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8"))
        k01 = bytes.fromhex(candidate["K01"])
        if len(k01) != 16 or sha256(k01) != acceptance["slot_sha256"]["K01"]:
            raise RuntimeError("K01 fails the original acceptance commitment")
        actual_coords = [(k01[i], k01[i + 1]) for i in range(0, 16, 2)]
        if actual_coords != COORDINATES:
            raise RuntimeError(f"Frozen K01 coordinates changed: {actual_coords}")
        nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
        if nonce != DESK_NONCE:
            raise RuntimeError("Desk nonce differs from the pinned source value")
        control = "a good watch leaves the room ready for the next pair of hands"
        control_hmac = hmac.new(nonce, control.encode("utf-8"), hashlib.sha256).digest()[:16]
        if control_hmac.hex().upper() != EXPECTED_N02_HMAC16:
            raise RuntimeError("Original N02 known-answer control failed")
        if acceptance["slot_sha256"]["K08"] != EXPECTED_K08_SHA256:
            raise RuntimeError("K08 acceptance target differs from pinned value")
        report["controls"] = {
            "K01_sha256": sha256(k01),
            "N02_hmac16": control_hmac.hex().upper(),
            "N02_control_passed": True,
            "K08_target_sha256": EXPECTED_K08_SHA256,
        }

        report["source_metadata"] = fetch_metadata()
        page_tokens: dict[int, list[str]] = {}
        for page in sorted({p for p, _ in COORDINATES}):
            scan_index, mapping = resolve_printed_page(
                page,
                int(report["source_metadata"]["pageCount"]),
                window=int(report["folio_scan_window"]),
            )
            report["folio_resolution"].append(mapping)
            if scan_index is None:
                raise RuntimeError(
                    f"Printed folio {page} was not uniquely resolved in the bounded scan window"
                )

            image_bytes, content_type, source_url = fetch_page_image(scan_index, zoom=3)
            source_image_path = OUT / "images" / f"source-printed-page-{page}-scan-{scan_index}.bin"
            source_image_path.write_bytes(image_bytes)
            image_path = OUT / "images" / f"printed-page-{page}-scan-{scan_index}.png"
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            full_margin = read_margin_folio(image)
            verified_zones = [
                name for name, row in full_margin.items()
                if row["tokens"] == [str(page)]
            ]
            if not verified_zones:
                raise RuntimeError(
                    f"Resolved scan PA{scan_index} did not repeat printed folio {page} at full resolution"
                )
            image.save(image_path, format="PNG")
            ocr = pytesseract.image_to_string(image, lang="eng", config="--psm 4")
            ocr_path = OUT / "ocr" / f"printed-page-{page}-scan-{scan_index}.txt"
            ocr_path.write_text(ocr, encoding="utf-8")
            body = clean_body_lines(ocr, page)
            tokens = WORD_PATTERN.findall(body)
            page_tokens[page] = tokens
            page_row = {
                "printed_page": page,
                "google_books_scan_index": scan_index,
                "folio_verified": True,
                "folio_verified_zones": verified_zones,
                "full_resolution_margin_ocr": full_margin,
                "source_url": source_url,
                "image_content_type": content_type,
                "source_image_path": str(source_image_path),
                "source_image_bytes": len(image_bytes),
                "source_image_sha256": sha256(image_bytes),
                "normalized_png_sha256": sha256(image_path.read_bytes()),
                "image_dimensions": list(image.size),
                "ocr_sha256": sha256(ocr.encode("utf-8")),
                "body_sha256": sha256(body.encode("utf-8")),
                "body_word_count": len(tokens),
                "requested_word_positions": [w for p, w in COORDINATES if p == page],
                "selected_word": None,
                "first_20_body_tokens": tokens[:20],
            }
            report["pages"].append(page_row)
            print("PAGE " + json.dumps(page_row, sort_keys=True), flush=True)

        selected = []
        for page, word_position in COORDINATES:
            tokens = page_tokens[page]
            if not 1 <= word_position <= len(tokens):
                raise RuntimeError(
                    f"Page {page} has {len(tokens)} body words; requested {word_position}"
                )
            selected.append(tokens[word_position - 1])
            for row in report["pages"]:
                if row["printed_page"] == page:
                    row["selected_word"] = tokens[word_position - 1]
                    row["selected_word_context"] = tokens[max(0, word_position - 4):word_position + 3]

        report["candidate_result"] = verify_phrase(selected)
        report["status"] = (
            "MATCH" if report["candidate_result"]["acceptance_match"]
            else "NO_MATCH_ON_EXACT_1889_GOOGLE_BOOKS_COPY_AFTER_PRINTED_FOLIO_VERIFICATION"
        )
        print("CANDIDATE_RESULT " + json.dumps(report["candidate_result"], sort_keys=True), flush=True)
        return 0
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["status"] = "INCOMPLETE"
        print("INCOMPLETE " + json.dumps(report, sort_keys=True), flush=True)
        return 2
    finally:
        (OUT / "summary.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    raise SystemExit(main())
