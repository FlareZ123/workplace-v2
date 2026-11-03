"""K04 source-only test of legacy CPython version-1 text-seeded MT19937.

Distinct from the earlier SHA-512 CPython version-2 string-seed study.
Each structured source identifier pair is a complete generator hypothesis.
The disputed ESC-N ACK2 payload, route mask and K04 commitment are omitted.
Run on Windows 11 with Python 3 from this repository.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(os.environ.get(
    "H17_EVIDENCE_ROOT",
    Path(__file__).resolve().parents[2] / "resources" / "evidence",
))
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TEXT_MANIFEST_SHA = "54e136f19efc05fd72493071a7d70963afa7698a9a15f7690c9e3a9d5ead38b4"
SUFFIXES = {".txt", ".eml", ".json", ".jsonl", ".ini", ".log", ".csv", ".html", ".md"}
DELIMITERS = ("", "-", ":", "/", "|", " ")
MAX_WINDOWS = 512


def source_seeds() -> list[str]:
    files = sorted(
        p for p in ROOT.rglob("*")
        if p.is_file() and p.suffix in SUFFIXES and p.name != "spool-reconstruction.log"
    )
    assert len(files) == 39
    digest = hashlib.sha256()
    corpus = []
    for file in files:
        data = file.read_bytes()
        digest.update(file.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\\0")
        digest.update(data)
        digest.update(b"\\0")
        corpus.append(data.decode("utf-8", errors="replace"))
    assert digest.hexdigest() == TEXT_MANIFEST_SHA
    raw = "\\n".join(corpus)
    ids = set(re.findall(r"\\b[A-Z0-9]{2,}(?:[-/:][A-Z0-9]+){1,5}\\b", raw))
    ids.update(re.findall(r"\\b(?:2026|2025)[-/.]?[0-9]{2}[-/.]?[0-9]{2}(?:T[0-9:+-]{4,20}Z?)?", raw))
    ids.update(re.findall(r"\\b(?:PS-\\d{6}-\\d{4}|AX-\\d{4}|IR-\\d{6}-H17|H17-IR-\\d{6}|PTW-\\d{3}|REC8/1|ESC-[NS])\\b", raw))
    ids.update((
        "H17", "H-17", "IR-261003-H17", "H17-IR-261003", "ESC-N", "ESC-S",
        "WATCH-SPARE", "REC8/1", "2026-10-03", "20261003", "2026-09-24",
        "20260924", "Noyes Energy Group", "H-17 archive", "Archive", "ARCHIVE",
    ))
    selected = sorted(
        token for token in ids if len(token) <= 48 and any(c.isalpha() for c in token)
        and re.search(r"T21:1[234]:", token) is None and not token.lower().startswith("0x")
    )
    assert len(selected) == 202
    return selected


def source_packets() -> dict[int, list[tuple[int, str, bool, tuple[int, ...]]]]:
    spool = (ROOT / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    lines = [line for line in spool.decode("ascii").splitlines() if line and not line.startswith("#")]
    assert len(lines) == 133
    header = lines[129].split(" PAYLOAD=")[0]
    assert "JOB=PS-261003-0417" in header and "ATTEMPT=2" in header
    index = defaultdict(list)
    for i, line in enumerate(lines[:96]):
        payload = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1))
        chunks = [payload[j:j+4] for j in range(0, 16, 4)]
        for reverse in (False, True):
            ordered = chunks[::-1] if reverse else chunks
            for endian in ("little", "big"):
                four = tuple(int.from_bytes(word, endian) for word in ordered)
                index[four[-1]].append((i, endian, reverse, four))
    assert sum(map(len, index.values())) == 96*4
    return index


def draw(seed: str, index: dict, maximum: int) -> tuple[int, list]:
    rng = random.Random()
    rng.seed(seed, version=1)
    last = [-1, -1, -1, -1]
    near = 0
    matches = []
    for pos in range(maximum + 3):
        word = rng.getrandbits(32)
        last.pop(0)
        last.append(word)
        for packet, endian, reverse, four in index.get(word, ()):
            near += 1
            if tuple(last) == four:
                matches.append((seed, packet, pos-3, endian, reverse))
    return near, matches


def main() -> None:
    keys = source_seeds()
    controls = source_packets()
    synthetic = "H17-IR-261003:PS-261003-0417"
    rng = random.Random()
    rng.seed(synthetic, version=1)
    truth = [rng.getrandbits(32) for _ in range(177)][173:]
    assert len(truth) == 4
    positive_index = {truth[-1]: [(0, "little", False, tuple(truth))]}
    assert draw(synthetic, positive_index, MAX_WINDOWS)[1] == [
        (synthetic, 0, 173, "little", False)
    ]
    checked = near = 0
    hits = []
    for a in keys:
        for b in keys:
            if a == b:
                continue
            for sep in DELIMITERS:
                n, matched = draw(a+sep+b, controls, MAX_WINDOWS)
                checked += 1
                near += n
                hits.extend(matched)
    assert checked == 243612 and near == 16 and hits == []
    print(json.dumps({
        "producer": "CPython random.Random(str) legacy version=1",
        "source_identifiers": len(keys),
        "structured_seeds": checked,
        "generator_words_tested": checked*(MAX_WINDOWS+3),
        "later_intact_packets_reserved": 36,
        "first_word_matches": near,
        "complete_original_packet_matches": hits,
        "planted_later_window_positive": "PASS",
        "selected_ACK2_payload_used": False,
        "K04_mask_or_commitment_used": False,
    }, indent=2))


if __name__ == "__main__":
    main()
