#!/usr/bin/env python3
"""Evaluate the two frozen K08 page/word constructions on signed 1889 Falcon scans."""
from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
import os
import re
import tempfile
from io import BytesIO
from pathlib import Path
from types import ModuleType
from typing import Any

import fcntl
from PIL import Image
import pytesseract

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "agent7-falcon-signed-dual"
MANIFEST = OUT / "manifest.json"
VOLUME_ID = "fQYN_SZzCFgC"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
EXPECTED_K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
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


def load_helper() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "falcon_1889_pageword",
        ROOT / "agents/agent10/k08_falcon_1889_pageword.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the frozen Falcon tokenization helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(value, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    lock_path.unlink(missing_ok=True)


def load_ps0323() -> tuple[dict[str, str], bytes]:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    if sha256(raw) != SPOOL_SHA256:
        raise RuntimeError("spool reconstruction source hash changed")
    matches: list[dict[str, str]] = []
    pattern = re.compile(
        r"(?P<timestamp>\S+) JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) "
        r"STATE=(?P<state>\w+) CLASS=(?P<class>\w+) "
        r"PAYLOAD=(?P<payload>[A-F0-9]{32}) DEST=(?P<dest>\S+)"
    )
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
        raise RuntimeError("PS-0323 source role changed")
    packet = bytes.fromhex(row["payload"])
    coordinates = [(packet[i], packet[i + 1]) for i in range(0, 16, 2)]
    if coordinates != PS0323_COORDINATES:
        raise RuntimeError("PS-0323 coordinate bytes changed")
    return row, packet


def select_words(
    coordinates: list[tuple[int, int]], page_tokens: dict[int, list[str]]
) -> list[str]:
    words: list[str] = []
    for printed_page, position in coordinates:
        tokens = page_tokens[printed_page]
        if not 1 <= position <= len(tokens):
            raise RuntimeError(
                f"page {printed_page} has {len(tokens)} body words; requested {position}"
            )
        words.append(tokens[position - 1])
    return words


