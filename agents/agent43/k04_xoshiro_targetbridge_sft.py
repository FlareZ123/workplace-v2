"""H-17 xoshiro128** forward/backward full K04 coupon scan.

Run: python agents/agent43/k04_xoshiro_targetbridge_sft.py resources
Uses all 132 intact printer packets. The disputed selected ACK is excluded.
"""
import hashlib
import json
import re
import sys
from pathlib import Path
from k04_xoshiro_allpairs_sft import MASK, SOURCE_SHA, gf2_masks, output, recover, rol, ror, step

MAX_GAP = 4096


def back(state):
    aa, bb, cc, dd = state
    d1 = ror(dd, 11)
    a = aa ^ d1
    v = cc ^ bb
    b = (v ^ (v << 9) ^ (v << 18) ^ (v << 27)) & MASK
    return a, b, bb ^ b ^ a, d1 ^ b


def stream4(state):
    words = []
    for _ in range(4):
        words.append(output(state))
        state = step(state)
    return words


def component(words, endian, reverse, xor_mask):
    if reverse:
        words = words[::-1]
    payload = b"".join(word.to_bytes(4, endian) for word in words)
    return bytes(x ^ y for x, y in zip(payload, xor_mask))


def probe(initial, endian, reverse, xor_mask, digest, max_gap):
    forward = initial
    backward = initial
    for _ in range(4):
        forward = step(forward)
        backward = back(backward)
    fw, bw = stream4(forward), stream4(backward)
    tail = forward
    for _ in range(4):
        tail = step(tail)
    for gap in range(max_gap):
        if hashlib.sha256(component(fw, endian, reverse, xor_mask)).digest() == digest:
            return "forward", gap
        if hashlib.sha256(component(bw, endian, reverse, xor_mask)).digest() == digest:
            return "backward", gap
        forward = step(forward)
        fw = fw[1:] + [output(tail)]
        tail = step(tail)
        backward = back(backward)
        bw = [output(backward)] + bw[:3]
    return None


def run(root):
    source = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA
    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    xor_mask = bytes.fromhex(route["K04"]["masked_component"])
    digest = bytes.fromhex(acceptance["slot_sha256"]["K04"])

    packets = []
    for line in source.decode("ascii").splitlines():
        match = re.search(
            r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([A-F0-9]{32})",
            line,
        )
        if match is None:
            continue
        job, attempt, state, category, value = match.groups()
        if (job, attempt, state, category) == ("PS-261003-0417", "2", "ACK", "RECOVER"):
            continue
        packets.append(bytes.fromhex(value))
    assert len(packets) == 132

    seed = (0x1A2B3C4D, 0xC0FFEE01, 0xDEADBEEF, 0xFEE1DEAD)
    assert step(back(seed)) == seed
    assert back(step(seed)) == seed
    forward = seed
    for _ in range(4 + 378):
        forward = step(forward)
    planted = hashlib.sha256(component(stream4(forward), "little", False, xor_mask)).digest()
    assert probe(seed, "little", False, xor_mask, planted, 512) == ("forward", 378)
    backward = seed
    for _ in range(4 + 131):
        backward = back(backward)
    planted = hashlib.sha256(component(stream4(backward), "little", False, xor_mask)).digest()
    assert probe(seed, "little", False, xor_mask, planted, 512) == ("backward", 131)
    print("SYNTHETIC: state inverse, +378 and -131 complete-coupon recovery PASS")

    masks = gf2_masks()
    checks = 0
    for endian in ("little", "big"):
        for reverse in (False, True):
            matches = []
            for index, raw in enumerate(packets):
                words = [int.from_bytes(raw[k:k + 4], endian) for k in range(0, 16, 4)]
                if reverse:
                    words.reverse()
                state = recover(words, masks)
                result = probe(state, endian, reverse, xor_mask, digest, MAX_GAP)
                checks += 2 * MAX_GAP
                if result is not None:
                    matches.append((index, result))
            print(f"ORIGINAL: {endian=} {reverse=} sources=132 "
                  f"full-coupons={2 * MAX_GAP * 132} matches={matches}", flush=True)
            assert not matches
    assert checks == 4_325_376
    print(f"ORIGINAL: {checks} complete K04 commitment checks; zero accepted")
    print("Selected copied ACK excluded; no verified K04 byte claimed")


if __name__ == "__main__":
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
