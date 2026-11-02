"""H-17 K04: four same-job buffers, freely reassembled 32-bit words (read-only).

Usage: python agents/agent9/k04_fourbuff_word_sft.py h17-archive-dump.zip
Unlike the prior three-RECOVER-buffer experiment, this adds the earlier
0417 LABEL ACK to the source word pool. Original source/commitment unchanged.
"""
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def search(path: Path):
    with ZipFile(path) as z:
        spool = z.read("evidence/print/spool-reconstruction.log")
        route = json.loads(z.read("evidence/recovery-routing.json"))
        inventory = json.loads(z.read("acceptance.json"))
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    lines = [s for s in spool.decode().splitlines()
             if "JOB=PS-261003-0417 " in s]
    assert len(lines) == 4
    stages = [(re.search(r"CLASS=(\w+)", s).group(1),
               re.search(r"STATE=(\w+)", s).group(1),
               re.search(r"ATTEMPT=(\d+)", s).group(1)) for s in lines]
    assert stages == [
        ("LABEL", "ACK", "1"),
        ("RECOVER", "REQUESTED", "1"),
        ("RECOVER", "ACK", "2"),
        ("RECOVER", "REQUESTED", "3")]
    payloads = [bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", s).group(1))
                for s in lines]
    words = [p[i:i+4] for p in payloads for i in range(0, 16, 4)]
    options = words + [w[::-1] for w in words]
    assert len(options) == len(set(options)) == 32
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = bytes.fromhex(inventory["slot_sha256"]["K04"])
    assert hashlib.sha256(bytes(a ^ b for a, b in zip(payloads[2], mask))).digest() != target
    frozen_positive = (21, 1, 14, 27)
    planted = b"".join(options[i] for i in frozen_positive)
    expected = bytes(a ^ b for a, b in zip(planted, mask))
    positive_digest = hashlib.sha256(expected).digest()
    by_slot = [[bytes(a ^ b for a, b in zip(w, mask[4*j:4*j+4]))
                for w in options] for j in range(4)]
    count = 0
    real_hits = []
    positive_hits = []
    for a, b, c, d in itertools.product(range(32), repeat=4):
        count += 1
        coupon = by_slot[0][a] + by_slot[1][b] + by_slot[2][c] + by_slot[3][d]
        digest = hashlib.sha256(coupon).digest()
        if digest == target:
            real_hits.append((a, b, c, d, coupon.hex().upper()))
        if digest == positive_digest:
            positive_hits.append((a, b, c, d, coupon.hex().upper()))
    assert count == 1048576
    assert positive_hits == [(*frozen_positive, expected.hex().upper())]
    print("spool_sha256", SPOOL_SHA)
    print("unique_source_32bit_fragments", len(options))
    print("source_order", stages)
    print("tested_assignments", count)
    print("synthetic_exact_hit", len(positive_hits))
    print("real_original_commitment_hits", len(real_hits))
    for hit in real_hits:
        print("K04_CANDIDATE", hit)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python k04_fourbuff_word_sft.py original.zip")
    search(Path(sys.argv[1]))
