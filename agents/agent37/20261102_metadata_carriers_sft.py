"""Bounded, read-only K04 metadata-carrier recovery probe (2026-11-02).

Source: exact 128 ordinary PS-261003-0300..0427 printer rows.
Hypotheses: one metadata-dependent bit per row, or a 16-byte summary of
previous ordinary payloads selected by an arbitrary CLASS x DEST truth table.
No claim that either was a historical printer encoding.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROW = re.compile(r"JOB=PS-261003-(\d{4}).*?STATE=ACK CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)")
CLASSES = ("LABEL", "STORES", "RECOVER")
DESTS = ("store", "desk", "bench")


def xor(*values: bytes) -> bytes:
    return bytes([sum(((v[i] >> k) & 1) for v in values) % 2
                  for i in range(16) for k in []]) if False else bytes(
        __import__("functools").reduce(int.__xor__, (v[i] for v in values), 0)
        for i in range(16))


def main() -> None:
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = []
    for i, line in enumerate(raw.decode("ascii").splitlines()[1:129]):
        m = ROW.search(line)
        assert m is not None and "+00:00 JOB=" in line
        job, klass, payload, dest = m.groups()
        assert int(job) == 300 + i
        cell = 3 * CLASSES.index(klass) + DESTS.index(dest)
        rows.append((cell, bytes.fromhex(payload)))
    assert len(rows) == 128
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    ack = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
    controls = (
        bytes.fromhex("234BE186E97EE05830909790E336109E"),
        bytes.fromhex("432475F72A62DB39F3D5693E2C937FA4"),
    )
    checks = 0
    matches = []
    heldout_matches = []
    synthetic_bit = False
    synthetic_aggregate = False

    def try_coupon(coupon: bytes, model: str, params: tuple) -> None:
        nonlocal checks
        for mode, key in (("coupon", xor(coupon, mask)),
                          ("component", coupon),
                          ("correction", xor(coupon, ack, mask))):
            checks += 1
            if hashlib.sha256(key).digest() == target:
                matches.append((model, params, mode, key.hex().upper()))

    for table in range(512):
        bits = [(table >> cell) & 1 for cell, _ in rows]
        for reverse in (False, True):
            ordered = bits[::-1] if reverse else bits
            for msb in (False, True):
                coupon = bytes(sum(bit << (7-j if msb else j)
                                   for j, bit in enumerate(ordered[i:i+8]))
                               for i in range(0, 128, 8))
                if table == 7 and not reverse and msb:
                    control = bytes(sum(((7 >> cell) & 1) << (7-j)
                                        for j, (cell, _) in enumerate(rows[i:i+8]))
                                    for i in range(0, 128, 8))
                    synthetic_bit = hashlib.sha256(xor(coupon, mask)).digest() == hashlib.sha256(xor(control, mask)).digest()
                try_coupon(coupon, "one-bit", (table, reverse, msb))

        if table == 0:
            continue
        group = [payload for cell, payload in rows if table & (1 << cell)]
        if not group:
            continue
        data = b"".join(group)
        byte_sum = bytes(sum(p[i] for p in group) & 255 for i in range(16))
        grouped = {
            "xor": xor(*group),
            "sum": byte_sum,
            "md5": hashlib.md5(data).digest(),
            "sha256-first": hashlib.sha256(data).digest()[:16],
            "sha256-last": hashlib.sha256(data).digest()[16:],
            "blake2s": hashlib.blake2s(data, digest_size=16).digest(),
        }
        for algorithm, coupon in grouped.items():
            if table == 1 and algorithm == "xor":
                control = xor(*(p for c,p in rows if c == 0))
                synthetic_aggregate = hashlib.sha256(xor(control, mask)).digest() == hashlib.sha256(xor(coupon, mask)).digest()
            for index, known in enumerate(controls):
                if coupon == known:
                    heldout_matches.append((table, algorithm, index))
            try_coupon(coupon, "group-summary", (table, algorithm))

    assert synthetic_bit and synthetic_aggregate
    assert checks == 6144 + 9198
    print(json.dumps({
        "original_spool_sha256": SOURCE_SHA,
        "ordinary_rows": len(rows),
        "metadata_truth_tables": 512,
        "group_truth_tables": 511,
        "summary_algorithms": 6,
        "reduction_paths": 3,
        "all_checked": checks,
        "synthetic_positive_controls": 2,
        "late_RECOVER_group_summary_hits": heldout_matches,
        "original_K04_commitment_hits": matches,
    }, indent=2))


if __name__ == "__main__":
    main()
