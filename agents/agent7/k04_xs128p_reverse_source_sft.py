#!/usr/bin/env python3
"""Invert the later K04 request to recover full earlier xorshift128+ coupons.

Reuses the source-pinned forward test's complete 2^26 native inverter.
Only the original 18:03 REQUESTED packet is fitted. The original 18:02
ACK2 copied payload is excluded. Predict x2/x3 via inverse transitions,
check unmodified K04 commitment, then check 18:01 as independent holdout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

from k04_xs128p_source_sft import read_original, find_selected_job, invert, step, MOD

MASK64 = MOD - 1


def reverse(l: int, r: int) -> tuple[int, int]:
    s = r ^ l ^ (l >> 26)
    v = s ^ (s >> 17) ^ (s >> 34) ^ (s >> 51)
    old_a = v ^ (v << 23 & MASK64) ^ (v << 46 & MASK64)
    return old_a & MASK64, l


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--root", type=Path, default=Path("resources"))
    args = parser.parse_args()
    compiler = next((path for name in ("gcc", "clang", "cc")
                     if (path := shutil.which(name))), None)
    assert compiler is not None
    source_c = Path(__file__).with_name("k04_xs128p_inverse.c")
    rng = random.Random(20261123)
    for index in range(100000):
        a, b = rng.getrandbits(64), rng.getrandbits(64)
        assert reverse(*step(a, b)) == (a, b), index
    print("PLANTED: 100000 exact reverse-state transition controls PASS", flush=True)
    with tempfile.TemporaryDirectory(prefix="h17-xs128p-reverse-") as directory:
        binary = Path(directory, "inverse" + (".exe" if os.name == "nt" else ""))
        subprocess.run([
            compiler, "-O3", "-std=c11", "-o", str(binary), str(source_c)
        ], check=True)
        raw = read_original(args.bundle, args.root)
        route = json.loads(raw["evidence/recovery-routing.json"])
        acceptance = json.loads(raw["acceptance.json"])
        mask = bytes.fromhex(route["K04"]["masked_component"])
        target = acceptance["slot_sha256"]["K04"]
        requests = find_selected_job(raw["evidence/print/spool-reconstruction.log"])
        counts = []
        for endian in ("big", "little"):
            for swap in (False, True):
                def unpack(data: bytes) -> list[int]:
                    words = [int.from_bytes(data[i:i + 8], endian) for i in (0, 8)]
                    return list(reversed(words)) if swap else words

                def pack(words: list[int]) -> bytes:
                    arranged = list(reversed(words)) if swap else words
                    return b"".join(v.to_bytes(8, endian) for v in arranged)

                x0, x1 = unpack(requests[0])
                x4, x5 = unpack(requests[2])
                fitted = invert(binary, x4, x5)
                observations = []
                for state in fitted:
                    states = {4: (state["state_a"], state["state_b"])}
                    for index in (3, 2, 1, 0):
                        states[index] = reverse(*states[index + 1])
                    backwards = [(states[index][0] + states[index][1]) & MASK64
                                 for index in (0, 1, 2, 3)]
                    coupon = pack(backwards[2:4])
                    component = bytes(a ^ b for a, b in zip(coupon, mask))
                    observations.append({
                        "coupon_hex": coupon.hex().upper(),
                        "component_hex": component.hex().upper(),
                        "component_sha256": hashlib.sha256(component).hexdigest(),
                        "original_commitment_hit": hashlib.sha256(component).hexdigest() == target,
                        "first_REQUESTED_holdout_hit": backwards[:2] == [x0, x1],
                    })
                counts.append((len(fitted),
                               sum(c["original_commitment_hit"] for c in observations),
                               sum(c["first_REQUESTED_holdout_hit"] for c in observations)))
                print(json.dumps({
                    "fit": "18:03 REQUESTED", "endian": endian, "swap64": swap,
                    "models": len(fitted), "candidates": observations
                }, indent=2), flush=True)
        assert counts == [(1, 0, 0), (1, 0, 0), (0, 0, 0), (0, 0, 0)], counts
        print("ORIGINAL: 2 full backwards coupons, zero accepted; zero first-request holdouts", flush=True)


if __name__ == "__main__":
    main()
