#!/usr/bin/env python3
"""Read-only extraction of an authorized Windows Sticky Notes plum.sqlite.

The source database and its optional -wal/-shm sidecars are copied byte-for-byte
into a temporary directory before SQLite opens them. SQLite therefore may
rebuild a shared-memory index only in the temporary copy, never beside the
source. This helper deliberately accepts only a file named plum.sqlite;
it does not inspect browser history, credentials, cookies, or arbitrary DBs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import tempfile
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

MAX_DB_BYTES = 64 * 1024 * 1024
MAX_ROWS = 100_000
MAX_CELL_BYTES = 4 * 1024 * 1024
MAX_TOTAL_TEXT = 64 * 1024 * 1024
MAX_RAW_SPANS = 100_000
MIN_RAW_RUN = 8
PRINTABLE = re.compile(rb"[\x20-\x7e]{" + str(MIN_RAW_RUN).encode() + rb",}")
UTF16LE_RUN = re.compile(rb"(?:[\x09\x0a\x0d\x20-\x7e]\x00){" + str(MIN_RAW_RUN).encode() + rb",}")
UTF16BE_RUN = re.compile(rb"(?:\x00[\x09\x0a\x0d\x20-\x7e]){" + str(MIN_RAW_RUN).encode() + rb",}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_regular_file(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ValueError(f"source must be a regular non-symlink file: {path}")
    if info.st_size > MAX_DB_BYTES:
        raise ValueError(f"source exceeds {MAX_DB_BYTES} byte limit: {path}")
    return info


def _copy_snapshot(
    source: Path,
    target_dir: Path,
    expected_root: dict[str, tuple[int, int, str] | None],
) -> dict[str, Any]:
    """Copy one coherent DB/WAL/SHM/rollback-journal set and verify every byte."""
    files: list[dict[str, Any]] = []
    for suffix in ("", "-wal", "-shm", "-journal"):
        path = source if not suffix else Path(str(source) + suffix)
        expected = expected_root.get(str(path))
        exists = path.exists()
        if expected is None:
            if exists:
                raise RuntimeError(f"source sidecar appeared during snapshot: {path}")
            if suffix:
                files.append({"path": str(path), "present": False})
                continue
            raise RuntimeError(f"source database disappeared during snapshot: {path}")
        if not exists:
            raise RuntimeError(f"source file disappeared during snapshot: {path}")

        info = _safe_regular_file(path)
        expected_size, expected_mtime_ns, expected_digest = expected
        if info.st_size != expected_size or info.st_mtime_ns != expected_mtime_ns:
            raise RuntimeError(f"source changed before snapshot copy: {path}")
        digest = sha256_file(path)
        if digest != expected_digest:
            raise RuntimeError(f"source hash changed before snapshot copy: {path}")

        target = target_dir / (source.name + suffix)
        shutil.copyfile(path, target)
        copied_size = target.stat().st_size
        copied_digest = sha256_file(target)
        if copied_size != info.st_size or copied_digest != digest:
            raise RuntimeError(f"snapshot copy mismatch; refusing mixed SQLite sidecar set: {path}")
        files.append({
            "path": str(path), "present": True, "size": info.st_size,
            "sha256": digest, "copied_sha256": copied_digest,
            "snapshot_copy_verified": True,
            "copied_to_temporary_snapshot": True,
        })
    return {"files": files}


def _carve_raw_text(path: Path, original_path: str) -> dict[str, Any]:
    data = path.read_bytes()
    spans: list[dict[str, Any]] = []
    seen: set[tuple[int, str, str]] = set()
    patterns = ((PRINTABLE, "ascii"), (UTF16LE_RUN, "utf-16le"), (UTF16BE_RUN, "utf-16be"))
    for pattern, encoding in patterns:
        for match in pattern.finditer(data):
            try:
                text = match.group().decode(encoding, "strict")
            except UnicodeDecodeError:
                continue
            text = text.strip("\x00")
            key = (match.start(), encoding, text)
            if not text or key in seen:
                continue
            seen.add(key)
            spans.append({"offset": match.start(), "encoding": encoding, "text": text})
            if len(spans) >= MAX_RAW_SPANS:
                break
        if len(spans) >= MAX_RAW_SPANS:
            break
    return {
        "source_file": original_path,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "minimum_run_characters": MIN_RAW_RUN,
        "span_limit": MAX_RAW_SPANS,
        "spans": spans,
        "truncated": len(spans) >= MAX_RAW_SPANS,
    }


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _blob_text(value: bytes) -> dict[str, Any]:
    if len(value) > MAX_CELL_BYTES:
        return {"type": "blob", "size": len(value), "sha256": hashlib.sha256(value).hexdigest(), "text_extraction": "cell_too_large"}
    candidates: list[dict[str, str]] = []
    for encoding in ("utf-8", "utf-16le", "utf-16be"):
        try:
            decoded = value.decode(encoding)
        except UnicodeDecodeError:
            continue
        if decoded and sum(ch.isprintable() or ch in "\r\n\t" for ch in decoded) / len(decoded) >= 0.85:
            candidates.append({"encoding": encoding, "text": decoded})
    if not candidates:
        spans = [m.group().decode("ascii", "replace") for m in PRINTABLE.finditer(value)]
        return {
            "type": "blob", "size": len(value),
            "sha256": hashlib.sha256(value).hexdigest(),
            "printable_ascii_spans": spans,
        }
    return {
        "type": "blob", "size": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "decoded_text_candidates": candidates,
    }


def _json_value(value: Any, total_text: list[int]) -> Any:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        encoded = value.encode("utf-8", "replace")
        if len(encoded) > MAX_CELL_BYTES:
            return {"type": "text", "size": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest(), "text_extraction": "cell_too_large"}
        if total_text[0] + len(encoded) > MAX_TOTAL_TEXT:
            return {"type": "text", "size": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest(), "text_extraction": "total_text_limit"}
        total_text[0] += len(encoded)
        return value
    if isinstance(value, (bytes, bytearray, memoryview)):
        return _blob_text(bytes(value))
    return str(value)


def extract_plum_database(database_path: str | os.PathLike[str]) -> dict[str, Any]:
    source = Path(database_path).absolute()
    if source.name.casefold() != "plum.sqlite":
        raise ValueError("only an authorized file named plum.sqlite is accepted")
    _safe_regular_file(source)

    before_root: dict[str, tuple[int, int, str] | None] = {}
    for suffix in ("", "-wal", "-shm", "-journal"):
        path = source if not suffix else Path(str(source) + suffix)
        if path.exists():
            info = _safe_regular_file(path)
            before_root[str(path)] = (info.st_size, info.st_mtime_ns, sha256_file(path))
        else:
            before_root[str(path)] = None

    with tempfile.TemporaryDirectory(prefix="h17-plum-snapshot-") as temp_name:
        temp_dir = Path(temp_name)
        sidecar_info = _copy_snapshot(source, temp_dir, before_root)
        raw_carving = []
        for item in sidecar_info["files"]:
            if not item.get("present"):
                continue
            original_path = item["path"]
            suffix = "" if original_path == str(source) else original_path[len(str(source)):]
            copied_path = temp_dir / (source.name + suffix)
            raw_carving.append(_carve_raw_text(copied_path, original_path))
        temp_db = temp_dir / "plum.sqlite"
        uri = "file:" + quote(str(temp_db), safe="/:") + "?mode=ro"
        connection: sqlite3.Connection | None = None
        sqlite_error: str | None = None
        output_tables: list[dict[str, Any]] = []
        total_text = [0]
        total_rows = 0
        sqlite_opened = False
        try:
            connection = sqlite3.connect(uri, uri=True, timeout=2.0)
            sqlite_opened = True
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA query_only=ON")
            connection.execute("PRAGMA busy_timeout=2000")
            tables = connection.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
            for table_row in tables:
                table_name = table_row["name"]
                quoted = _quote_identifier(table_name)
                columns = [row["name"] for row in connection.execute(f"PRAGMA table_info({quoted})").fetchall()]
                try:
                    cursor = connection.execute(f"SELECT rowid AS __h17_rowid__, * FROM {quoted}")
                    has_rowid = True
                except sqlite3.OperationalError:
                    cursor = connection.execute(f"SELECT * FROM {quoted}")
                    has_rowid = False
                rows: list[dict[str, Any]] = []
                for row_index, row in enumerate(cursor):
                    if total_rows >= MAX_ROWS:
                        break
                    total_rows += 1
                    row_data = dict(row)
                    rowid = row_data.pop("__h17_rowid__", None) if has_rowid else None
                    values = {column: _json_value(row_data.get(column), total_text) for column in columns}
                    rows.append({"row_index": row_index, "rowid": rowid, "values": values})
                output_tables.append({"name": table_name, "schema": table_row["sql"], "columns": columns, "rows": rows})
                if total_rows >= MAX_ROWS:
                    break
        except sqlite3.Error as exc:
            sqlite_error = f"{type(exc).__name__}: {exc}"
        finally:
            if connection is not None:
                connection.close()

        after_root: dict[str, tuple[int, int, str] | None] = {}
        for path_text in before_root:
            path = Path(path_text)
            if path.exists():
                info = _safe_regular_file(path)
                after_root[path_text] = (info.st_size, info.st_mtime_ns, sha256_file(path))
            else:
                after_root[path_text] = None
        unchanged = before_root == after_root
        return {
            "schema": "h17-sticky-notes-intake/v1",
            "created_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "source_database": str(source),
            "source_files": sidecar_info["files"],
            "raw_text_carving": raw_carving,
            "source_unchanged": unchanged,
            "source_hashes_before_after_match": unchanged,
            "sqlite_error": sqlite_error,
            "safety": {
                "source_files_modified": False,
                "source_opened_directly_by_sqlite": False,
                "sqlite_open_attempted_temporary_byte_copy_read_only": True,
                "sqlite_opened_temporary_byte_copy_read_only": sqlite_opened,
                "wal_shm_copied_when_present": True,
                "rollback_journal_copied_when_present": True,
                "only_plum_sqlite_accepted": True,
                "browser_history_or_credentials_opened": False,
                "network_access": False,
            },
            "limits": {
                "max_database_or_sidecar_bytes": MAX_DB_BYTES,
                "max_rows": MAX_ROWS,
                "max_cell_bytes": MAX_CELL_BYTES,
                "max_total_text_bytes": MAX_TOTAL_TEXT,
            },
            "summary": {
                "tables": len(output_tables), "rows": total_rows,
                "text_bytes_emitted": total_text[0],
                "wal_present": any(item.get("path", "").endswith("-wal") and item.get("present") for item in sidecar_info["files"]),
                "shm_present": any(item.get("path", "").endswith("-shm") and item.get("present") for item in sidecar_info["files"]),
                "journal_present": any(item.get("path", "").endswith("-journal") and item.get("present") for item in sidecar_info["files"]),
            },
            "tables": output_tables,
        }


def write_json(result: dict[str, Any], output_path: str | os.PathLike[str]) -> Path:
    output = Path(output_path).absolute()
    source = Path(result["source_database"]).resolve(strict=True)
    if os.path.commonpath((str(source.parent), str(output))) == str(source.parent):
        raise ValueError("output must be outside the source database directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", help="authorized Sticky Notes database named plum.sqlite")
    parser.add_argument("--json-out", help="write extracted records to a JSON file outside the source directory")
    args = parser.parse_args(argv)
    result = extract_plum_database(args.database)
    if args.json_out:
        output = write_json(result, args.json_out)
        print(json.dumps({"output": str(output), **result["summary"], "source_unchanged": result["source_unchanged"]}, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["source_unchanged"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
