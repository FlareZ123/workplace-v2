#!/usr/bin/env python3
"""Screen exact contiguous text spans against the REC8/1 K08 commitment.

Run from the repository root:
  python agents/agent10/k08_literal_span_screen.py --root resources

Or against the supplied archive export:
  python agents/agent10/k08_literal_span_screen.py --root /path/to/h17-archive-dump
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

TEXT_SUFFIXES = {
    ".eml", ".txt", ".html", ".csv", ".ini", ".json", ".jsonl", ".md", ".log"
}


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\\s]", " ", text)
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("resources"))
    parser.add_argument("--max-words", type=int, default=128)
    args = parser.parse_args()

    root = args.root.resolve()
    evidence = root / "evidence"
    acceptance = json.loads((root / "acceptance.json").read_text(encoding="utf-8"))
    routing = json.loads((evidence / "recovery-routing.json").read_text(encoding="utf-8"))
    target = acceptance["slot_sha256"]["K08"]
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])

    files = sorted(
        p for p in evidence.rglob("*")
        if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES
    )
    start_here = root / "START_HERE.md"
    if start_here.is_file():
        files.append(start_here)

    total_tokens = 0
    total_windows = 0
    matches = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        words = normalize(text).split()
        total_tokens += len(words)
        upper = min(args.max_words, len(words))
        relative = str(path.relative_to(root))
        for width in range(1, upper + 1):
            for start in range(len(words) - width + 1):
                phrase = " ".join(words[start:start + width])
                digest = hmac.new(nonce, phrase.encode("ascii"), hashlib.sha256).digest()[:16]
                total_windows += 1
                if hashlib.sha256(digest).hexdigest() == target:
                    matches.append({
                        "file": relative,
                        "word_start_zero_based": start,
                        "word_count": width,
                        "phrase": phrase,
                        "component": digest.hex().upper(),
                    })

    print(json.dumps({
        "root": str(root),
        "files_scanned": len(files),
        "tokens_scanned": total_tokens,
        "max_words": args.max_words,
        "candidate_windows": total_windows,
        "matches": matches,
        "excluded_binary_files": [
            "evidence/h17-supplemental-office-files/BX25-08.pdf",
            "evidence/recorder/trip-recorder.raw",
        ],
    }, indent=2))
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
