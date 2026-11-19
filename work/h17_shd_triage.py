#!/usr/bin/env python3
"""Read-only string triage for recovered Windows print shadow (.SHD) files.

This is deliberately NOT a structural SHD parser. The internal SHD layout is
version-dependent and not fully specified here. It reports only bounded
printable ASCII and UTF-16LE ASCII-subset runs with byte offsets, encodings,
raw bytes and file hashes. A hit is a candidate string, not an authenticated
field mapping. The input file is never modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

DEFAULT_MAX_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_STRINGS = 10000
DEFAULT_MIN_CHARS = 4
DEFAULT_MAX_RUN_CHARS = 4096


def _ascii_runs(data: bytes, min_chars: int, max_run_chars: int):
    pattern = re.compile(rb"[\x20-\x7e]{%d,}" % min_chars)
    for match in pattern.finditer(data):
        raw = match.group(0)[:max_run_chars]
        yield {
            "offset": match.start(),
            "length_bytes": len(raw),
            "encoding": "ascii",
            "text": raw.decode("ascii"),
            "raw_hex": raw.hex().upper(),
        }


def _utf16le_ascii_runs(data: bytes, min_chars: int, max_run_chars: int):
    # SHD metadata commonly uses Windows wide strings. Keep this deliberately
    # conservative: only report UTF-16LE code units whose high byte is zero
    # and whose low byte is printable ASCII (or whitespace). This avoids
    # treating arbitrary binary words as printable CJK/Unicode text. Non-ASCII
    # UTF-16 strings are outside this triage tool's coverage.
    for alignment in (0, 1):
        i = alignment
        while i + 1 < len(data):
            start = i
            chars = []
            while i + 1 < len(data) and len(chars) < max_run_chars:
                low, high = data[i], data[i + 1]
                if high == 0 and (0x20 <= low <= 0x7e or low in (0x09, 0x0a, 0x0d)):
                    chars.append(chr(low))
                    i += 2
                else:
                    break
            if len(chars) >= min_chars:
                raw = data[start:i]
                yield {
                    "offset": start,
                    "length_bytes": len(raw),
                    "encoding": "utf-16le-ascii",
                    "alignment": alignment,
                    "text": "".join(chars),
                    "raw_hex": raw.hex().upper(),
                }
            i = max(i + 2, start + 2)


def extract_strings(data: bytes, min_chars: int = DEFAULT_MIN_CHARS,
                    max_strings: int = DEFAULT_MAX_STRINGS,
                    max_run_chars: int = DEFAULT_MAX_RUN_CHARS):
    if min_chars < 1 or max_strings < 1 or max_run_chars < min_chars:
        raise ValueError("invalid extraction limits")
    found = list(_ascii_runs(data, min_chars, max_run_chars))
    found.extend(_utf16le_ascii_runs(data, min_chars, max_run_chars))
    found.sort(key=lambda item: (item["offset"], item["encoding"], item["length_bytes"]))
    deduped = []
    seen = set()
    for item in found:
        key = (item["offset"], item["length_bytes"], item["encoding"], item["raw_hex"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= max_strings:
            break
    return deduped


def inspect(path: Path, min_chars: int, max_strings: int, max_bytes: int):
    if path.is_symlink() or not path.is_file():
        raise ValueError("input must be a regular non-symlink file")
    stat = path.stat()
    if stat.st_size > max_bytes:
        raise ValueError(f"file exceeds max-bytes ({stat.st_size} > {max_bytes})")
    data = path.read_bytes()
    header = data[:16]
    return {
        "path": str(path),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "header_hex": header.hex().upper(),
        "first_u16le": int.from_bytes(data[:2], "little") if len(data) >= 2 else None,
        "second_u16le": int.from_bytes(data[2:4], "little") if len(data) >= 4 else None,
        "strings": extract_strings(data, min_chars=min_chars, max_strings=max_strings),
        "interpretation_limit": "string triage only; offsets do not establish SHD field semantics",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--min-chars", type=int, default=DEFAULT_MIN_CHARS)
    parser.add_argument("--max-strings", type=int, default=DEFAULT_MAX_STRINGS)
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args(argv)
    if args.min_chars < 1 or args.max_strings < 1 or args.max_bytes < 1:
        parser.error("limits must be positive")
    results = []
    for path in args.paths:
        try:
            results.append(inspect(path, args.min_chars, args.max_strings, args.max_bytes))
        except Exception as exc:
            results.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})
    print(json.dumps({"files": results}, indent=2, ensure_ascii=False))
    return 0 if all("error" not in item for item in results) else 2


if __name__ == "__main__":
    sys.exit(main())
