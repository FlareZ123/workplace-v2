#!/usr/bin/env python3
"""Read-only OCR/barcode intake for already-rendered K04 print media.

This is a post-render adapter, not an SPL/SHD parser or renderer. It scans
page images produced by a separately identified native print renderer. It
does not authenticate the source job, printer, physical output, or custody;
those require the native queue/job manifest and output witness.

For each image it records the original file hash and dimensions, decodes
supported barcodes/QR codes, optionally OCRs visible text, and tests only
complete 16-byte values (raw bytes or 32 hex characters) against the
unchanged K04 commitment and route XOR mask. It performs no image rotation,
warping, threshold search, or source mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any, Iterable

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
HEX32_RE = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")
HEX_BYTES_RE = re.compile(
    r"(?i)(?<![0-9a-f])(?:[0-9a-f]{2}(?:[\s:.-]+)){15}[0-9a-f]{2}(?![0-9a-f])"
)


def candidate_hit(block: bytes, target_digest: bytes, mask: bytes):
    """Return (kind, component) only for a complete 16-byte commitment match."""
    if len(block) != 16:
        return None
    if hashlib.sha256(block).digest() == target_digest:
        return "direct_component", block
    unmasked = bytes(a ^ b for a, b in zip(block, mask))
    if hashlib.sha256(unmasked).digest() == target_digest:
        return "payload_xor_route_mask", unmasked
    return None


def text_hex_candidates(text: str) -> Iterable[tuple[str, bytes]]:
    """Yield only exact 16-byte hex tokens, contiguous or byte-separated."""
    seen: set[bytes] = set()
    for match in HEX32_RE.finditer(text):
        token = match.group(0)
        try:
            value = bytes.fromhex(token)
        except ValueError:
            continue
        if len(value) == 16 and value not in seen:
            seen.add(value)
            yield token, value
    for match in HEX_BYTES_RE.finditer(text):
        token = match.group(0)
        compact = re.sub(r"[\s:.-]+", "", token)
        try:
            value = bytes.fromhex(compact)
        except ValueError:
            continue
        if len(value) == 16 and value not in seen:
            seen.add(value)
            yield token, value


def data_candidates(data: bytes) -> Iterable[tuple[str, bytes]]:
    """Yield a binary 16-byte token and/or exact ASCII-hex representations."""
    if len(data) == 16:
        yield "raw-16-byte", data
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError:
        return
    for label, value in text_hex_candidates(text):
        yield f"ascii-hex:{label}", value


def _bbox(rect: Any) -> dict[str, int] | None:
    if rect is None:
        return None
    try:
        return {
            "left": int(rect.left),
            "top": int(rect.top),
            "width": int(rect.width),
            "height": int(rect.height),
        }
    except Exception:
        return None


def _record_decoded(
    *,
    image_path: str,
    engine: str,
    symbology: str | None,
    data: bytes,
    bbox: dict[str, int] | None,
    target_digest: bytes,
    mask: bytes,
    records: list[dict[str, Any]],
    hits: list[dict[str, Any]],
) -> None:
    try:
        text_value = data.decode("utf-8")
    except UnicodeDecodeError:
        text_value = None
    record = {
        "image": image_path,
        "engine": engine,
        "symbology": symbology,
        "bbox": bbox,
        "data_hex": data.hex().upper(),
        "data_utf8": text_value,
    }
    records.append(record)
    for candidate_label, candidate in data_candidates(data):
        result = candidate_hit(candidate, target_digest, mask)
        if result:
            kind, component = result
            hits.append(
                {
                    **record,
                    "candidate_representation": candidate_label,
                    "match_kind": kind,
                    "component_hex": component.hex().upper(),
                    "component_sha256": hashlib.sha256(component).hexdigest(),
                }
            )


def _record_ocr(
    *,
    image_path: str,
    text: str,
    target_digest: bytes,
    mask: bytes,
    records: list[dict[str, Any]],
    hits: list[dict[str, Any]],
) -> None:
    records.append(
        {
            "image": image_path,
            "engine": "tesseract-ocr",
            "symbology": None,
            "bbox": None,
            "data_utf8": text,
        }
    )
    for token, candidate in text_hex_candidates(text):
        result = candidate_hit(candidate, target_digest, mask)
        if result:
            kind, component = result
            hits.append(
                {
                    "image": image_path,
                    "engine": "tesseract-ocr",
                    "symbology": None,
                    "bbox": None,
                    "candidate_representation": f"ocr-hex:{token}",
                    "match_kind": kind,
                    "component_hex": component.hex().upper(),
                    "component_sha256": hashlib.sha256(component).hexdigest(),
                }
            )


def consolidate_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge duplicate decodes of the same bytes without counting engines as evidence."""
    merged: dict[tuple[str, str, str], dict[str, Any]] = {}
    for hit in hits:
        key = (hit["image"], hit["component_hex"], hit["match_kind"])
        if key not in merged:
            merged[key] = {
                "image": hit["image"],
                "component_hex": hit["component_hex"],
                "component_sha256": hit["component_sha256"],
                "match_kind": hit["match_kind"],
                "decoder_engines": [],
                "candidate_representations": [],
                "observations": [],
            }
        item = merged[key]
        if hit["engine"] not in item["decoder_engines"]:
            item["decoder_engines"].append(hit["engine"])
        if hit["candidate_representation"] not in item["candidate_representations"]:
            item["candidate_representations"].append(hit["candidate_representation"])
        item["observations"].append({
            "engine": hit["engine"],
            "symbology": hit["symbology"],
            "bbox": hit["bbox"],
        })
    return list(merged.values())


