#!/usr/bin/env python3
"""Test retained 16-byte print payloads as BIP39-128 entropy for K08.

This is a finite source-motivated construction: a 16-byte payload from a
shelf-card/final-envelope print job could be the 128-bit entropy for a
12-word BIP39 phrase. Each resulting phrase is checked against the original
K08 HMAC16->SHA256 commitment. No seed search or wordlist phrase generation.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path


def normalize(phrase: str) -> str:
    phrase = phrase.lower()
    phrase = re.sub(r"[^a-z0-9\s]", " ", phrase)
    return " ".join(phrase.split())


def bip39_128(entropy: bytes, wordlist: list[str]) -> str:
    if len(entropy) != 16:
        raise ValueError(f"expected 16-byte entropy, got {len(entropy)}")
    checksum = hashlib.sha256(entropy).digest()[0] >> 4
    bitstream = f"{int.from_bytes(entropy, 'big'):0128b}{checksum:04b}"
    if len(bitstream) != 132:
        raise AssertionError(len(bitstream))
    indexes = [int(bitstream[i:i + 11], 2) for i in range(0, 132, 11)]
    return " ".join(wordlist[index] for index in indexes)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    data_root = args.data_root
    if data_root is None:
        data_root = repo_root / "resources"
        if not (data_root / "evidence").is_dir():
            data_root = repo_root

    spool_path = data_root / "evidence/print/spool-reconstruction.log"
    route_path = data_root / "evidence/recovery-routing.json"
    acceptance_path = data_root / "acceptance.json"
    wordlist_path = Path(__file__).resolve().parent / "data/bip39-english.txt"

    spool_bytes = spool_path.read_bytes()
    route_bytes = route_path.read_bytes()
    acceptance_bytes = acceptance_path.read_bytes()
    wordlist_bytes = wordlist_path.read_bytes()

    wordlist = wordlist_bytes.decode("utf-8").splitlines()
    if len(wordlist) != 2048 or len(set(wordlist)) != 2048:
        raise ValueError("BIP39 English wordlist must contain 2048 unique entries")

    route = json.loads(route_bytes)
    acceptance = json.loads(acceptance_bytes)
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    row_re = re.compile(
        r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) "
        r"CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$"
    )
    rows = []
    for line in spool_bytes.decode("utf-8").splitlines():
        match = row_re.match(line)
        if not match:
            continue
        timestamp, job, attempt, state, job_class, payload_hex, destination = match.groups()
        payload = bytes.fromhex(payload_hex)
        rows.append({
            "timestamp": timestamp,
            "job": job,
            "attempt": int(attempt),
            "state": state,
            "class": job_class,
            "destination": destination,
            "payload_hex": payload_hex,
            "payload": payload,
        })

    hits = []
    for row in rows:
        phrase = bip39_128(row["payload"], wordlist)
        normalized = normalize(phrase)
        mac16 = hmac.new(key, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
        commitment = hashlib.sha256(mac16).hexdigest()
        if commitment == target:
            hits.append({
                "job": row["job"],
                "attempt": row["attempt"],
                "state": row["state"],
                "class": row["class"],
                "destination": row["destination"],
                "payload_hex": row["payload_hex"],
                "phrase": phrase,
                "normalized": normalized,
                "mac16": mac16.hex(),
            })

    print(json.dumps({
        "construction": "each retained 16-byte spool payload as BIP39-128 entropy",
        "mnemonic_length_words": 12,
        "payload_rows": len(rows),
        "unique_payloads": len({row["payload"] for row in rows}),
        "candidate_count": len(rows),
        "special_carriers": {
            job: [
                {"attempt": row["attempt"], "payload_hex": row["payload_hex"]}
                for row in rows if row["job"] == job
            ]
            for job in ("PS-261003-0300", "PS-261003-0323")
        },
        "hits": hits,
        "target_sha256": target,
        "input_sha256": {
            "spool": hashlib.sha256(spool_bytes).hexdigest(),
            "routing": hashlib.sha256(route_bytes).hexdigest(),
            "acceptance": hashlib.sha256(acceptance_bytes).hexdigest(),
            "bip39_english": hashlib.sha256(wordlist_bytes).hexdigest(),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
