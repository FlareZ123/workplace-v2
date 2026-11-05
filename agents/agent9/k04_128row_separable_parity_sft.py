"""H17 K04: 128 regular spool rows as a parity-coded 128-bit coupon.

Only standard library. Run with archive extraction directory as first argument.
Original material and acceptance are read-only.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
K04_SHA = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")


def main(root: Path) -> None:
    spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    route = (root / "evidence/recovery-routing.json").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(route).hexdigest() == ROUTE_SHA
    assert bytes.fromhex(json.loads(route)["K04"]["masked_component"]) == MASK
    lines = [s for s in spool.decode("ascii").splitlines() if "PAYLOAD=" in s]
    rows = []
    for job in range(300, 428):
        matched = [s for s in lines if f"JOB=PS-261003-{job:04d} " in s
                   and "ATTEMPT=1" in s and "STATE=ACK" in s]
        assert len(matched) == 1
        rows.append(bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", matched[0]).group(1)))
    assert len(rows) == 128

    # A column is the vector of its bit from all 128 ordered regular rows.
    cols = [[sum(((row[j] >> bit) & 1) << rowid
                 for rowid, row in enumerate(rows))
             for j in range(16)] for bit in range(8)]
    agg = [0] * 8
    lo = int.from_bytes(MASK, "little")
    hi = int.from_bytes(MASK, "big")

    # Planted full-digest positive from a nontrivial separable parity program.
    pb, pt = 0x3295, 0xB4
    pv = 0
    for b in range(8):
        for j in range(16):
            if (pb >> j) & 1 and (pt >> b) & 1:
                pv ^= cols[b][j]
    planted = hashlib.sha256((pv ^ hi).to_bytes(16, "big")).digest()

    real_hits = []
    planted_hits = []
    checks = 0
    prev_byte_mask = 0
    digest = hashlib.sha256
    for i in range(1, 65536):
        # Gray order permits one new byte lane per outer mask.
        byte_mask = i ^ (i >> 1)
        lane = (byte_mask ^ prev_byte_mask).bit_length() - 1
        prev_byte_mask = byte_mask
        for bit in range(8):
            agg[bit] ^= cols[bit][lane]

        parity_stream = 0
        prev_bit_mask = 0
        for q in range(1, 256):
            bit_mask = q ^ (q >> 1)
            bit = (bit_mask ^ prev_bit_mask).bit_length() - 1
            parity_stream ^= agg[bit]
            prev_bit_mask = bit_mask
            for view, candidate in enumerate((
                (parity_stream ^ lo).to_bytes(16, "little"),
                (parity_stream ^ hi).to_bytes(16, "big")
            )):
                d = digest(candidate).digest()
                checks += 1
                if d == K04_SHA:
                    real_hits.append((byte_mask, bit_mask, view, candidate.hex()))
                if d == planted:
                    planted_hits.append((byte_mask, bit_mask, view))
        if i % 8192 == 0:
            print("progress", i, checks, len(real_hits), flush=True)
    assert checks == 65535 * 255 * 2
    assert planted_hits == [(pb, pt, 1)], planted_hits
    print(json.dumps({"full_slot_checks": checks, "original_matches": real_hits,
                      "synthetic_matches": planted_hits}, sort_keys=True))
    assert not real_hits


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "resources"))
