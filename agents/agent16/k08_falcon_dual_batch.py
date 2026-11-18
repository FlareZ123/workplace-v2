#!/usr/bin/env python3
"""One cached, source-pinned batch for K01 and PS-0323 Falcon page/word tests.

This imports Agent 10's exact 1889-edition folio/OCR/tokenization helpers and
resolves the union of both frozen coordinate sets in one process. It does not
create a workflow; use one existing Falcon manual workflow to run it.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from types import ModuleType
from typing import Any

from PIL import Image
import pytesseract

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "agent16-falcon-dual-batch"
VOLUME_ID = "fQYN_SZzCFgC"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
EXPECTED_K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
REPORT: dict[str, Any] | None = None
K01_COORDINATES = [
    (4, 154), (171, 46), (28, 222), (122, 130),
    (205, 124), (96, 35), (67, 3), (201, 26),
]
PS0323_COORDINATES = [
    (30, 81), (239, 210), (229, 202), (143, 78),
    (31, 200), (180, 146), (151, 179), (215, 79),
]


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


@dataclass
class CacheStats:
    image_fetches: int = 0
    image_cache_hits: int = 0
    margin_ocr_runs: int = 0
    margin_cache_hits: int = 0


def install_shared_cache(falcon: Any, volume_id: str) -> CacheStats:
    """Memoize source images and margin OCR across all printed-page windows."""
    original_fetch = falcon.fetch_page_image
    original_margin = falcon.read_margin_folio
    image_cache: dict[tuple[str, int, int], tuple[bytes, str, str]] = {}
    margin_cache: dict[tuple[str, str, tuple[int, int], str], dict[str, Any]] = {}
    stats = CacheStats()

    def cached_fetch(page: int, zoom: int = 3) -> tuple[bytes, str, str]:
        key = (volume_id, int(page), int(zoom))
        if key in image_cache:
            stats.image_cache_hits += 1
            return image_cache[key]
        value = original_fetch(page, zoom=zoom)
        image_cache[key] = value
        stats.image_fetches += 1
        return value

    def cached_margin(image: Image.Image) -> dict[str, Any]:
        pixels = image.tobytes()
        key = (volume_id, image.mode, image.size, sha256(pixels))
        if key in margin_cache:
            stats.margin_cache_hits += 1
            return margin_cache[key]
        value = original_margin(image)
        margin_cache[key] = value
        stats.margin_ocr_runs += 1
        return value

    falcon.fetch_page_image = cached_fetch
    falcon.read_margin_folio = cached_margin
    return stats


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
    if (row["attempt"], row["state"], row["class"], row["dest"]) != ("1", "ACK", "RECOVER", "store"):
        raise RuntimeError(f"PS-0323 source role changed: {row}")
    packet = bytes.fromhex(row["payload"])
    coordinates = [(packet[i], packet[i + 1]) for i in range(0, 16, 2)]
    if coordinates != PS0323_COORDINATES:
        raise RuntimeError(f"PS-0323 coordinate bytes changed: {coordinates}")
    return row, packet


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
    """Preserve each selected body word and its local OCR-token context."""
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
                max(0, word_position - 4):word_position + 3
            ],
        })
    return contexts


def write_report(report: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    global REPORT
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "images").mkdir(exist_ok=True)
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
    if k01_coordinates != K01_COORDINATES:
        raise RuntimeError(f"frozen K01 coordinates changed: {k01_coordinates}")

    n02 = falcon.verify_phrase(
        ["a", "good", "watch", "leaves", "the", "room", "ready", "for", "the", "next", "pair", "of", "hands"]
    )
    if n02["derived_K08_component_hex"] != EXPECTED_N02_HMAC16 or n02["acceptance_match"]:
        raise RuntimeError("N02 original HMAC known-answer control failed")

    ps0323_row, ps0323_packet = load_ps0323()
    metadata = falcon.fetch_metadata()
    if metadata.get("pageCount") != 308 or not str(metadata.get("publishedDate", "")).startswith("1889"):
        raise RuntimeError(f"wrong Falcon edition metadata: {metadata}")

    cache_stats = install_shared_cache(falcon, VOLUME_ID)
    coordinate_sets = {
        "K01_WN14": K01_COORDINATES,
        "PS0323": PS0323_COORDINATES,
    }
    unique_pages = sorted({page for coords in coordinate_sets.values() for page, _ in coords})
    scan_windows = {
        page: set(range(max(0, page - 12), min(int(metadata["pageCount"]) - 1, page + 12) + 1))
        for page in unique_pages
    }
    naive_scan_fetches = sum(len(indices) for indices in scan_windows.values())
    unique_scan_indices = sorted(set().union(*scan_windows.values()))
    report: dict[str, Any] = {
        "status": "INCOMPLETE",
        "volume_id": VOLUME_ID,
        "volume_metadata": metadata,
        "spool_sha256": SPOOL_SHA256,
        "k01_component_hex": k01.hex().upper(),
        "ps0323_row": ps0323_row,
        "ps0323_payload_hex": ps0323_packet.hex().upper(),
        "coordinate_sets": {name: coords for name, coords in coordinate_sets.items()},
        "body_word_rule": {
            "position_base": 1,
            "word_pattern": falcon.WORD_PATTERN.pattern,
            "preprocessing": (
                "Agent10 clean_body_lines(): remove standalone numeric folios, title/running "
                "heads and all-uppercase display lines; join line-wrap hyphenation."
            ),
            "context": "up to four preceding tokens, selected token, and two following tokens",
        },
        "unique_printed_pages": unique_pages,
        "naive_scan_window_fetches": naive_scan_fetches,
        "unique_scan_indices_in_union": len(unique_scan_indices),
        "scan_window_fetches_saved_by_cache": naive_scan_fetches - len(unique_scan_indices),
        "n02_positive_control": n02,
        "folio_resolution": {},
        "page_results": {},
        "candidate_results": {},
        "cache_stats": None,
        "interpretation": (
            "Both frozen coordinate hypotheses share one source-pinned folio/image/OCR batch. "
            "A commitment hit is an experimental candidate, not historical authentication of "
            "the physical copy or a causal N23-to-PS0323 link."
        ),
    }
    REPORT = report
    report["cache_stats"] = vars(cache_stats)
    write_report(report)

    page_tokens: dict[int, list[str]] = {}
    for page in unique_pages:
        scan_index, folio_map = falcon.resolve_printed_page(
            page, int(metadata["pageCount"]), window=12
        )
        report["folio_resolution"][str(page)] = folio_map
        if scan_index is None:
            raise RuntimeError(f"printed folio {page} was not uniquely resolved")

        image_bytes, content_type, source_url = falcon.fetch_page_image(scan_index, zoom=3)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        margin = falcon.read_margin_folio(image)
        verified_zones = [
            name for name, info in margin.items() if info["tokens"] == [str(page)]
        ]
        if not verified_zones:
            raise RuntimeError(f"full-resolution folio check failed for printed page {page}")

        source_image_path = OUT / "images" / f"source-printed-page-{page}-scan-{scan_index}.bin"
        source_image_path.write_bytes(image_bytes)
        image_path = OUT / "images" / f"printed-page-{page}-scan-{scan_index}.png"
        image.save(image_path, format="PNG")
        ocr = pytesseract.image_to_string(image, lang="eng", config="--psm 4")
        ocr_path = OUT / "ocr" / f"printed-page-{page}-scan-{scan_index}.txt"
        ocr_path.write_text(ocr, encoding="utf-8")
        body = falcon.clean_body_lines(ocr, page)
        tokens = falcon.WORD_PATTERN.findall(body)
        page_tokens[page] = tokens

        requested = {
            name: [word for p, word in coords if p == page]
            for name, coords in coordinate_sets.items()
        }
        selected_context_by_set: dict[str, list[dict[str, Any]]] = {}
        for name, coords in coordinate_sets.items():
            rows = []
            for requested_page, word_position in coords:
                if requested_page != page:
                    continue
                if not 1 <= word_position <= len(tokens):
                    raise RuntimeError(
                        f"printed page {page} has {len(tokens)} body tokens; requested {word_position}"
                    )
                rows.append({
                    "body_word_position_1based": word_position,
                    "selected_word": tokens[word_position - 1],
                    "context_tokens_up_to_4_before_2_after": tokens[
                        max(0, word_position - 4):word_position + 3
                    ],
                })
            if rows:
                selected_context_by_set[name] = rows
        report["page_results"][str(page)] = {
            "printed_page": page,
            "google_books_scan_index": scan_index,
            "unique_folio_match_count": folio_map["unique_match_count"],
            "folio_verified_zones": verified_zones,
            "folio_resolution": folio_map,
            "source_url": source_url,
            "image_content_type": content_type,
            "source_image_path": str(source_image_path.relative_to(ROOT)),
            "source_image_bytes": len(image_bytes),
            "source_image_sha256": sha256(image_bytes),
            "normalized_png_sha256": sha256(image_path.read_bytes()),
            "image_dimensions": list(image.size),
            "ocr_path": str(ocr_path.relative_to(ROOT)),
            "ocr_sha256": sha256(ocr.encode("utf-8")),
            "body_sha256": sha256(body.encode("utf-8")),
            "body_word_count": len(tokens),
            "requested_word_positions": requested,
            "selected_word_context": selected_context_by_set,
        }
        report["cache_stats"] = vars(cache_stats)
        write_report(report)
        print("PAGE " + json.dumps(report["page_results"][str(page)], sort_keys=True), flush=True)

    for name, coords in coordinate_sets.items():
        words = candidate_words(coords, page_tokens)
        result = falcon.verify_phrase(words)
        result["words_in_coordinate_order"] = result.pop("words_in_K01_byte_order")
        report["candidate_results"][name] = {
            **result,
            "coordinate_set": name,
            "coordinate_pairs": coords,
            "selected_word_context": candidate_contexts(coords, page_tokens),
            "status": "MATCH" if result["acceptance_match"] else "NO_MATCH_ON_EXACT_1889_GOOGLE_BOOKS_COPY",
        }
        print("CANDIDATE_RESULT " + name + " " + json.dumps(report["candidate_results"][name], sort_keys=True), flush=True)

    report["cache_stats"] = vars(cache_stats)
    report["status"] = "COMPLETE"
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
