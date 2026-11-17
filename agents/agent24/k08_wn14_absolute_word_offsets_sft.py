#!/usr/bin/env python3
"""Bounded K08 hypothesis: K01's eight 16-bit byte-pairs are absolute word
indices into a source book, yielding the eight-word keeper phrase.

This is distinct from page/word extraction. It tests only two source-motivated
books (the named Riddle of the Sands and the 1887 second-edition Land of the
Broads candidate), both byte orders, and zero-/one-based indexing. It does not
search arbitrary wordlists or mutate any source/acceptance files.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import struct
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = json.loads((ROOT / "resources/candidate.json").read_text(encoding="utf-8"))
ROUTE = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8"))
ACCEPT = json.loads((ROOT / "resources/acceptance.json").read_text(encoding="utf-8"))

K01 = bytes.fromhex(CANDIDATE["K01"])
NONCE = bytes.fromhex(ROUTE["K08"]["desk_nonce"])
TARGET = ACCEPT["slot_sha256"]["K08"]

SOURCES = [
    {
        "name": "riddle-of-the-sands-1903-gutenberg",
        "url": "https://www.gutenberg.org/files/2360/2360-0.txt",
        "kind": "text",
        "gutenberg": True,
    },
    {
        "name": "land-of-the-broads-1887-second-edition",
        "url": "https://archive.org/download/landofbroadsprat00suffrich/landofbroadsprat00suffrich_djvu.txt",
        "kind": "text",
        "fallback_pdf": "https://upload.wikimedia.org/wikipedia/commons/d/d5/The_land_of_the_Broads_-_a_pratical_and_illustrated_guide_to_the_extensive_but_little-known_district_of_the_broads_of_Norfolk_and_Suffolk_%28IA_landofbroadsprat00suffrich%29.pdf",
    },
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "H17-Archive-Research/1.0 (public-domain text probe)"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        data = response.read()
        if response.status != 200 or not data:
            raise RuntimeError(f"HTTP {response.status}, {len(data)} bytes")
        return data


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\\s]", " ", text)
    return re.sub(r"\\s+", " ", text).strip()


def strip_gutenberg(text: str) -> str:
    start = re.search(r"\\*\\*\\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\\n]*", text, re.I)
    end = re.search(r"\\*\\*\\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\\n]*", text, re.I)
    if start:
        text = text[start.end():]
    if end:
        text = text[:end.start()]
    return text


def extract_pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is required for the Wikimedia PDF fallback") from exc
    reader = PdfReader(BytesIO(data))
    return "\\n".join(page.extract_text() or "" for page in reader.pages)


def check_phrase(words: list[str]) -> dict[str, object]:
    phrase = normalize(" ".join(words))
    component = hmac.new(NONCE, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
    digest = hashlib.sha256(component).hexdigest()
    return {
        "words": words,
        "normalized_phrase": phrase,
        "derived_K08_component": component.hex().upper(),
        "derived_K08_sha256": digest,
        "acceptance_match": digest == TARGET,
    }


def main() -> None:
    assert len(K01) == 16
    assert hashlib.sha256(K01).hexdigest() == ACCEPT["slot_sha256"]["K01"]
    control = "a good watch leaves the room ready for the next pair of hands"
    control_hmac = hmac.new(NONCE, control.encode("utf-8"), hashlib.sha256).digest()[:16]
    assert control_hmac.hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    print("K01", K01.hex().upper())
    print("K01_BYTE_PAIRS", [K01[i:i+2].hex().upper() for i in range(0, 16, 2)])
    print("K08_TARGET_SHA256", TARGET)
    report: dict[str, object] = {
        "hypothesis": "eight K01 16-bit byte-pairs are absolute normalized-word offsets into a source book",
        "K01": K01.hex().upper(),
        "byte_pairs": [K01[i:i+2].hex().upper() for i in range(0, 16, 2)],
        "target_K08_sha256": TARGET,
        "sources": [],
    }

    for source in SOURCES:
        entry: dict[str, object] = {"name": source["name"], "url": source["url"]}
        try:
            try:
                raw = fetch(source["url"])
                source_url = source["url"]
                if source.get("kind") == "pdf":
                    text = extract_pdf_text(raw)
                else:
                    text = raw.decode("utf-8-sig", errors="replace")
            except Exception as primary_error:
                fallback = source.get("fallback_pdf")
                if not fallback:
                    raise
                raw = fetch(fallback)
                source_url = fallback
                text = extract_pdf_text(raw)
                entry["primary_fetch_error"] = f"{type(primary_error).__name__}: {primary_error}"
            if source.get("gutenberg"):
                text = strip_gutenberg(text)
            normalized = normalize(text)
            tokens = normalized.split()
            entry.update({
                "used_url": source_url,
                "source_bytes": len(raw),
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                "normalized_word_count": len(tokens),
            })
            results = []
            for endian, fmt in (("big", ">8H"), ("little", "<8H")):
                indexes = list(struct.unpack(fmt, K01))
                for base in (0, 1):
                    positions = [i - base for i in indexes]
                    if any(i < 0 or i >= len(tokens) for i in positions):
                        results.append({
                            "endian": endian,
                            "index_base": base,
                            "indexes": indexes,
                            "status": "OUT_OF_RANGE",
                        })
                        continue
                    words = [tokens[i] for i in positions]
                    result = check_phrase(words)
                    result.update({
                        "endian": endian,
                        "index_base": base,
                        "indexes": indexes,
                    })
                    results.append(result)
                    print(json.dumps({"source": source["name"], **result}, sort_keys=True))
            entry["results"] = results
            entry["any_acceptance_match"] = any(
                isinstance(r, dict) and r.get("acceptance_match") for r in results
            )
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            print(json.dumps({"source": source["name"], "error": entry["error"]}, sort_keys=True))
        report["sources"].append(entry)

    out = Path("k08_wn14_absolute_word_offsets_report.json")
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    print("REPORT", out)
    print("ANY_ACCEPTANCE_MATCH", any(
        s.get("any_acceptance_match", False) for s in report["sources"]
    ))


if __name__ == "__main__":
    main()
