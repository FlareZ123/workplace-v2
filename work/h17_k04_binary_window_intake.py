#!/usr/bin/env python3
"""Read-only exact K04 commitment scanner for recovered native spool/AX-7782 files.

Scans raw 16-byte windows and standalone ASCII/UTF-16LE/UTF-16BE
32-hex-character tokens, including native OLE/CFB printer files. For each
candidate block B it checks both SHA256(B) and SHA256(B XOR route_mask) against
the K04 component commitment. It also descends into ZIP, TAR, and GZIP members
without extracting them to disk. No heuristic transformations are attempted.

The target and route mask are loaded from local acceptance/routing files at runtime and are never emitted.
Use --self-test to validate raw, masked, and ASCII-hex detection without any
historical source files. Inputs are never modified.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import os
import re
import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

from h17_redaction import redact_by_default, redact_sensitive

import h17_ax7782_object_intake as intake

OPAQUE_PDF_SHA256 = intake.OPAQUE_PDF_SHA256
from h17_k04_image_barcode_intake import read_image_barcodes
from h17_k04_emf_dib_intake import extract_emf_dib_bmps
from h17_k04_pdf_barcode_intake import (
    iter_pdf_barcode_images, iter_pdf_coupon_text, iter_pdf_embedded_files,
)
from h17_k04_pcl_raster_intake import extract_pcl_raster_images
from h17_ooxml_text_intake import iter_ooxml_text_units
from h17_emf_text import extract_emf_text
from h17_xps_text import could_contain_xps, extract_xps_text
from h17_xps_glyph_indices import extract_xps_glyph_streams

DEFAULT_MAX_MEMBER = 256 * 1024 * 1024
DEFAULT_MAX_TOTAL = 512 * 1024 * 1024
DEFAULT_MAX_DEPTH = 4
DEFAULT_MAX_MEMBERS = 10000
HEX32 = re.compile(rb"(?i)(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")
# Windows native print streams also commonly store coupon text as UTF-16.
# Match exact 32-character tokens in either byte order, preserving boundaries.
HEX32_UTF16LE = re.compile(rb"(?i)(?<![0-9a-f]\x00)(?:[0-9a-f]\x00){32}(?![0-9a-f]\x00)")
HEX32_UTF16BE = re.compile(rb"(?i)(?<!\x00[0-9a-f])(?:\x00[0-9a-f]){32}(?!\x00[0-9a-f])")
HEX16_GROUPED = re.compile(rb"(?i)(?<![0-9a-f])(?:[0-9a-f]{2}[\s:.-]{1,3}){15}[0-9a-f]{2}(?![0-9a-f])")
BASE64_16 = re.compile(rb"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{22}==(?![A-Za-z0-9+/=])")

UUID_16 = re.compile(
    rb"(?i)(?<![a-z0-9])[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-"
    rb"[a-f0-9]{4}-[a-f0-9]{12}(?![a-z0-9])"
)
BASE32_16 = re.compile(
    rb"(?i)(?<![a-z2-7])[a-z2-7]{26}(?:={6})?(?![a-z2-7=])"
)
BASE64_URLSAFE_16 = re.compile(
    rb"(?<![A-Za-z0-9+/_-])[A-Za-z0-9+/_-]{22}(?:==)?"
    rb"(?![A-Za-z0-9+/_=-])"
)



def magic(data: bytes) -> str:
    if data.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        return "zip"
    if data.startswith(b"\x1f\x8b"):
        return "gzip"
    if len(data) >= 262 and data[257:262] == b"ustar":
        return "tar"
    if data.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "ole-compound"
    if data.startswith(b"%PDF-"):
        return "pdf"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith((b"II*\x00", b"MM\x00*")):
        return "tiff"
    if data.startswith(b"BM"):
        return "bmp"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith(b"\x7fELF"):
        return "elf"
    return "unknown"


def candidate_hit(block: bytes, target_digest: bytes, mask: bytes):
    """Return (kind, component_bytes) if block is a component or masked payload."""
    if hashlib.sha256(block).digest() == target_digest:
        return "direct_component", block
    unmasked = bytes(a ^ b for a, b in zip(block, mask))
    if hashlib.sha256(unmasked).digest() == target_digest:
        return "payload_xor_route_mask", unmasked
    return None


def scan_bytes(name: str, data: bytes, target_digest: bytes, mask: bytes, stride: int):
    hits = []
    seen = set()
    if len(data) >= 16:
        for offset in range(0, len(data) - 15, stride):
            block = data[offset:offset + 16]
            hit = candidate_hit(block, target_digest, mask)
            if hit:
                kind, component = hit
                key = (kind, offset, component)
                if key not in seen:
                    seen.add(key)
                    hits.append({"source": name, "encoding": "raw-window", "offset": offset,
                                 "kind": kind, "component_hex": component.hex().upper(),
                                 "window_hex": block.hex().upper()})
    for match in HEX32.finditer(data):
        try:
            block = bytes.fromhex(match.group().decode("ascii"))
        except ValueError:
            continue
        hit = candidate_hit(block, target_digest, mask)
        if hit:
            kind, component = hit
            key = (kind, match.start(), component)
            if key not in seen:
                seen.add(key)
                hits.append({"source": name, "encoding": "ascii-hex-token", "offset": match.start(),
                             "kind": kind, "component_hex": component.hex().upper(),
                             "window_hex": block.hex().upper()})
    for encoding, pattern, codec in (
        ("utf16le-hex-token", HEX32_UTF16LE, "utf-16le"),
        ("utf16be-hex-token", HEX32_UTF16BE, "utf-16be"),
    ):
        for match in pattern.finditer(data):
            block = bytes.fromhex(match.group().decode(codec))
            hit = candidate_hit(block, target_digest, mask)
            if hit:
                kind, component = hit
                key = (kind, match.start(), component)
                if key not in seen:
                    seen.add(key)
                    hits.append({"source": name, "encoding": encoding,
                                 "offset": match.start(), "kind": kind,
                                 "component_hex": component.hex().upper(),
                                 "window_hex": block.hex().upper()})
    for match in HEX16_GROUPED.finditer(data):
        compact = re.sub(rb"[\s:.-]", b"", match.group())
        block = bytes.fromhex(compact.decode("ascii"))
        hit = candidate_hit(block, target_digest, mask)
        if hit:
            kind, component = hit
            key = (kind, match.start(), component)
            if key not in seen:
                seen.add(key)
                hits.append({"source": name, "encoding": "grouped-hex-bytes",
                             "offset": match.start(), "kind": kind,
                             "component_hex": component.hex().upper(),
                             "window_hex": block.hex().upper()})
    for match in BASE64_16.finditer(data):
        block = base64.b64decode(match.group(), validate=True)
        hit = candidate_hit(block, target_digest, mask)
        if hit:
            kind, component = hit
            key = (kind, match.start(), component)
            if key not in seen:
                seen.add(key)
                hits.append({"source": name, "encoding": "base64-16bytes",
                             "offset": match.start(), "kind": kind,
                             "component_hex": component.hex().upper(),
                             "window_hex": block.hex().upper()})
    for match in UUID_16.finditer(data):
        payload = bytes.fromhex(match.group().replace(b"-", b"").decode("ascii"))
        for order, block in (
            ("rfc", payload),
            ("windows-guid", payload[0:4][::-1] + payload[4:6][::-1]
             + payload[6:8][::-1] + payload[8:]),
        ):
            hit = candidate_hit(block, target_digest, mask)
            if hit:
                kind, component = hit
                hits.append({"source": name, "encoding": "uuid-" + order,
                             "offset": match.start(), "kind": kind,
                             "component_hex": component.hex().upper(),
                             "window_hex": block.hex().upper()})
    for match in BASE32_16.finditer(data):
        token = match.group().upper().rstrip(b"=")
        block = base64.b32decode(token + b"======", casefold=True)
        hit = candidate_hit(block, target_digest, mask)
        if hit:
            kind, component = hit
            hits.append({"source": name, "encoding": "base32-16bytes",
                         "offset": match.start(), "kind": kind,
                         "component_hex": component.hex().upper(),
                         "window_hex": block.hex().upper()})
    for match in BASE64_URLSAFE_16.finditer(data):
        token = match.group()
        if token.endswith(b"==") and b"-" not in token and b"_" not in token:
            continue  # Already handled by the strict standard Base64 branch.
        block = base64.urlsafe_b64decode(token.rstrip(b"=") + b"==")
        if len(block) != 16:
            continue
        hit = candidate_hit(block, target_digest, mask)
        if hit:
            kind, component = hit
            hits.append({"source": name, "encoding": "base64url-16bytes",
                         "offset": match.start(), "kind": kind,
                         "component_hex": component.hex().upper(),
                         "window_hex": block.hex().upper()})
    return hits


def scan_member(name: str, data: bytes, depth: int, budget: list[int], target_digest: bytes,
                mask: bytes, stride: int, max_member: int, max_depth: int):
    sha256 = hashlib.sha256(data).hexdigest()
    if sha256 == OPAQUE_PDF_SHA256:
        budget[2] += 1
        budget[0] += len(data)
        return {"name": name, "size": len(data), "sha256": sha256,
                "status": "skipped_opaque_pdf"}
    if intake.is_opaque_pdf_name(name):
        budget[2] += 1
        budget[0] += len(data)
        return {"name": name, "size": len(data),
                "status": "skipped_opaque_pdf_by_name"}
    kind = magic(data)
    # OLE/CFB has no member walker here. Scan its original bytes directly so
    # a complete coupon inside a native Workbook/Book/SHD stream is observable.
    container = kind in {"zip", "tar", "gzip"} or name.casefold().endswith((".eml", ".msg"))
    result = {"name": name, "size": len(data), "sha256": sha256, "magic": kind}
    budget[2] += 1
    if budget[2] > budget[3]:
        result["scan_limit"] = "member-count cap exceeded"
        return result
    if len(data) > max_member:
        result["scan_limit"] = "member exceeds max-member-bytes"
        return result
    budget[0] += len(data)
    if budget[0] > budget[1]:
        result["scan_limit"] = "cumulative decompressed/read byte budget exceeded"
        return result
    result["hits"] = [] if container else scan_bytes(name, data, target_digest, mask, stride)
    if kind == "zip":
        for label, authored in iter_ooxml_text_units(data):
            result["hits"].extend(scan_bytes(
                f"{name}!/{label}", authored, target_digest, mask, stride
            ))
    if kind == "pdf":
        for label, text_bytes in iter_pdf_coupon_text(data):
            result["hits"].extend(scan_bytes(
                f"{name}!/{label}", text_bytes, target_digest, mask, stride
            ))
        for label, image_bytes in iter_pdf_barcode_images(data):
            decoded, diagnostics = read_image_barcodes(image_bytes)
            if diagnostics:
                result.setdefault("pdf_barcode_diagnostics", []).append({
                    "source": label, "errors": diagnostics,
                })
            for symbol, coupon_data in decoded:
                for hit in scan_bytes(
                    f"{name}!/{label}-{symbol}", coupon_data,
                    target_digest, mask, stride,
                ):
                    hit["encoding"] = f"pdf-image-{symbol}-{hit['encoding']}"
                    result["hits"].append(hit)
    if kind in {"png", "jpeg", "tiff", "gif", "bmp", "webp"}:
        decoded, decoder_errors = read_image_barcodes(data)
        if decoder_errors:
            result["image_barcode_diagnostics"] = decoder_errors
        for symbol, coupon_data in decoded:
            for hit in scan_bytes(
                f"{name}!/image-{symbol}", coupon_data, target_digest, mask, stride
            ):
                hit["encoding"] = f"image-{symbol}-{hit['encoding']}"
                result["hits"].append(hit)

    if kind == "ole-compound" and name.casefold().endswith(".msg"):
        from h17_ax7782_k08_phrase_intake import iter_text_streams
        errors: list[dict] = []
        text_budget = [0]
        for source, payload in iter_text_streams(
            name, data, 0, text_budget, errors, False, None, [],
        ):
            if source == name and payload == data:
                continue  # The raw Outlook OLE carrier was scanned above.
            result["hits"].extend(scan_bytes(
                source, payload, target_digest, mask, stride,
            ))
        if errors:
            result["msg_decode_diagnostics"] = errors
    if not container and b"\x1b*r" in data and b"\x1b*b" in data:
        for label, png in extract_pcl_raster_images(data):
            decoded, diagnostics = read_image_barcodes(png)
            if diagnostics:
                result.setdefault("pcl_raster_diagnostics", []).append({
                    "source": label, "errors": diagnostics,
                })
            for symbol, coupon_data in decoded:
                for hit in scan_bytes(
                    f"{name}!/{label}-{symbol}", coupon_data,
                    target_digest, mask, stride,
                ):
                    hit["encoding"] = f"pcl-raster-{symbol}-{hit['encoding']}"
                    result["hits"].append(hit)
    if not container and b" EMF" in data and any(name.casefold().endswith(suffix)
                               for suffix in (".spl", ".prn", ".emf")):
        for label, bitmap in extract_emf_dib_bmps(data):
            decoded, diagnostics = read_image_barcodes(bitmap)
            if diagnostics:
                result.setdefault("emf_bitmap_diagnostics", []).append({
                    "record": label, "errors": diagnostics,
                })
            for symbol, coupon_data in decoded:
                for hit in scan_bytes(
                    f"{name}!/{label}-{symbol}", coupon_data,
                    target_digest, mask, stride,
                ):
                    hit["encoding"] = f"emf-bitmap-{symbol}-{hit['encoding']}"
                    result["hits"].append(hit)
    if not container and b" EMF" in data and any(name.casefold().endswith(suffix)
                               for suffix in (".spl", ".prn", ".emf")):
        for label, text in extract_emf_text(data):
            result["hits"].extend(scan_bytes(
                f"{name}!/{label}", text, target_digest, mask, stride
            ))
            compact_hex = text.translate(None, b" \t\r\n:.-")
            if compact_hex != text:
                result["hits"].extend(scan_bytes(
                    f"{name}!/{label}-grouped-hex", compact_hex,
                    target_digest, mask, stride
                ))
    if could_contain_xps(data):
        for label, text in extract_xps_text(data):
            result["hits"].extend(scan_bytes(
                f"{name}!/{label}", text, target_digest, mask, stride
            ))
            compact_hex = text.translate(None, b" \t\r\n:.-")
            if compact_hex != text:
                result["hits"].extend(scan_bytes(
                    f"{name}!/{label}-grouped-hex", compact_hex,
                    target_digest, mask, stride
                ))
        # Glyphs/Indices pages require font mapping; the adapter refuses
        # incomplete or ambiguous coverage instead of emitting guessed text.
        try:
            glyph_streams = extract_xps_glyph_streams(data)
        except Exception as exc:
            result.setdefault("extraction_errors", []).append({
                "extractor": "xps-glyph-indices",
                "error": f"{type(exc).__name__}:{exc}",
            })
        else:
            for label, text in glyph_streams:
                result["hits"].extend(scan_bytes(
                    f"{name}!/{label}", text, target_digest, mask, stride
                ))
                compact_hex = text.translate(None, b" \t\r\n:.-")
                if compact_hex != text:
                    result["hits"].extend(scan_bytes(
                        f"{name}!/{label}-grouped-hex", compact_hex,
                        target_digest, mask, stride
                    ))
    if depth >= max_depth:
        if result["magic"] in {"zip", "tar", "gzip"}:
            result["scan_limit"] = "max-depth reached"
        return result

    children = []
    kind = result["magic"]
    if kind == "zip":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                for item in archive.infolist():
                    path = PurePosixPath(item.filename)
                    mode = (item.external_attr >> 16) & 0xFFFF
                    if (item.is_dir() or item.file_size > max_member or path.is_absolute()
                            or ".." in path.parts or stat.S_ISLNK(mode)):
                        continue
                    if intake.is_opaque_pdf_name(item.filename):
                        children.append({
                            "name": f"{name}!/{item.filename}",
                            "size": item.file_size,
                            "status": "skipped_opaque_pdf_by_name",
                        })
                        continue
                    with archive.open(item) as stream:
                        child = stream.read(max_member + 1)
                    children.append(scan_member(f"{name}!/{item.filename}", child, depth + 1,
                                                budget, target_digest, mask, stride, max_member, max_depth))
                    if budget[0] > budget[1] or budget[2] >= budget[3]:
                        result["scan_limit"] = "cumulative byte or member-count cap reached"
                        break
        except (zipfile.BadZipFile, OSError, RuntimeError, EOFError) as exc:
            result["container_error"] = str(exc)
    elif kind == "tar":
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
                for item in archive.getmembers():
                    path = PurePosixPath(item.name)
                    if (not item.isfile() or item.size > max_member or path.is_absolute()
                            or ".." in path.parts):
                        continue
                    if intake.is_opaque_pdf_name(item.name):
                        children.append({
                            "name": f"{name}!/{item.name}",
                            "size": item.size,
                            "status": "skipped_opaque_pdf_by_name",
                        })
                        continue
                    stream = archive.extractfile(item)
                    if stream is not None:
                        child = stream.read(max_member + 1)
                        children.append(scan_member(f"{name}!/{item.name}", child, depth + 1,
                                                    budget, target_digest, mask, stride, max_member, max_depth))
                        if budget[0] > budget[1] or budget[2] >= budget[3]:
                            result["scan_limit"] = "cumulative byte or member-count cap reached"
                            break
        except (tarfile.TarError, OSError, EOFError) as exc:
            result["container_error"] = str(exc)
    elif kind == "pdf":
        for filename, payload in iter_pdf_embedded_files(data):
            child = scan_member(
                f"{name}!/{filename}", payload, depth + 1, budget,
                target_digest, mask, stride, max_member, max_depth,
            )
            children.append(child)
            if budget[0] > budget[1] or budget[2] >= budget[3]:
                result["scan_limit"] = "PDF embedded-file member budget reached"
                break
    elif name.casefold().endswith(".eml"):
        from email import policy
        from email.parser import BytesParser

        try:
            message = BytesParser(policy=policy.default).parsebytes(data)
            for index, part in enumerate(message.walk()):
                if part.is_multipart():
                    continue
                filename = part.get_filename() or f"mime-part-{index}.bin"
                filename = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
                if intake.is_opaque_pdf_name(filename):
                    children.append({
                        "name": f"{name}!/{filename}",
                        "status": "skipped_opaque_pdf_by_name",
                    })
                    continue
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                child = scan_member(
                    f"{name}!/{filename}", payload, depth + 1, budget,
                    target_digest, mask, stride, max_member, max_depth,
                )
                children.append(child)
                if budget[0] > budget[1] or budget[2] >= budget[3]:
                    result["scan_limit"] = "MIME member budget reached"
                    break
        except (ValueError, TypeError, LookupError) as exc:
            result["container_error"] = f"MIME parse failed: {type(exc).__name__}: {exc}"
    elif kind == "gzip":
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
                child = stream.read(max_member + 1)
            children.append(scan_member(f"{name}!/<gzip-payload>", child, depth + 1,
                                        budget, target_digest, mask, stride, max_member, max_depth))
        except (OSError, EOFError) as exc:
            result["container_error"] = str(exc)
    if children:
        result["members"] = children
    return result


def walk_files(root: Path):
    if root.is_file():
        if not root.is_symlink():
            yield root
        return
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(base) / d).is_symlink())
        for filename in sorted(files):
            path = Path(base) / filename
            if path.is_file() and not path.is_symlink():
                yield path


@redact_by_default
def run_scan(root: Path, target_hex: str, mask_hex: str, stride: int,
             max_member: int, max_total: int, max_depth: int, max_members: int):
    target_digest = bytes.fromhex(target_hex)
    mask = bytes.fromhex(mask_hex)
    budget = [0, max_total, 0, max_members]
    files = []
    all_hits = []
    skipped = []
    for path in walk_files(root):
        try:
            size = path.stat().st_size
            if size > max_member:
                skipped.append({"path": str(path), "size": size, "reason": "file exceeds max-member-bytes"})
                continue
            data = path.read_bytes()
            scanned = scan_member(str(path), data, 0, budget, target_digest, mask,
                                  stride, max_member, max_depth)
            files.append(scanned)
            all_hits.extend(scanned.get("hits", []))

            def collect(node):
                for child in node.get("members", []):
                    all_hits.extend(child.get("hits", []))
                    collect(child)
            collect(scanned)
        except OSError as exc:
            skipped.append({"path": str(path), "reason": str(exc)})
        if budget[0] > max_total or budget[2] >= max_members:
            skipped.append({"path": str(path), "reason": "cumulative byte or member-count budget reached; scan stopped"})
            break
    return {"input": str(root), "target_sha256": target_hex.lower(), "route_mask_hex": mask.hex().upper(),
            "stride": stride, "files": files, "files_scanned": len(files),
            "bytes_scanned_or_decompressed": budget[0], "members_scanned": budget[2],
            "max_members": max_members, "hits": all_hits, "skipped": skipped,
            "interpretation": "A direct hit is a 16-byte component. A masked hit is a 16-byte source payload whose XOR with the published route mask hashes to the K04 commitment. XPS/OXPS UnicodeString and unambiguous glyph-index text are scanned; inspect per-file extraction_errors and scan_limit fields. No hit does not exclude incomplete glyph mapping, bitmap/outline-only text, or unsupported print framing."}


def self_test():
    component = bytes(range(16))
    mask = bytes(range(16))
    payload = bytes(a ^ b for a, b in zip(component, mask))
    target = hashlib.sha256(component).digest()
    blob = b"prefix" + payload + b"middle=" + component.hex().encode("ascii") + b"=suffix"
    hits = scan_bytes("fixture", blob, target, mask, 1)
    kinds = {h["kind"] for h in hits}
    encodings = {h["encoding"] for h in hits}
    assert "payload_xor_route_mask" in kinds, hits
    assert "direct_component" in kinds, hits
    assert "raw-window" in encodings and "ascii-hex-token" in encodings, hits
    # Original scanner suppressed every byte of an OLE-compound source:
    # it classified CFB as a container but had no CFB member traversal.
    # Keep the complete planted coupon inside a source-signature CFB blob.
    ole_blob = bytes.fromhex("D0CF11E0A1B11AE1") + bytes(48) + payload + bytes(32)
    budget = [0, 100_000, 0, 100]
    ole = scan_member("fixture.xls", ole_blob, 0, budget,
                      target, mask, 1, 100_000, 4)
    assert ole["magic"] == "ole-compound", ole
    assert any(hit["kind"] == "payload_xor_route_mask" for hit in ole["hits"]), ole
    utf16_hits = []
    for codec, label in (("utf-16le", "utf16le-hex-token"),
                         ("utf-16be", "utf16be-hex-token")):
        encoded_coupon = ("!" + payload.hex().upper() + "!").encode(codec)
        found = scan_bytes("fixture.spl", encoded_coupon, target, mask, 1)
        assert any(hit["kind"] == "payload_xor_route_mask"
                   and hit["encoding"] == label for hit in found), (codec, found)
        utf16_hits.append(label)
    grouped_hex = ":".join(
        payload.hex().upper()[i:i + 2] for i in range(0, 32, 2)
    ).encode("ascii")
    b64 = base64.b64encode(payload)
    for label, token in (("grouped-hex-bytes", grouped_hex),
                         ("base64-16bytes", b64)):
        found = scan_bytes("fixture.spl", b"[" + token + b"]", target, mask, 1)
        assert any(hit["kind"] == "payload_xor_route_mask"
                   and hit["encoding"] == label for hit in found), (label, found)
    return {"ok": True, "hits": len(hits), "kinds": sorted(kinds),
            "encodings": sorted(encodings), "ole_compound_coupon": "PASS",
            "utf16_encodings": utf16_hits,
            "grouped_hex_and_base64": "PASS"}


def load_k04_rules(resources: Path) -> tuple[str, str]:
    route = json.loads((resources / "evidence" / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    mask_hex = str(route["K04"]["masked_component"])
    target_hex = str(acceptance["slot_sha256"]["K04"])
    if len(target_hex) != 64 or len(mask_hex) != 32:
        raise ValueError("invalid K04 commitment or route-mask width")
    bytes.fromhex(target_hex)
    bytes.fromhex(mask_hex)
    return target_hex, mask_hex


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="native spool file or directory, or AX-7782 object")
    parser.add_argument("--resources", type=Path, default=Path(__file__).resolve().parents[1] / "resources")
    parser.add_argument("--stride", type=int, default=1, help="raw-window byte stride; default 1 is exhaustive")
    parser.add_argument("--max-member-bytes", type=int, default=DEFAULT_MAX_MEMBER)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL)
    parser.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH)
    parser.add_argument("--max-members", type=int, default=DEFAULT_MAX_MEMBERS)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return
    if args.input is None:
        parser.error("--input is required unless --self-test is used")
    try:
        target_hex, mask_hex = load_k04_rules(args.resources)
    except Exception as exc:
        parser.error(type(exc).__name__)
    if (args.stride < 1 or args.max_member_bytes < 1 or args.max_total_bytes < 1
            or args.max_depth < 0 or args.max_members < 1):
        parser.error("stride/member/total limits must be positive and max-depth nonnegative")
    if not args.input.exists():
        parser.error(f"input does not exist: {args.input}")
    if args.json_out:
        output_path = args.json_out.resolve()
        input_path = args.input.resolve()
        if output_path == input_path or (input_path.is_dir() and input_path in output_path.parents):
            parser.error("--json-out must be outside the input file/directory; source inputs remain read-only")
    result = run_scan(args.input, target_hex, mask_hex, args.stride,
                      args.max_member_bytes, args.max_total_bytes, args.max_depth, args.max_members)
    result = redact_sensitive(result)
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
