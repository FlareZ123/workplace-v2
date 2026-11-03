"""K04 SFT: single-packet V8 xorshift128 byte-output inversion.

Original attempt 1 constrains four direct-output states. Scan complete
hypothetical attempt-2 coupons at offsets 16..8192, and independently
test attempt 3 at offsets 16..16384. Also test reversed-64 cache mode.
The disputed attempt-2 ACK is never read. This is a speculative producer
model, not a claim that the historical spool used V8.

Closest prior art: workplace-v1 agent49's two-buffer fixed-gap test.
Run: python agents/agent7/k04_v8_retry_lowrank_sft.py resources
Standard library only; original files unchanged.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

M = (1 << 64) - 1
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def step(a, b):
    x, y = a, b
    a = y
    x ^= (x << 23) & M
    x ^= x >> 17
    x ^= y
    x ^= y >> 26
    return a, x & M, (a >> 56) & 255

def outputs(state, count, reverse):
    a, b = state & M, state >> 64
    values = []
    n = (count + 63) // 64 * 64 if reverse else count
    for _ in range(n):
        a, b, byte = step(a, b)
        values.append(byte)
    if reverse:
        values = [byte for start in range(0, n, 64)
                  for byte in reversed(values[start:start + 64])]
    return bytes(values[:count])

def invert(observed, reverse):
    indices = list(range(63, 47, -1)) if reverse else list(range(16))
    columns = []
    for j in range(128):
        a = (1 << j) & M
        b = (1 << j) >> 64
        sample = []
        for _ in range(max(indices) + 1):
            a, b, byte = step(a, b)
            sample.append(byte)
        columns.append(sum(((sample[t] >> bit) & 1) << (8 * i + bit)
                           for i, t in enumerate(indices) for bit in range(8)))
    basis = {}
    for bit in range(128):
        row = sum(((col >> bit) & 1) << j for j, col in enumerate(columns))
        rhs = (observed[bit // 8] >> (bit % 8)) & 1
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row, rhs
                break
            oldrow, oldrhs = basis[pivot]
            row ^= oldrow
            rhs ^= oldrhs
        else:
            if rhs:
                return None, len(basis)
    free = [j for j in range(128) if j not in basis]
    states = []
    for selection in range(1 << len(free)):
        s = sum(1 << bit for k, bit in enumerate(free) if selection >> k & 1)
        for bit in sorted(basis):
            row, rhs = basis[bit]
            if ((row & s).bit_count() & 1) != rhs:
                s ^= 1 << bit
        assert outputs(s, 16, reverse) == observed
        states.append(s)
    return states, len(basis)

def original(root):
    source = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    attempts = {}
    for line in source.decode("ascii").splitlines():
        # Selection is strict and happens before reading any PAYLOAD.
        if "JOB=PS-261003-0417" not in line or "STATE=REQUESTED" not in line:
            continue
        for attempt, timestamp in (("1", "2026-10-03T18:01:00Z"),
                                   ("3", "2026-10-03T18:03:00Z")):
            if not line.startswith(timestamp) or f"ATTEMPT={attempt} " not in line:
                continue
            assert "CLASS=RECOVER" in line and "DEST=bench" in line
            attempts[attempt] = bytes.fromhex(
                re.search(r"PAYLOAD=([A-F0-9]{32})", line).group(1))
    assert set(attempts) == {"1", "3"}
    routes = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    assert routes["K04"]["source"].startswith("escrow coupon")
    return attempts["1"], attempts["3"], (
        bytes.fromhex(routes["K04"]["masked_component"]),
        bytes.fromhex(acceptance["slot_sha256"]["K04"]))

def main(root):
    for reverse in (False, True):
        for seed in (1, 0x1234567890ABCDEF0123456789ABCDEF, (1 << 128) - 1):
            sample = outputs(seed, 16, reverse)
            states, rank = invert(sample, reverse)
            assert rank == 126 and seed in states and len(states) == 4
    print("SYNTHETIC_STATE_INVERSION 6/6 PASS")

    first, third, (mask, commitment) = original(root)
    for reverse in (False, True):
        states, rank = invert(first, reverse)
        label = "reverse_64_cache" if reverse else "direct_high_byte"
        if states is None:
            print(label, "first_packet_INCONSISTENT", "rank_to_failure", rank)
            continue
        print(label, "first_packet_rank", rank, "states", len(states))
        hits = []
        heldout = []
        count = 0
        for i, state in enumerate(states):
            stream = outputs(state, 16400, reverse)
            assert stream[:16] == first
            for start in range(16, 16385):
                if stream[start:start + 16] == third:
                    heldout.append((i, start))
                if start > 8192:
                    continue
                candidate = bytes(a ^ b for a, b in zip(stream[start:start + 16], mask))
                count += 1
                if hashlib.sha256(candidate).digest() == commitment:
                    hits.append((i, start, candidate.hex().upper()))
        print(label, "candidate_count", count, "K04_HITS", hits)
        print(label, "third_packet_heldout_matches", heldout)

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
