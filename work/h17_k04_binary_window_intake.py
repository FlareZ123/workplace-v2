#!/usr/bin/env python3
"""Read-only exact K04 commitment scanner for recovered native spool/AX-7782 files.

Scans raw 16-byte windows and standalone 32-hex-character tokens. For each
candidate block B it checks both SHA256(B) and SHA256(B XOR route_mask) against
the K04 component commitment. It also descends into ZIP, TAR, and GZIP members
without extracting them to disk. No heuristic transformations are attempted.

The default target/mask are the current REC8/1 K04 acceptance/routing values.
Use --self-test to validate raw, masked, and ASCII-hex detection without any
historical source files. Inputs are never modified.
"""
from __future__ import annotations

import argparse
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

DEFAULT_TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
DEFAULT_MASK = "8556C8CB6140A7F9A5123AC7571BEE1C"
DEFAULT_MAX_MEMBER = 256 * 1024 * 1024
DEFAULT_MAX_TOTAL = 512 * 1024 * 1024
DEFAULT_MAX_DEPTH = 4
DEFAULT_MAX_MEMBERS = 10000
HEX32 = re.compile(rb"(?i)(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")


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
    return hits


def scan_member(name: str, data: bytes, depth: int, budget: list[int], target_digest: bytes,
                mask: bytes, stride: int, max_member: int, max_depth: int):
    result = {"name": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
              "magic": magic(data)}
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
    result["hits"] = scan_bytes(name, data, target_digest, mask, stride)
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
            "interpretation": "A direct hit is a 16-byte component. A masked hit is a 16-byte source payload whose XOR with the published route mask hashes to the K04 commitment. No hit means only that the scanned bytes/containers did not expose either representation."}


def self_test():
    component = bytes(range(16))
    mask = bytes.fromhex(DEFAULT_MASK)
    payload = bytes(a ^ b for a, b in zip(component, mask))
    target = hashlib.sha256(component).digest()
    blob = b"prefix" + payload + b"middle=" + component.hex().encode("ascii") + b"=suffix"
    hits = scan_bytes("fixture", blob, target, mask, 1)
    kinds = {h["kind"] for h in hits}
    encodings = {h["encoding"] for h in hits}
    assert "payload_xor_route_mask" in kinds, hits
    assert "direct_component" in kinds, hits
    assert "raw-window" in encodings and "ascii-hex-token" in encodings, hits
    return {"ok": True, "hits": len(hits), "kinds": sorted(kinds), "encodings": sorted(encodings)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="native spool file or directory, or AX-7782 object")
    parser.add_argument("--target-sha256", default=DEFAULT_TARGET, help="K04 component commitment (64 hex chars)")
    parser.add_argument("--mask", default=DEFAULT_MASK, help="16-byte route mask (32 hex chars)")
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
    if len(args.target_sha256) != 64 or len(args.mask) != 32:
        parser.error("target must be 64 hex chars and mask must be 32 hex chars")
    try:
        bytes.fromhex(args.target_sha256)
        bytes.fromhex(args.mask)
    except ValueError:
        parser.error("target and mask must be valid hexadecimal")
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
    result = run_scan(args.input, args.target_sha256, args.mask, args.stride,
                      args.max_member_bytes, args.max_total_bytes, args.max_depth, args.max_members)
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
