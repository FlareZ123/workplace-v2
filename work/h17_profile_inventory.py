"""Read-only inventory for an authorized H-17 retired-office profile image.

The scanner records paths and metadata for every non-excluded file. It hashes
only files whose path or extension is relevant to the K04/K08 source search.
It never parses document contents, opens credential stores, follows symlinks or
Windows reparse points, or writes inside the source tree.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any, Iterable

_CHUNK_SIZE = 1024 * 1024
_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)

_SENSITIVE_COMPONENTS = {
    "cookies", "credentials", "credential store", "vault", "keychains",
    "passwords", "login data", "web data", "oneauth", "identitycache",
    "tokenbroker", "protect", "crypto", "logins", "sam", "security",
    "wallet", "passkeys", "autofill", "form history",
}
_SENSITIVE_FILENAMES = {
    "cookies.sqlite", "cookies-journal", "login data", "login data for account",
    "web data", "local state", "logins.json", "key4.db", "key3.db",
    "signons.sqlite", "cert9.db", "cert8.db", "sam", "security", "sam.log1", "sam.log2",
    "security.log1", "security.log2", "ntds.dit", "ntds.dit.log1", "ntds.dit.log2",
    "form history", "autofill",
}
_SENSITIVE_SUFFIXES = {".pfx", ".p12", ".key", ".kdbx", ".pem"}

_CATEGORY_TOKENS = {
    "printer": (
        "ps-261003-0417", "ps-261003-0416", "ps-261003-0323", "fa-17",
        "esc-n", "printer", "spool", "printservice", "print service",
        "queue", "port monitor", "driver",
    ),
    "mail": ("outlook", "mailbox", "mapi", "message store", "mail"),
    "notes": ("onenote", "onecache", "sticky notes", "plum.sqlite", "onenoteofflinecache"),
    "photo_caption": (
        "photo", "caption", "galley", "desk-images", "wn-14", "pictures",
        "camera roll", "image",
    ),
    "profile_metadata": (
        "ntuser.dat", "usrclass.dat", "windows.edb", "recentdocs", "recent",
        "jumplist", "jump list", "thumbcache", "thumbs.db", "webcache",
        "browser", "chrome", "edge", "firefox", "cache", "history", "downloads",
        "autorecover", "auto-recover", "search", "esent",
        "system32/config/system", "system32/config/software",
    ),
    "transfer_archive": (
        "ax-7782", "ir-261003-h17", "bundle 06", "bundle06", "transfer",
        "handoff print", "records/index",
    ),
    "office_document": (
        "mug-stock", "wn-14", "desk-note", "desk note", "scanrelease",
        "renewal-ledger", "supplier", "receipt", "envelope",
    ),
}
_CATEGORY_EXTENSIONS = {
    "printer": {".spl", ".shd", ".evtx"},
    "mail": {".pst", ".ost", ".nst", ".msg", ".eml", ".mbox"},
    "notes": {".one", ".onecache"},
    "photo_caption": {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".webp", ".xmp"},
    "profile_metadata": {".dat", ".edb", ".sqlite", ".db", ".automaticdestinations-ms", ".customdestinations-ms"},
    "transfer_archive": {".zip", ".7z", ".tar", ".gz", ".vhd", ".vhdx", ".wim", ".img", ".raw"},
    "office_document": {".xls", ".xlsx", ".xlsm", ".doc", ".docx", ".ppt", ".pptx", ".pdf", ".html", ".htm", ".txt"},
}


def _utc(timestamp: float) -> str:
    return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _is_reparse_or_link(path: str, info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & _REPARSE_POINT)


def _sensitive_reason(relative_path: str) -> str | None:
    path = Path(relative_path)
    parts = [part.casefold() for part in path.parts]
    name = path.name.casefold()
    if name in _SENSITIVE_FILENAMES:
        return "sensitive_filename"
    if path.suffix.casefold() in _SENSITIVE_SUFFIXES:
        return "sensitive_suffix"
    for part in parts:
        if part in _SENSITIVE_COMPONENTS:
            return "sensitive_path_component"
        if any(token in part for token in ("password", "credential", "cookie", "keychain", "tokenbroker")):
            return "sensitive_path_component"
    return None


def _classify(relative_path: str) -> tuple[list[str], list[str]]:
    normalized = relative_path.replace("\\", "/").casefold()
    suffix = Path(relative_path).suffix.casefold()
    categories: set[str] = set()
    matched: set[str] = set()
    for category, tokens in _CATEGORY_TOKENS.items():
        for token in tokens:
            if token in normalized:
                categories.add(category)
                matched.add(token)
    for category, suffixes in _CATEGORY_EXTENSIONS.items():
        if suffix in suffixes:
            categories.add(category)
            matched.add(suffix)
    return sorted(categories), sorted(matched)


def _magic_label(prefix: bytes) -> str:
    if prefix.startswith(b"%PDF-"):
        return "PDF"
    if prefix.startswith(b"PK\x03\x04"):
        return "ZIP"
    if prefix.startswith(b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"):
        return "OLE_COMPOUND"
    if prefix.startswith(b"SQLite format 3\x00"):
        return "SQLITE3"
    if prefix.startswith(b"ElfFile\x00"):
        return "EVTX"
    if prefix.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    if prefix.startswith(b"\xff\xd8\xff"):
        return "JPEG"
    if prefix.startswith((b"II*\x00", b"MM\x00*")):
        return "TIFF"
    if prefix.startswith(b"!BDN"):
        return "PST_OR_OST"
    return "UNKNOWN"


def _hash_file(path: str, before: os.stat_result) -> dict[str, Any]:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        prefix = stream.read(16)
        digest.update(prefix)
        while chunk := stream.read(_CHUNK_SIZE):
            digest.update(chunk)
    after = os.stat(path, follow_symlinks=False)
    stable = before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns
    return {
        "sha256": digest.hexdigest() if stable else None,
        "hash_status": "stable" if stable else "changed_during_read",
        "magic": _magic_label(prefix),
    }


def build_inventory(source_root: str | os.PathLike[str]) -> dict[str, Any]:
    root_input = Path(source_root).absolute()
    root_info = os.lstat(root_input)
    if _is_reparse_or_link(str(root_input), root_info) or not stat.S_ISDIR(root_info.st_mode):
        raise ValueError("source_root must be a real directory, not a link or reparse point")
    root = root_input.resolve(strict=True)

    files: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    skipped_sensitive = 0
    skipped_links = 0

    def walk(directory: str, relative_directory: str) -> None:
        nonlocal skipped_sensitive, skipped_links
        try:
            with os.scandir(directory) as entries:
                ordered = sorted(entries, key=lambda item: item.name.casefold())
        except OSError as exc:
            errors.append({"path": relative_directory or ".", "error": f"scandir:{type(exc).__name__}:{exc}"})
            return

        for entry in ordered:
            relative = f"{relative_directory}/{entry.name}" if relative_directory else entry.name
            if _sensitive_reason(relative):
                skipped_sensitive += 1
                continue
            try:
                info = entry.stat(follow_symlinks=False)
                if _is_reparse_or_link(entry.path, info):
                    skipped_links += 1
                    continue
                if stat.S_ISDIR(info.st_mode):
                    walk(entry.path, relative)
                    continue
                if not stat.S_ISREG(info.st_mode):
                    continue
                categories, matched = _classify(relative)
                record: dict[str, Any] = {
                    "path": relative.replace("\\", "/"),
                    "size": info.st_size,
                    "mtime_utc": _utc(info.st_mtime),
                    "categories": categories,
                    "matched_terms": matched,
                    "hash_status": "not_hashed_non_candidate",
                    "sha256": None,
                    "magic": None,
                }
                if hasattr(info, "st_birthtime"):
                    record["created_utc"] = _utc(info.st_birthtime)
                if categories:
                    try:
                        record.update(_hash_file(entry.path, info))
                    except OSError as exc:
                        record["hash_status"] = f"read_error:{type(exc).__name__}"
                        errors.append({"path": relative, "error": f"hash:{type(exc).__name__}:{exc}"})
                files.append(record)
            except OSError as exc:
                errors.append({"path": relative, "error": f"stat:{type(exc).__name__}:{exc}"})

    walk(str(root), "")
    files.sort(key=lambda item: item["path"].casefold())
    return {
        "schema": "h17-profile-inventory/v1",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_root": str(root),
        "scope": "paths and metadata for non-excluded files; SHA-256 only for K04/K08-relevant candidates",
        "safety": {
            "read_only": True,
            "network_access": False,
            "content_parsing": False,
            "symlinks_and_reparse_points_followed": False,
            "credential_cookie_and_key_store_paths_opened": False,
        },
        "summary": {
            "files_listed": len(files),
            "candidate_files_hashed": sum(item["sha256"] is not None for item in files),
            "skipped_sensitive_paths": skipped_sensitive,
            "skipped_links_or_reparse_points": skipped_links,
            "errors": len(errors),
        },
        "files": files,
        "errors": errors,
    }


def write_inventory(inventory: dict[str, Any], output_path: str | os.PathLike[str]) -> Path:
    output_input = Path(output_path).absolute()
    output = output_input.parent.resolve() / output_input.name
    root = Path(inventory["source_root"]).resolve(strict=True)
    try:
        common = os.path.commonpath((os.path.normcase(str(root)), os.path.normcase(str(output))))
    except ValueError:
        common = ""
    if common == os.path.normcase(str(root)):
        raise ValueError("output_path must be outside source_root")

    output.parent.mkdir(parents=True, exist_ok=True)
    lock_path = output.with_name(output.name + ".lock")
    lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    temporary_path: str | None = None
    try:
        lock_payload = f"pid={os.getpid()} created={dt.datetime.now(dt.timezone.utc).isoformat()}\n".encode("utf-8")
        os.write(lock_fd, lock_payload)
        os.fsync(lock_fd)
        file_fd, temporary_path = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=str(output.parent))
        with os.fdopen(file_fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(inventory, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, output)
        temporary_path = None
    finally:
        os.close(lock_fd)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
    return output


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", help="authorized, read-only copy of the retired-office profile")
    parser.add_argument("output_json", help="manifest path outside source_root")
    args = parser.parse_args(argv)
    inventory = build_inventory(args.source_root)
    output = write_inventory(inventory, args.output_json)
    print(json.dumps({"output": str(output), **inventory["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
