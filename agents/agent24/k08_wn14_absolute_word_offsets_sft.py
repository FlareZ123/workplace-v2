#!/usr/bin/env python3
"""Fail-closed K08 experiment: interpret K01 as eight absolute word offsets.

This is an exploratory, bounded candidate test against one identified public
text transcription of *The Riddle of the Sands* (1903). It tests exactly four
interpretations: big/little-endian 16-bit offsets, each zero-/one-based. It
does not claim that David's physical map-back book was this novel.

A source retrieval/quality failure is INCOMPLETE, never NO_MATCH. The script
pins the original route and acceptance files, validates the known K01 and N02
controls, hashes the fetched source, requires a complete text, and evaluates
all four offset interpretations before emitting a verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import struct
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = ROOT / "resources/candidate.json"
ROUTING_PATH = ROOT / "resources/evidence/recovery-routing.json"
ACCEPTANCE_PATH = ROOT / "resources/acceptance.json"

EXPECTED_ROUTING_SHA256 = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
EXPECTED_ACCEPTANCE_SHA256 = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
EXPECTED_SOURCE_SHA256 = ""  # populated only after a source-only acquisition run

SOURCE = {
    "name": "riddle-of-the-sands-1903-ajhw-full-text",
    "edition_note": "Public full-text transcription of Erskine Childers, The Riddle of the Sands (1903)",
    "url": "https://www.ajhw.co.uk/books/book160/book160.html",
    "min_bytes": 100_000,
    "min_words": 50_000,
    "required_markers": [
        "the riddle of the sands",
        "the little drab book",
    ],
}


class VisibleText(HTMLParser):
    """Extract visible body text; omit scripts, styles, and non-text payloads."""
    SKIP = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.body_seen = False
        self.in_body = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "body":
            self.body_seen = True
            self.in_body = True
        if tag in self.SKIP:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
        if tag == "body":
            self.in_body = False

    def handle_data(self, data: str) -> None:
        if self.skip_depth == 0 and (self.in_body or not self.body_seen):
            self.parts.append(data)

    def text(self) -> str:
        return "\n".join(self.parts)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_source(url: str) -> tuple[bytes, str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; H17-Archive-Research/1.0)",
            "Accept": "text/html,application/xhtml+xml,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        raw = response.read()
        status = getattr(response, "status", 200)
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        if status != 200 or not raw:
            raise RuntimeError(f"HTTP {status}; bytes={len(raw)}")
        charset = response.headers.get_content_charset() or "cp1252"
    if len(raw) < SOURCE["min_bytes"]:
        raise RuntimeError(f"source too small: {len(raw)} bytes")
    if "html" not in content_type.lower() and b"<html" not in raw[:8192].lower():
        raise RuntimeError(f"unexpected content type: {content_type!r}")
    decoded = raw.decode(charset, errors="replace")
    parser = VisibleText()
    parser.feed(decoded)
    visible = parser.text()
    normalized = normalize(visible)
    tokens = normalized.split()
    if len(tokens) < SOURCE["min_words"]:
        raise RuntimeError(
            f"incomplete text: {len(tokens)} normalized words; "
            f"minimum is {SOURCE['min_words']}"
        )
    missing = [
        marker for marker in SOURCE["required_markers"]
        if marker not in normalized
    ]
    if missing:
        raise RuntimeError(f"required book markers missing: {missing}")
    return raw, visible, final_url


def phrase_check(words: list[str], nonce: bytes, target: str) -> dict[str, object]:
    phrase = normalize(" ".join(words))
    component = hmac.new(nonce, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
    digest = sha256(component)
    return {
        "selected_words": words,
        "normalized_phrase": phrase,
        "hmac16_hex": component.hex().upper(),
        "component_sha256": digest,
        "target_sha256": target,
        "commitment_match": digest == target,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquire-only", action="store_true", help="fetch, validate, and hash the source without testing offsets")
    args = parser.parse_args()

    report_path = Path("k08_wn14_absolute_word_offsets_report.json")
    report: dict[str, object] = {
        "hypothesis": "K01 as eight ordered absolute normalized-word offsets into one identified book text",
        "source": {
            "name": SOURCE["name"],
            "edition_note": SOURCE["edition_note"],
            "requested_url": SOURCE["url"],
        },
        "experiment_complete": False,
        "source_available": False,
        "interpretations": [],
    }

    try:
        routing_bytes = ROUTING_PATH.read_bytes()
        acceptance_bytes = ACCEPTANCE_PATH.read_bytes()
        if sha256(routing_bytes) != EXPECTED_ROUTING_SHA256:
            raise RuntimeError("recovery-routing.json SHA-256 pin mismatch")
        if sha256(acceptance_bytes) != EXPECTED_ACCEPTANCE_SHA256:
            raise RuntimeError("acceptance.json SHA-256 pin mismatch")

        routing = json.loads(routing_bytes)
        acceptance = json.loads(acceptance_bytes)
        candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
        k01 = bytes.fromhex(candidate["K01"])
        nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
        target = acceptance["slot_sha256"]["K08"]
        k01_target = acceptance["slot_sha256"]["K01"]

        if len(k01) != 16:
            raise RuntimeError(f"K01 length is {len(k01)}, expected 16")
        if sha256(k01) != k01_target:
            raise RuntimeError("K01 does not pass its original acceptance commitment")

        control = "a good watch leaves the room ready for the next pair of hands"
        control_hmac = hmac.new(nonce, control.encode("utf-8"), hashlib.sha256).digest()[:16]
        if control_hmac.hex().upper() != EXPECTED_N02_HMAC16:
            raise RuntimeError("original N02 HMAC known-answer control failed")

        report.update({
            "routing_sha256": sha256(routing_bytes),
            "acceptance_sha256": sha256(acceptance_bytes),
            "K01_hex": k01.hex().upper(),
            "K01_sha256": sha256(k01),
            "K08_target_sha256": target,
            "N02_control": {
                "phrase": control,
                "hmac16_hex": control_hmac.hex().upper(),
                "passed": True,
            },
        })

        raw, visible, final_url = fetch_source(SOURCE["url"])
        normalized = normalize(visible)
        tokens = normalized.split()
        report["source"].update({
            "resolved_url": final_url,
            "raw_bytes": len(raw),
            "raw_sha256": sha256(raw),
            "visible_text_sha256": sha256(visible.encode("utf-8")),
            "normalized_text_sha256": sha256(normalized.encode("utf-8")),
            "normalized_word_count": len(tokens),
            "required_markers_passed": SOURCE["required_markers"],
        })
        report["source_available"] = True

        if args.acquire_only:
            report["verdict"] = "SOURCE_ACQUIRED_NOT_TESTED"
            report["experiment_complete"] = False
            print(json.dumps(report, indent=2, sort_keys=True))
            report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"REPORT {report_path}")
            return 0

        if not EXPECTED_SOURCE_SHA256:
            raise RuntimeError("source digest is not pinned; run --acquire-only first")
        if report["source"]["raw_sha256"] != EXPECTED_SOURCE_SHA256:
            raise RuntimeError("fetched source SHA-256 does not match the pinned source copy")
        report["source"]["source_sha256_pin_passed"] = True

        for endian, fmt in (("big", ">8H"), ("little", "<8H")):
            offsets = list(struct.unpack(fmt, k01))
            for base in (0, 1):
                positions = [offset - base for offset in offsets]
                interpretation: dict[str, object] = {
                    "endian": endian,
                    "index_base": base,
                    "encoded_offsets": offsets,
                    "token_positions": positions,
                }
                if any(position < 0 or position >= len(tokens) for position in positions):
                    interpretation["status"] = "OUT_OF_RANGE"
                else:
                    words = [tokens[position] for position in positions]
                    interpretation.update(phrase_check(words, nonce, target))
                    interpretation["status"] = (
                        "MATCH" if interpretation["commitment_match"] else "NO_MATCH"
                    )
                report["interpretations"].append(interpretation)

        if len(report["interpretations"]) != 4:
            raise RuntimeError("not all four endian/base interpretations were evaluated")
        report["experiment_complete"] = True
        report["verdict"] = (
            "CANDIDATE_MATCH"
            if any(x.get("commitment_match") for x in report["interpretations"])
            else "NO_MATCH"
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"REPORT {report_path}")
        return 0
    except Exception as exc:
        report["verdict"] = "SOURCE_OR_INPUT_INCOMPLETE"
        report["error"] = f"{type(exc).__name__}: {exc}"
        print(json.dumps(report, indent=2, sort_keys=True))
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"REPORT {report_path}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