def scan_frame(
    rgb: Any,
    image_path: str,
    target_digest: bytes,
    mask: bytes,
    *,
    do_ocr: bool,
    records: list[dict[str, Any]],
    hits: list[dict[str, Any]],
    warnings: list[str],
) -> None:
    zbar_qr_seen = False
    try:
        from pyzbar.pyzbar import decode as zbar_decode

        for obj in zbar_decode(rgb):
            symbology = str(getattr(obj, "type", "unknown"))
            if "QR" in symbology.upper():
                zbar_qr_seen = True
            _record_decoded(
                image_path=image_path,
                engine="zbar/pyzbar",
                symbology=symbology,
                data=bytes(obj.data),
                bbox=_bbox(getattr(obj, "rect", None)),
                target_digest=target_digest,
                mask=mask,
                records=records,
                hits=hits,
            )
    except Exception as exc:
        warnings.append(f"zbar-unavailable:{type(exc).__name__}:{exc}")

    # ZBar handles multiple QR/barcode symbols. Use OpenCV only as a QR
    # fallback when ZBar is unavailable or found no QR.
    if not zbar_qr_seen:
        try:
            import cv2
            import numpy as np

            detector = cv2.QRCodeDetector()
            array = np.asarray(rgb)
            value, points, _ = detector.detectAndDecode(array)
            if value:
                _record_decoded(
                    image_path=image_path,
                    engine="opencv-qrcode",
                    symbology="QRCODE",
                    data=value.encode("utf-8"),
                    bbox=None,
                    target_digest=target_digest,
                    mask=mask,
                    records=records,
                    hits=hits,
                )
        except Exception as exc:
            warnings.append(f"opencv-unavailable:{type(exc).__name__}:{exc}")

    if do_ocr:
        try:
            import pytesseract

            text = pytesseract.image_to_string(rgb, config="--psm 6")
            if text.strip():
                _record_ocr(
                    image_path=image_path,
                    text=text,
                    target_digest=target_digest,
                    mask=mask,
                    records=records,
                    hits=hits,
                )
        except Exception as exc:
            warnings.append(f"tesseract-unavailable:{type(exc).__name__}:{exc}")


def scan_image(
    path: Path,
    target_digest: bytes,
    mask: bytes,
    *,
    do_ocr: bool = True,
) -> dict[str, Any]:
    from PIL import Image

    raw = path.read_bytes()
    file_hash = hashlib.sha256(raw).hexdigest()
    records: list[dict[str, Any]] = []
    hits: list[dict[str, Any]] = []
    warnings: list[str] = []
    frames: list[dict[str, int]] = []

    with Image.open(path) as image:
        frame_count = int(getattr(image, "n_frames", 1))
        for frame_index in range(frame_count):
            image.seek(frame_index)
            image.load()
            width, height = image.size
            frames.append({"index": frame_index, "width": width, "height": height})
            rgb = image.convert("RGB")
            frame_path = (
                f"{path}#frame={frame_index}"
                if frame_count > 1
                else str(path)
            )
            scan_frame(
                rgb,
                frame_path,
                target_digest,
                mask,
                do_ocr=do_ocr,
                records=records,
                hits=hits,
                warnings=warnings,
            )

    unique_hits = consolidate_hits(hits)
    first_frame = frames[0] if frames else {"width": 0, "height": 0}
    return {
        "path": str(path),
        "file_sha256": file_hash,
        "width": first_frame["width"],
        "height": first_frame["height"],
        "frame_count": len(frames),
        "frames": frames,
        "decoded_record_count": len(records),
        "candidate_hit_count": len(unique_hits),
        "decoded_records": records,
        "candidate_hits": unique_hits,
        "warnings": warnings,
    }


def load_k04_rules(resources_dir: Path) -> tuple[bytes, bytes]:
    acceptance = json.loads((resources_dir / "acceptance.json").read_text(encoding="utf-8"))
    routing = json.loads(
        (resources_dir / "evidence" / "recovery-routing.json").read_text(encoding="utf-8")
    )
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    if len(target) != 32 or len(mask) != 16:
        raise ValueError("unexpected K04 commitment or route-mask length")
    return target, mask


