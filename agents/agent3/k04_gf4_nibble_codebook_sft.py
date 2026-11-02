"""H-17 selected spool coupon: entire 4-bit affine recoding channel, read-only.

Hypothesis: a global invertible hex-nibble remapping has changed many observed
bytes before/after the K04 route mask. The original archive does not attest
this copy fault. The code tests every invertible GF(2)^4 linear map and offset.
"""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def rank4(rows):
    rows = list(rows)
    rank = 0
    for bit in range(3, -1, -1):
        pivot = next((i for i in range(rank, 4) if rows[i] & (1 << bit)), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(4):
            if i != rank and rows[i] & (1 << bit):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def table(rows, offset):
    return [offset ^ sum(((value & row).bit_count() % 2) << bit
                         for bit, row in enumerate(rows)) for value in range(16)]


def transcode(raw, lookup):
    return bytes(lookup[value >> 4] * 16 + lookup[value & 15] for value in raw)


def xor(left, right):
    return bytes(a ^ b for a, b in zip(left, right))


def main():
    source = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    records = {}
    for line in source.decode("ascii").splitlines():
        fields = dict(part.split("=", 1) for part in line.split() if "=" in part)
        if {"JOB", "CLASS", "ATTEMPT", "STATE", "PAYLOAD"} <= fields.keys():
            identity = tuple(fields[field] for field in ("JOB", "CLASS", "ATTEMPT", "STATE"))
            records[identity] = bytes.fromhex(fields["PAYLOAD"])
    selected = records[("PS-261003-0417", "RECOVER", "2", "ACK")]
    assert selected.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"

    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    original_mask = bytes.fromhex(route["K04"]["masked_component"])
    target = bytes.fromhex(json.loads((ROOT / "acceptance.json").read_text())
                           ["slot_sha256"]["K04"])

    plant = table((1, 3, 5, 8), 5)
    assert rank4((1, 3, 5, 8)) == 4
    synthetic = hashlib.sha256(xor(transcode(selected, plant), original_mask)).digest()
    count = controls = 0
    matches = []
    for rows in itertools.product(range(16), repeat=4):
        if rank4(rows) != 4:
            continue
        for shift in range(16):
            lookup = table(rows, shift)
            copied = transcode(selected, lookup)
            masked = transcode(original_mask, lookup)
            for stage, candidate in (
                ("payload", xor(copied, original_mask)),
                ("mask", xor(selected, masked)),
                ("both", xor(copied, masked)),
            ):
                digest = hashlib.sha256(candidate).digest()
                count += 1
                if digest == synthetic and stage == "payload":
                    controls += 1
                    assert rows == (1, 3, 5, 8) and shift == 5
                if digest == target:
                    matches.append((stage, rows, shift, candidate.hex().upper()))
    assert count == 967680 and controls == 1

    # Independent source check on whether a single nibble codebook could
    # translate complete intact records across two same-job handoffs.
    conflicts = {}
    for job, before, after in (
        ("PS-261003-0417", ("LABEL", "1", "ACK"), ("RECOVER", "1", "REQUESTED")),
        ("PS-261003-0420", ("STORES", "1", "ACK"), ("RECOVER", "2", "ACK")),
    ):
        first = records[(job, *before)].hex().upper()
        second = records[(job, *after)].hex().upper()
        seen = {}
        wrong = 0
        for old, new in zip(first, second):
            if old in seen and seen[old] != new:
                wrong += 1
            else:
                seen[old] = new
        conflicts[job] = wrong
    assert conflicts == {"PS-261003-0417": 19, "PS-261003-0420": 17}

    print(json.dumps({
        "original_source_sha256": SPOOL_SHA,
        "channel": "all invertible 4-bit GF(2) affine nibble remappings",
        "tested": count,
        "synthetic_positive": controls,
        "original_commitment_matches": matches,
        "independent_same_job_codebook_conflicts": conflicts,
        "interpretation": "Hypothetical channel rejected, no recovered K04 bit",
    }, indent=2))


if __name__ == "__main__":
    main()
