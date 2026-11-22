"""Reproduce the four source-derived complete K04 templates.

Selected PS-0417 ACK2 copied payload is excluded before parsing. This source-only
reproducer validates the fixed components searched in k04_mt_threeword_free32_scan.cpp,
without redundantly executing each 2^32 residual.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
K04_TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
EXPECTED = {
    (45, 98, 0, 0): "9B1222B432AD70512F49799500000000",
    (45, 98, 0, 1): "9E3499EAD038B488FA2D93C900000000",
    (45, 98, 1, 0): "000000007F044D86F6FFED6FDD40AD4E",
    (45, 98, 1, 1): "000000007A22F6D8146A29B608244712",
}


def unright(x, step):
    result = x
    for _ in range(5):
        result = x ^ (result >> step)
    return result & 0xFFFFFFFF


def unleft(x, step, mask):
    result = x
    for _ in range(5):
        result = x ^ ((result << step) & mask)
    return result & 0xFFFFFFFF


def untemper(x):
    return unright(unleft(unleft(unright(x, 18), 15, 0xEFC60000), 7, 0x9D2C5680), 11)


def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    return (x ^ (x >> 18)) & 0xFFFFFFFF


def twist(a, b):
    w = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (w >> 1) ^ (0x9908B0DF if (b & 1) else 0)


def source(path):
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    lines = [line for line in raw.decode("ascii").splitlines() if line and not line.startswith("#")]
    assert len(lines) == 133
    assert all(x in lines[129] for x in (
        "JOB=PS-261003-0417", "STATE=ACK", "ATTEMPT=2", "CLASS=RECOVER"))
    parsed = []
    for index, line in enumerate(lines):
        if index == 129:
            parsed.append(None)
            continue
        match = re.search(r"\bPAYLOAD=([0-9A-F]{32})\b", line)
        assert match, index
        blob = bytes.fromhex(match.group(1))
        parsed.append(tuple(untemper(int.from_bytes(blob[4*i:4*(i+1)], "little"))
                            for i in range(4)))
    return parsed


def main():
    spool = ROOT / "resources/evidence/print/spool-reconstruction.log"
    route = ROOT / "resources/evidence/recovery-routing.json"
    acceptance = ROOT / "resources/acceptance.json"
    assert hashlib.sha256(route.read_bytes()).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(acceptance.read_bytes()).hexdigest() == ACCEPT_SHA
    assert bytes.fromhex(json.loads(route.read_text())["K04"]["masked_component"]) == MASK
    assert json.loads(acceptance.read_text())["slot_sha256"]["K04"] == K04_TARGET
    for x in (0, 1, 0xDEADBEEF, 0xFFFFFFFF):
        assert untemper(temper(x)) == x
    native = source(spool)
    for (r, k, first_lane, middle_lane), expected in EXPECTED.items():
        bits = bytearray(16)
        for offset in range(3):
            at = first_lane + offset
            x = native[k][middle_lane+offset] ^ twist(
                native[r][offset], native[r][offset+1])
            raw = temper(x).to_bytes(4, "little")
            bits[4*at:4*(at+1)] = bytes(
                a ^ b for a, b in zip(raw, MASK[4*at:4*(at+1)]))
        assert bits.hex().upper() == expected
        missing = 3 if first_lane == 0 else 0
        print("TEMPLATE", f"r{r}_k{k}_q{first_lane}_i{middle_lane}",
              expected, "FREE_WORD", missing)
        planted = bytearray(bits)
        planted[4*missing:4*(missing+1)] = (0x17C0FFEE).to_bytes(4, "little")
        assert hashlib.sha256(planted).hexdigest() != K04_TARGET
    print("SOURCE_PASS selected_ACK2_payload_excluded templates=4 "
          "fixed_words_per_template=3 each_residual=2^32")


if __name__ == "__main__":
    main()
