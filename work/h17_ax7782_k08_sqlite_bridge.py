#!/usr/bin/env python3
"""Read-only SQLite/WAL extension for the authorized AX-7782 K08 intake.

The companion K08 scanner handles nested ZIP/TAR/GZIP, MIME, PDF, images,
metadata and exact normalized text spans, but intentionally does not decode
SQLite internals. This bridge finds only Windows Sticky Notes databases named
plum.sqlite and their adjacent -wal/-shm files, snapshots those members to a
temporary directory, uses the existing read-only Sticky Notes extractor, and
checks actual row text plus raw database/WAL text against the original K08
commitment. Raw binary-carved spans also receive a bounded character-offset
pass so printable SQLite page framing cannot fuse itself to the first word.
It does not guess wording, open other databases, or modify the source object.

Example:
    python work/h17_ax7782_k08_sqlite_bridge.py --object /path/to/AX-7782 \
        --resources resources --json-out /tmp/ax7782-k08-intake.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator

import h17_ax7782_k08_phrase_intake as phrase_intake
import h17_sticky_notes_intake as sticky_intake

MAX_RAW_STARTS = 100_000
MAX_RAW_SPAN_CHARS = 16_384


def _normalized_member_path(name: str) -> PurePosixPath:
    return PurePosixPath(name.replace("\\", "/"))


def _canonical_member_ref(name: str) -> str:
    """Remove iterator-only GZIP/attachment suffixes from a source reference."""
    if name.endswith("!/<gzip-payload>"):
        name = name.rsplit("!/", 1)[0]
    return re.sub(r"\[\d+\]$", "", name)


def _member_location(name: str) -> tuple[str, str, str]:
    """Return (container identity, parent path, basename) for a leaf ref."""
    if "!/" in name:
        container, member = name.rsplit("!/", 1)
    else:
        container, member = "<root>", name
    path = _normalized_member_path(member)
    basename = re.sub(r"\[\d+\]$", "", path.name)
    # The companion iterator labels a decoded GZIP payload generically. Recover
    # a Sticky Notes filename only when the enclosing member explicitly names it.
    if basename.casefold() == "<gzip-payload>":
        if "!/" in container:
            outer_container, gzip_member = container.rsplit("!/", 1)
        else:
            outer_container, gzip_member = "<root>", container
        gzip_path = _normalized_member_path(gzip_member)
        if gzip_path.name.casefold().endswith(".gz"):
            container = outer_container
            path = gzip_path
            basename = gzip_path.name[:-3]
    return container, str(path.parent), basename.casefold()


def _iter_strings(value: Any, label: str = "value") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        if value:
            yield label, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _iter_strings(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_strings(item, f"{label}[{index}]")


def scan_embedded_raw_span(text: str, nonce: bytes, target: bytes, source: str,
                           base_offset: int, byte_stride: int, max_words: int,
                           hits: list[dict[str, Any]],
                           start_budget: list[int]) -> tuple[int, int, bool]:
    """Scan every alphanumeric start offset in a binary-carved text run.

    SQLite page/WAL framing can be printable and directly abut the first
    character of a note, e.g. \`gn1the keeper ...\`. The ordinary text scanner
    correctly starts at word boundaries, but that loses the note's first word
    when the binary prefix is fused to it. This bounded raw-only pass tests
    exact contiguous spans from every character offset without changing K08
    normalization or editing any candidate wording.
    """
    normalized = phrase_intake.normalize(text)
    tokens = list(re.finditer(r"[a-z0-9]+", normalized))
    if not tokens:
        return 0, 0, False
    spans_tested = 0
    starts_tested = 0
    truncated = len(normalized) > MAX_RAW_SPAN_CHARS
    scan_text = normalized[:MAX_RAW_SPAN_CHARS]
    tokens = [match for match in tokens if match.start() < len(scan_text)]
    ends = [min(match.end(), len(scan_text)) for match in tokens]
    token_index = 0
    for char_start, char in enumerate(scan_text):
        if not ("a" <= char <= "z" or "0" <= char <= "9"):
            continue
        if start_budget[0] <= 0:
            truncated = True
            break
        start_budget[0] -= 1
        starts_tested += 1
        while token_index < len(tokens) and ends[token_index] <= char_start:
            token_index += 1
        if token_index >= len(tokens):
            break
        first = scan_text[char_start:ends[token_index]]
        if not first:
            continue
        phrase_words = [first]
        component = phrase_intake.k08_component(nonce, first)
        spans_tested += 1
        if hashlib.sha256(component).digest() == target:
            hits.append({"source": source, "char_start": char_start,
                         "byte_offset": base_offset + char_start if byte_stride == 1 else None,
                         "word_count": 1, "normalized_phrase": first,
                         "component_hex": component.hex().upper()})
        for next_index in range(token_index + 1, min(len(tokens), token_index + max_words)):
            phrase_words.append(tokens[next_index].group())
            candidate = " ".join(phrase_words)
            component = phrase_intake.k08_component(nonce, candidate)
            spans_tested += 1
            if hashlib.sha256(component).digest() == target:
                hits.append({"source": source, "char_start": char_start,
                             "byte_offset": base_offset + char_start if byte_stride == 1 else None,
                             "word_count": len(phrase_words),
                             "normalized_phrase": candidate,
                             "component_hex": component.hex().upper()})
    return spans_tested, starts_tested, truncated


def scan_sqlite_members(data: bytes, object_name: str, nonce: bytes,
                        target: bytes, max_words: int = 32,
                        pdf_password: str | None = None) -> dict[str, Any]:
    """Scan exact plum.sqlite members and adjacent WAL/SHM for K08 matches."""
    if not 1 <= max_words <= 256:
        raise ValueError("max_words must be between 1 and 256")
    errors: list[dict[str, str]] = []
    groups: dict[tuple[str, str], dict[str, list[tuple[str, bytes]]]] = defaultdict(
        lambda: {"db": [], "wal": [], "shm": []}
    )
    stream_count = 0
    for name, member in phrase_intake.iter_text_streams(
            object_name, data, 0, [0], errors, ocr=False, pdf_password=pdf_password):
        stream_count += 1
        container, parent, basename = _member_location(name)
        key = (container, parent)
        if basename == "plum.sqlite":
            groups[key]["db"].append((name, member))
        elif basename == "plum.sqlite-wal":
            groups[key]["wal"].append((name, member))
        elif basename == "plum.sqlite-shm":
            groups[key]["shm"].append((name, member))

    database_summaries: list[dict[str, Any]] = []
    hits: list[dict[str, Any]] = []
    spans_tested = 0
    text_inputs = 0
    raw_start_budget = [MAX_RAW_STARTS]
    raw_starts_tested = 0
    raw_scan_truncated = False
    for (container, parent), members in sorted(groups.items()):
        if len(members["db"]) != 1:
            errors.append({"source": f"{container}!/{parent}",
                           "error": "expected exactly one plum.sqlite in this directory"})
            continue
        if len(members["wal"]) > 1 or len(members["shm"]) > 1:
            errors.append({"source": f"{container}!/{parent}",
                           "error": "duplicate plum.sqlite-wal or plum.sqlite-shm sidecar; skipped"})
            continue

        db_stream_name, db_bytes = members["db"][0]
        db_name = _canonical_member_ref(db_stream_name)
        if not db_bytes.startswith(b"SQLite format 3\x00"):
            errors.append({"source": db_name, "error": "plum.sqlite member lacks SQLite format 3 header"})
            continue
        wal_stream = members["wal"][0] if members["wal"] else None
        shm_stream = members["shm"][0] if members["shm"] else None
        wal_item = (_canonical_member_ref(wal_stream[0]), wal_stream[1]) if wal_stream else None
        shm_item = (_canonical_member_ref(shm_stream[0]), shm_stream[1]) if shm_stream else None
        if len(db_bytes) > sticky_intake.MAX_DB_BYTES:
            errors.append({"source": db_name, "error": "plum.sqlite exceeds Sticky Notes extractor size cap"})
            continue
        if wal_item and len(wal_item[1]) > sticky_intake.MAX_DB_BYTES:
            errors.append({"source": wal_item[0], "error": "WAL exceeds Sticky Notes extractor size cap"})
            continue
        if shm_item and len(shm_item[1]) > sticky_intake.MAX_DB_BYTES:
            errors.append({"source": shm_item[0], "error": "SHM exceeds Sticky Notes extractor size cap"})
            continue

        with tempfile.TemporaryDirectory(prefix="h17-ax7782-plum-") as temp_name:
            temp_dir = Path(temp_name)
            db_path = temp_dir / "plum.sqlite"
            db_path.write_bytes(db_bytes)
            if wal_item:
                Path(str(db_path) + "-wal").write_bytes(wal_item[1])
            if shm_item:
                Path(str(db_path) + "-shm").write_bytes(shm_item[1])
            try:
                extracted = sticky_intake.extract_plum_database(db_path)
            except Exception as exc:
                errors.append({"source": db_name, "error": f"Sticky Notes extraction failed: {exc}"})
                continue

        source_map = {"plum.sqlite": db_name}
        if wal_item:
            source_map["plum.sqlite-wal"] = wal_item[0]
        if shm_item:
            source_map["plum.sqlite-shm"] = shm_item[0]
        database_summary = {
            "source_member": db_name,
            "database_sha256": hashlib.sha256(db_bytes).hexdigest(),
            "database_size": len(db_bytes),
            "wal_member": wal_item[0] if wal_item else None,
            "wal_sha256": hashlib.sha256(wal_item[1]).hexdigest() if wal_item else None,
            "shm_member": shm_item[0] if shm_item else None,
            "shm_sha256": hashlib.sha256(shm_item[1]).hexdigest() if shm_item else None,
            "wal_present": bool(wal_item),
            "shm_present": bool(shm_item),
            "table_names": [table["name"] for table in extracted["tables"]],
            "table_count": extracted["summary"]["tables"],
            "logical_row_count": extracted["summary"]["rows"],
            "raw_text_span_count": sum(len(item["spans"]) for item in extracted["raw_text_carving"]),
            "snapshot_source_unchanged": extracted["source_unchanged"],
            "candidate_text_inputs": 0,
            "candidate_spans_tested": 0,
        }

        for table in extracted["tables"]:
            for row in table["rows"]:
                row_id = row["rowid"] if row["rowid"] is not None else row["row_index"]
                for column, value in row["values"].items():
                    for value_label, text in _iter_strings(value, f"{table['name']}[{row_id}].{column}"):
                        text_inputs += 1
                        database_summary["candidate_text_inputs"] += 1
                        tested = phrase_intake.scan_phrase_spans(
                            text, nonce, target,
                            f"{db_name}::{value_label}", max_words, hits
                        )
                        spans_tested += tested
                        database_summary["candidate_spans_tested"] += tested

        for carving in extracted["raw_text_carving"]:
            for span in carving["spans"]:
                text_inputs += 1
                database_summary["candidate_text_inputs"] += 1
                carved_basename = Path(carving["source_file"]).name.casefold()
                source_member = source_map.get(carved_basename, db_name)
                source = f"{source_member}@{span['offset']}:{span['encoding']}"
                encoding = span["encoding"]
                byte_stride = 2 if encoding in {"utf-16le", "utf-16be"} else 1
                embedded_tested, starts_tested, truncated = scan_embedded_raw_span(
                    span["text"], nonce, target, source, span["offset"], byte_stride,
                    max_words, hits, raw_start_budget
                )
                spans_tested += embedded_tested
                raw_starts_tested += starts_tested
                raw_scan_truncated = raw_scan_truncated or truncated
                database_summary["candidate_spans_tested"] += embedded_tested

        database_summaries.append(database_summary)

    # Deduplicate exact same source/phrase matches without erasing distinct carriers.
    unique_hits: list[dict[str, Any]] = []
    seen_hits: set[tuple[str, str, str]] = set()
    for hit in hits:
        key = (hit["source"], hit["normalized_phrase"], hit["component_hex"])
        if key not in seen_hits:
            seen_hits.add(key)
            unique_hits.append(hit)

    return {
        "text_streams_seen": stream_count,
        "plum_databases_found": len(database_summaries),
        "databases": database_summaries,
        "text_inputs_scanned": text_inputs,
        "normalized_contiguous_spans_tested": spans_tested,
        "raw_character_starts_tested": raw_starts_tested,
        "raw_scan_truncated": raw_scan_truncated,
        "raw_character_start_budget": MAX_RAW_STARTS,
        "raw_span_character_cap": MAX_RAW_SPAN_CHARS,
        "max_phrase_words": max_words,
        "original_k08_commitment_hits": unique_hits,
        "errors": errors,
    }


def inspect_object(path: Path, resources: Path, transfer_id: str = "AX-7782",
                   ocr: bool = False, max_phrase_words: int = 32,
                   pdf_password: str | None = None) -> dict[str, Any]:
    """Run the existing K08 object scanner plus the SQLite/WAL extension."""
    if not path.is_file() or path.is_symlink():
        raise ValueError("object must be a regular, non-symlink file")
    before_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    base = phrase_intake.inspect_object(path, resources, transfer_id, ocr,
                                        max_phrase_words, pdf_password)
    nonce, target = phrase_intake.load_k08_rules(resources)
    data = path.read_bytes()
    sqlite_result = scan_sqlite_members(data, path.name, nonce, target,
                                        max_phrase_words, pdf_password)
    after_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if before_hash != after_hash or base.get("object", {}).get("sha256") != before_hash:
        raise RuntimeError("source object changed during read-only K08 intake")
    sqlite_result["source_object_sha256"] = before_hash
    sqlite_result["source_object_unchanged"] = True
    base_hits = list(base["K08_search"]["original_commitment_hits"])
    base_hits.extend(sqlite_result["original_k08_commitment_hits"])
    unique_hits: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for hit in base_hits:
        key = (hit["source"], hit["normalized_phrase"], hit["component_hex"])
        if key not in seen:
            seen.add(key)
            unique_hits.append(hit)
    base["K08_search"]["original_commitment_hits"] = unique_hits
    base["K08_search"]["normalized_contiguous_spans_tested"] += sqlite_result["normalized_contiguous_spans_tested"]
    base["K08_search"]["sqlite_text_inputs_scanned"] = sqlite_result["text_inputs_scanned"]
    base["sqlite_intake"] = sqlite_result
    return base


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", required=True, type=Path, help="authorized local AX-7782 8 MiB object")
    parser.add_argument("--resources", type=Path, default=Path("resources"))
    parser.add_argument("--transfer", default="AX-7782")
    parser.add_argument("--ocr", action="store_true")
    parser.add_argument("--pdf-password", help="only a separately authorized password; never guessed")
    parser.add_argument("--max-phrase-words", type=int, default=32)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)
    if not 1 <= args.max_phrase_words <= 256:
        parser.error("--max-phrase-words must be between 1 and 256")
    if not args.object.is_file() or args.object.is_symlink():
        parser.error("--object must be a regular, non-symlink file")
    if args.json_out:
        output_path = args.json_out.resolve()
        resources_path = args.resources.resolve()
        if args.json_out.is_symlink():
            parser.error("--json-out must not be a symlink")
        if output_path == args.object.resolve() or output_path == resources_path or resources_path in output_path.parents:
            parser.error("--json-out must be outside the source object and resources tree")
    try:
        result = inspect_object(args.object, args.resources, args.transfer,
                                args.ocr, args.max_phrase_words, args.pdf_password)
    except Exception as exc:
        parser.error(str(exc))
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
