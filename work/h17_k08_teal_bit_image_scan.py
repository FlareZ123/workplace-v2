#!/usr/bin/env python3
"""Read-only K08 image-channel intake scanner.

Hypothesis: the eight-note ATEALBIT selector plus the blue/colour/photo references
may point to a low-bit payload in a crew photograph. This tool does not assume
that hypothesis is true. It scans only caller-supplied image files, checks a
small, explicit set of colour/bit-plane layouts, and validates candidate text
against the K08 HMAC commitment.

No network access; no image modification. Candidate text is emitted only on
an exact commitment match.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Iterator

import numpy as np
from PIL import Image

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp"}
ASCII_RUN = re.compile(r"[\x20-\x7e]{4,}")
WORD = re.compile(r"[a-z0-9]+")


def normalize_phrase(value: str) -> str:
    value = value.lower()
    value = "".join(c if ("a" <= c <= "z" or "0" <= c <= "9" or c.isspace()) else " " for c in value)
    return " ".join(value.split())


def k08_matches(value: str, nonce: bytes, commitment: str) -> bool:
    normalized = normalize_phrase(value)
    if not normalized:
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


def _ngrams(text: str, max_words: int = 20) -> Iterator[str]:
    words = WORD.findall(text.lower())
    # Avoid quadratic blow-up on a full-page OCR or a long image payload.
    if len(words) > 300:
        words = words[:300]
    for start in range(len(words)):
        for width in range(2, min(max_words, len(words) - start) + 1):
            yield " ".join(words[start : start + width])
    if words:
        yield " ".join(words)


def _bit_variants(image: Image.Image) -> Iterator[tuple[str, np.ndarray]]:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    # Include hue as a separate channel: a literal "teal bit" may refer to the
    # green/blue balance rather than one raw RGB channel.
    hsv = np.asarray(image.convert("HSV"), dtype=np.uint8)
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


def scan_image(path: Path, nonce: bytes, commitment: str, max_words: int = 20) -> list[dict]:
    matches: list[dict] = []
    with Image.open(path) as opened:
        frames = getattr(opened, "n_frames", 1)
        for frame in range(frames):
            if frames > 1:
                opened.seek(frame)
            image = opened.copy()
            for layout, bits in _bit_variants(image):
                seen: set[str] = set()
                for run in _candidate_texts(bits):
                    # Keep only short runs likely to be a caption; long random
                    # printable regions are not useful phrase candidates.
                    run = run[:4096]
                    for candidate in _ngrams(run, max_words=max_words):
                        normalized = normalize_phrase(candidate)
                        if normalized in seen:
                            continue
                        seen.add(normalized)
                        if k08_matches(normalized, nonce, commitment):
                            matches.append({
                                "file": str(path),
                                "frame": frame,
                                "layout": layout,
                                "phrase": normalized,
                            })
    return matches


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
    parser.add_argument("--images", type=Path, required=True, help="directory containing authorized source images")
    parser.add_argument("--evidence-root", type=Path, required=True, help="directory containing recovery-routing.json and acceptance.json")
    parser.add_argument("--max-words", type=int, default=20)
    args = parser.parse_args()
    nonce, commitment = load_commitment(args.evidence_root)
    files = sorted(p for p in args.images.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
    all_matches: list[dict] = []
    errors: list[dict] = []
    for path in files:
        try:
            all_matches.extend(scan_image(path, nonce, commitment, max_words=args.max_words))
        except Exception as exc:  # keep the intake moving past one damaged image
            errors.append({"file": str(path), "error": type(exc).__name__})
    print(json.dumps({"images_scanned": len(files), "matches": all_matches, "errors": errors}, indent=2))
    return 0 if all_matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
