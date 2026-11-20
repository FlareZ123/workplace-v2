#!/usr/bin/env python3
"""Read-only USMT migration-store triage/extraction wrapper for H-17 evidence.

This tool never invokes LoadState or changes a source store. It delegates only
verification and selective extraction to Microsoft's UsmtUtils.exe. The input
store is hashed before and after the operation; extracted files are separately
hashed into a manifest. A real USMT store and the matching Windows ADK/USMT
UsmtUtils.exe are required for production use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

DEFAULT_INCLUDE = [
    "mug-stock.xls",
    "desktop-move-2026.html",
    "scanrelease.txt",
    "IR-261003-H17.txt",
    "transfer-index.htm",
    "*.eml",
    "*.msg",
    "*.doc",
    "*.docx",
    "*.xls",
    "*.xlsx",
    "*.ppt",
    "*.pptx",
    "*.rtf",
    "*.csv",
    "*.xml",
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.tif",
    "*.tiff",
    "*.sqlite",
    "*.db",
    "*.sqlite-wal",
    "*.sqlite-shm",
    "*-wal",
    "*-shm",
    "*.pdf",
    "*.html",
    "*.txt",
]
REPORTS = {"summary": None, "catalog": "catalog", "all": "all", "failureonly": "failureonly"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def related_store_files(store: Path) -> list[Path]:
    """Return the primary store plus adjacent USMT .mig segment members."""
    candidates = {store}
    match = re.match(r"^(.*)\.mig\d*$", store.name, flags=re.IGNORECASE)
    if match:
        stem = match.group(1)
        pattern = re.compile(re.escape(stem) + r"\.mig\d*$", flags=re.IGNORECASE)
        for path in store.parent.iterdir():
            if pattern.fullmatch(path.name):
                if path.is_symlink():
                    raise ValueError(f"USMT segment must not be a symlink: {path}")
                if path.is_file():
                    candidates.add(path.resolve())
    return sorted(candidates, key=lambda p: p.name.lower())


def hash_store_set(store: Path) -> list[dict[str, object]]:
    records = []
    for path in related_store_files(store):
        records.append({"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)})
    return records


def hash_tree(root: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    if not root.exists():
        return records
    root_resolved = root.resolve()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        try:
            if path.is_symlink():
                records.append({"path": rel, "symlink_target": os.readlink(path)})
                continue
            if not path.is_file():
                continue
            resolved = path.resolve()
            try:
                resolved.relative_to(root_resolved)
            except ValueError:
                records.append({"path": rel, "error": "resolved path escapes extraction root"})
                continue
            records.append({
                "path": rel,
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            })
        except OSError as exc:
            records.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
    return records


def build_verify_args(store: Path, log: Path, report: str, keyfile: Path | None = None,
                      algorithm: str | None = None) -> list[str]:
    option = "/verify" if report == "summary" else f"/verify:{REPORTS[report]}"
    args = [option, str(store), f"/l:{log}"]
    if keyfile is not None:
        args.append(f"/decrypt:{algorithm}" if algorithm else "/decrypt")
        args.append(f"/keyfile:{keyfile}")
    return args


def build_extract_args(store: Path, destination: Path, log: Path, includes: Iterable[str],
                       keyfile: Path | None = None, algorithm: str | None = None) -> list[str]:
    patterns = ",".join(includes)
    args = ["/extract", str(store), f"/i:{patterns}", str(destination), f"/l:{log}"]
    if keyfile is not None:
        args.append(f"/decrypt:{algorithm}" if algorithm else "/decrypt")
        args.append(f"/keyfile:{keyfile}")
    return args


def prepare_output(out: Path) -> None:
    if out.is_symlink():
        raise ValueError(f"output path must not be a symlink: {out}")
    if out.exists():
        if not out.is_dir():
            raise ValueError(f"output path exists and is not a directory: {out}")
        if any(out.iterdir()):
            raise ValueError(f"output directory is not empty; choose a new destination: {out}")
    else:
        out.mkdir(parents=True)


def run_intake(store: Path, tool: Path, out: Path, mode: str = "verify",
               report: str = "all", includes: Iterable[str] | None = None,
               keyfile: Path | None = None, algorithm: str | None = None,
               timeout: int = 600) -> dict[str, object]:
    if store.is_symlink():
        raise ValueError(f"input store must not be a symlink: {store}")
    if out.is_symlink():
        raise ValueError(f"output path must not be a symlink: {out}")
    store = store.resolve()
    tool = tool.resolve()
    out = out.resolve()
    if not store.is_file():
        raise ValueError(f"input store is not a regular file: {store}")
    if keyfile is not None and not keyfile.is_file():
        raise ValueError(f"key file does not exist: {keyfile}")
    if keyfile is not None:
        keyfile = keyfile.resolve()
    if timeout <= 0:
        raise ValueError("--timeout must be positive")
    if algorithm and keyfile is None:
        raise ValueError("--alg requires --keyfile; plaintext keys are deliberately unsupported")
    if mode not in {"verify", "extract"}:
        raise ValueError(f"unsupported mode: {mode}")
    if report not in REPORTS:
        raise ValueError(f"unsupported verification report: {report}")
    if mode == "extract":
        includes = list(includes or DEFAULT_INCLUDE)
    if mode == "verify" and includes:
        raise ValueError("--include is valid only with --mode extract")
    if not tool.is_file():
        found = shutil.which(str(tool)) or shutil.which("UsmtUtils.exe") or shutil.which("usmtutils")
        if found:
            tool = Path(found).resolve()
        else:
            raise FileNotFoundError(
                "UsmtUtils.exe was not found. Use the matching Windows ADK/USMT tools; "
                "do not substitute LoadState or modify the source system."
            )

    prepare_output(out)
    extracted = out / "files"

    usmt_log = out / "usmtutils.log"
    runner_log = out / "runner.log"
    manifest_path = out / "manifest.json"
    before = {"size": store.stat().st_size, "sha256": sha256_file(store)}
    before_segments = hash_store_set(store)
    if mode == "verify":
        args = build_verify_args(store, usmt_log, report, keyfile, algorithm)
        destination = None
    else:
        args = build_extract_args(store, extracted, usmt_log, includes or DEFAULT_INCLUDE, keyfile, algorithm)
        destination = extracted

    started = time.monotonic()
    completed = subprocess.run([str(tool), *args], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout, check=False)
    elapsed = time.monotonic() - started
    after = {"size": store.stat().st_size, "sha256": sha256_file(store)}
    after_segments = hash_store_set(store)
    source_unchanged = before == after and before_segments == after_segments
    extracted_files = hash_tree(destination) if destination is not None else []
    runner_log.write_text(
        "COMMAND: " + " ".join([tool.name, *args]) + "\n"
        + "RETURN CODE: " + str(completed.returncode) + "\n\n"
        + "STDOUT\n" + completed.stdout + "\nSTDERR\n" + completed.stderr,
        encoding="utf-8",
    )
    manifest: dict[str, object] = {
        "tool": tool.name,
        "mode": mode,
        "input": {"path": str(store), **before},
        "input_after": after,
        "input_segments_before": before_segments,
        "input_segments_after": after_segments,
        "input_unchanged": source_unchanged,
        "return_code": completed.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "verification_report": report if mode == "verify" else None,
        "include_patterns": list(includes or DEFAULT_INCLUDE) if mode == "extract" else [],
        "decrypt_requested": keyfile is not None,
        "keyfile_supplied": keyfile is not None,
        "algorithm_supplied": algorithm is not None,
        "usmt_log": str(usmt_log),
        "runner_log": str(runner_log),
        "extracted_files": extracted_files,
        "warning": None if source_unchanged else "Source store changed during intake; treat output as invalid.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not source_unchanged:
        raise RuntimeError("source store changed during intake; see manifest and log")
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(completed.returncode, [str(tool), *args],
                                            output=completed.stdout, stderr=completed.stderr)
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("store", type=Path, help="original compressed USMT migration store (read-only)")
    parser.add_argument("--tool", type=Path, default=Path("UsmtUtils.exe"), help="path to matching UsmtUtils.exe")
    parser.add_argument("--mode", choices=("verify", "extract"), default="verify")
    parser.add_argument("--report", choices=tuple(REPORTS), default="all", help="verification report type (default: all files)")
    parser.add_argument("--out", type=Path, required=True, help="new/empty output directory for logs, manifest, and extracted files")
    parser.add_argument("--include", action="append", default=None, help="USMT include pattern; repeatable; extract mode only")
    parser.add_argument("--keyfile", type=Path, default=None, help="authorized USMT decryption key file (never a key string)")
    parser.add_argument("--alg", default=None, help="USMT encryption algorithm; requires --keyfile")
    parser.add_argument("--timeout", type=int, default=600)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    try:
        manifest = run_intake(ns.store, ns.tool, ns.out, ns.mode, ns.report,
                              ns.include, ns.keyfile, ns.alg, ns.timeout)
    except (ValueError, FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError,
            RuntimeError, OSError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
