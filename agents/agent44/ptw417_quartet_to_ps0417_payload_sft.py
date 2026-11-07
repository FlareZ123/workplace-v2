#!/usr/bin/env python3
"""Bounded PTW-417 quartet -> selected PS-0417 payload producer screen.

Tests only direct identity, standard digest, K04-mask keyed-hash and CPython
MT seed forms for the source-derived latest signed/as-left four-bay quartet.
It does not test or infer a PTW-to-PS foreign key.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
SEALS = EVIDENCE / "maintenance" / "seal-receipts.jsonl"
SPOOL = EVIDENCE / "print" / "spool-reconstruction.log"
ROUTING = EVIDENCE / "recovery-routing.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_quartet() -> bytes:
    rows = [json.loads(line) for line in SEALS.read_text(encoding="utf-8").splitlines() if line.strip()]
    current = {}
    for row in rows:
        if (
            row["permit"] == "PTW-417"
            and row.get("state") == "CLOSED"
            and row.get("fitment") == "AS_LEFT"
            and row.get("signed") is True
            and row.get("asset")
        ):
            bay = row["bay"]
            previous = current.get(bay)
            if previous is None or row["revision"] > previous["revision"]:
                current[bay] = row
    assert set(current) == {"A", "B", "C", "D"}
    return b"".join(bytes.fromhex(current[bay]["serial"].removeprefix("SG-")) for bay in "ABCD")


def load_selected_payload() -> bytes:
    matches = []
    for line in SPOOL.read_text(encoding="utf-8").splitlines():
        if "JOB=PS-261003-0417 " not in line:
            continue
        fields = dict(part.split("=", 1) for part in line.split() if "=" in part)
        if fields.get("ATTEMPT") == "2" and fields.get("STATE") == "ACK" and fields.get("CLASS") == "RECOVER":
            matches.append(bytes.fromhex(fields["PAYLOAD"]))
    assert len(matches) == 1
    return matches[0]


def main() -> None:
    quartet = load_quartet()
    target = load_selected_payload()
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    k04_mask = bytes.fromhex(routing["K04"]["masked_component"])
    orders = {
        "ABCD": quartet,
        "BDAC": quartet[4:8] + quartet[12:16] + quartet[0:4] + quartet[8:12],
        "DCBA": b"".join(quartet[i:i + 4] for i in (12, 8, 4, 0)),
        "CADB": b"".join(quartet[i:i + 4] for i in (8, 0, 12, 4)),
    }

    results = []
    for order_name, message in orders.items():
        results.append((order_name, "identity", message))
        for algorithm in ("md5", "sha256", "sha3_256", "blake2s", "blake2b"):
            results.append((order_name, algorithm, getattr(hashlib, algorithm)(message).digest()[:16]))
        results.append((order_name, "hmac-sha256-k04-key", hmac.new(k04_mask, message, hashlib.sha256).digest()[:16]))
        results.append((order_name, "blake2s-k04-key", hashlib.blake2s(message, key=k04_mask).digest()[:16]))
        for seed_name, seed in (
            ("raw-bytes", message),
            ("hex-text", message.hex()),
            ("int-big", int.from_bytes(message, "big")),
            ("int-little", int.from_bytes(message, "little")),
        ):
            results.append((order_name, f"cpython-random-{seed_name}", random.Random(seed).randbytes(16)))

    hits = [
        {"order": order_name, "method": method, "value": value.hex().upper()}
        for order_name, method, value in results
        if value == target
    ]
    output = {
        "source_sha256": {
            str(SEALS.relative_to(ROOT)): sha256(SEALS),
            str(SPOOL.relative_to(ROOT)): sha256(SPOOL),
            str(ROUTING.relative_to(ROOT)): sha256(ROUTING),
        },
        "permit": "PTW-417",
        "quartet_order": "latest signed CLOSED/AS_LEFT revision per bay, A/B/C/D",
        "quartet_hex": quartet.hex().upper(),
        "target_job": "PS-261003-0417",
        "target_event": "ATTEMPT=2 STATE=ACK CLASS=RECOVER",
        "target_payload_hex": target.hex().upper(),
        "candidate_orders": list(orders),
        "comparisons": len(results),
        "hits": hits,
    }
    print(json.dumps(output, indent=2))
    assert len(quartet) == len(target) == 16
    assert len(results) == 48
    assert not hits


if __name__ == "__main__":
    main()
