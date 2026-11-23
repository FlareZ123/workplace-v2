#!/usr/bin/env python3
"""Exact K08 phrase scanner for an authorized, read-only H-17 profile inventory.

The profile inventory is produced by work/h17_profile_inventory.py. This
scanner consumes only hashed, K04/K08-relevant inventory entries, verifies
each file's SHA-256 before reading it, and searches decoded text, Office/PDF
content, JPEG/PNG/TIFF metadata and optional OCR, ZIP/TAR/GZIP members, and
SQLite text/BLOB columns (notably Sticky Notes' plum.sqlite). XPS/OXPS
Glyphs/Indices runs are decoded through embedded fonts when mapping is unambiguous.
Windows thumbnail-cache databases are carved in memory from hash-verified bytes;
teal-bit HMAC hits retain an explicit unresolved image-to-caption source link.
Pillow is used as a fallback for other supported image formats. It never writes to source files,
does not inspect credential stores, and does not guess PDF passwords.

By default it excludes Outlook PST/OST/NSF stores and all mail-category files.
Use --include-eml-msg only if the records custodian has separately authorized
those specific message files. This tool does not parse PST/OST stores.

Typical use:
  python work/h17_profile_inventory.py /mnt/read-only-profile /tmp/h17-profile.json
  python work/h17_profile_k08_phrase_scan.py --inventory /tmp/h17-profile.json \
      --resources /path/to/extracted-h17-resources --ocr --json-out /tmp/k08-scan.json
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sqlite3
import stat
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import h17_ax7782_k08_phrase_intake as phrase
import h17_k08_teal_bit_image_scan as teal_image
import h17_thumbcache_image_carve as thumbcache
import h17_onenote_intake as onenote
from h17_emf_text import extract_emf_text
from h17_xps_text import could_contain_xps, extract_xps_text
from h17_xps_glyph_indices import extract_xps_glyph_streams

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
SQLITE_MAGIC = b"SQLite format 3\x00"
REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
DEFAULT_MAX_FILE_BYTES = 256 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 512 * 1024 * 1024
DEFAULT_MAX_SQLITE_ROWS = 20000
DEFAULT_MAX_CELL_BYTES = 4 * 1024 * 1024

IMAGE_SUFFIXES = {
    ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".heif", ".webp",
    ".bmp", ".gif", ".psd", ".cr2", ".nef", ".arw", ".dng", ".orf",
    ".raf", ".rw2",
}


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
        if not include_eml_msg or suffix not in MESSAGE_SUFFIXES:
            return False
        return True

    if categories & DEFAULT_CATEGORIES:
        return True
    if "profile_metadata" in categories:
        return any(token in relative for token in PROFILE_METADATA_ALLOW)
    return False


def _sqlite_text_streams(
    path: Path,
    display_name: str,
    max_rows: int,
    max_cell_bytes: int,
    errors: list[dict[str, str]],
) -> Iterator[tuple[str, bytes]]:
    """Read SQLite text/BLOB columns through a query-only, read-only connection."""
    if path.stat().st_size < len(SQLITE_MAGIC):
        return
    try:
        with path.open("rb") as probe:
            if probe.read(len(SQLITE_MAGIC)) != SQLITE_MAGIC:
                return
    except OSError as exc:
        errors.append({"source": display_name, "error": f"sqlite-probe:{type(exc).__name__}:{exc}"})
        return

    connection = None
    try:
        uri = path.as_uri() + "?mode=ro"
        connection = sqlite3.connect(uri, uri=True, timeout=1.0)
        connection.execute("PRAGMA query_only=ON")
        try:
            connection.execute("PRAGMA trusted_schema=OFF")
        except sqlite3.DatabaseError:
            pass

        tables = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        for table_name, create_sql in tables:
            safe_table = '"' + str(table_name).replace('"', '""') + '"'
            if create_sql:
                yield f"{display_name}!/<schema:{table_name}>", str(create_sql).encode("utf-8", "replace")
            columns = connection.execute(f"PRAGMA table_info({safe_table})").fetchall()
            selected = []
            for column in columns:
                column_name = str(column[1])
                declared_type = str(column[2] or "").upper()
                if any(t in declared_type for t in ("TEXT", "CHAR", "CLOB", "BLOB")) or not declared_type:
                    selected.append(column_name)
            if not selected:
                continue
            select_columns = ", ".join('"' + name.replace('"', '""') + '"' for name in selected)
            query = f"SELECT {select_columns} FROM {safe_table} LIMIT ?"
            try:
                cursor = connection.execute(query, (max_rows,))
                row_index = 0
                for row in cursor:
                    for column_name, value in zip(selected, row):
                        source = f"{display_name}!/{table_name}/{column_name}[{row_index}]"
                        if isinstance(value, str):
                            encoded = value.encode("utf-8", "replace")
                            if encoded:
                                yield source, encoded
                        elif isinstance(value, bytes) and 0 < len(value) <= max_cell_bytes:
                            yield source, value
                    row_index += 1
            except sqlite3.DatabaseError as exc:
                errors.append({
                    "source": f"{display_name}!/{table_name}",
                    "error": f"sqlite-table-read:{type(exc).__name__}:{exc}",
                })
    except (sqlite3.DatabaseError, OSError, ValueError) as exc:
        errors.append({"source": display_name, "error": f"sqlite-open:{type(exc).__name__}:{exc}"})
    finally:
        if connection is not None:
            connection.close()


def _scan_stream(
    stream_name: str,
    data: bytes,
    nonce: bytes,
    target: bytes,
    max_phrase_words: int,
    hits: list[dict[str, Any]],
) -> int:
    tested = 0
    seen_normalized: set[str] = set()
    for label, text in phrase.decode_text_variants(data, stream_name):
        normalized = phrase.normalize(text)
        if not normalized or normalized in seen_normalized:
            continue
        seen_normalized.add(normalized)
        tested += phrase.scan_phrase_spans(
            text,
            nonce,
            target,
            f"{stream_name} [{label}]",
            max_phrase_words,
            hits,
        )
    return tested


def _image_fallback_streams(
    data: bytes,
    display_name: str,
    ocr: bool,
    errors: list[dict[str, str]],
) -> Iterator[tuple[str, bytes]]:
    """Extract metadata/OCR for image formats not handled by the shared parser."""
    try:
        from PIL import Image, ExifTags
        with Image.open(io.BytesIO(data)) as image:
            metadata = []
            try:
                for tag, value in image.getexif().items():
                    label = ExifTags.TAGS.get(tag, str(tag))
                    if isinstance(value, bytes):
                        value = value.decode("utf-8", "replace")
                    metadata.append(f"{label}: {value}")
            except Exception:
                pass
            for key, value in getattr(image, "info", {}).items():
                if isinstance(value, bytes):
                    value = value.decode("utf-8", "replace")
                metadata.append(f"{key}: {value}")
            if metadata:
                yield f"{display_name}!/<image-metadata-fallback>", "\n".join(metadata).encode("utf-8", "replace")
            if ocr:
                try:
                    import pytesseract
                    from PIL import ImageOps
                    frame_count = int(getattr(image, "n_frames", 1))
                    for frame_index in range(frame_count):
                        try:
                            image.seek(frame_index)
                            frame = ImageOps.exif_transpose(image.copy()).convert("RGB")
                            frame.thumbnail((3000, 3000))
                            text = pytesseract.image_to_string(frame)
                            if text.strip():
                                frame_suffix = f"#frame={frame_index}" if frame_count > 1 else ""
                                yield f"{display_name}!/<image-ocr-fallback>{frame_suffix}", text.encode("utf-8", "replace")
                        except Exception as frame_exc:
                            errors.append({
                                "source": f"{display_name}#frame={frame_index}",
                                "error": f"image-ocr-fallback:{type(frame_exc).__name__}:{frame_exc}",
                            })
                except Exception as exc:
                    errors.append({"source": display_name, "error": f"image-ocr-fallback:{type(exc).__name__}:{exc}"})
    except ImportError as exc:
        errors.append({"source": display_name, "error": f"image-fallback-unavailable:{exc}"})
    except Exception as exc:
        errors.append({"source": display_name, "error": f"image-fallback-unavailable:{type(exc).__name__}:{exc}"})


def scan_inventory(
    inventory_path: Path,
    nonce: bytes,
    target: bytes,
    max_phrase_words: int = 48,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_sqlite_rows: int = DEFAULT_MAX_SQLITE_ROWS,
    max_cell_bytes: int = DEFAULT_MAX_CELL_BYTES,
    ocr: bool = False,
    include_eml_msg: bool = False,
) -> dict[str, Any]:
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if inventory.get("schema") != "h17-profile-inventory/v1":
        raise ValueError("unsupported profile inventory schema")
    root = Path(inventory["source_root"]).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("inventory source_root is not a directory")

    hits: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    files_considered = files_scanned = sqlite_files = sqlite_tables = 0
    streams_scanned = spans_tested = bytes_scanned = 0
    thumbnail_cache_files_scanned = thumbnail_cache_images_found = 0
    thumbnail_cache_unique_images_scanned = thumbnail_cache_duplicate_images = 0
    thumbnail_cache_images_skipped_limit = thumbnail_cache_image_hmac_hits = 0
    onenote_files_scanned = onenote_pages_scanned = 0
    onenote_historical_revisions_scanned = onenote_streams_scanned = 0
    seen_thumbnail_images: dict[str, list[dict[str, Any]]] = {}
    global_budget = [0]
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
            if size > max_file_bytes:
                skipped.append({"path": relative, "reason": "file_size_limit"})
                continue
            if bytes_scanned + size > max_total_bytes:
                skipped.append({"path": relative, "reason": "total_size_limit"})
                continue
            actual_hash = _sha256_file(path)
            if actual_hash.casefold() != expected_hash.casefold():
                skipped.append({"path": relative, "reason": "sha256_changed_since_inventory"})
                continue
            data = path.read_bytes()
            bytes_scanned += size
        except (OSError, ValueError, TypeError) as exc:
            skipped.append({"path": relative, "reason": f"source_unavailable:{type(exc).__name__}:{exc}"})
            continue

        files_scanned += 1
        display_name = relative.replace("\\", "/")
        lower_name = display_name.casefold()

        try:
            structured_onenote = False
            if path.suffix.casefold() == ".one":
                try:
                    onenote_result = onenote.extract_onenote_document(path, display_name)
                except onenote.OneNoteDependencyUnavailable as exc:
                    errors.append({
                        "source": display_name,
                        "error": f"onenote-decoder-unavailable:{exc}",
                    })
                except Exception as exc:
                    errors.append({
                        "source": display_name,
                        "error": f"onenote-decoder:{type(exc).__name__}:{exc}",
                    })
                else:
                    onenote_files_scanned += 1
                    onenote_pages_scanned += int(onenote_result.get("pages", 0))
                    onenote_historical_revisions_scanned += int(
                        onenote_result.get("historical_revisions", 0)
                    )
                    for warning in onenote_result.get("warnings", []):
                        errors.append({
                            "source": display_name,
                            "error": f"onenote-history-warning:{warning}",
                        })
                    for stream in onenote_result.get("streams", []):
                        stream_text = str(stream.get("text", ""))
                        if not stream_text:
                            continue
                        stream_source = str(stream.get("source", display_name))
                        streams_scanned += 1
                        onenote_streams_scanned += 1
                        spans_tested += _scan_stream(
                            stream_source,
                            stream_text.encode("utf-8", "replace"),
                            nonce, target, max_phrase_words, hits,
                        )
                    structured_onenote = bool(onenote_result.get("streams"))

            if data.startswith(SQLITE_MAGIC):
                sqlite_files += 1
                for source, stream_data in _sqlite_text_streams(
                    path, display_name, max_sqlite_rows, max_cell_bytes, errors
                ):
                    for nested_source, nested_data in phrase.iter_text_streams(
                        source, stream_data, 1, global_budget, errors, ocr, None
                    ):
                        streams_scanned += 1
                        spans_tested += _scan_stream(
                            nested_source, nested_data, nonce, target, max_phrase_words, hits
                        )
                    if "<schema:" in source:
                        sqlite_tables += 1
                # Also scan raw SQLite pages for embedded printable/UTF-16 text.
                for source, stream_data in phrase.iter_text_streams(
                    display_name, data, 0, global_budget, errors, ocr, None
                ):
                    streams_scanned += 1
                    spans_tested += _scan_stream(
                        source, stream_data, nonce, target, max_phrase_words, hits
                    )
            else:
                if not structured_onenote:
                    for source, stream_data in phrase.iter_text_streams(
                        display_name, data, 0, global_budget, errors, ocr, None
                    ):
                        streams_scanned += 1
                        spans_tested += _scan_stream(
                            source, stream_data, nonce, target, max_phrase_words, hits
                        )
                if could_contain_xps(data):
                    for label, stream_data in extract_xps_text(data):
                        streams_scanned += 1
                        spans_tested += _scan_stream(
                            f"{display_name}!/{label}", stream_data, nonce, target, max_phrase_words, hits
                        )
                    # Glyphs/Indices pages require font mapping. The adapter
                    # fails closed on ambiguous or incomplete page coverage.
                    try:
                        glyph_streams = extract_xps_glyph_streams(data)
                    except Exception as exc:
                        errors.append({
                            "source": display_name,
                            "error": f"xps-glyph-indices:{type(exc).__name__}:{exc}",
                        })
                    else:
                        for label, stream_data in glyph_streams:
                            streams_scanned += 1
                            spans_tested += _scan_stream(
                                f"{display_name}!/{label}", stream_data,
                                nonce, target, max_phrase_words, hits
                            )
                if ("printer" in (record.get("categories") or []) or path.suffix.casefold() == ".emf") and b" EMF" in data:
                    for label, stream_data in extract_emf_text(data):
                        streams_scanned += 1
                        spans_tested += _scan_stream(
                            f"{display_name}!/{label}", stream_data, nonce, target, max_phrase_words, hits
                        )
                if path.suffix.casefold() in IMAGE_SUFFIXES and phrase.intake.magic(data) not in {"jpeg", "png", "tiff"}:
                    for source, stream_data in _image_fallback_streams(data, display_name, ocr, errors):
                        streams_scanned += 1
                        spans_tested += _scan_stream(
                            source, stream_data, nonce, target, max_phrase_words, hits
                        )
        except Exception as exc:
            errors.append({"source": display_name, "error": f"scan-error:{type(exc).__name__}:{exc}"})

        if "thumbcache" in lower_name or lower_name.endswith("thumbs.db"):
            thumbnail_cache_files_scanned += 1
            try:
                carved = thumbcache.carve_bytes(
                    data,
                    display_name,
                    max_image_bytes=32 * 1024 * 1024,
                    max_pixels=25_000_000,
                )
                thumbnail_cache_images_found += len(carved)
                for image in carved:
                    image_bytes = data[image.offset:image.offset + image.length]
                    image_sha256 = hashlib.sha256(image_bytes).hexdigest()
                    if len(image_bytes) != image.length or image_sha256 != image.sha256:
                        errors.append({
                            "source": display_name,
                            "error": f"thumbnail-cache-carved-image-integrity:{image.offset}",
                        })
                        continue

                    cached_matches = seen_thumbnail_images.get(image_sha256)
                    if cached_matches is None:
                        if thumbnail_cache_unique_images_scanned >= 4096:
                            thumbnail_cache_images_skipped_limit += 1
                            continue
                        cached_matches = teal_image.scan_image_bytes(
                            image_bytes,
                            f"{display_name}@0x{image.offset:x}",
                            nonce,
                            target.hex(),
                            max_words=min(max_phrase_words, 48),
                        )
                        seen_thumbnail_images[image_sha256] = cached_matches
                        thumbnail_cache_unique_images_scanned += 1
                    else:
                        thumbnail_cache_duplicate_images += 1

                    # A cache hit proves only that an exact committed phrase was
                    # encoded in these image bytes. The byte-carver does not
                    # recover the original image path, capture time, N14 link,
                    # or Emily authorship, so preserve that uncertainty.
                    for match in cached_matches:
                        hits.append({
                            "source": display_name,
                            "source_type": "thumbnail_cache_image_candidate",
                            "source_offset": image.offset,
                            "image_sha256": image_sha256,
                            "frame": match["frame"],
                            "layout": match["layout"],
                            "phrase": match["phrase"],
                            "source_link_status": (
                                "unresolved: thumbnail-cache carving does not recover "
                                "the original image path/time or N14-to-Emily caption link"
                            ),
                            "historical_authentication": "not established",
                        })
                        thumbnail_cache_image_hmac_hits += 1
            except Exception as exc:
                errors.append({
                    "source": display_name,
                    "error": f"thumbnail-cache-scan:{type(exc).__name__}:{exc}",
                })

    return {
        "schema": "h17-profile-k08-phrase-scan/v1",
        "inventory": str(inventory_path),
        "source_root": str(root),
        "source_writes_performed": False,
        "credential_stores_opened": False,
        "mail_stores_opened": False,
        "include_eml_msg": include_eml_msg,
        "ocr_enabled": ocr,
        "files_considered": files_considered,
        "files_scanned": files_scanned,
        "sqlite_files_scanned": sqlite_files,
        "sqlite_schema_streams": sqlite_tables,
        "onenote": {
            "files_scanned": onenote_files_scanned,
            "pages_scanned": onenote_pages_scanned,
            "historical_revisions_scanned": onenote_historical_revisions_scanned,
            "text_streams_scanned": onenote_streams_scanned,
            "version_selection": "not performed; current and historical pages are emitted separately",
            "dependency": "optional aspose-note package; see work/requirements-h17-onenote.txt",
        },
        "text_streams_scanned": streams_scanned,
        "normalized_contiguous_spans_tested": spans_tested,
        "thumbnail_cache": {
            "files_scanned": thumbnail_cache_files_scanned,
            "images_found": thumbnail_cache_images_found,
            "unique_images_scanned": thumbnail_cache_unique_images_scanned,
            "duplicate_images_reused": thumbnail_cache_duplicate_images,
            "images_skipped_limit": thumbnail_cache_images_skipped_limit,
            "image_hmac_hits": thumbnail_cache_image_hmac_hits,
            "max_unique_images": 4096,
            "max_image_pixels": 25_000_000,
        },
        "bytes_scanned": bytes_scanned,
        "max_phrase_words": max_phrase_words,
        "hits": hits,
        "skipped": skipped,
        "errors": errors,
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }


def self_test() -> dict[str, Any]:
    import tempfile

    test_nonce = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    planted = "the voices stayed around the table after the long watch"
    test_target = hashlib.sha256(
        phrase.k08_component(test_nonce, phrase.normalize(planted))
    ).digest()

    with tempfile.TemporaryDirectory(prefix="h17-profile-k08-test-") as temp:
        root = Path(temp) / "profile"
        (root / "notes").mkdir(parents=True)
        (root / "photos").mkdir(parents=True)
        text_path = root / "photos" / "caption.txt"
        text_path.write_text("A quiet caption. " + planted + ". End.", encoding="utf-8")
        db_path = root / "notes" / "plum.sqlite"
        connection = sqlite3.connect(db_path)
        connection.execute("CREATE TABLE Note (id INTEGER PRIMARY KEY, Text TEXT)")
        connection.execute("INSERT INTO Note(Text) VALUES (?)", (planted,))
        connection.commit()
        connection.close()

        files = []
        for path, categories in (
            (text_path, ["photo_caption"]),
            (db_path, ["notes"]),
        ):
            files.append({
                "path": path.relative_to(root).as_posix(),
                "size": path.stat().st_size,
                "sha256": _sha256_file(path),
                "categories": categories,
            })
        inventory_path = Path(temp) / "inventory.json"
        inventory_path.write_text(json.dumps({
            "schema": "h17-profile-inventory/v1",
            "source_root": str(root),
            "files": files,
        }), encoding="utf-8")

        before = {str(path): _sha256_file(path) for path in (text_path, db_path)}
        result = scan_inventory(
            inventory_path, test_nonce, test_target,
            max_phrase_words=16, max_file_bytes=1024 * 1024,
            max_total_bytes=4 * 1024 * 1024,
        )
        after = {str(path): _sha256_file(path) for path in (text_path, db_path)}
        if before != after:
            raise AssertionError("self-test detected source mutation")
        if len(result["hits"]) < 2:
            raise AssertionError(f"expected text-file and SQLite hits, got {result['hits']}")
        if not any("plum.sqlite!/Note/Text" in hit["source"] for hit in result["hits"]):
            raise AssertionError("SQLite Sticky Notes test did not produce a hit")
        return {
            "ok": True,
            "minimum_expected_hits": 2,
            "actual_hits": len(result["hits"]),
            "files_scanned": result["files_scanned"],
            "sqlite_files_scanned": result["sqlite_files_scanned"],
            "source_unchanged": before == after,
        }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, help="JSON output from h17_profile_inventory.py")
    parser.add_argument("--resources", type=Path, help="extracted H-17 resources root containing evidence/ and acceptance.json")
    parser.add_argument("--max-phrase-words", type=int, default=48)
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument("--max-sqlite-rows", type=int, default=DEFAULT_MAX_SQLITE_ROWS)
    parser.add_argument("--max-cell-bytes", type=int, default=DEFAULT_MAX_CELL_BYTES)
    parser.add_argument("--ocr", action="store_true", help="enable OCR for image/PDF pages when optional dependencies are installed")
    parser.add_argument("--include-eml-msg", action="store_true", help="include only .eml/.msg files after separate custodian authorization; PST/OST stores remain excluded")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.inventory is None or args.resources is None:
        parser.error("--inventory and --resources are required unless --self-test is used")
    if args.max_phrase_words < 1 or args.max_file_bytes < 1 or args.max_total_bytes < 1:
        parser.error("phrase/file/total limits must be positive")
    if args.max_sqlite_rows < 1 or args.max_cell_bytes < 1:
        parser.error("SQLite limits must be positive")
    resources = args.resources.resolve(strict=True)
    nonce, target = phrase.load_k08_rules(resources)
    result = scan_inventory(
        args.inventory.resolve(strict=True),
        nonce, target,
        max_phrase_words=args.max_phrase_words,
        max_file_bytes=args.max_file_bytes,
        max_total_bytes=args.max_total_bytes,
        max_sqlite_rows=args.max_sqlite_rows,
        max_cell_bytes=args.max_cell_bytes,
        ocr=args.ocr,
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
