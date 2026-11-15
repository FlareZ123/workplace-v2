#!/usr/bin/env python3
"""Read-only K04 binary-window scan over an authorized H-17 profile inventory.

Consumes the hashed inventory from h17_profile_inventory.py, re-verifies each
candidate file, then reuses h17_k04_binary_window_intake.py to search raw
16-byte windows, ASCII-hex tokens, and ZIP/TAR/GZIP members for either the
K04 component or a source payload whose XOR with the published route mask
matches the K04 commitment.

Only inventory categories relevant to the incident are scanned. Credential
stores and Outlook PST/OST/NSF stores are excluded; .eml/.msg files require
an explicit --include-eml-msg opt-in. Source files are never modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import h17_k04_binary_window_intake as k04

DEFAULT_CATEGORIES = {
    "notes",
    "photo_caption",
    "office_document",
    "transfer_archive",
    "profile_migration",
    "offline_files_cache",
    "printer",
}
PROFILE_METADATA_ALLOW = ("thumbcache", "thumbs.db")
MAIL_SUFFIXES = {".pst", ".ost", ".nst", ".mbox"}
MESSAGE_SUFFIXES = {".eml", ".msg"}
REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _is_reparse_or_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return True
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & REPARSE_POINT
    )


def _safe_inventory_path(root: Path, relative: str) -> Path:
    rel = PurePosixPath(relative.replace("\\", "/"))
    if rel.is_absolute() or not rel.parts or any(part in ("", ".", "..") for part in rel.parts):
        raise ValueError("unsafe inventory-relative path")
    candidate = root.joinpath(*rel.parts)
    resolved = candidate.resolve(strict=True)
    try:
        common = os.path.commonpath((os.path.normcase(str(root)), os.path.normcase(str(resolved))))
    except ValueError as exc:
        raise ValueError("inventory path escapes source root") from exc
    if common != os.path.normcase(str(root)):
        raise ValueError("inventory path escapes source root")
    if _is_reparse_or_link(candidate) or not resolved.is_file():
        raise ValueError("source is not a regular, non-link file")
    return resolved


def _include_record(record: dict[str, Any], include_eml_msg: bool) -> bool:
    categories = set(record.get("categories") or [])
    relative = str(record.get("path", "")).replace("\\", "/").casefold()
    suffix = Path(relative).suffix.casefold()
    if suffix in MAIL_SUFFIXES:
        return False
    if "mail" in categories:
        return include_eml_msg and suffix in MESSAGE_SUFFIXES
    if categories & DEFAULT_CATEGORIES:
        return True
    if "profile_metadata" in categories:
        return any(token in relative for token in PROFILE_METADATA_ALLOW)
    return False


def _collect_hits(node: dict[str, Any], output: list[dict[str, Any]]) -> None:
    for hit in node.get("hits", []):
        output.append(hit)
    for child in node.get("members", []):
        _collect_hits(child, output)


def scan_inventory(
    inventory_path: Path,
    target_hex: str,
    mask_hex: str,
    stride: int = 1,
    max_member_bytes: int = k04.DEFAULT_MAX_MEMBER,
    max_total_bytes: int = k04.DEFAULT_MAX_TOTAL,
    max_depth: int = k04.DEFAULT_MAX_DEPTH,
    max_members: int = k04.DEFAULT_MAX_MEMBERS,
    include_eml_msg: bool = False,
) -> dict[str, Any]:
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if inventory.get("schema") != "h17-profile-inventory/v1":
        raise ValueError("unsupported profile inventory schema")
    root = Path(inventory["source_root"]).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("inventory source_root is not a directory")

    target_digest = bytes.fromhex(target_hex)
    mask = bytes.fromhex(mask_hex)
    budget = [0, max_total_bytes, 0, max_members]
    files: list[dict[str, Any]] = []
    hits: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    files_considered = files_scanned = 0
    started = time.monotonic()

    for record in inventory.get("files", []):
        if not isinstance(record, dict) or not _include_record(record, include_eml_msg):
            continue
        files_considered += 1
        relative = str(record.get("path", ""))
        expected_hash = record.get("sha256")
        expected_size = record.get("size")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            skipped.append({"path": relative, "reason": "no_inventory_sha256"})
            continue
        try:
            path = _safe_inventory_path(root, relative)
            size = path.stat().st_size
            if expected_size is not None and int(expected_size) != size:
                skipped.append({"path": relative, "reason": "size_changed_since_inventory"})
                continue
            if size > max_member_bytes:
                skipped.append({"path": relative, "reason": "file_size_limit"})
                continue
            if budget[0] + size > max_total_bytes or budget[2] >= max_members:
                skipped.append({"path": relative, "reason": "cumulative_budget_reached"})
                break
            actual_hash = _sha256_file(path)
            if actual_hash.casefold() != expected_hash.casefold():
                skipped.append({"path": relative, "reason": "sha256_changed_since_inventory"})
                continue
            data = path.read_bytes()
        except (OSError, ValueError, TypeError) as exc:
            skipped.append({"path": relative, "reason": f"source_unavailable:{type(exc).__name__}:{exc}"})
            continue

        try:
            scanned = k04.scan_member(
                relative.replace("\\", "/"),
                data,
                0,
                budget,
                target_digest,
                mask,
                stride,
                max_member_bytes,
                max_depth,
            )
            files_scanned += 1
            file_hits: list[dict[str, Any]] = []
            _collect_hits(scanned, file_hits)
            hits.extend(file_hits)
            files.append({
                "path": relative.replace("\\", "/"),
                "size": size,
                "sha256": actual_hash,
                "magic": scanned.get("magic"),
                "hits": file_hits,
                "scan_limit": scanned.get("scan_limit"),
                "container_error": scanned.get("container_error"),
            })
        except Exception as exc:
            skipped.append({"path": relative, "reason": f"scan_error:{type(exc).__name__}:{exc}"})
        if budget[0] > max_total_bytes or budget[2] >= max_members:
            skipped.append({"path": relative, "reason": "cumulative byte/member cap reached; scan stopped"})
            break

    return {
        "schema": "h17-profile-k04-binary-scan/v1",
        "inventory": str(inventory_path),
        "source_root": str(root),
        "source_writes_performed": False,
        "credential_stores_opened": False,
        "mail_stores_opened": False,
        "include_eml_msg": include_eml_msg,
        "files_considered": files_considered,
        "files_scanned": files_scanned,
        "bytes_scanned_or_decompressed": budget[0],
        "members_scanned": budget[2],
        "hits": hits,
        "files": files,
        "skipped": skipped,
        "stride": stride,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "interpretation": (
            "A direct hit is a 16-byte K04 component. A payload_xor_route_mask hit is a "
            "16-byte source payload whose XOR with the published route mask matches the "
            "K04 component commitment. No hit only excludes the hashed inventory entries "
            "actually scanned under the stated byte/member limits."
        ),
    }


def self_test() -> dict[str, Any]:
    import tempfile

    component = bytes(range(16))
    mask = bytes.fromhex("102132435465768798A9BACBDCEDFE0F")
    payload = bytes(a ^ b for a, b in zip(component, mask))
    target = hashlib.sha256(component).hexdigest()
    with tempfile.TemporaryDirectory(prefix="h17-profile-k04-test-") as temp:
        root = Path(temp) / "profile"
        (root / "printer").mkdir(parents=True)
        source = root / "printer" / "job.SPL"
        source.write_bytes(b"prefix:" + payload + b":hex:" + component.hex().encode("ascii"))
        inventory = {
            "schema": "h17-profile-inventory/v1",
            "source_root": str(root),
            "files": [{
                "path": "printer/job.SPL",
                "size": source.stat().st_size,
                "sha256": _sha256_file(source),
                "categories": ["printer"],
            }],
        }
        inventory_path = Path(temp) / "inventory.json"
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
        before = _sha256_file(source)
        result = scan_inventory(
            inventory_path, target, mask.hex(),
            max_member_bytes=1024 * 1024, max_total_bytes=4 * 1024 * 1024,
        )
        after = _sha256_file(source)
        kinds = {hit.get("kind") for hit in result["hits"]}
        encodings = {hit.get("encoding") for hit in result["hits"]}
        if before != after:
            raise AssertionError("self-test detected source mutation")
        if "direct_component" not in kinds or "payload_xor_route_mask" not in kinds:
            raise AssertionError(f"expected direct and masked hits, got {result['hits']}")
        if "raw-window" not in encodings or "ascii-hex-token" not in encodings:
            raise AssertionError(f"expected raw and ASCII-hex encodings, got {result['hits']}")
        return {
            "ok": True,
            "hits": len(result["hits"]),
            "kinds": sorted(kinds),
            "encodings": sorted(encodings),
            "source_unchanged": before == after,
        }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, help="JSON output from h17_profile_inventory.py")
    parser.add_argument("--resources", type=Path, help="extracted H-17 resources root containing evidence/ and acceptance.json")
    parser.add_argument("--stride", type=int, default=1, help="raw-window byte stride; 1 is exhaustive")
    parser.add_argument("--max-member-bytes", type=int, default=k04.DEFAULT_MAX_MEMBER)
    parser.add_argument("--max-total-bytes", type=int, default=k04.DEFAULT_MAX_TOTAL)
    parser.add_argument("--max-depth", type=int, default=k04.DEFAULT_MAX_DEPTH)
    parser.add_argument("--max-members", type=int, default=k04.DEFAULT_MAX_MEMBERS)
    parser.add_argument("--include-eml-msg", action="store_true", help="include only .eml/.msg after separate custodian authorization; PST/OST stores remain excluded")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.inventory is None or args.resources is None:
        parser.error("--inventory and --resources are required unless --self-test is used")
    if args.stride < 1 or args.max_member_bytes < 1 or args.max_total_bytes < 1 or args.max_depth < 0 or args.max_members < 1:
        parser.error("stride/member/total limits must be positive and max-depth nonnegative")

    resources = args.resources.resolve(strict=True)
    route = json.loads((resources / "evidence" / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    target_hex = acceptance["slot_sha256"]["K04"]
    mask_hex = route["K04"]["masked_component"]
    if target_hex.casefold() != k04.DEFAULT_TARGET.casefold() or mask_hex.casefold() != k04.DEFAULT_MASK.casefold():
        parser.error("K04 source rules do not match the constants in h17_k04_binary_window_intake.py")

    result = scan_inventory(
        args.inventory.resolve(strict=True),
        target_hex,
        mask_hex,
        stride=args.stride,
        max_member_bytes=args.max_member_bytes,
        max_total_bytes=args.max_total_bytes,
        max_depth=args.max_depth,
        max_members=args.max_members,
        include_eml_msg=args.include_eml_msg,
    )
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        output_path = args.json_out.resolve()
        root = Path(result["source_root"]).resolve()
        try:
            if os.path.commonpath((os.path.normcase(str(root)), os.path.normcase(str(output_path)))) == os.path.normcase(str(root)):
                parser.error("--json-out must be outside source_root")
        except ValueError:
            pass
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
