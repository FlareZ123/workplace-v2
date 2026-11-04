"""H-17 K04 serial differential/Gray-code readback probe; historical files read-only."""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(os.getenv("H17_SOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
SPOOL_PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ACK = "A9A9DC5731A5E2AE879C47215C2559D5"
MASK = "8556C8CB6140A7F9A5123AC7571BEE1C"
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

def to_bits(data: bytes, lsb: bool) -> list[int]:
    return [(byte >> shift) & 1 for byte in data
            for shift in (range(8) if lsb else range(7, -1, -1))]

def from_bits(data: list[int], lsb: bool) -> bytes:
    return bytes(sum(bit << shift for shift, bit in
                 zip((range(8) if lsb else range(7, -1, -1)), data[i:i+8]))
                 for i in range(0, len(data), 8))

def codec(data: bytes, group: int, lag: int, lsb: bool,
          reverse: bool, inverse: bool, seed: int) -> bytes:
    inp = to_bits(data, lsb)
    out = [0] * len(inp)
    for start in range(0, len(inp), group * 8):
        x = inp[start:start+group*8]
        if reverse:
            x = x[::-1]
        y = [0] * len(x)
        for i, v in enumerate(x):
            prev = (y if inverse else x)[i-lag] if i >= lag else seed
            y[i] = v ^ prev
        if reverse:
            y.reverse()
        out[start:start+group*8] = y
    return from_bits(out, lsb)

def bxor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def run() -> None:
    spool = ROOT / "evidence/print/spool-reconstruction.log"
    assert hashlib.sha256(spool.read_bytes()).hexdigest() == SPOOL_PIN
    selected = [line for line in spool.read_text().splitlines()
                if "JOB=PS-261003-0417" in line and "ATTEMPT=2" in line
                and "STATE=ACK" in line and "CLASS=RECOVER" in line]
    assert len(selected) == 1
    assert re.search(r"PAYLOAD=([0-9A-F]{32})", selected[0]).group(1) == ACK
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    assert route["K04"]["masked_component"] == MASK
    assert acceptance["slot_sha256"]["K04"] == TARGET
    ack, mask = bytes.fromhex(ACK), bytes.fromhex(MASK)
    target = bytes.fromhex(TARGET)
    produced = {s: set() for s in ("payload", "mask", "component")}
    attempts = {s: 0 for s in produced}
    planted = bxor(codec(ack, 4, 3, True, True, True, 1), mask)
    planted_hash = hashlib.sha256(planted).digest()
    positive, hits = 0, []
    for group in (1, 2, 4, 8, 16):
        for lag in range(1, 8):
            for lsb in (False, True):
                for reverse in (False, True):
                    for inverse in (False, True):
                        for seed in (0, 1):
                            params = (group, lag, lsb, reverse, inverse, seed)
                            for stage in produced:
                                if stage == "payload":
                                    candidate = bxor(codec(ack, *params), mask)
                                elif stage == "mask":
                                    candidate = bxor(ack, codec(mask, *params))
                                else:
                                    candidate = codec(bxor(ack, mask), *params)
                                attempts[stage] += 1
                                produced[stage].add(candidate)
                                digest = hashlib.sha256(candidate).digest()
                                if digest == target:
                                    hits.append((stage, params, candidate.hex()))
                                if stage == "payload" and digest == planted_hash:
                                    positive += 1
    assert attempts == {"payload": 560, "mask": 560, "component": 560}
    assert positive == 2
    assert not hits, hits
    assert len(set.union(*produced.values())) == 1408
    print(json.dumps({"original_hits": hits, "assignments": attempts,
                      "unique_per_stage": {s: len(v) for s, v in produced.items()},
                      "unique_global": len(set.union(*produced.values())),
                      "planted_positive_hits": positive}, indent=2))

if __name__ == "__main__":
    run()
