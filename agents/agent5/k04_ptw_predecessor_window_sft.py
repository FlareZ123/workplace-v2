#!/usr/bin/env python3
"""Source-pinned cross-stream test of PTW predecessor serials against PS payloads."""
from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"

PINS = {
    "maintenance/seal-receipts.jsonl": "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}
ACCEPTANCE_SHA256 = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
K04_SHA256 = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

SPOOL_ROW = re.compile(
    r"JOB=PS-261003-(\d{4})\s+ATTEMPT=(\d+)\s+STATE=(\w+)\s+"
    r"CLASS=(\w+)\s+PAYLOAD=([0-9A-F]{32})\s+DEST=(\w+)"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def xor16(left: bytes, right: bytes) -> bytes:
    assert len(left) == len(right) == 16
    return bytes(a ^ b for a, b in zip(left, right))


def serial_bytes(row: dict) -> bytes:
    serial = row["serial"]
    assert re.fullmatch(r"SG-[0-9A-F]{8}", serial), serial
    return bytes.fromhex(serial[3:])


def main() -> None:
    source_bytes = {}
    for relative, expected in PINS.items():
        raw = (EVIDENCE / relative).read_bytes()
        assert sha256(raw) == expected, f"source pin mismatch: {relative}"
        source_bytes[relative] = raw

    acceptance_raw = (ROOT / "acceptance.json").read_bytes()
    assert sha256(acceptance_raw) == ACCEPTANCE_SHA256
    acceptance = json.loads(acceptance_raw)
    route = json.loads(source_bytes["recovery-routing.json"])
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert len(mask) == 16
    assert acceptance["slot_sha256"]["K04"] == K04_SHA256

    by_permit = collections.defaultdict(list)
    for line in source_bytes["maintenance/seal-receipts.jsonl"].splitlines():
        if not line:
            continue
        row = json.loads(line)
        match = re.fullmatch(r"PTW-(\d+)", row.get("permit", ""))
        if match and 390 <= int(match.group(1)) <= 416:
            by_permit[int(match.group(1))].append(row)

    assert set(by_permit) == set(range(390, 417))
    for permit, rows in by_permit.items():
        assert len(rows) == 1, (permit, len(rows))
        row = rows[0]
        assert (row["state"], row["fitment"], row["signed"], row["revision"]) == (
            "CLOSED", "AS_LEFT", True, 1
        )
        assert len(serial_bytes(row)) == 4

    spool = collections.defaultdict(list)
    for line in source_bytes["print/spool-reconstruction.log"].decode("utf-8").splitlines():
        match = SPOOL_ROW.search(line)
        if match:
            job, attempt, state, job_class, payload, destination = match.groups()
            spool[int(job)].append({
                "attempt": int(attempt),
                "state": state,
                "class": job_class,
                "payload": bytes.fromhex(payload),
                "dest": destination,
            })

    assert all(len(spool[n]) == 1 and len(spool[n][0]["payload"]) == 16
               for n in range(390, 417))
    selected_rows = [
        row for row in spool[417]
        if (row["attempt"], row["state"], row["class"], row["dest"])
        == (2, "ACK", "RECOVER", "bench")
    ]
    assert len(selected_rows) == 1
    selected_payload = selected_rows[0]["payload"]

    def serial_window(job: int, reverse_permits: bool = False,
                      reverse_each_serial: bool = False) -> bytes:
        permits = list(range(job - 4, job))
        if reverse_permits:
            permits.reverse()
        chunks = [serial_bytes(by_permit[p][0]) for p in permits]
        if reverse_each_serial:
            chunks = [chunk[::-1] for chunk in chunks]
        return b"".join(chunks)

    def pipe_hash_window(job: int) -> bytes:
        serials = [by_permit[p][0]["serial"] for p in range(job - 4, job)]
        return hashlib.sha256("|".join(serials).encode("ascii")).digest()[:16]

    def matches_component(candidate_component: bytes, observed_payload: bytes) -> bool:
        return xor16(candidate_component, mask) == observed_payload

    orientations = {
        "ascending_printed": (False, False),
        "descending_printed": (True, False),
        "ascending_each_serial_reversed": (False, True),
        "descending_each_serial_reversed": (True, True),
    }

    raw_component_hits = []
    raw_payload_hits = []
    hash_component_hits = []
    for job in range(394, 417):
        observed = spool[job][0]["payload"]
        for name, (reverse_permits, reverse_each) in orientations.items():
            component = serial_window(job, reverse_permits, reverse_each)
            if matches_component(component, observed):
                raw_component_hits.append((job, name))
            if component == observed:
                raw_payload_hits.append((job, name))
        hashed_component = pipe_hash_window(job)
        if matches_component(hashed_component, observed):
            hash_component_hits.append(job)

    assert not raw_component_hits
    assert not raw_payload_hits
    assert not hash_component_hits

    # Positive control: the comparator recognizes a planted component/payload pair.
    planted_component = serial_window(400)
    planted_payload = xor16(planted_component, mask)
    assert matches_component(planted_component, planted_payload)
    assert not matches_component(planted_component, spool[400][0]["payload"])

    raw_target_component = serial_window(417)
    raw_target_payload = xor16(raw_target_component, mask)
    raw_target_digest = sha256(raw_target_component)

    hash_target_component = pipe_hash_window(417)
    hash_target_payload = xor16(hash_target_component, mask)
    hash_target_digest = sha256(hash_target_component)

    # Secondary candidate: latest singleton serial for each bay before PTW-417.
    latest_by_bay = {}
    for permit, rows in by_permit.items():
        row = rows[0]
        bay = row["bay"]
        if bay not in latest_by_bay or permit > latest_by_bay[bay][0]:
            latest_by_bay[bay] = (permit, row)
    assert set(latest_by_bay) == set("ABCD")

    latest_blocks = {}
    for order in ("ABCD", "BDAC"):
        component = b"".join(serial_bytes(latest_by_bay[bay][1]) for bay in order)
        predicted_payload = xor16(component, mask)
        latest_blocks[order] = {
            "permits": [latest_by_bay[bay][0] for bay in order],
            "component": component.hex().upper(),
            "component_sha256": sha256(component),
            "predicted_payload": predicted_payload.hex().upper(),
            "payload_matches_selected": predicted_payload == selected_payload,
        }

    assert raw_target_payload != selected_payload
    assert raw_target_digest != K04_SHA256
    assert hash_target_payload != selected_payload
    assert hash_target_digest != K04_SHA256
    assert all(v["component_sha256"] != K04_SHA256
               and not v["payload_matches_selected"] for v in latest_blocks.values())

    print("SOURCE_PINS=PASS")
    print("PTW_SINGLETONS=27; PS_SAME_SUFFIX_SINGLETON_PACKETS=27")
    print("PREDECESSOR_CONTROLS=23; RAW_COMPONENT_XOR_MASK_HITS=0")
    print("PREDECESSOR_CONTROLS=23; RAW_UNMASKED_PAYLOAD_HITS=0")
    print("PREDECESSOR_CONTROLS=23; SHA256_PIPE_COMPONENT_XOR_MASK_HITS=0")
    print("RAW_ORIENTATIONS=4; SYNTHETIC_POSITIVE_CONTROL=PASS")
    print(f"PS0417_SELECTED_ACK2={selected_payload.hex().upper()}")
    print(f"PTW413_416_RAW_COMPONENT={raw_target_component.hex().upper()}")
    print(f"PTW413_416_PREDICTED_PAYLOAD={raw_target_payload.hex().upper()}")
    print(f"PTW413_416_COMPONENT_SHA256={raw_target_digest}")
    print(f"PTW413_416_SHA256_PIPE_COMPONENT={hash_target_component.hex().upper()}")
    print(f"PTW413_416_SHA256_PIPE_PREDICTED_PAYLOAD={hash_target_payload.hex().upper()}")
    print(f"PTW413_416_SHA256_PIPE_COMPONENT_SHA256={hash_target_digest}")
    print(f"OFFICIAL_K04_SHA256={K04_SHA256}")
    print("LATEST_PER_BAY_CANDIDATES=" + json.dumps(latest_blocks, sort_keys=True))
    print("K04_RECOVERY=NO_HIT")


if __name__ == "__main__":
    main()
