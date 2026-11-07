#!/usr/bin/env python3
"""Source-pinned PTW serial -> same-suffix printer-payload relation screen."""
from __future__ import annotations

import hashlib
import hmac
import itertools
import json
import random
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
SEAL_HASH = "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

KEYS = {
    "K01": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K02": bytes.fromhex("0D7E3AB56FB75DA3EB0E2E06786D239E"),
    "K03": bytes.fromhex("1384AF96E25D6ADA666209CB55E062FA"),
    "K05": bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
    "K06": bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
    "K07": bytes.fromhex("93495F5E425AB8E592123DABAEB68545"),
    "ROUTE_MASK": bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C"),
    "K08_NONCE": bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497"),
}
SEPARATORS = (b"", b"|", b":", b"\n")
HASHES = ("md5", "sha1", "sha256", "sha3_256", "blake2s", "blake2b")


def load_controls():
    seal_path = RESOURCES / "evidence/maintenance/seal-receipts.jsonl"
    spool_path = RESOURCES / "evidence/print/spool-reconstruction.log"
    assert hashlib.sha256(seal_path.read_bytes()).hexdigest() == SEAL_HASH
    assert hashlib.sha256(spool_path.read_bytes()).hexdigest() == SPOOL_HASH

    seals = [json.loads(line) for line in seal_path.read_text().splitlines()]
    spool = []
    for line in spool_path.read_text().splitlines():
        match = re.search(
            r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) "
            r"CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)",
            line,
        )
        if match:
            spool.append({
                "ts": line.split(" JOB=")[0],
                "job": int(match.group(1)),
                "attempt": int(match.group(2)),
                "state": match.group(3),
                "cls": match.group(4),
                "payload": bytes.fromhex(match.group(5)),
                "dest": match.group(6),
            })

    controls = []
    for permit in range(390, 417):
        receipts = [
            row for row in seals
            if row.get("permit") == f"PTW-{permit}"
            and row.get("signed")
            and row.get("state") == "CLOSED"
            and row.get("fitment") == "AS_LEFT"
        ]
        jobs = [row for row in spool if row["job"] == permit]
        assert len(receipts) == len(jobs) == 1, (permit, len(receipts), len(jobs))
        receipt, job = receipts[0], jobs[0]
        assert job["state"] == "ACK"
        controls.append({
            "permit": permit,
            "bay": receipt["bay"],
            "serial": receipt["serial"].split("-")[-1].upper(),
            "job": job["job"],
            "attempt": job["attempt"],
            "state": job["state"],
            "cls": job["cls"],
            "dest": job["dest"],
            "ts": job["ts"],
            "payload": job["payload"],
        })
    assert len(controls) == 27
    return controls


def field_values(row):
    serial = bytes.fromhex(row["serial"])
    timestamp = row["ts"]
    dt = __import__("datetime").datetime.fromisoformat(timestamp)
    unix = int(dt.timestamp())
    return {
        "serial": [serial, row["serial"].encode(), ("SG-" + row["serial"]).encode(),
                   row["serial"].lower().encode()],
        "permit": [str(row["permit"]).encode(), f"PTW-{row['permit']}".encode()],
        "job": [str(row["job"]).encode(), f"PS-261003-{row['job']:04d}".encode(),
                f"{row['job']:04d}".encode()],
        "bay": [row["bay"].encode()],
        "class": [row["cls"].encode(), row["cls"].lower().encode()],
        "dest": [row["dest"].encode(), row["dest"].upper().encode()],
        "state": [row["state"].encode()],
        "attempt": [str(row["attempt"]).encode()],
        "time": [timestamp.encode(), dt.strftime("%H:%M:%S").encode(),
                 struct.pack(">I", unix), struct.pack("<I", unix)],
    }


def digest_message_screen(first):
    values = field_values(first)
    names = tuple(values)
    metadata = tuple(name for name in names if name != "serial")
    messages = 0
    outputs = 0
    hits = []
    target = first["payload"]

    for size in range(1, 4):
        for others in itertools.combinations(metadata, size - 1):
            subset = ("serial",) + others
            for order in itertools.permutations(subset):
                ranges = [range(len(values[name])) for name in order]
                for reps in itertools.product(*ranges):
                    for separators in itertools.product(SEPARATORS, repeat=size - 1):
                        message = b"".join(
                            values[name][rep] + (separators[i] if i < size - 1 else b"")
                            for i, (name, rep) in enumerate(zip(order, reps))
                        )
                        messages += 1
                        digests = []
                        for algorithm in HASHES:
                            digest = hashlib.new(algorithm, message).digest()
                            digests.extend((digest[:16], digest[-16:]))
                        for key in KEYS.values():
                            digest = hmac.new(key, message, hashlib.sha256).digest()
                            digests.extend((digest[:16], digest[-16:]))
                        for key in KEYS.values():
                            digests.append(hashlib.blake2s(message, key=key, digest_size=16).digest())
                            digests.append(hashlib.blake2b(message, key=key, digest_size=16).digest())
                        outputs += len(digests)
                        if any(digest == target for digest in digests):
                            hits.append((order, reps, separators, message.hex()))
    return messages, outputs, hits


