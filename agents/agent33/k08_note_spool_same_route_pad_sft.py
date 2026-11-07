#!/usr/bin/env python3
"""Test a source-motivated same-queue pad hypothesis for K08.

The hypothesis is conditional on the inferred Nxx -> PS-261003-(0300+N)
crosswalk and on N18/N23 sharing one RECOVER/store output transform.
This script never reads the selected K04 payload.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

EXPECTED = {
    "notes": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "spool": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "route": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
EXPECTED_N18_HMAC16 = "A3100AE1ABB9C8D58315D9EBF326978B"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def read_note(notes_text: str, note_id: str) -> str:
    lines = notes_text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(note_id + " /"):
            body = []
            for following in lines[index + 1:]:
                if re.match(r"N\d{2} /", following):
                    break
                if following.strip():
                    body.append(following.strip())
            if not body:
                raise AssertionError(f"{note_id} has no body")
            return " ".join(body)
    raise AssertionError(f"{note_id} not found")


def spool_row(spool_text: str, suffix: int) -> tuple[int, str, str, bytes, str, int]:
    job = f"PS-261003-{suffix:04d}"
    pattern = re.compile(
        rf"JOB={job} ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) "
        rf"PAYLOAD=([0-9A-F]{{32}}) DEST=(\S+)"
    )
    found = []
    for line_number, line in enumerate(spool_text.splitlines(), 1):
        match = pattern.search(line)
        if match:
            attempt, state, job_class, payload, dest = match.groups()
            found.append(
                (int(attempt), state, job_class, bytes.fromhex(payload), dest, line_number)
            )
    if len(found) != 1:
        raise AssertionError(f"{job}: expected one row, found {len(found)}")
    attempt, state, job_class, payload, dest, line_number = found[0]
    return attempt, state, job_class, payload, dest, line_number


def permutation(name: str) -> tuple[int, ...]:
    if name == "identity":
        return tuple(range(16))
    if name == "reverse_words":
        return tuple(range(12, 16)) + tuple(range(8, 12)) + tuple(range(4, 8)) + tuple(range(0, 4))
    if name == "reverse_bytes_in_words":
        return tuple(word * 4 + byte for word in range(4) for byte in (3, 2, 1, 0))
    if name == "reverse_all":
        return tuple(reversed(range(16)))
    raise ValueError(name)


def permute(data: bytes, order: tuple[int, ...]) -> bytes:
    return bytes(data[index] for index in order)


def unpermute(data: bytes, order: tuple[int, ...]) -> bytes:
    result = bytearray(16)
    for output_index, input_index in enumerate(order):
        result[input_index] = data[output_index]
    return bytes(result)


def recover_xor(known_hmac: bytes, known_payload: bytes, target_payload: bytes,
                order: tuple[int, ...]) -> bytes:
    h = permute(known_hmac, order)
    known = permute(known_payload, order)
    target = permute(target_payload, order)
    pad = bytes(a ^ b for a, b in zip(known, h))
    return unpermute(bytes(a ^ b for a, b in zip(target, pad)), order)


def recover_add128(known_hmac: bytes, known_payload: bytes, target_payload: bytes,
                   order: tuple[int, ...], endian: str) -> bytes:
    h = permute(known_hmac, order)
    known = permute(known_payload, order)
    target = permute(target_payload, order)
    offset = (int.from_bytes(known, endian) - int.from_bytes(h, endian)) % (1 << 128)
    recovered = (int.from_bytes(target, endian) - offset) % (1 << 128)
    return unpermute(recovered.to_bytes(16, endian), order)


def recover_add_bytewise(known_hmac: bytes, known_payload: bytes, target_payload: bytes,
                         order: tuple[int, ...]) -> bytes:
    h = permute(known_hmac, order)
    known = permute(known_payload, order)
    target = permute(target_payload, order)
    offset = bytes((a - b) & 0xFF for a, b in zip(known, h))
    recovered = bytes((a - b) & 0xFF for a, b in zip(target, offset))
    return unpermute(recovered, order)


def synthetic_controls(nonce: bytes) -> int:
    known = hmac.new(nonce, b"known commissioning label", hashlib.sha256).digest()[:16]
    target = hmac.new(nonce, b"synthetic final caption", hashlib.sha256).digest()[:16]
    checked = 0
    for layout in ("identity", "reverse_words", "reverse_bytes_in_words", "reverse_all"):
        order = permutation(layout)
        h = permute(known, order)
        t = permute(target, order)
        pad = bytes(range(0x30, 0x40))
        p_known = bytes(a ^ b for a, b in zip(h, pad))
        p_target = bytes(a ^ b for a, b in zip(t, pad))
        assert recover_xor(known, unpermute(p_known, order), unpermute(p_target, order), order) == target
        checked += 1

        for endian in ("big", "little"):
            offset = 0x102132435465768798A9BACBDCEDFE0F
            p_known_i = (int.from_bytes(h, endian) + offset) % (1 << 128)
            p_target_i = (int.from_bytes(t, endian) + offset) % (1 << 128)
            p_known_b = p_known_i.to_bytes(16, endian)
            p_target_b = p_target_i.to_bytes(16, endian)
            recovered = recover_add128(
                known, unpermute(p_known_b, order), unpermute(p_target_b, order), order, endian
            )
            assert recovered == target
            checked += 1

        byte_offset = bytes(range(16))
        p_known_b = bytes((a + b) & 0xFF for a, b in zip(h, byte_offset))
        p_target_b = bytes((a + b) & 0xFF for a, b in zip(t, byte_offset))
        recovered = recover_add_bytewise(
            known, unpermute(p_known_b, order), unpermute(p_target_b, order), order
        )
        assert recovered == target
        checked += 1
    return checked


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
    evidence = root / "resources" / "evidence"
    files = {
        "notes": evidence / "crew" / "noticeboard-and-desk-notes.txt",
        "spool": evidence / "print" / "spool-reconstruction.log",
        "route": evidence / "recovery-routing.json",
        "acceptance": root / "resources" / "acceptance.json",
    }
    raw = {name: path.read_bytes() for name, path in files.items()}
    for name, data in raw.items():
        actual = digest(data)
        if actual != EXPECTED[name]:
            raise AssertionError(f"{name} SHA256 mismatch: {actual}")

    notes_text = raw["notes"].decode("utf-8")
    spool_text = raw["spool"].decode("utf-8")
    route = json.loads(raw["route"])
    acceptance = json.loads(raw["acceptance"])
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target_commitment = acceptance["slot_sha256"]["K08"]

    n18_text = read_note(notes_text, "N18")
    n23_text = read_note(notes_text, "N23")
    if ":" not in n18_text:
        raise AssertionError("N18 role label is missing")
    if "margin" not in n23_text.lower() or "envelope" not in n23_text.lower():
        raise AssertionError("N23 is no longer the expected margin/envelope locator")
    n18_phrase = n18_text.split(":", 1)[1].strip()
    h18 = hmac.new(nonce, normalize(n18_phrase).encode("utf-8"), hashlib.sha256).digest()[:16]
    if h18.hex().upper() != EXPECTED_N18_HMAC16:
        raise AssertionError("N18 HMAC16 control mismatch")

    # The note-to-job relation is a hypothesis. Assert only the observed
    # matching fields and retain the crosswalk's non-authenticated status.
    n18_row = spool_row(spool_text, 318)
    n23_row = spool_row(spool_text, 323)
    for label, row in (("N18/0318", n18_row), ("N23/0323", n23_row)):
        attempt, state, job_class, payload, dest, line_number = row
        if (attempt, state, job_class, dest) != (1, "ACK", "RECOVER", "store"):
            raise AssertionError(f"{label}: unexpected selector tuple")
        if len(payload) != 16:
            raise AssertionError(f"{label}: payload length mismatch")

    p18 = n18_row[3]
    p23 = n23_row[3]
    operations = []
    for layout in ("identity", "reverse_words", "reverse_bytes_in_words", "reverse_all"):
        order = permutation(layout)
        operations.append(("xor", layout, recover_xor(h18, p18, p23, order)))
        for endian in ("big", "little"):
            operations.append(
                (f"add128-{endian}", layout, recover_add128(h18, p18, p23, order, endian))
            )
        operations.append(("add-bytewise", layout, recover_add_bytewise(h18, p18, p23, order)))

    hits = []
    for operation, layout, candidate in operations:
        candidate_hash = digest(candidate)
        match = candidate_hash == target_commitment
        print(
            f"MODEL operation={operation} layout={layout} "
            f"candidate={candidate.hex().upper()} sha256={candidate_hash} "
            f"match={'YES' if match else 'NO'}"
        )
        if match:
            hits.append((operation, layout, candidate.hex().upper()))

    control_count = synthetic_controls(nonce)
    if control_count != 16:
        raise AssertionError(f"expected 16 synthetic controls, got {control_count}")
    print(
        "SUMMARY N18_JOB=0318 N23_JOB=0323 "
        f"N18_HMAC16={h18.hex().upper()} "
        f"N18_PAYLOAD={p18.hex().upper()} N23_PAYLOAD={p23.hex().upper()} "
        f"MODELS={len(operations)} HITS={len(hits)} "
        f"SYNTHETIC_CONTROLS={control_count}/16"
    )
    print(
        "LIMIT: conditional on inferred note/job crosswalk and a shared "
        "RECOVER/store transport; ACK does not authenticate payload integrity."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
