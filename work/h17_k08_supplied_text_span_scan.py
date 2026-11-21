#!/usr/bin/env python3
"""Scan supplied H-17 text carriers for contiguous K08 phrase spans.

PDFs and other binary/media carriers are deliberately not opened. This is a
bounded text-corpus check, not a complete source-intake or a phrase generator.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

TEXT_SUFFIXES = {
    ".md", ".txt", ".eml", ".log", ".json", ".jsonl", ".csv", ".html", ".ini"
}
EXCLUDED_NAMES = {
    "acceptance.json", "candidate.json", "candidate.template.json", "verify.py"
}
MAX_WORDS_DEFAULT = 64


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def load_inputs_zip(path: Path):
    archive = zipfile.ZipFile(path)
    names = set(archive.namelist())
    route = json.loads(archive.read("evidence/recovery-routing.json").decode("utf-8"))
    acceptance = json.loads(archive.read("acceptance.json").decode("utf-8"))
    excluded_pdfs = sorted(
        n for n in names if PurePosixPath(n).suffix.lower() == ".pdf"
    )
    carriers = []
    for info in archive.infolist():
        p = PurePosixPath(info.filename)
        if info.is_dir() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if p.name in EXCLUDED_NAMES:
            continue
        carriers.append((info.filename, archive.read(info.filename)))
    return route, acceptance, carriers, excluded_pdfs


def load_inputs_dir(root: Path):
    if (root / "resources" / "evidence" / "recovery-routing.json").is_file():
        base = root / "resources"
    else:
        base = root
    route_path = base / "evidence" / "recovery-routing.json"
    acceptance_path = base / "acceptance.json"
    route = json.loads(route_path.read_text(encoding="utf-8"))
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    carriers = []
    excluded_pdfs = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            excluded_pdfs.append(str(path.relative_to(base)))
            continue
        if suffix not in TEXT_SUFFIXES or path.name in EXCLUDED_NAMES:
            continue
        carriers.append((str(path.relative_to(base)), path.read_bytes()))
    return route, acceptance, carriers, sorted(excluded_pdfs)


def scan(route, acceptance, carriers, max_words: int):
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    total_tokens = 0
    total_spans = 0
    hits = []
    per_file = []
    for name, raw in carriers:
        text = raw.decode("utf-8", errors="replace")
        words = normalize(text).split()
        total_tokens += len(words)
        tested = 0
        for start in range(len(words)):
            phrase_words = []
            stop = min(len(words), start + max_words)
            for end in range(start, stop):
                phrase_words.append(words[end])
                phrase = " ".join(phrase_words)
                component = hmac.new(
                    nonce, phrase.encode("utf-8"), hashlib.sha256
                ).digest()[:16]
                tested += 1
                if hashlib.sha256(component).hexdigest() == target:
                    hits.append({
                        "source": name,
                        "start_word": start,
                        "end_word_exclusive": end + 1,
                        "phrase": phrase,
                        "component": component.hex().upper(),
                    })
        total_spans += tested
        per_file.append({"source": name, "words": len(words), "spans": tested})
    return {
        "files_scanned": len(carriers),
        "tokens": total_tokens,
        "max_words": max_words,
        "contiguous_spans_tested": total_spans,
        "hits": hits,
        "per_file": per_file,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="original ZIP or extracted source directory")
    parser.add_argument("--max-words", type=int, default=MAX_WORDS_DEFAULT)
    args = parser.parse_args()
    if args.max_words < 1:
        parser.error("--max-words must be at least 1")
    if args.source.is_file() and zipfile.is_zipfile(args.source):
        route, acceptance, carriers, excluded_pdfs = load_inputs_zip(args.source)
        source_kind = "zip"
        source_sha256 = hashlib.sha256(args.source.read_bytes()).hexdigest()
    elif args.source.is_dir():
        route, acceptance, carriers, excluded_pdfs = load_inputs_dir(args.source)
        source_kind = "directory"
        source_sha256 = None
    else:
        parser.error("source must be an H-17 ZIP or extracted source directory")
    result = scan(route, acceptance, carriers, args.max_words)
    result.update({
        "source_kind": source_kind,
        "source_sha256": source_sha256,
        "excluded_pdf_members_not_opened": excluded_pdfs,
        "normalization": "lowercase; replace non-ASCII-alphanumeric/non-whitespace with spaces; collapse whitespace; trim",
        "derivation": "HMAC-SHA256(desk_nonce, normalized UTF-8 phrase)[:16], then SHA256(component)",
        "interpretation": "A zero-hit result excludes only contiguous spans in scanned text carriers up to max_words; it does not exclude omitted originals, images, workbook cells, native print media, noncontiguous selections, or longer phrases.",
    })
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
