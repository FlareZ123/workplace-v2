#!/usr/bin/env python3
"""Read-only, source-gated K08 N14 teal-image intake.

The recovery path is restricted to the two source-literal layouts:
teal-mask-green-low-if-even and teal-mask-blue-low-if-even. It admits one
original image only when a caller-supplied source manifest binds its exact
SHA-256 to N14 and declares the photo-to-Emily-final-caption relationship.

The manifest is a source-link assertion that must be checked against the
underlying record; this code cannot authenticate its provenance. An HMAC hit
is candidate evidence, not historical authentication. The standalone CLI
remains single-image and manifest-bound. The internal scan_image_bytes entry
point also supports hash-verified thumbnail-cache carving; such hits must keep
their original-image and caption-source link explicitly unresolved.

No directory sweeps, generic channel layouts, image transforms, network access,
or image modification. The original pixel order is preserved.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import sys
from io import BytesIO
from pathlib import Path
from typing import Iterator

WORK = Path(__file__).resolve().parent
if str(WORK) not in sys.path:
    sys.path.insert(0, str(WORK))
from h17_ax7782_object_intake import OPAQUE_PDF_SHA256
from h17_redaction import redact_sensitive

import numpy as np
from PIL import Image

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp"}
SOURCE_LITERAL_LAYOUTS = (
    "teal-mask-green-low-if-even",
    "teal-mask-blue-low-if-even",
)
SOURCE_LINK_TYPES = {
    "album_membership",
    "board_membership",
    "caption_sidecar",
    "timestamp_author",
    "original_print_position",
}
ASCII_RUN = re.compile(r"[\x20-\x7e]{4,}")
WORD = re.compile(r"[a-z0-9]+")


def normalize_phrase(value: str) -> str:
    value = value.lower()
    value = "".join(c if ("a" <= c <= "z" or "0" <= c <= "9" or c.isspace()) else " " for c in value)
    return " ".join(value.split())


def k08_matches(value: str, nonce: bytes, commitment: str) -> bool:
    normalized = normalize_phrase(value)
    if not 8 <= len(normalized) <= 96:
        return False
    component = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    return hashlib.sha256(component).hexdigest().lower() == commitment.lower()


def _runs_from_bytes(data: bytes) -> Iterator[str]:
    # ASCII is the likely format for a manually remembered caption. UTF-16 is
    # included because office/profile exports often store Unicode text that way.
    for match in ASCII_RUN.finditer(data.decode("latin1", errors="ignore")):
        yield match.group(0)
    for encoding in ("utf-16le", "utf-16be"):
        try:
            text = data.decode(encoding, errors="ignore")
        except UnicodeError:
            continue
        for match in re.finditer(r"[\x20-\x7e]{4,}", text):
            yield match.group(0)


def _ngrams(text: str, max_words: int = 48) -> Iterator[str]:
    words = WORD.findall(text.lower())
    # K08 accepts normalized phrases of 8–96 characters. The maximum possible
    # word count in that domain is 48 (48 one-character tokens plus 47 spaces).
    # Scan every start position; bound each span by both constraints.
    for start in range(len(words)):
        phrase_words: list[str] = []
        for end in range(start, min(len(words), start + max_words)):
            phrase_words.append(words[end])
            phrase = " ".join(phrase_words)
            if len(phrase) > 96:
                break
            if len(phrase) >= 8:
                yield phrase


def _bit_variants(image: Image.Image, source_literal_only: bool = False) -> Iterator[tuple[str, np.ndarray]]:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    # Include hue as a separate channel: a literal "teal bit" may refer to the
    # green/blue balance rather than one raw RGB channel.
    hsv = np.asarray(image.convert("HSV"), dtype=np.uint8)

    # Source-literal bounded branch: "A TEAL BIT" + "LOW IF EVEN".
    # Select teal/cyan pixels once, in row-major image order. Absolute pixel
    # index parity chooses the green/blue bit plane: bit 0 for even, bit 1 for odd.
    teal_mask = (
        (hsv[:, :, 0] >= 110) & (hsv[:, :, 0] <= 150)
        & (hsv[:, :, 1] >= 64) & (hsv[:, :, 2] >= 32)
    )
    teal_indices = np.flatnonzero(teal_mask.ravel(order="C"))
    bit_positions = (teal_indices & 1).astype(np.uint8)
    for channel_name, channel in (("green", rgba[:, :, 1]), ("blue", rgba[:, :, 2])):
        values = channel.ravel(order="C")[teal_indices]
        bits = ((values >> bit_positions) & 1).astype(np.uint8)
        yield f"teal-mask-{channel_name}-low-if-even", bits
    if source_literal_only:
        return
    channels = {
        "green": rgba[:, :, 1],
        "blue": rgba[:, :, 2],
        "alpha": rgba[:, :, 3],
        "hue": hsv[:, :, 0],
    }
    for name, channel in channels.items():
        if name == "alpha" and np.all(channel == 255):
            continue
        for bit in (0, 1):
            yield f"{name}-bit{bit}", ((channel >> bit) & 1).ravel(order="C")
            yield f"{name}-bit{bit}-column", ((channel >> bit) & 1).T.ravel(order="C")
    g = rgba[:, :, 1]
    b = rgba[:, :, 2]
    for bit in (0, 1):
        gb = np.stack(((g >> bit) & 1, (b >> bit) & 1), axis=-1)
        bg = np.stack(((b >> bit) & 1, (g >> bit) & 1), axis=-1)
        yield f"green-blue-interleave-bit{bit}", gb.ravel(order="C")
        yield f"blue-green-interleave-bit{bit}", bg.ravel(order="C")
        yield f"green-xor-blue-bit{bit}", (((g ^ b) >> bit) & 1).ravel(order="C")
        yield f"green-minus-blue-bit{bit}", (((g.astype(np.int16) - b.astype(np.int16)) & 0xff) >> bit & 1).ravel(order="C")


def _candidate_texts(bits: np.ndarray) -> Iterator[str]:
    # Try each possible bit alignment and both packing conventions. Inversion
    # catches simple white/black or active-low encodings.
    for offset in range(8):
        aligned = bits[offset:]
        for bitorder in ("big", "little"):
            packed = np.packbits(aligned, bitorder=bitorder).tobytes()
            for payload in (packed, bytes(x ^ 0xff for x in packed)):
                yield from _runs_from_bytes(payload)


def scan_image_bytes(
    data: bytes, source_name: str, nonce: bytes, commitment: str,
    max_words: int = 48,
) -> list[dict]:
    """Scan one exact image byte payload using the two frozen teal layouts."""
    if not 1 <= max_words <= 48:
        raise ValueError("max_words must be between 1 and the source-fixed maximum 48")
    matches: list[dict] = []
    with Image.open(BytesIO(data)) as opened:
        frames = getattr(opened, "n_frames", 1)
        for frame in range(frames):
            if frames > 1:
                opened.seek(frame)
            image = opened.copy()
            for layout, bits in _bit_variants(image, source_literal_only=True):
                seen: set[str] = set()
                for run in _candidate_texts(bits):
                    # Keep only short runs likely to be a caption; long random
                    # printable regions are not useful phrase candidates.
                    for candidate in _ngrams(run, max_words=max_words):
                        normalized = normalize_phrase(candidate)
                        if normalized in seen:
                            continue
                        seen.add(normalized)
                        if k08_matches(normalized, nonce, commitment):
                            matches.append({
                                "file": source_name,
                                "frame": frame,
                                "layout": layout,
                                "phrase": normalized,
                            })
    return matches


def scan_image(path: Path, nonce: bytes, commitment: str, max_words: int = 48) -> list[dict]:
    """Scan one image file using only the two frozen source-literal teal layouts."""
    return scan_image_bytes(
        path.read_bytes(), str(path), nonce, commitment, max_words=max_words
    )


def validate_n14_source_manifest(image_path: Path, manifest_path: Path) -> dict:
    """Fail closed unless one original image is explicitly linked to N14/Emily."""
    if image_path.is_symlink() or not image_path.is_file():
        raise ValueError("image must be a regular, non-symlink file")
    if image_path.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError("unsupported image extension")
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("source manifest must be a regular, non-symlink file")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required = (
        "note_id", "image_path", "image_sha256", "photo_author",
        "final_caption_author", "link_type", "evidence_ref", "link_evidence",
    )
    missing = [key for key in required if not manifest.get(key)]
    if missing:
        raise ValueError(f"source manifest missing required fields: {', '.join(missing)}")
    if manifest["note_id"] != "N14":
        raise ValueError("source manifest note_id must be N14")
    if manifest["photo_author"] != "Gabriel":
        raise ValueError("source manifest photo_author must be Gabriel for N14")
    if manifest["final_caption_author"] != "Emily":
        raise ValueError("source manifest must link to Emily's final caption")
    if manifest["link_type"] not in SOURCE_LINK_TYPES:
        raise ValueError("source manifest link_type is not an admitted source relation")

    declared = Path(manifest["image_path"])
    declared_path = declared.resolve() if declared.is_absolute() else (manifest_path.parent / declared).resolve()
    if declared_path != image_path.resolve():
        raise ValueError("source manifest image_path does not identify the supplied image")

    actual_sha256 = hashlib.sha256(image_path.read_bytes()).hexdigest()
    if actual_sha256 == OPAQUE_PDF_SHA256:
        raise ValueError("hash-pinned BX25-08 PDF is hash-only and cannot be used as an image witness")
    if str(manifest["image_sha256"]).lower() != actual_sha256:
        raise ValueError("source manifest image_sha256 does not match the original image bytes")
    if not isinstance(manifest["evidence_ref"], str) or not manifest["evidence_ref"].strip():
        raise ValueError("source manifest evidence_ref must identify the underlying source record")
    if not isinstance(manifest["link_evidence"], str) or len(manifest["link_evidence"].strip()) < 20:
        raise ValueError("source manifest link_evidence must explain the image-to-caption relationship")

    return {
        "note_id": "N14",
        "image_path": str(image_path),
        "image_sha256": actual_sha256,
        "photo_author": "Gabriel",
        "final_caption_author": "Emily",
        "link_type": manifest["link_type"],
        "evidence_ref": manifest["evidence_ref"],
        "link_evidence": manifest["link_evidence"],
        "manifest_path": str(manifest_path),
        "status": "declared source link; underlying provenance still requires human verification",
    }


def scan_authorized_n14_image(
    image_path: Path, manifest_path: Path, nonce: bytes, commitment: str,
    max_words: int = 48,
) -> dict:
    """Run the frozen decoder on exactly one manifest-bound N14 image."""
    source_link = validate_n14_source_manifest(image_path, manifest_path)
    matches = scan_image(image_path, nonce, commitment, max_words=max_words)
    with Image.open(image_path) as opened:
        frames_scanned = getattr(opened, "n_frames", 1)
    return {
        "image": {
            "path": str(image_path),
            "sha256": source_link["image_sha256"],
            "frames_scanned": frames_scanned,
        },
        "source_link_assertion": source_link,
        "layouts_tested": list(SOURCE_LITERAL_LAYOUTS),
        "candidate_streams_per_frame": len(SOURCE_LITERAL_LAYOUTS) * 8 * 2 * 2,
        "matches": matches,
        "historical_authentication": "not established by an HMAC hit or manifest declaration alone",
    }


def load_commitment(evidence_root: Path) -> tuple[bytes, str]:
    # Support both layouts used by the repository and the supplied ZIP:
    # resources/{acceptance.json,evidence/recovery-routing.json} and
    # archive/{acceptance.json,evidence/recovery-routing.json}.
    routing_path = evidence_root / "recovery-routing.json"
    if not routing_path.exists():
        routing_path = evidence_root / "evidence" / "recovery-routing.json"
    acceptance_path = evidence_root / "acceptance.json"
    if not acceptance_path.exists():
        acceptance_path = evidence_root.parent / "acceptance.json"
    routing = json.loads(routing_path.read_text(encoding="utf-8"))
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    commitment = acceptance["slot_sha256"]["K08"]
    return nonce, commitment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True, help="one original N14 image; directory sweeps are not supported")
    parser.add_argument("--source-manifest", type=Path, required=True, help="manifest binding this exact image to N14 and Emily's final-caption source")
    parser.add_argument("--evidence-root", type=Path, required=True, help="directory containing recovery-routing.json and acceptance.json")
    parser.add_argument("--max-words", type=int, default=48)
    args = parser.parse_args()
    try:
        nonce, commitment = load_commitment(args.evidence_root)
        result = scan_authorized_n14_image(
            args.image, args.source_manifest, nonce, commitment,
            max_words=args.max_words,
        )
    except Exception as exc:
        print(json.dumps(redact_sensitive({"error": f"{type(exc).__name__}: {exc}", "matches": []}), indent=2))
        return 2
    print(json.dumps(redact_sensitive(result), indent=2))
    return 0 if result["matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
