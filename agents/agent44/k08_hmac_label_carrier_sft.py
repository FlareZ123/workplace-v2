#!/usr/bin/env python3
"""Exact K08 HMAC16-to-printer-LABEL carrier join; read-only source test."""
from __future__ import annotations
import configparser
import hashlib
import hmac
import json
import re
from collections import defaultdict
from pathlib import Path

NOTES_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA256 = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def select_k04_row_header_only(lines: list[str], route_job: str) -> int:
    """Select the latest RECOVER ACK without reading PAYLOAD or DEST."""
    selected = []
    header = re.compile(
        r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)(?=\s|$)"
    )
    for index, line in enumerate(lines):
        match = header.match(line)
        if match is None:
            continue
        timestamp, job, attempt, state, record_class = match.groups()
        if job == route_job and state == "ACK" and record_class == "RECOVER":
            selected.append((int(attempt), timestamp, index))
    if not selected:
        raise ValueError("No route-selected RECOVER ACK found")
    return max(selected, key=lambda item: (item[0], item[1]))[2]


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    evidence = root / "resources" / "evidence"
    notes_raw = (evidence / "crew" / "noticeboard-and-desk-notes.txt").read_bytes()
    spool_raw = (evidence / "print" / "spool-reconstruction.log").read_bytes()
    route_raw = (evidence / "recovery-routing.json").read_bytes()
    assert hashlib.sha256(notes_raw).hexdigest() == NOTES_SHA256
    assert hashlib.sha256(spool_raw).hexdigest() == SPOOL_SHA256
    assert hashlib.sha256(route_raw).hexdigest() == ROUTE_SHA256

    labels = configparser.ConfigParser()
    labels.read(evidence / "archive-labels.ini", encoding="utf-8")
    route_job = labels["printer_routes_2026-09-01_to_2026-10-03"]["ESC-N"]
    lines = [
        line for line in spool_raw.decode("ascii").splitlines()
        if line.startswith("2026-")
    ]
    assert len(lines) == 133
    selected_index = select_k04_row_header_only(lines, route_job)
    assert selected_index == 129

    packets = []
    label_packets = []
    for index, line in enumerate(lines):
        header = re.match(
            r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)(?=\s|$)",
            line,
        )
        assert header is not None
        if index == selected_index:
            # The disputed selected payload is never parsed.
            continue
        record_class = header.group(5)
        payload_match = re.search(r"(?:^|\s)PAYLOAD=([0-9A-F]{32})(?=\s|$)", line)
        assert payload_match is not None, ("missing intact packet payload", index)
        payload = bytes.fromhex(payload_match.group(1))
        assert len(payload) == 16
        packets.append(payload)
        if record_class == "LABEL":
            label_packets.append(payload)

    assert len(packets) == 132 and len(label_packets) == 52
    route = json.loads(route_raw)
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])

    note_entries = list(
        re.finditer(
            r"(?m)^N(\d{2}) / ([^\n]+)\n([^\n]+)",
            notes_raw.decode("utf-8"),
        )
    )
    assert len(note_entries) == 24
    provenance = defaultdict(list)
    for match in note_entries:
        note_id, author, caption_line = match.groups()
        caption = (
            caption_line.split(":", 1)[-1].strip()
            if ":" in caption_line
            else caption_line.strip()
        )
        words = normalize(caption).split()
        for start in range(len(words)):
            for length in range(1, min(40, len(words) - start) + 1):
                phrase = " ".join(words[start : start + length])
                provenance[phrase].append((note_id, author, start, length))

    digests = {
        phrase: hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]
        for phrase in provenance
    }
    assert digests[
        "a good watch leaves the room ready for the next pair of hands"
    ].hex().upper() == N02_HMAC16

    def exact_matches(payloads: list[bytes]):
        payload_index = defaultdict(list)
        for index, payload in enumerate(payloads):
            payload_index[payload].append(index)
        return [
            (phrase, index)
            for phrase, digest in digests.items()
            for index in payload_index.get(digest, [])
        ]

    label_hits = exact_matches(label_packets)
    all_hits = exact_matches(packets)

    # Synthetic positive: the same scanner must recover a planted literal HMAC16.
    planted_phrase = "a good watch leaves the room ready for the next pair of hands"
    planted_digest = digests[planted_phrase]
    synthetic_hits = exact_matches(label_packets + [planted_digest])
    assert (planted_phrase, len(label_packets)) in synthetic_hits
    assert len([hit for hit in synthetic_hits if hit[1] == len(label_packets)]) == 1

    print(
        json.dumps(
            {
                "notes_sha256": NOTES_SHA256,
                "spool_sha256": SPOOL_SHA256,
                "route_sha256": ROUTE_SHA256,
                "note_entries": len(note_entries),
                "unique_normalized_spans": len(provenance),
                "span_occurrences": sum(len(refs) for refs in provenance.values()),
                "intact_packets": len(packets),
                "intact_label_packets": len(label_packets),
                "selected_k04_row_zero_based": selected_index,
                "exact_label_hmac16_hits": label_hits,
                "exact_all_class_hmac16_hits": all_hits,
                "synthetic_exact_hmac16_positive": "PASS",
                "normalization": "lowercase; non-[a-z0-9 whitespace] to space; collapse whitespace",
                "hmac": "HMAC-SHA256(desk_nonce, normalized UTF-8)[:16]",
                "selected_payload_parsed": False,
                "acceptance_commitment_consulted": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
