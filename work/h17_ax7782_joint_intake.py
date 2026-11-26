#!/usr/bin/env python3
"""Run the AX-7782, K04-window and K08-text/SQLite intakes together.

This is an orchestration wrapper, not a new scanner. It runs the repository's
three read-only tools against one authorized local object, stores intermediate
JSON only in a short-lived temporary directory, and emits one combined report.
The K08 SQLite bridge wraps the exact phrase scanner and additionally recovers
only named Windows Sticky Notes plum.sqlite databases with adjacent WAL/SHM.
It never edits the source object, candidate, acceptance or verifier. Any PDF
password must be supplied explicitly; none is guessed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from h17_redaction import redact_sensitive
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _tail(value: Any) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    return str(value or "")[-4000:]


def run_tool(name: str, command: list[str], output: Path, timeout: int) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, check=False,
            cwd=ROOT, stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "tool": name,
            "status": "timeout",
            "timeout_seconds": timeout,
        }
    if not output.is_file():
        return {
            "tool": name,
            "status": "error",
            "returncode": proc.returncode,
        }
    try:
        result = json.loads(output.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "tool": name,
            "status": "invalid-json",
            "returncode": proc.returncode,
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {
        "tool": name,
        "status": "ok" if proc.returncode == 0 else "nonzero",
        "returncode": proc.returncode,
        "result": result,
    }


def inspect_joint(
    source: Path,
    resources: Path,
    transfer: str = "AX-7782",
    ocr: bool = False,
    pdf_password: str | None = None,
    max_phrase_words: int = 48,
    stride: int = 1,
    timeout: int = 300,
    allow_pdf_source: bool = False,
) -> dict[str, Any]:
    source = source.expanduser().absolute()
    resources = resources.expanduser().absolute()
    if source.is_symlink() or not source.is_file():
        raise ValueError("--object must be a regular, non-symlink file")
    if not resources.is_dir():
        raise ValueError("--resources must be an existing directory")
    if not 1 <= max_phrase_words <= 256 or stride < 1 or timeout < 1:
        raise ValueError("max-phrase-words, stride and timeout must be positive and in range")

    source_size = source.stat().st_size
    source_hash_before = sha256_file(source)
    python = sys.executable

    with tempfile.TemporaryDirectory(prefix="h17-joint-intake-") as tmp_name:
        tmp = Path(tmp_name)
        transfer_out = tmp / "transfer.json"
        k04_out = tmp / "k04.json"
        k08_out = tmp / "k08.json"

        transfer_cmd = [
            python, str(WORK / "h17_ax7782_object_intake.py"),
            "--object", str(source), "--resources", str(resources),
            "--transfer", transfer, "--json-out", str(transfer_out),
        ]
        if ocr:
            transfer_cmd.append("--ocr")
        transfer_result = run_tool("transfer-validation", transfer_cmd, transfer_out, timeout)

        k04_cmd = [
            python, str(WORK / "h17_k04_binary_window_intake.py"),
            "--input", str(source), "--resources", str(resources), "--stride", str(stride),
            "--json-out", str(k04_out),
        ]
        k04_result = run_tool("k04-binary-window", k04_cmd, k04_out, timeout)

        k08_cmd = [
            python, str(WORK / "h17_ax7782_k08_sqlite_bridge.py"),
            "--object", str(source), "--resources", str(resources),
            "--transfer", transfer, "--max-phrase-words", str(max_phrase_words),
            "--json-out", str(k08_out),
        ]
        if ocr:
            k08_cmd.append("--ocr")
        if pdf_password is not None:
            k08_cmd.extend(["--pdf-password", pdf_password])
        if allow_pdf_source:
            k08_cmd.append("--allow-pdf-source")
        k08_result = run_tool("k08-exact-phrase", k08_cmd, k08_out, timeout)

    source_hash_after = sha256_file(source)
    if source_hash_before != source_hash_after:
        raise RuntimeError("source object changed during joint intake")

    return {
        "source": {
            "name": source.name,
            "bytes": source_size,
            "sha256_before": source_hash_before,
            "sha256_after": source_hash_after,
            "unchanged": True,
        },
        "parameters": {
            "transfer": transfer,
            "ocr_enabled": ocr,
            "pdf_password_supplied": pdf_password is not None,
            "pdf_source_authorized": allow_pdf_source,
            "max_phrase_words": max_phrase_words,
            "k04_raw_window_stride": stride,
            "timeout_per_tool_seconds": timeout,
        },
        "intakes": {
            "transfer_validation": transfer_result,
            "k04_binary_window": k04_result,
            "k08_exact_phrase": k08_result,
        },
        "interpretation": (
            "This report aggregates existing read-only intakes. A matching byte window or phrase is a candidate only; "
            "promote nothing until the original component commitment and source rule are independently satisfied."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", required=True, type=Path)
    parser.add_argument("--resources", type=Path, default=ROOT / "resources")
    parser.add_argument("--transfer", default="AX-7782")
    parser.add_argument("--ocr", action="store_true")
    parser.add_argument("--pdf-password", help="password for an independently authorized PDF; never guessed")
    parser.add_argument("--allow-pdf-source", action="store_true", help="attest independent provenance for non-quarantined PDFs; never use for BX25-08 or derivatives")
    parser.add_argument("--max-phrase-words", type=int, default=48)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    source = args.object.expanduser().absolute()
    resources = args.resources.expanduser().absolute()
    if args.json_out:
        out = args.json_out.expanduser().resolve(strict=False)
        if out == source.resolve(strict=False) or out == resources or resources in out.parents:
            parser.error("--json-out must be outside the source object and resources tree")
    try:
        result = inspect_joint(
            source, resources, args.transfer, args.ocr, args.pdf_password,
            args.max_phrase_words, args.stride, args.timeout, args.allow_pdf_source,
        )
    except Exception as exc:
        parser.error(type(exc).__name__)
    result = redact_sensitive(result)
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
