"""Decode text-bearing archive layers and test K08 contiguous HMAC spans.

This scan is intentionally bounded to UTF-8 source files and common textual
encodings (HTML entities, URL percent escapes, JSON string escapes, printable
Base64 and hex payloads). It does not claim to decode arbitrary encrypted or
binary print payloads.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import html
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent8"))
import k08_independent_lexical_ab_3b_sft as base

BASE64_RE = re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{24,512}={0,2}(?![A-Za-z0-9+/])")
HEX_RE = re.compile(r"(?<![A-Fa-f0-9])[A-Fa-f0-9]{32,512}(?![A-Fa-f0-9])")


def printable_utf8(data: bytes) -> str | None:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    ratio = sum(ch.isprintable() or ch.isspace() for ch in text) / max(1, len(text))
    return text if ratio >= 0.90 and len(text.strip()) >= 8 else None


def iter_files(root: Path, archive: Path | None):
    if archive is not None:
        with zipfile.ZipFile(archive) as handle:
            for item in handle.infolist():
                if not item.is_dir():
                    yield item.filename, handle.read(item.filename)
    else:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                yield path.relative_to(root).as_posix(), path.read_bytes()


def text_variants(name: str, raw: bytes):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return [], 0, 0

    variants = [
        ("raw", text),
        ("html_unescape", html.unescape(text)),
        ("url_unquote", unquote(text)),
        ("html_then_url", unquote(html.unescape(text))),
    ]
    if name.lower().endswith(".json"):
        try:
            variants.append((
                "json_decoded",
                json.dumps(json.loads(text), ensure_ascii=False, sort_keys=True),
            ))
        except json.JSONDecodeError:
            pass

    base64_count = 0
    for token in BASE64_RE.findall(text):
        try:
            decoded = printable_utf8(base64.b64decode(token, validate=True))
        except (binascii.Error, ValueError):
            decoded = None
        if decoded is not None:
            variants.append(("base64", decoded))
            base64_count += 1

    hex_count = 0
    for token in HEX_RE.findall(text):
        if len(token) % 2:
            continue
        try:
            decoded = printable_utf8(bytes.fromhex(token))
        except ValueError:
            decoded = None
        if decoded is not None:
            variants.append(("hex", decoded))
            hex_count += 1

    return variants, base64_count, hex_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT / "resources" / "evidence")
    parser.add_argument("--max-words", type=int, default=32)
    args = parser.parse_args()

    _, _, nonce, target = base.load_sources()
    files_seen = 0
    utf8_files = 0
    variants_seen = 0
    base64_payloads = 0
    hex_payloads = 0
    span_tests = 0
    hits = []

    for name, raw in iter_files(args.root, args.archive):
        files_seen += 1
        variants, b64_count, hex_count = text_variants(name, raw)
        if not variants:
            continue
        utf8_files += 1
        base64_payloads += b64_count
        hex_payloads += hex_count
        seen_normalized = set()

        for method, text in variants:
            normalized = base.norm(text)
            if not normalized or normalized in seen_normalized:
                continue
            seen_normalized.add(normalized)
            variants_seen += 1
            words = normalized.split()
            for start in range(len(words)):
                for end in range(start + 1, min(len(words), start + args.max_words) + 1):
                    phrase = " ".join(words[start:end])
                    span_tests += 1
                    component = base.candidate_component(nonce, phrase)
                    if hashlib.sha256(component).hexdigest() == target:
                        hits.append({
                            "file": name,
                            "decode_method": method,
                            "phrase": phrase,
                            "word_count": len(phrase.split()),
                        })

    print(json.dumps({
        "files_seen": files_seen,
        "utf8_files": utf8_files,
        "unique_normalized_variants": variants_seen,
        "printable_base64_payloads": base64_payloads,
        "printable_hex_payloads": hex_payloads,
        "contiguous_spans_tested": span_tests,
        "max_words": args.max_words,
        "hits": hits,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
