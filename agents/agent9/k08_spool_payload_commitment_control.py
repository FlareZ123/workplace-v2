#!/usr/bin/env python3
"""Source-pinned direct K08 commitment control over the 133 surviving print-spool payloads."""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
ACCEPTANCE = ROOT / "resources" / "acceptance.json"
ROUTING = EVIDENCE / "recovery-routing.json"
SPOOL = EVIDENCE / "print" / "spool-reconstruction.log"

EXPECTED_ACCEPTANCE = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
EXPECTED_ROUTING = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
EXPECTED_SPOOL = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
PATTERN = re.compile(
    r"JOB=(\S+).*?ATTEMPT=(\d+).*?STATE=(\S+).*?CLASS=(\S+).*?PAYLOAD=([0-9A-Fa-f]{32}).*?DEST=(\S+)"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    for path, expected in (
        (ACCEPTANCE, EXPECTED_ACCEPTANCE),
        (ROUTING, EXPECTED_ROUTING),
        (SPOOL, EXPECTED_SPOOL),
    ):
        actual = sha256(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"{path.name} hash mismatch: {actual}")

    acceptance = json.loads(ACCEPTANCE.read_text())
    routing = json.loads(ROUTING.read_text())
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    records = []
    for line_number, line in enumerate(SPOOL.read_text().splitlines(), 1):
        match = PATTERN.search(line)
        if not match:
            continue
        job, attempt, state, job_class, payload_hex, dest = match.groups()
        records.append({
            "line": line_number,
            "job": job,
            "attempt": int(attempt),
            "state": state,
            "class": job_class,
            "payload_hex": payload_hex.upper(),
            "dest": dest,
        })
    if len(records) != 133:
        raise SystemExit(f"expected 133 payload records, found {len(records)}")
    payloads = [bytes.fromhex(row["payload_hex"]) for row in records]
    if len({row["payload_hex"] for row in records}) != 133:
        raise SystemExit("expected 133 unique payloads")

    direct_hits = []
    text_candidates = {}
    printable_ascii = 0
    for row, payload in zip(records, payloads):
        for view_name, raw in (("forward-bytes", payload), ("reversed-bytes", payload[::-1])):
            if sha256(raw) == target:
                direct_hits.append({"record": row, "view": view_name})

        for view_name, text in (
            ("hex-forward", payload.hex()),
            ("hex-reversed", payload[::-1].hex()),
        ):
            normalized = normalize(text)
            text_candidates.setdefault(normalized, []).append({
                "record": row,
                "view": view_name,
            })

        if all(32 <= byte <= 126 for byte in payload):
            printable_ascii += 1
            decoded = payload.decode("ascii")
            normalized = normalize(decoded)
            if normalized:
                text_candidates.setdefault(normalized, []).append({
                    "record": row,
                    "view": "printable-ascii",
                })

    hmac_hits = []
    for normalized, origins in text_candidates.items():
        digest16 = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
        if sha256(digest16) == target:
            hmac_hits.append({"normalized": normalized, "origins": origins})

    ps0323 = [row for row in records if row["job"].endswith("-0323")]
    output = {
        "source_hashes": {
            "acceptance.json": EXPECTED_ACCEPTANCE,
            "recovery-routing.json": EXPECTED_ROUTING,
            "print/spool-reconstruction.log": EXPECTED_SPOOL,
        },
        "record_count": len(records),
        "unique_payload_count": len({row["payload_hex"] for row in records}),
        "class_counts": dict(Counter(row["class"] for row in records)),
        "state_counts": dict(Counter(row["state"] for row in records)),
        "destination_counts": dict(Counter(row["dest"] for row in records)),
        "printable_ascii_payload_count": printable_ascii,
        "direct_component_checks": 2 * len(records),
        "direct_component_hits": direct_hits,
        "unique_normalized_hex_or_ascii_candidates": len(text_candidates),
        "hmac_candidate_hits": hmac_hits,
        "PS-0323_records": ps0323,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
