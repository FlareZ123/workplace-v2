#!/usr/bin/env python3
"""K08 candidate: PS-0323 as eight printed-page/body-word byte pairs.

This is a single bounded hypothesis, distinct from WN-14/K01 page-word
coordinates and from PS-0323 as eight u16 absolute word offsets. It uses the
exact 1889 Google Books Falcon volume and Agent 10's folio/OCR/tokenization
functions. The N23 -> PS-0323 association remains structural, not causal.
"""
from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
import re
from io import BytesIO

from PIL import Image
import pytesseract

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "agent3-ps0323-falcon-pageword"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
EXPECTED_K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
VOLUME_ID = "fQYN_SZzCFgC"

spec = importlib.util.spec_from_file_location(
    "falcon_1889_pageword",
    ROOT / "agents/agent10/k08_falcon_1889_pageword.py",
)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load pinned Falcon page-word extraction functions")
falcon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(falcon)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        m = pattern.search(line)
        if m and m.group("job") == "PS-261003-0323":
            matches.append(m.groupdict())
    if len(matches) != 1:
        raise RuntimeError(f"expected one PS-0323 row, found {len(matches)}")
    row = matches[0]
    if (row["attempt"], row["state"], row["class"], row["dest"]) != ("1", "ACK", "RECOVER", "store"):
        raise RuntimeError(f"PS-0323 source role changed: {row}")
    return row, bytes.fromhex(row["payload"])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "images").mkdir(exist_ok=True)
    (OUT / "ocr").mkdir(exist_ok=True)

    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text(encoding="utf-8"))
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    if nonce != falcon.DESK_NONCE:
        raise RuntimeError("K08 desk nonce differs from pinned Falcon helper")
    target = acceptance["slot_sha256"]["K08"]
    if target != EXPECTED_K08_SHA256 or target != falcon.EXPECTED_K08_SHA256:
        raise RuntimeError("K08 acceptance commitment changed")

    n02 = falcon.verify_phrase(
        ["a", "good", "watch", "leaves", "the", "room", "ready", "for", "the", "next", "pair", "of", "hands"]
    )
    if n02["derived_K08_component_hex"] != EXPECTED_N02_HMAC16 or not n02["acceptance_match"] is False:
        raise RuntimeError("N02 HMAC known-answer control failed")

    row, packet = load_ps0323()
    coordinates = [(packet[i], packet[i + 1]) for i in range(0, 16, 2)]
    if coordinates != [(30, 81), (239, 210), (229, 202), (143, 78), (31, 200), (180, 146), (151, 179), (215, 79)]:
        raise RuntimeError(f"PS-0323 page/word bytes changed: {coordinates}")

    metadata = falcon.fetch_metadata()
    if metadata.get("pageCount") != 308 or "1889" not in metadata.get("publishedDate", ""):
        raise RuntimeError(f"wrong Falcon edition metadata: {metadata}")

    report = {
        "hypothesis": "PS-0323 payload bytes = eight one-based (printed_page, body_word) coordinate pairs",
        "volume_id": VOLUME_ID,
        "volume_metadata": metadata,
        "spool_sha256": SPOOL_SHA256,
        "spool_row": row,
        "payload_hex": packet.hex().upper(),
        "coordinates_page_word_1based": coordinates,
        "n02_positive_control": n02,
        "page_results": [],
        "selected_words": [],
        "candidate_result": None,
        "status": "INCOMPLETE",
        "interpretation": "A match would be a candidate K08 recovery, not proof that this transcription is David's physical copy or that N23 caused PS-0323.",
    }

    page_tokens: dict[int, list[str]] = {}
    for page, word_position in coordinates:
        scan_index, folio_map = falcon.resolve_printed_page(
            page,
            int(metadata["pageCount"]),
            window=12,
        )
        if scan_index is None:
            raise RuntimeError(f"printed page {page} not uniquely resolved: {folio_map}")
        image_bytes, content_type, source_url = falcon.fetch_page_image(scan_index, zoom=3)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        margin = falcon.read_margin_folio(image)
        verified_zones = [
            name for name, info in margin.items()
            if info["tokens"] == [str(page)]
        ]
        if not verified_zones:
            raise RuntimeError(f"full-resolution folio check failed for printed page {page}")
        image_path = OUT / "images" / f"printed-page-{page}-scan-{scan_index}.png"
        image.save(image_path, format="PNG")
        ocr = pytesseract.image_to_string(image, lang="eng", config="--psm 4")
        ocr_path = OUT / "ocr" / f"printed-page-{page}-scan-{scan_index}.txt"
        ocr_path.write_text(ocr, encoding="utf-8")
        body = falcon.clean_body_lines(ocr, page)
        tokens = falcon.WORD_PATTERN.findall(body)
        page_tokens[page] = tokens
        if not 1 <= word_position <= len(tokens):
            raise RuntimeError(
                f"printed page {page} has {len(tokens)} body tokens; requested word {word_position}"
            )
        selected_word = tokens[word_position - 1]
        page_result = {
            "printed_page": page,
            "body_word_position": word_position,
            "google_books_scan_index": scan_index,
            "folio_verified_zones": verified_zones,
            "folio_resolution": folio_map,
            "source_url": source_url,
            "image_content_type": content_type,
            "image_sha256": sha256(image_bytes),
            "image_dimensions": list(image.size),
            "ocr_sha256": sha256(ocr.encode("utf-8")),
            "body_sha256": sha256(body.encode("utf-8")),
            "body_word_count": len(tokens),
            "selected_word": selected_word,
            "word_context": tokens[max(0, word_position - 4):word_position + 3],
        }
        report["page_results"].append(page_result)
        report["selected_words"].append(selected_word)
        print("PAGE " + json.dumps(page_result, sort_keys=True), flush=True)

    report["candidate_result"] = falcon.verify_phrase(report["selected_words"])
    report["status"] = "MATCH" if report["candidate_result"]["acceptance_match"] else "NO_MATCH_ON_PS0323_PAGEWORD_FALCON_1889"
    print("CANDIDATE_RESULT " + json.dumps(report["candidate_result"], sort_keys=True), flush=True)
    print(report["status"], flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("INCOMPLETE " + json.dumps({"error": f"{type(exc).__name__}: {exc}"}), flush=True)
        raise