def contexts(
    coordinates: list[tuple[int, int]], page_tokens: dict[int, list[str]]
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for printed_page, position in coordinates:
        tokens = page_tokens[printed_page]
        result.append({
            "printed_page": printed_page,
            "body_word_position_1based": position,
            "body_word_count": len(tokens),
            "selected_word": tokens[position - 1],
            "context_tokens": tokens[max(0, position - 4):position + 3],
        })
    return result


def main() -> int:
    falcon = load_helper()
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text(encoding="utf-8"))
    candidate = json.loads((ROOT / "resources/candidate.json").read_text(encoding="utf-8"))
    routing = json.loads(
        (ROOT / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if manifest["volume_id"] != VOLUME_ID or manifest["complete"] is not True:
        raise RuntimeError("signed page manifest is incomplete or belongs to the wrong volume")
    target = acceptance["slot_sha256"]["K08"]
    if target != EXPECTED_K08_SHA256 or target != falcon.EXPECTED_K08_SHA256:
        raise RuntimeError("K08 acceptance commitment changed")
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    if nonce != falcon.DESK_NONCE:
        raise RuntimeError("K08 nonce changed")

    k01 = bytes.fromhex(candidate["K01"])
    if len(k01) != 16 or sha256(k01) != acceptance["slot_sha256"]["K01"]:
        raise RuntimeError("K01 no longer passes its original acceptance commitment")
    if [(k01[i], k01[i + 1]) for i in range(0, 16, 2)] != K01_COORDINATES:
        raise RuntimeError("K01 frozen coordinate derivation changed")

    n02 = falcon.verify_phrase(
        ["a", "good", "watch", "leaves", "the", "room", "ready",
         "for", "the", "next", "pair", "of", "hands"]
    )
    if n02["derived_K08_component_hex"] != EXPECTED_N02_HMAC16:
        raise RuntimeError("N02 HMAC known-answer control failed")

    ps0323_row, ps0323_packet = load_ps0323()
    records = {int(row["printed_page"]): row for row in manifest["records"]}
    expected_pages = sorted({p for coords in (K01_COORDINATES, PS0323_COORDINATES) for p, _ in coords})
    if sorted(records) != expected_pages:
        raise RuntimeError("signed page manifest does not contain the exact frozen page set")

    page_tokens: dict[int, list[str]] = {}
    page_results: dict[str, Any] = {}
    for printed_page in expected_pages:
        row = records[printed_page]
        signed_url = str(row["signed_image_url"])
        if f"id={VOLUME_ID}" not in signed_url or f"pg=PA{printed_page}" not in signed_url or "sig=" not in signed_url:
            raise RuntimeError(f"page {printed_page} signed source URL lost its identity fields")
        source_path = OUT / str(row["filename"])
        raw = source_path.read_bytes()
        if len(raw) != int(row["bytes"]) or sha256(raw) != row["sha256"]:
            raise RuntimeError(f"page {printed_page} source bytes differ from capture manifest")

        image = Image.open(BytesIO(raw)).convert("RGB")
        if image.width <= 500 or image.height <= 700:
            raise RuntimeError(f"page {printed_page} has implausible scan dimensions {image.size}")

        ocr = pytesseract.image_to_string(image, lang="eng", config="--psm 4")
        body = falcon.clean_body_lines(ocr, printed_page)
        tokens = falcon.WORD_PATTERN.findall(body)
        if not tokens:
            raise RuntimeError(f"page {printed_page} produced no body words")
        page_tokens[printed_page] = tokens
        (OUT / "ocr").mkdir(exist_ok=True)
        ocr_path = OUT / "ocr" / f"p{printed_page}.txt"
        ocr_path.write_text(ocr, encoding="utf-8")

        margin = falcon.read_margin_folio(image)
        requested_positions = sorted({
            position
            for coordinate_set in (K01_COORDINATES, PS0323_COORDINATES)
            for page_number, position in coordinate_set
            if page_number == printed_page
        })
        page_results[str(printed_page)] = {
            "source_image_sha256": row["sha256"],
            "source_image_bytes": row["bytes"],
            "image_dimensions": list(image.size),
            "signed_image_url": signed_url,
            "ocr_sha256": sha256(ocr.encode("utf-8")),
            "body_sha256": sha256(body.encode("utf-8")),
            "body_word_count": len(tokens),
            "requested_word_positions": requested_positions,
            "margin_ocr": margin,
            "first_20_body_tokens": tokens[:20],
        }
        print(
            "FALCON_PAGE "
            + json.dumps({
                "printed_page": printed_page,
                "body_word_count": len(tokens),
                "requested_positions": requested_positions,
                "margin_ocr": margin,
            }, sort_keys=True),
            flush=True,
        )

    candidate_results: dict[str, Any] = {}
    for name, coordinate_set in (
        ("K01_WN14", K01_COORDINATES),
        ("PS0323", PS0323_COORDINATES),
    ):
        words = select_words(coordinate_set, page_tokens)
        phrase = falcon.normalize_phrase(words)
        component = hmac.new(nonce, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
        digest = sha256(component)
        result = {
            "coordinate_set": coordinate_set,
            "words": words,
            "normalized_phrase": phrase,
            "derived_K08_component_hex": component.hex().upper(),
            "derived_K08_sha256": digest,
            "acceptance_match": digest == target,
            "selected_word_contexts": contexts(coordinate_set, page_tokens),
        }
        candidate_results[name] = result
        print("FALCON_CANDIDATE " + name + " " + json.dumps(result, sort_keys=True), flush=True)

    report = {
        "status": "COMPLETE",
        "source": {
            "title": 'The "Falcon" on the Baltic',
            "author": "Edward Frederick Knight",
            "publisher": "W. H. Allen",
            "year": 1889,
            "google_books_volume_id": VOLUME_ID,
            "acquisition": "viewer-generated signed Google Books page images",
        },
        "spool_sha256": SPOOL_SHA256,
        "ps0323_row": ps0323_row,
        "ps0323_payload_hex": ps0323_packet.hex().upper(),
        "k01_component_hex": k01.hex().upper(),
        "n02_hmac16_control": n02["derived_K08_component_hex"],
        "k08_target_sha256": target,
        "word_rule": {
            "position_base": 1,
            "ocr": "Tesseract eng --psm 4",
            "pattern": falcon.WORD_PATTERN.pattern,
            "cleanup": "Agent10 clean_body_lines",
        },
        "pages": page_results,
        "candidates": candidate_results,
        "any_acceptance_match": any(
            result["acceptance_match"] for result in candidate_results.values()
        ),
    }
    atomic_json(OUT / "summary.json", report)
    print(
        "FALCON_SIGNED_DUAL_COMPLETE "
        + json.dumps({
            name: result["acceptance_match"]
            for name, result in candidate_results.items()
        }, sort_keys=True),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
