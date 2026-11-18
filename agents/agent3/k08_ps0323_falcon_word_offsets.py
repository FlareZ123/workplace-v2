#!/usr/bin/env python3
"""Bounded K08 candidate: interpret PS-0323's 16-byte packet as 8 u16
absolute word offsets into the public 1889 Falcon transcription.

This tests a new source-indexed complete-object construction, not a historical
identity claim. MAIL-20/N23 -> PS-0323 is only a structural note/job crosswalk;
the exact native output is absent. The book is a candidate because MAIL-09
describes David's map-back book and the 1889 Falcon edition has a rear foldout.
The original K08 HMAC and SHA-256 commitments are unchanged.
"""
from __future__ import annotations

import hashlib
import hmac
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

SOURCE_URL = "https://soul-trade.com/sailing/falcon/falcon_frames.htm"
SOURCE_SHA256 = "2741b1054d1369a7dcfc51b32da1f4b4931c5ca8a10c9b200cee548db496176e"
WORD_STREAM_SHA256 = "36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "agent3-ps0323-falcon-word-offsets.json"


class PlainText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in ("script", "style"):
            self.skip_depth += 1
        if tag in ("p", "div", "h1", "h2", "h3", "h4", "br"):
            self.blocks.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self.skip_depth -= 1
        if tag in ("p", "div", "h1", "h2", "h3", "h4"):
            self.blocks.append(" ")

    def handle_data(self, data: str) -> None:
        if self.skip_depth == 0:
            self.blocks.append(data)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_book() -> tuple[bytes, list[str]]:
    req = Request(SOURCE_URL, headers={"User-Agent": "H17-local-history-research/1.0"})
    with urlopen(req, timeout=45) as response:
        raw = response.read()
    parser = PlainText()
    parser.feed(raw.decode("utf-8"))
    text = " ".join(parser.blocks)
    start = re.search(r"\bIN\s+the\s+summer\s+of\s+['’]86", text)
    end = re.search(r"October\s+2nd,\s+1888\.", text)
    if not start or not end or end.end() <= start.start():
        raise RuntimeError("Falcon body boundaries not found")
    book_text = text[start.start():end.end()]
    if not re.search(r"CHAPTER\s+XV\s+COPENHAGEN\s+AND\s+HOME", book_text, re.I):
        raise RuntimeError("Falcon Chapter XV marker missing")
    words = re.findall(r"[a-z0-9]+", book_text.lower())
    if sha256(raw) != SOURCE_SHA256:
        raise RuntimeError(f"Falcon source SHA changed: {sha256(raw)}")
    word_hash = sha256(" ".join(words).encode("ascii"))
    if word_hash != WORD_STREAM_SHA256:
        raise RuntimeError(f"Falcon word stream changed: {word_hash}")
    return raw, words


def spool_packets() -> dict[str, dict[str, str]]:
    path = ROOT / "resources/evidence/print/spool-reconstruction.log"
    raw = path.read_bytes()
    if sha256(raw) != SPOOL_SHA256:
        raise RuntimeError(f"spool source SHA changed: {sha256(raw)}")
    pattern = re.compile(
        r"(?P<timestamp>\S+) JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) "
        r"STATE=(?P<state>\w+) CLASS=(?P<class>\w+) "
        r"PAYLOAD=(?P<payload>[A-F0-9]{32}) DEST=(?P<dest>\S+)"
    )
    rows = {}
    for line in raw.decode("utf-8").splitlines():
        match = pattern.search(line)
        if match:
            row = match.groupdict()
            if row["job"] in ("PS-261003-0320", "PS-261003-0323"):
                if row["job"] in rows:
                    raise RuntimeError(f"duplicate selected job row: {row['job']}")
                rows[row["job"]] = row
    if set(rows) != {"PS-261003-0320", "PS-261003-0323"}:
        raise RuntimeError(f"missing N20/N23 packet rows: {sorted(rows)}")
    for job, row in rows.items():
        if (row["attempt"], row["state"], row["class"]) != ("1", "ACK", "RECOVER"):
            raise RuntimeError(f"unexpected source role for {job}: {row}")
    if rows["PS-261003-0323"]["dest"] != "store":
        raise RuntimeError(f"unexpected PS-0323 destination: {rows['PS-261003-0323']}")
    return rows


def normalize_phrase(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    if target != "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747":
        raise RuntimeError("K08 acceptance target changed")
    control = normalize_phrase(
        "A good watch leaves the room ready for the next pair of hands."
    )
    control16 = hmac.new(nonce, control.encode("utf-8"), hashlib.sha256).digest()[:16]
    if control16.hex().upper() != EXPECTED_N02_HMAC16:
        raise RuntimeError("N02 HMAC known-answer control failed")

    raw_book, words = fetch_book()
    rows = spool_packets()
    report = {
        "hypothesis": "PS-0323 packet = eight unsigned 16-bit absolute word offsets into the 1889 Falcon full-text body",
        "source_url": SOURCE_URL,
        "book_source_sha256": sha256(raw_book),
        "book_word_count": len(words),
        "book_word_stream_sha256": sha256(" ".join(words).encode("ascii")),
        "spool_sha256": SPOOL_SHA256,
        "positive_control_n02_hmac16": control16.hex().upper(),
        "packets": {},
        "candidate_count": 0,
        "matches": [],
        "interpretation": "A hit is an experimental commitment match, not proof that this transcription is David's physical copy or that N23 caused PS-0323.",
    }

    for job in ("PS-261003-0323", "PS-261003-0320"):
        row = rows[job]
        packet = bytes.fromhex(row["payload"])
        candidates = []
        for byte_order in ("big", "little"):
            offsets = [int.from_bytes(packet[i:i+2], byte_order) for i in range(0, 16, 2)]
            for base in (0, 1):
                positions = [x - base for x in offsets]
                if min(positions) < 0 or max(positions) >= len(words):
                    raise RuntimeError(f"out-of-range offsets for {job}: {positions}")
                phrase = " ".join(words[i] for i in positions)
                normalized = normalize_phrase(phrase)
                component = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
                digest = sha256(component)
                candidate = {
                    "byte_order": byte_order,
                    "index_base": base,
                    "offsets": offsets,
                    "positions": positions,
                    "words": [words[i] for i in positions],
                    "phrase": phrase,
                    "normalized_phrase": normalized,
                    "component_hex": component.hex().upper(),
                    "slot_sha256": digest,
                    "accepted": digest == target,
                }
                candidates.append(candidate)
                report["candidate_count"] += 1
                if candidate["accepted"]:
                    report["matches"].append({"job": job, **candidate})
        report["packets"][job] = {
            "timestamp": row["timestamp"],
            "attempt": row["attempt"],
            "state": row["state"],
            "class": row["class"],
            "destination": row["dest"],
            "payload_hex": row["payload"],
            "candidates": candidates,
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    print("ORIGINAL_K08_PASS" if report["matches"] else "NO_K08_MATCH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
