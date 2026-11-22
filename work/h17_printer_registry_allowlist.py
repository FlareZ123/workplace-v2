#!/usr/bin/env python3
"""Read-only allowlisted parser for an authenticated Windows .reg text export.

This tool is intentionally NOT a parser for NTUSER.DAT or arbitrary registry
hives. It accepts only a textual .reg export and emits values from these HKCU
locations:
  * ...\Devices (all values)
  * ...\PrinterPorts (all values)
  * ...\Windows (the value named Device only)
  * HKCU\\Printers\\Connections (values and descendant key names)

No other registry path or value is returned. Input is never modified. Output
is JSON on stdout; no output file is created.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

BASE = r"HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion"
DEVICES = BASE + r"\Devices"
PORTS = BASE + r"\PrinterPorts"
WINDOWS = BASE + r"\Windows"
CONNECTIONS = r"HKEY_CURRENT_USER\Printers\Connections"
DEFAULT_MAX_BYTES = 16 * 1024 * 1024

SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
VALUE_RE = re.compile(r'^\s*(?P<name>"(?:\\.|[^"\\])*"|@|[^=]+?)\s*=\s*(?P<data>.*)$')


def _decode_text(data: bytes) -> str:
    if data.startswith(b"\xff\xfe"):
        return data.decode("utf-16")
    if data.startswith(b"\xfe\xff"):
        return data.decode("utf-16")
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig")
    for encoding in ("utf-8", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise ValueError("input is not a supported textual .reg encoding")


def _unquote_reg(value: str) -> str:
    value = value.strip()
    if not (len(value) >= 2 and value[0] == '"' and value[-1] == '"'):
        return value
    out: list[str] = []
    i = 1
    end = len(value) - 1
    while i < end:
        ch = value[i]
        if ch == "\\" and i + 1 < end:
            nxt = value[i + 1]
            if nxt in ("\\", '"'):
                out.append(nxt)
                i += 2
                continue
            out.extend((ch, nxt))
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _norm_key(key: str) -> str:
    return key.replace("/", "\\").rstrip("\\").casefold()


def _allowed_key(key: str) -> tuple[bool, str | None]:
    n = _norm_key(key)
    if n == _norm_key(DEVICES):
        return True, "Devices"
    if n == _norm_key(PORTS):
        return True, "PrinterPorts"
    if n == _norm_key(WINDOWS):
        return True, "Windows.Device"
    root = _norm_key(CONNECTIONS)
    if n == root or n.startswith(root + "\\"):
        return True, "Printers\\Connections"
    return False, None


def _parse_value_name(name: str) -> str:
    name = name.strip()
    if name == "@":
        return "(Default)"
    return _unquote_reg(name)


def _value_type(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith('"'):
        return "REG_SZ"
    if raw.lower().startswith("dword:"):
        return "REG_DWORD"
    if raw.lower().startswith("qword:"):
        return "REG_QWORD"
    if raw.lower().startswith("hex(2):"):
        return "REG_EXPAND_SZ"
    if raw.lower().startswith("hex(7):"):
        return "REG_MULTI_SZ"
    if raw.lower().startswith("hex(1):"):
        return "REG_SZ_HEX"
    if raw.lower().startswith("hex("):
        return "REG_TYPED_HEX"
    if raw.lower().startswith("hex:"):
        return "REG_BINARY"
    return "UNKNOWN"


def parse_reg_text(text: str, source_name: str = "<memory>") -> dict[str, Any]:
    """Parse only allowlisted HKCU printer values from Registry Editor text."""
    entries: list[dict[str, Any]] = []
    allowed_sections: list[dict[str, Any]] = []
    current_key: str | None = None
    current_kind: str | None = None
    pending: str | None = None
    pending_line: int | None = None

    def commit_value() -> None:
        nonlocal pending, pending_line
        if pending is None or current_key is None or current_kind is None:
            pending = None
            pending_line = None
            return
        match = VALUE_RE.match(pending)
        if not match:
            pending = None
            pending_line = None
            return
        value_name = _parse_value_name(match.group("name"))
        raw_data = match.group("data").strip()
        if current_kind == "Windows.Device" and value_name.casefold() != "device":
            pending = None
            pending_line = None
            return
        entries.append({
            "registry_key": current_key,
            "allowlist_group": current_kind,
            "value_name": value_name,
            "value_type": _value_type(raw_data),
            "raw_data": raw_data,
            "decoded_string": _unquote_reg(raw_data) if raw_data.startswith('"') else None,
            "source_line": pending_line,
        })
        pending = None
        pending_line = None

    lines = text.splitlines()
    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(";") or stripped.startswith("//"):
            continue
        section = SECTION_RE.match(line)
        if section:
            commit_value()
            raw_key = section.group(1)
            if raw_key.startswith("-"):
                current_key = None
                current_kind = None
                continue
            ok, kind = _allowed_key(raw_key)
            current_key = raw_key if ok else None
            current_kind = kind if ok else None
            if ok:
                allowed_sections.append({"registry_key": raw_key, "allowlist_group": kind})
            continue
        if current_key is None:
            continue
        if pending is not None:
            pending += stripped
            if pending.rstrip().endswith("\\"):
                pending = pending.rstrip()[:-1]
                continue
            commit_value()
            continue
        if "=" not in line:
            continue
        pending = line.rstrip()
        pending_line = line_no
        if pending.rstrip().endswith("\\"):
            pending = pending.rstrip()[:-1]
            continue
        commit_value()

    commit_value()
    return {
        "source_name": source_name,
        "parser": "h17_printer_registry_allowlist_v1",
        "scope": "HKCU printer settings only; no binary hive parsing",
        "allowlisted_groups": ["Devices", "PrinterPorts", "Windows.Device", "Printers\\Connections"],
        "allowed_sections_seen": allowed_sections,
        "values": entries,
        "value_count": len(entries),
    }


def parse_reg_file(path: Path, max_bytes: int = DEFAULT_MAX_BYTES) -> dict[str, Any]:
    if path.suffix.casefold() != ".reg":
        raise ValueError("refusing non-.reg input; this tool does not parse NTUSER.DAT or binary hives")
    if path.is_symlink():
        raise ValueError("refusing symlink input; supply a preserved regular-file copy")
    if not path.is_file():
        raise ValueError("input must be a regular file")
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"input exceeds {max_bytes} byte safety limit")
    raw = path.read_bytes()
    if raw.startswith(b"regf"):
        raise ValueError("binary registry hive detected; refusing to parse")
    text = _decode_text(raw)
    if "Windows Registry Editor Version" not in text[:256] and "REGEDIT4" not in text[:256]:
        raise ValueError("missing Registry Editor header; refusing unverified text input")
    result = parse_reg_text(text, source_name=path.name)
    result["source_size_bytes"] = size
    result["source_sha256"] = hashlib.sha256(raw).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="authenticated textual .reg export")
    ap.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = ap.parse_args(argv)
    try:
        result = parse_reg_file(args.input, args.max_bytes)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
