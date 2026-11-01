"""Bounded original H-17 K04 retry-midpoint source hypothesis (Agent 25).

Run with the existing resources directory. The disputed attempt-2 copied payload
is deliberately excluded from the inputs. The source does not certify a
counter-like printer producer; NO_MATCH excludes only this tiny model.
"""
from __future__ import annotations

import configparser
from hashlib import sha256
import json
from pathlib import Path

MODULUS = 1 << 128
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def midpoints(first: bytes, third: bytes, endian: str) -> tuple[bytes, ...]:
    """Solve 2 * middle == first + third (mod 2**128)."""
    a = int.from_bytes(first, endian)
    c = int.from_bytes(third, endian)
    difference = (c - a) % MODULUS
    if difference & 1:
        return ()
    base = (a + difference // 2) % MODULUS
    return (
        base.to_bytes(16, endian),
        ((base + MODULUS // 2) % MODULUS).to_bytes(16, endian),
    )


def synthetic_controls() -> None:
    for endian in ("big", "little"):
        for mid, step in ((1234567890123456789, 1), (MODULUS - 7, 9)):
            first = ((mid - step) % MODULUS).to_bytes(16, endian)
            third = ((mid + step) % MODULUS).to_bytes(16, endian)
            assert mid.to_bytes(16, endian) in midpoints(first, third, endian)
        assert midpoints((0).to_bytes(16, endian),
                         (1).to_bytes(16, endian), endian) == ()
    print("SYNTHETIC_CONTROLS=6/6 PASS")


def main(root: Path) -> None:
    synthetic_controls()
    spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(spool).hexdigest() == SPOOL_HASH

    labels = configparser.ConfigParser()
    labels.read(root / "evidence/archive-labels.ini", encoding="utf-8")
    job = labels["printer_routes_2026-09-01_to_2026-10-03"]["ESC-N"]
    records: dict[int, bytes] = {}
    for line in spool.decode("ascii").splitlines():
        if not line.startswith("2026-10-03"):
            continue
        timestamp, *tokens = line.split()
        fields = dict(token.split("=", 1) for token in tokens)
        if fields["JOB"] != job or fields["CLASS"] != "RECOVER":
            continue
        attempt = int(fields["ATTEMPT"])
        if attempt not in (1, 3):
            continue
        assert fields["STATE"] == "REQUESTED"
        assert timestamp == ("2026-10-03T18:01:00Z" if attempt == 1
                             else "2026-10-03T18:03:00Z")
        assert attempt not in records
        records[attempt] = bytes.fromhex(fields["PAYLOAD"])
    assert set(records) == {1, 3}
    assert all(len(value) == 16 for value in records.values())

    # Generate the full source-only candidate map before reading the target.
    proposals = {
        order: midpoints(records[1], records[3], order)
        for order in ("big", "little")
    }

    routes = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    mask = bytes.fromhex(routes["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    assert len(mask) == 16 and len(target) == 64

    found = []
    for order, values in proposals.items():
        print("SOURCE_MODEL", order, "candidates", len(values))
        for coupon in values:
            component = bytes(x ^ y for x, y in zip(coupon, mask))
            if sha256(component).hexdigest() == target:
                found.append((order, component.hex().upper()))
    print("ORIGINAL_K04_CANDIDATE_ASSIGNMENTS", sum(map(len, proposals.values())))
    print("ORIGINAL_K04_MATCHES", found)
    assert not found


if __name__ == "__main__":
    import sys

    main(Path(sys.argv[1]) if len(sys.argv) == 2
         else Path(__file__).resolve().parents[2] / "resources")
