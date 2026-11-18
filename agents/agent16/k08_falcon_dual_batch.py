#!/usr/bin/env python3
"""Resolve the frozen Falcon coordinate sets against one signed full-window capture.

Every scan image is captured once by the viewer-backed Node step. This batch
loads the 236-image manifest, OCRs each margin once, resolves printed folios
against the complete union (not per-folio subwindows), then performs the two
frozen page/word constructions independently.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from io import BytesIO
from pathlib import Path
from types import ModuleType
from typing import Any
from urllib.parse import parse_qs, urlparse

from PIL import Image
import pytesseract

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / "work" / "agent7-falcon-signed-dual"
OUT = ROOT / "work" / "agent16-falcon-dual-batch"
VOLUME_ID = "fQYN_SZzCFgC"
PAGE_COUNT = 308
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
EXPECTED_K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
SCAN_RANGES = [[0, 43], [55, 79], [84, 108], [110, 251]]
SCAN_INDICES = [
    index
    for first, last in SCAN_RANGES
    for index in range(first, last + 1)
]
TARGET_PRINTED_PAGES = [
    4, 28, 30, 31, 67, 96, 122, 143,
    151, 171, 180, 201, 205, 215, 229, 239
]
EXPECTED_K01_COORDINATES = [
    (4, 154), (171, 46), (28, 222), (122, 130),
    (205, 124), (96, 35), (67, 3), (201, 26),
]
EXPECTED_PS0323_COORDINATES = [
    (30, 81), (239, 210), (229, 202), (143, 78),
    (31, 200), (180, 146), (151, 179), (215, 79),
]
MIN_IMAGE_BYTES = 50000
MIN_WIDTH = 500
MIN_HEIGHT = 700
REPORT: dict[str, Any] | None = None


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_falcon_helper() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "falcon_1889_pageword",
        ROOT / "agents/agent10/k08_falcon_1889_pageword.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Agent 10's pinned Falcon helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_report(report: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_ps0323() -> tuple[dict[str, str], bytes]:
    path = ROOT / "resources/evidence/print/spool-reconstruction.log"
    raw = path.read_bytes()
    if sha256(raw) != SPOOL_SHA256:
        raise RuntimeError(f"spool source SHA changed: {sha256(raw)}")
    pattern = re.compile(
        r"(?P<timestamp>\S+) JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) "
        r"STATE=(?P<state>\w+) CLASS=(?P<class>\w+) "
        r"PAYLOAD=(?P<payload>[A-F0-9]{32}) DEST=(?P<dest>\S+)"
    )
    matches = []
    for line in raw.decode("utf-8").splitlines():
        match = pattern.search(line)
        if match and match.group("job") == "PS-261003-0323":
            matches.append(match.groupdict())
    if len(matches) != 1:
        raise RuntimeError(f"expected one PS-0323 row, found {len(matches)}")
    row = matches[0]
    if (row["attempt"], row["state"], row["class"], row["dest"]) != (
        "1", "ACK", "RECOVER", "store"
    ):
        raise RuntimeError(f"PS-0323 source role changed: {row}")
    packet = bytes.fromhex(row["payload"])
    coordinates = [(packet[i], packet[i + 1]) for i in range(0, 16, 2)]
    if coordinates != EXPECTED_PS0323_COORDINATES:
        raise RuntimeError(f"PS-0323 coordinate bytes changed: {coordinates}")
    return row, packet


def validate_manifest() -> tuple[dict[str, Any], dict[int, dict[str, Any]]]:
    manifest_path = CAPTURE / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("signed full-window manifest is missing")
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("complete") is not True:
        raise RuntimeError("signed full-window capture is not marked complete")
    if manifest.get("volume_id") != VOLUME_ID:
        raise RuntimeError("signed capture volume ID mismatch")
    if manifest.get("published_date") != "1889":
        raise RuntimeError("signed capture edition marker mismatch")
    if manifest.get("page_count") != PAGE_COUNT:
        raise RuntimeError("signed capture page count mismatch")
    if manifest.get("zoom") != 3:
        raise RuntimeError("signed capture is not zoom=3")
    if manifest.get("scan_index_ranges") != SCAN_RANGES:
        raise RuntimeError("signed capture scan ranges differ from the frozen union")
    if manifest.get("scan_indices") != SCAN_INDICES:
        raise RuntimeError("signed capture scan-index list differs from the frozen union")
    if manifest.get("target_printed_pages") != TARGET_PRINTED_PAGES:
        raise RuntimeError("signed capture target folio list changed")
    records = manifest.get("records")
    if not isinstance(records, list) or len(records) != len(SCAN_INDICES):
        raise RuntimeError("signed capture does not contain exactly 236 records")
    by_index: dict[int, dict[str, Any]] = {}
    seen_hashes: dict[str, list[int]] = {}
    for record in records:
        index = record.get("scan_index")
        if not isinstance(index, int) or index in by_index:
            raise RuntimeError(f"invalid or duplicate scan index record: {index!r}")
        if record.get("error"):
            raise RuntimeError(f"scan index {index} capture error: {record['error']}")
        if record.get("zoom") != 3:
            raise RuntimeError(f"scan index {index} was not captured at zoom=3")
        url = record.get("signed_image_url", "")
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if parsed.hostname not in {"books.google.com", "books.google.es"}:
            raise RuntimeError(f"scan index {index} has an unexpected signed URL host")
        if not parsed.path.endswith("/books/content"):
            raise RuntimeError(f"scan index {index} URL is not a Books content image")
        if query.get("id") != [VOLUME_ID] or query.get("pg") != [f"PA{index}"]:
            raise RuntimeError(f"scan index {index} signed URL identity mismatch")
        if not query.get("sig") or query.get("zoom") != ["3"]:
            raise RuntimeError(f"scan index {index} signed URL lacks signature/full zoom")
        if not str(record.get("content_type", "")).startswith("image/"):
            raise RuntimeError(f"scan index {index} has a non-image content type")
        if int(record.get("bytes", 0)) < MIN_IMAGE_BYTES:
            raise RuntimeError(f"scan index {index} is placeholder-sized")
        filename = record.get("filename")
        if not filename or Path(filename).name != filename:
            raise RuntimeError(f"scan index {index} has an unsafe image filename")
        image_path = CAPTURE / filename
        if not image_path.is_file():
            raise RuntimeError(f"scan index {index} image bytes are missing")
        image_bytes = image_path.read_bytes()
        if len(image_bytes) != int(record["bytes"]):
            raise RuntimeError(f"scan index {index} byte count mismatch")
        image_sha = sha256(image_bytes)
        if image_sha != record.get("sha256"):
            raise RuntimeError(f"scan index {index} SHA-256 mismatch")
        with Image.open(BytesIO(image_bytes)) as source:
            source.load()
            dimensions = list(source.size)
            image = source.convert("RGB")
        if dimensions != [record.get("natural_width"), record.get("natural_height")]:
            raise RuntimeError(f"scan index {index} viewer/image dimension mismatch")
        if dimensions[0] <= MIN_WIDTH or dimensions[1] <= MIN_HEIGHT:
            raise RuntimeError(f"scan index {index} image dimensions are placeholder-sized")
        seen_hashes.setdefault(image_sha, []).append(index)
        by_index[index] = {
            "scan_index": index,
            "signed_image_url": url,
            "content_type": record["content_type"],
            "bytes": len(image_bytes),
            "sha256": image_sha,
            "dimensions": dimensions,
            "filename": filename,
            "image_bytes": image_bytes,
            "image": image,
        }
    if sorted(by_index) != SCAN_INDICES:
        raise RuntimeError("signed capture is missing or adds scan indices")
    duplicate_hashes = {
        digest: indices for digest, indices in seen_hashes.items() if len(indices) > 1
    }
    if duplicate_hashes:
        raise RuntimeError(
            "repeated-image fallback/duplicate image hashes: " +
            json.dumps(duplicate_hashes, sort_keys=True)
        )
    manifest_info = {
        "path": str(manifest_path.relative_to(ROOT)),
        "sha256": sha256(raw_manifest),
        "record_count": len(records),
        "complete": True,
        "duplicate_image_hashes": [],
    }
    return {"raw": manifest_info, "manifest": manifest}, by_index


def margin_tokens(margin: dict[str, Any]) -> dict[str, list[str]]:
    if not isinstance(margin, dict):
        raise RuntimeError("margin OCR did not return a zone mapping")
    required = {"top", "bottom", "left", "right"}
    if set(margin) != required:
        raise RuntimeError(f"margin OCR zones changed: {sorted(margin)}")
    result: dict[str, list[str]] = {}
    for zone in sorted(required):
        value = margin[zone]
        if not isinstance(value, dict) or not isinstance(value.get("tokens"), list):
            raise RuntimeError(f"margin OCR zone {zone} is malformed")
        result[zone] = [str(token) for token in value["tokens"]]
    return result


def candidate_words(
    coordinate_set: list[tuple[int, int]], page_tokens: dict[int, list[str]]
) -> list[str]:
    words = []
    for page, word_position in coordinate_set:
        tokens = page_tokens[page]
        if not 1 <= word_position <= len(tokens):
            raise RuntimeError(
                f"printed page {page} has {len(tokens)} body tokens; requested {word_position}"
            )
        words.append(tokens[word_position - 1])
    return words


def candidate_contexts(
    coordinate_set: list[tuple[int, int]], page_tokens: dict[int, list[str]]
) -> list[dict[str, Any]]:
    contexts = []
    for page, word_position in coordinate_set:
        tokens = page_tokens[page]
        if not 1 <= word_position <= len(tokens):
            raise RuntimeError(
                f"printed page {page} has {len(tokens)} body tokens; requested {word_position}"
            )
        contexts.append({
            "printed_page": page,
            "body_word_position_1based": word_position,
            "body_word_count": len(tokens),
            "selected_word": tokens[word_position - 1],
            "context_tokens_up_to_4_before_2_after": tokens[
                max(0, word_position - 5):word_position + 2
            ],
        })
    return contexts


def main() -> int:
    global REPORT
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ocr").mkdir(exist_ok=True)
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text(encoding="utf-8"))
    candidate = json.loads((ROOT / "resources/candidate.json").read_text(encoding="utf-8"))
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8"))
    falcon = load_falcon_helper()

    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    if nonce != falcon.DESK_NONCE:
        raise RuntimeError("K08 desk nonce differs from Agent 10's pinned helper")
    target = acceptance["slot_sha256"]["K08"]
    if target != EXPECTED_K08_SHA256 or target != falcon.EXPECTED_K08_SHA256:
        raise RuntimeError("K08 acceptance commitment changed")

    k01 = bytes.fromhex(candidate["K01"])
    if len(k01) != 16 or sha256(k01) != acceptance["slot_sha256"]["K01"]:
        raise RuntimeError("K01 candidate does not pass its original acceptance commitment")
    k01_coordinates = [(k01[i], k01[i + 1]) for i in range(0, 16, 2)]
    if k01_coordinates != EXPECTED_K01_COORDINATES:
        raise RuntimeError(f"frozen K01 coordinates changed: {k01_coordinates}")

    n02 = falcon.verify_phrase([
        "a", "good", "watch", "leaves", "the", "room", "ready",
        "for", "the", "next", "pair", "of", "hands"
    ])
    if n02["derived_K08_component_hex"] != EXPECTED_N02_HMAC16 or n02["acceptance_match"]:
        raise RuntimeError("N02 original HMAC known-answer control failed")

    ps0323_row, ps0323_packet = load_ps0323()
    metadata = falcon.fetch_metadata()
    if metadata.get("pageCount") != PAGE_COUNT or not str(
        metadata.get("publishedDate", "")
    ).startswith("1889"):
        raise RuntimeError(f"wrong Falcon edition metadata: {metadata}")

    manifest_info, manifest_images = validate_manifest()
    coordinate_sets = {
        "K01_WN14": EXPECTED_K01_COORDINATES,
        "PS0323": EXPECTED_PS0323_COORDINATES,
    }
    unique_pages = sorted({
        page for coordinates in coordinate_sets.values()
        for page, _ in coordinates
    })
    if unique_pages != TARGET_PRINTED_PAGES:
        raise RuntimeError("frozen printed-folio list does not match coordinate sets")

    report: dict[str, Any] = {
        "status": "INCOMPLETE",
        "volume_id": VOLUME_ID,
        "volume_metadata": metadata,
        "signed_capture_manifest": manifest_info["raw"],
        "spool_sha256": SPOOL_SHA256,
        "k01_component_hex": k01.hex().upper(),
        "ps0323_row": ps0323_row,
        "ps0323_payload_hex": ps0323_packet.hex().upper(),
        "coordinate_sets": {name: coordinates for name, coordinates in coordinate_sets.items()},
        "body_word_rule": {
            "position_base": 1,
            "word_pattern": falcon.WORD_PATTERN.pattern,
            "preprocessing": (
                "Agent10 clean_body_lines(): remove standalone numeric folios, title/running "
                "heads and all-uppercase display lines; join line-wrap hyphenation."
            ),
            "context": "up to four preceding tokens, selected token, and two following tokens",
        },
        "frozen_scan_index_ranges": SCAN_RANGES,
        "unique_scan_indices_in_union": len(SCAN_INDICES),
        "unique_printed_pages": unique_pages,
        "n02_positive_control": n02,
        "folio_resolution": {},
        "scan_evidence": [],
        "full_resolution_rechecks": {},
        "page_results": {},
        "candidate_results": {},
        "cache_stats": {
            "signed_image_fetches": len(SCAN_INDICES),
            "image_loads": len(SCAN_INDICES),
            "margin_ocr_runs": 0,
            "margin_ocr_cache_hits": 0,
            "selected_full_resolution_rechecks": 0,
        },
        "interpretation": (
            "One viewer-signed full-resolution image is fetched and cached per scan index. "
            "All 236 scan indices in the frozen union are margin-OCRed once. Every requested "
            "printed folio is resolved against the complete union, not an individual subwindow. "
            "The two frozen coordinate constructions are evaluated independently; a commitment "
            "hit is an experimental candidate, not historical authentication of the physical "
            "copy or a causal N23-to-PS0323 link."
        ),
    }
    REPORT = report
    write_report(report)

    # Cache each image and each margin-OCR result exactly once.
    scan_evidence: dict[int, dict[str, Any]] = {}
    for scan_index in SCAN_INDICES:
        source = manifest_images[scan_index]
        margin = falcon.read_margin_folio(source["image"])
        zones = margin_tokens(margin)
        matched_folios = sorted({
            page for page in unique_pages
            if any(tokens == [str(page)] for tokens in zones.values())
        })
        scan_evidence[scan_index] = {
            "scan_index": scan_index,
            "source_url": source["signed_image_url"],
            "image_content_type": source["content_type"],
            "source_image_bytes": source["bytes"],
            "source_image_sha256": source["sha256"],
            "image_dimensions": source["dimensions"],
            "capture_zoom": 3,
            "margin_ocr": margin,
            "exact_target_folios_in_margin": matched_folios,
        }
        report["cache_stats"]["margin_ocr_runs"] += 1
        report["scan_evidence"].append(scan_evidence[scan_index])
        write_report(report)
        (OUT / "folio-evidence.json").write_text(
            json.dumps(report["scan_evidence"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(
            "MARGIN_OCR " + json.dumps({
                "scan_index": scan_index,
                "source_image_sha256": source["sha256"],
                "image_dimensions": source["dimensions"],
                "exact_target_folios_in_margin": matched_folios,
                "margin_ocr": zones,
            }, sort_keys=True),
            flush=True,
        )

    # Each printed folio must have exactly one exact margin-token match across
    # the complete union of 236 scan indices.
    scan_to_folios: dict[int, list[int]] = {}
    for printed_page in unique_pages:
        matches = []
        for scan_index in SCAN_INDICES:
            evidence = scan_evidence[scan_index]
            zones = margin_tokens(evidence["margin_ocr"])
            matching_zones = [
                zone for zone, tokens in zones.items()
                if tokens == [str(printed_page)]
            ]
            if matching_zones:
                matches.append({
                    "scan_index": scan_index,
                    "matching_zones": matching_zones,
                    "source_image_sha256": evidence["source_image_sha256"],
                    "source_url": evidence["source_url"],
                    "image_dimensions": evidence["image_dimensions"],
                })
                scan_to_folios.setdefault(scan_index, []).append(printed_page)
        report["folio_resolution"][str(printed_page)] = {
            "printed_page": printed_page,
            "search_scope": "complete_frozen_236_scan_index_union",
            "unique_match_count": len(matches),
            "matches": matches,
            "status": "UNIQUE" if len(matches) == 1 else "AMBIGUOUS_OR_MISSING",
        }
    reused_scan_indices = {
        scan_index: pages for scan_index, pages in scan_to_folios.items() if len(set(pages)) > 1
    }
    if reused_scan_indices:
        raise RuntimeError(
            "one scan image exactly matches multiple requested printed folios: " +
            json.dumps(reused_scan_indices, sort_keys=True)
        )
    bad_folios = {
        page: value["unique_match_count"]
        for page, value in report["folio_resolution"].items()
        if value["unique_match_count"] != 1
    }
    if bad_folios:
        raise RuntimeError(
            "each requested printed folio requires exactly one full-union match; " +
            json.dumps(bad_folios, sort_keys=True)
        )

    selected_scan_by_page = {
        int(page): value["matches"][0]["scan_index"]
        for page, value in report["folio_resolution"].items()
    }

    # Preserve the full image and folio evidence for all 236 indices.
    report["scan_evidence"] = [
        scan_evidence[index] for index in SCAN_INDICES
    ]
    (OUT / "folio-evidence.json").write_text(
        json.dumps(report["scan_evidence"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(report)

    page_tokens: dict[int, list[str]] = {}
    for printed_page in unique_pages:
        scan_index = selected_scan_by_page[printed_page]
        source = manifest_images[scan_index]
        evidence = scan_evidence[scan_index]
        raw = source["image_bytes"]
        # Recheck the selected full-resolution image from the exact cached bytes.
        if sha256(raw) != evidence["source_image_sha256"]:
            raise RuntimeError(f"selected page {printed_page} full-resolution SHA changed")
        selected_image = source["image"]
        selected_dimensions = list(selected_image.size)
        if selected_dimensions != evidence["image_dimensions"]:
            raise RuntimeError(f"selected page {printed_page} full-resolution dimensions changed")
        matching_zones = [
            zone for zone, tokens in margin_tokens(evidence["margin_ocr"]).items()
            if tokens == [str(printed_page)]
        ]
        if not matching_zones:
            raise RuntimeError(f"selected page {printed_page} cached full-resolution folio check failed")
        report["full_resolution_rechecks"][str(printed_page)] = {
            "printed_page": printed_page,
            "scan_index": scan_index,
            "capture_zoom": 3,
            "source_image_sha256": evidence["source_image_sha256"],
            "image_dimensions": selected_dimensions,
            "exact_matching_margin_zones": matching_zones,
            "margin_ocr_reused_from_cache": True,
            "verified": True,
        }
        report["cache_stats"]["selected_full_resolution_rechecks"] += 1

        ocr = pytesseract.image_to_string(selected_image, lang="eng", config="--psm 4")
        if not ocr.strip():
            raise RuntimeError(f"full-page body OCR returned no text for printed page {printed_page}")
        ocr_path = OUT / "ocr" / f"printed-page-{printed_page}-scan-{scan_index}.txt"
        ocr_path.write_text(ocr, encoding="utf-8")
        body = falcon.clean_body_lines(ocr, printed_page)
        tokens = falcon.WORD_PATTERN.findall(body)
        if not tokens:
            raise RuntimeError(f"normalized body OCR returned no words for printed page {printed_page}")
        page_tokens[printed_page] = tokens

        requested = {
            name: [word for page, word in coordinates if page == printed_page]
            for name, coordinates in coordinate_sets.items()
        }
        selected_context_by_set: dict[str, list[dict[str, Any]]] = {}
        for name, coordinates in coordinate_sets.items():
            rows = []
            for page, word_position in coordinates:
                if page != printed_page:
                    continue
                if not 1 <= word_position <= len(tokens):
                    raise RuntimeError(
                        f"printed page {printed_page} has {len(tokens)} body tokens; "
                        f"requested {word_position}"
                    )
                rows.append({
                    "body_word_position_1based": word_position,
                    "selected_word": tokens[word_position - 1],
                    "context_tokens_up_to_4_before_2_after": tokens[
                        max(0, word_position - 5):word_position + 2
                    ],
                })
            if rows:
                selected_context_by_set[name] = rows
        report["page_results"][str(printed_page)] = {
            "printed_page": printed_page,
            "google_books_scan_index": scan_index,
            "unique_folio_match_count": 1,
            "folio_verified_zones": matching_zones,
            "source_url": evidence["source_url"],
            "image_content_type": evidence["image_content_type"],
            "source_image_path": str((CAPTURE / source["filename"]).relative_to(ROOT)),
            "source_image_bytes": evidence["source_image_bytes"],
            "source_image_sha256": evidence["source_image_sha256"],
            "image_dimensions": selected_dimensions,
            "capture_zoom": 3,
            "full_resolution_recheck": report["full_resolution_rechecks"][str(printed_page)],
            "ocr_path": str(ocr_path.relative_to(ROOT)),
            "ocr_sha256": sha256(ocr.encode("utf-8")),
            "body_sha256": sha256(body.encode("utf-8")),
            "body_word_count": len(tokens),
            "requested_word_positions": requested,
            "selected_word_context": selected_context_by_set,
        }
        write_report(report)
        print("PAGE " + json.dumps(report["page_results"][str(printed_page)], sort_keys=True), flush=True)

    for name, coordinates in coordinate_sets.items():
        words = candidate_words(coordinates, page_tokens)
        result = falcon.verify_phrase(words)
        result["words_in_coordinate_order"] = result.pop("words_in_K01_byte_order")
        report["candidate_results"][name] = {
            **result,
            "coordinate_set": name,
            "coordinate_pairs": coordinates,
            "selected_word_context": candidate_contexts(coordinates, page_tokens),
            "status": (
                "MATCH" if result["acceptance_match"]
                else "NO_MATCH_ON_EXACT_1889_GOOGLE_BOOKS_COPY"
            ),
        }
        print(
            "CANDIDATE_RESULT " + name + " " +
            json.dumps(report["candidate_results"][name], sort_keys=True),
            flush=True,
        )

    report["cache_stats"]["signed_image_fetches"] = len(SCAN_INDICES)
    report["cache_stats"]["image_loads"] = len(SCAN_INDICES)
    report["status"] = "COMPLETE"
    report["complete_frozen_constructions"] = len(report["candidate_results"]) == 2
    report["any_k08_acceptance_match"] = any(
        value["acceptance_match"] for value in report["candidate_results"].values()
    )
    write_report(report)
    print("BATCH_COMPLETE " + json.dumps(report["cache_stats"], sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        partial = REPORT if REPORT is not None else {"status": "INCOMPLETE"}
        partial["status"] = "INCOMPLETE"
        partial["error"] = f"{type(exc).__name__}: {exc}"
        write_report(partial)
        print("INCOMPLETE " + json.dumps({"error": partial["error"]}), flush=True)
        raise