def serial_as_key_screen(first):
    values = field_values(first)
    metadata = tuple(name for name in values if name != "serial")
    serial_forms = values["serial"]
    messages = 0
    outputs = 0
    hits = []

    for size in range(1, 4):
        for subset in itertools.combinations(metadata, size):
            for order in itertools.permutations(subset):
                ranges = [range(len(values[name])) for name in order]
                for reps in itertools.product(*ranges):
                    for separators in itertools.product(SEPARATORS, repeat=size - 1):
                        message = b"".join(
                            values[name][rep] + (separators[i] if i < size - 1 else b"")
                            for i, (name, rep) in enumerate(zip(order, reps))
                        )
                        messages += 1
                        for serial_key in serial_forms:
                            digest = hmac.new(serial_key, message, hashlib.sha256).digest()
                            candidates = [digest[:16], digest[-16:]]
                            candidates.append(hashlib.blake2s(message, key=serial_key, digest_size=16).digest())
                            candidates.append(hashlib.blake2b(message, key=serial_key, digest_size=16).digest())
                            for algorithm in ("md5", "sha1", "sha256"):
                                derived_key = hashlib.new(algorithm, serial_key).digest()
                                candidates.append(hmac.new(derived_key, message, hashlib.sha256).digest()[:16])
                            outputs += len(candidates)
                            if any(candidate == first["payload"] for candidate in candidates):
                                hits.append((order, reps, separators, serial_key.hex(), message.hex()))
    return messages, outputs, hits


def cpython_outputs(seed):
    outputs = {"randbytes16": random.Random(seed).randbytes(16)}
    outputs["getrand128_be"] = random.Random(seed).getrandbits(128).to_bytes(16, "big")
    outputs["getrand128_le"] = random.Random(seed).getrandbits(128).to_bytes(16, "little")
    for endian in ("big", "little"):
        for reverse in (False, True):
            rng = random.Random(seed)
            words = [rng.getrandbits(32) for _ in range(4)]
            if reverse:
                words.reverse()
            outputs[f"words_{endian}_{reverse}"] = b"".join(
                word.to_bytes(4, endian) for word in words
            )
    rng = random.Random(seed)
    outputs["bytes_getrand8"] = bytes(rng.getrandbits(8) for _ in range(16))
    return outputs


def seed_forms(row):
    serial = bytes.fromhex(row["serial"])
    number = row["permit"]
    forms = {
        "int_be": int.from_bytes(serial, "big"),
        "int_le": int.from_bytes(serial, "little"),
        "hex_upper": row["serial"],
        "hex_lower": row["serial"].lower(),
        "serial_upper": "SG-" + row["serial"],
        "serial_lower": "sg-" + row["serial"].lower(),
        "permit": f"PTW-{number}",
        "job_suffix": f"{number:04d}",
        "job_full": f"PS-261003-{number:04d}",
        "bytes_be": serial,
        "bytes_le": serial[::-1],
        "serial_plus_job": serial + f"PS-261003-{number:04d}".encode(),
        "job_plus_serial": f"PS-261003-{number:04d}".encode() + serial,
    }
    return forms


def cpython_seed_screen(controls):
    outputs = 0
    hits = []
    for row in controls:
        for name, seed in seed_forms(row).items():
            for output_name, output in cpython_outputs(seed).items():
                outputs += 1
                if output == row["payload"]:
                    hits.append((row["permit"], name, output_name))
        serial = bytes.fromhex(row["serial"])
        bases = (
            ("serial", serial),
            ("serialhex", row["serial"].encode()),
            ("serialjob", serial + f"PS-261003-{row['job']:04d}".encode()),
            ("jobserial", f"PS-261003-{row['job']:04d}".encode() + serial),
        )
        for base_name, base in bases:
            for algorithm in ("sha256", "sha512", "md5"):
                digest = hashlib.new(algorithm, base).digest()
                derived_seeds = (
                    int.from_bytes(digest, "big"),
                    int.from_bytes(digest, "little"),
                    digest,
                    digest.hex(),
                )
                for seed in derived_seeds:
                    for output_name, output in cpython_outputs(seed).items():
                        outputs += 1
                        if output == row["payload"]:
                            hits.append((row["permit"], base_name + algorithm, output_name))
    return outputs, hits


def main():
    controls = load_controls()
    message_count, digest_count, digest_hits = digest_message_screen(controls[0])
    key_message_count, key_digest_count, key_hits = serial_as_key_screen(controls[0])
    cpython_count, cpython_hits = cpython_seed_screen(controls)

    print(f"same-suffix intact PTW/PS controls: {len(controls)}")
    print(f"serial-in-message constructions: {message_count}")
    print(f"serial-in-message digest outputs: {digest_count}")
    print(f"serial-in-message exact first-control hits: {len(digest_hits)}")
    print(f"metadata messages with serial as key: {key_message_count}")
    print(f"serial-as-key digest outputs: {key_digest_count}")
    print(f"serial-as-key exact first-control hits: {len(key_hits)}")
    print(f"per-record CPython seed outputs: {cpython_count}")
    print(f"per-record CPython exact payload hits: {len(cpython_hits)}")
    for hit in digest_hits + key_hits + cpython_hits:
        print("HIT", hit)


if __name__ == "__main__":
    main()
