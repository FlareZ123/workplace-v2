"""H-17 K04: exact backward-MT pair-of-original-printer-packets hypothesis.

Source SHA, coupon route, and target commitment are immutable. The selected copied
ACK2 bytes are never opened. Run from repository checkout with Python standard library.
"""
from pathlib import Path
import hashlib
import json
import re
import random

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
U = 0xFFFFFFFF
MAG = 0x9908B0DF
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def untemper(x: int) -> int:
    x ^= x >> 18
    x ^= (x << 15) & 0xEFC60000
    previous = x
    for _ in range(6):
        x = previous ^ ((x << 7) & 0x9D2C5680)
    previous = x
    for _ in range(6):
        x = previous ^ (x >> 11)
    return x & U

def temper(x: int) -> int:
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & U

def twist(a: int, b: int) -> int:
    value = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (value >> 1) ^ (MAG if b & 1 else 0)

def predict(a: list[int], b: list[int], predecessor_msb: int) -> bytes:
    words = [
        b[i] ^ twist((predecessor_msb << 31) if i == 0 else a[i-1], a[i])
        for i in range(4)
    ]
    return b"".join(temper(x).to_bytes(4, "little") for x in words)

def run() -> None:
    raw = (EVIDENCE / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    route = json.loads((EVIDENCE / "recovery-routing.json").read_text(encoding="utf-8"))
    accept = json.loads((ROOT / "resources" / "acceptance.json").read_text(encoding="utf-8"))
    mask = bytes.fromhex(route["K04"]["masked_component"])
    digest = accept["slot_sha256"]["K04"]
    lines = [x for x in raw.decode("ascii").splitlines() if x.startswith("2026-")]
    assert len(lines) == 133
    assert lines[129].startswith("2026-10-03T18:02:00Z")
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    prior = []
    for i, line in enumerate(lines[:129]):
        m = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert m is not None
        packet = bytes.fromhex(m[1])
        prior.append([untemper(int.from_bytes(packet[4*k:4*k+4], "little")) for k in range(4)])
    assert len(prior) == 129
    hits = []
    count = 0
    for i in range(len(prior)):
        for j in range(i + 1, len(prior)):
            for bit in (0, 1):
                packet = predict(prior[i], prior[j], bit)
                candidate = bytes(x ^ y for x, y in zip(packet, mask))
                count += 1
                if hashlib.sha256(candidate).hexdigest() == digest:
                    hits.append((i, j, bit, candidate.hex().upper()))
    assert count == 16512
    assert not hits, hits
    print("ORIGINAL 8256 ordered chronological pairs; 16512 complete K04 components; 0 PASS")

    # Seven independently seeded true MT streams: withhold all four target draws.
    for seed in (0, 1, 7, 23, 99, 5489, 0xABCDEF12):
        rng = random.Random(seed)
        observed = [rng.getrandbits(32) for _ in range(1200)]
        q = 951
        a = [untemper(v) for v in observed[q-623:q-619]]
        b = [untemper(v) for v in observed[q-227:q-223]]
        bit = untemper(observed[q-624]) >> 31
        truth = b"".join(v.to_bytes(4, "little") for v in observed[q:q+4])
        assert predict(a, b, bit) == truth
        assert predict(a, b, bit ^ 1) != truth
    print("GENUINE WITHHELD FOUR-WORD PRODUCER CONTROLS 7/7 PASS")

if __name__ == "__main__":
    run()
