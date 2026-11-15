#!/usr/bin/env python3
"""Exact K08 literal-span scan over every textual source file in resources/evidence.

This is a source-bounded candidate test, not a paraphrase generator or a claim
that the final wording must occur literally in the retained export.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

TEXT_SUFFIXES = {
    ".txt", ".eml", ".html", ".htm", ".json", ".jsonl", ".csv",
    ".ini", ".log", ".md",
}
EXPECTED_FILES = 40
EXPECTED_WORDS = 16_355
EXPECTED_OCCURRENCES = 966_116
EXPECTED_UNIQUE = 900_769
EXPECTED_MANIFEST = "908762b3ab5228d1034b850613c10daa58ba68d13a0e446a97dc5a0be35d0457"
EXPECTED_ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
EXPECTED_ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"


def normalized_words(text: str) -> list[str]:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.findall(r"[a-z0-9]+", text)


def component(nonce: bytes, phrase: str) -> bytes:
    return hmac.digest(nonce, phrase.encode("ascii"), "sha256")[:16]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--resource-root", type=Path,
        help="directory containing evidence/ and acceptance.json (default: repository resources/)",
    )
    args = parser.parse_args()
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2] if len(script_path.parents) > 2 else Path.cwd()
    resource_root = (args.resource_root or (repo_root / "resources")).resolve()
    evidence = resource_root / "evidence"
    route_raw = (evidence / "recovery-routing.json").read_bytes()
    acceptance_raw = (resource_root / "acceptance.json").read_bytes()
    assert hashlib.sha256(route_raw).hexdigest() == EXPECTED_ROUTE_SHA
    assert hashlib.sha256(acceptance_raw).hexdigest() == EXPECTED_ACCEPTANCE_SHA
    route = json.load