def discover_images(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() in IMAGE_SUFFIXES else []
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def self_test() -> dict[str, Any]:
    try:
        import qrcode
        from PIL import Image
        from pyzbar.pyzbar import decode as zbar_decode
    except Exception as exc:
        raise RuntimeError(f"self-test dependencies unavailable: {exc}") from exc

    mask = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    component = bytes.fromhex("102132435465768798A9BACBDCEDFE0F")
    payload = bytes(a ^ b for a, b in zip(component, mask))
    target = hashlib.sha256(component).digest()
    direct = candidate_hit(component, target, mask)
    if direct is None or direct[0] != "direct_component":
        raise AssertionError("direct 16-byte component control failed")

    with tempfile.TemporaryDirectory(prefix="h17-k04-rendered-selftest-") as temp:
        image_path = Path(temp) / "synthetic-payload.png"
        qr = qrcode.QRCode(box_size=8, border=4)
        qr.add_data(payload.hex().upper())
        qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save(image_path)

        decoded = zbar_decode(Image.open(image_path).convert("RGB"))
        if not decoded:
            raise AssertionError("synthetic QR was not decoded by zbar")
        data = bytes(decoded[0].data)
        candidates = list(data_candidates(data))
        if not candidates:
            raise AssertionError("synthetic QR did not yield a 16-byte hex candidate")
        matches = [candidate_hit(value, target, mask) for _, value in candidates]
        matches = [item for item in matches if item]
        if len(matches) != 1 or matches[0][0] != "payload_xor_route_mask":
            raise AssertionError(f"synthetic masked QR did not match uniquely: {matches}")

        wrong = bytes((payload[0] ^ 1,)) + payload[1:]
        if candidate_hit(wrong, target, mask) is not None:
            raise AssertionError("altered payload unexpectedly matched")

        # A fax-style multi-page TIFF must scan every frame, not only page 1.
        control_qr = qrcode.make("unrelated-control-page")
        payload_qr = qrcode.make(payload.hex().upper())
        multipage_path = Path(temp) / "synthetic-fax-two-page.tiff"
        control_qr.convert("RGB").save(
            multipage_path,
            save_all=True,
            append_images=[payload_qr.convert("RGB")],
            compression="tiff_lzw",
        )
        multipage_result = scan_image(
            multipage_path, target, mask, do_ocr=False
        )
        if multipage_result["frame_count"] != 2:
            raise AssertionError("multi-page TIFF frame count was not preserved")
        if multipage_result["candidate_hit_count"] != 1:
            raise AssertionError(
                "multi-page TIFF did not yield exactly one candidate"
            )
        if "#frame=1" not in multipage_result["candidate_hits"][0]["image"]:
            raise AssertionError("candidate page index was not preserved")

    return {
        "self_test": "PASS",
        "synthetic_payload_hex": payload.hex().upper(),
        "expected_component_hex": component.hex().upper(),
        "match_count": 1,
        "direct_component_control": "PASS",
        "wrong_payload_hits": 0,
        "multipage_tiff_control": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image_root", nargs="?", type=Path)
    parser.add_argument("--resources-dir", type=Path, default=Path("resources"))
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--no-ocr", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        result = self_test()
        output = json.dumps(result, indent=2)
    else:
        if args.image_root is None:
            parser.error("image_root is required unless --self-test is used")
        target, mask = load_k04_rules(args.resources_dir)
        images = discover_images(args.image_root)
        files = []
        for path in images:
            try:
                files.append(scan_image(path, target, mask, do_ocr=not args.no_ocr))
            except Exception as exc:
                files.append({
                    "path": str(path),
                    "error": f"image-intake:{type(exc).__name__}:{exc}",
                    "frame_count": 0,
                    "frames": [],
                    "decoded_record_count": 0,
                    "candidate_hit_count": 0,
                    "decoded_records": [],
                    "candidate_hits": [],
                    "warnings": [],
                })
        hits = [hit for item in files for hit in item["candidate_hits"]]
        output_obj = {
            "schema_version": 1,
            "source_kind": "already-rendered-print-page-images",
            "target_commitment_sha256": target.hex(),
            "route_mask_hex": mask.hex().upper(),
            "image_count": len(files),
            "frame_count": sum(x.get("frame_count", 0) for x in files),
            "decoded_record_count": sum(x["decoded_record_count"] for x in files),
            "candidate_hit_count": len(hits),
            "candidate_hits": hits,
            "files": files,
            "interpretation_limit": (
                "This tool does not parse/render SPL/SHD, authenticate a queue/job, "
                "identify a printer/driver, or prove physical collection/custody. "
                "A hit is only a byte-level candidate until the image is bound to "
                "the exact native job and physical output by independent records. "
                "A no-hit does not exclude unsupported symbologies, unreadable media, "
                "non-hex text encodings, glyph/outline content, or missing pages."
            ),
        }
        output = json.dumps(output_obj, indent=2)

    if args.json_out:
        args.json_out.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
