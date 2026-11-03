"""H-17 source-only PCG32-XSH-RR full 32-bit seed gate for the other ACK2.

Exhaust both standard scalar initstate values and source field-specific PCG
streams (attempt=2 or job suffix=417), checking all four word-order/endian
views of the intact 18:25 PS-261003-0420 ACK2. The selected 0417 ACK2,
route mask, K04 acceptance digest and target are never used as input.
The PCG32 transition and seeding follow pcg-random.org/using-pcg-c.html.
Requires NumPy. Run as a single file from an unchanged repo checkout.
"""
from pathlib import Path
from hashlib import sha256
import re
import time
import numpy as np

A = np.uint64(6364136223846793005)
ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
assert sha256(SPOOL.read_bytes()).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
rows = [line for line in SPOOL.read_text().splitlines()
        if "JOB=PS-261003-0420 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line]
assert len(rows) == 1 and "DEST=bench" in rows[0]
original = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", rows[0]).group(1))
assert original.hex().upper() == "432475F72A62DB39F3D5693E2C937FA4"
views = [(endian, reversed_words)
         for endian in ("little", "big") for reversed_words in (False, True)]
prefixes = {
    int.from_bytes(original[12:16] if reverse else original[:4], endian):
    (endian, reverse) for endian, reverse in views
}

def first_batch(old):
    x = (((old >> np.uint64(18)) ^ old) >> np.uint64(27)).astype(np.uint32)
    r = (old >> np.uint64(59)).astype(np.uint32)
    return ((x >> r) | (x << ((-r) & np.uint32(31)))).astype(np.uint32)

def output_words(seed, sequence):
    inc = (sequence << 1) | 1
    state = (seed + inc) * 6364136223846793005 + inc
    output = []
    for _ in range(4):
        state &= (1 << 64) - 1
        rot = state >> 59
        x = (((state >> 18) ^ state) >> 27) & ((1 << 32) - 1)
        output.append(((x >> rot) | (x << ((-rot) & 31))) & ((1 << 32) - 1))
        state = state * 6364136223846793005 + inc
    return output

def scan():
    started = time.monotonic()
    first_hits = full_hits = 0
    batch = 1 << 20
    for sequence in (2, 417):
        inc = (sequence << 1) | 1
        for start in range(0, 1 << 32, batch):
            if start % (1 << 27) == 0:
                print("PROGRESS", sequence, start, flush=True)
            seeds = np.arange(start, start + batch, dtype=np.uint64)
            state = (seeds + np.uint64(inc)) * A + np.uint64(inc)
            outputs = first_batch(state)
            for first, view in prefixes.items():
                for idx in np.flatnonzero(outputs == np.uint32(first)):
                    seed = int(seeds[idx])
                    words = output_words(seed, sequence)
                    endian, reverse = view
                    recovered = b"".join(w.to_bytes(4, endian)
                                         for w in (words[::-1] if reverse else words))
                    first_hits += 1
                    full_hits += recovered == original
                    print("FIRST_WORD", sequence, seed, view,
                          recovered.hex().upper(), "FULL", recovered == original,
                          flush=True)
    print("COMPLETE_SEEDS", 2 * (1 << 32), "FIRST_WORD_HITS", first_hits,
          "FULL_PACKET_HITS", full_hits, "SECONDS", round(time.monotonic()-started, 2))
    return first_hits, full_hits

def controls():
    for sequence in (2, 417):
        seed = 0x12345678
        words = output_words(seed, sequence)
        inc = (sequence << 1) | 1
        state = (np.array([seed], dtype=np.uint64) + np.uint64(inc)) * A + np.uint64(inc)
        assert int(first_batch(state)[0]) == words[0]
    seed, sequence = 54321, 2
    words = output_words(seed, sequence)
    seeds = np.arange(seed-20, seed+20, dtype=np.uint64)
    inc = (sequence << 1) | 1
    state = (seeds + np.uint64(inc)) * A + np.uint64(inc)
    assert list(np.flatnonzero(first_batch(state) == np.uint32(words[0]))) == [20]
    assert output_words(int(seeds[20]), sequence) == words
    print("SYNTHETIC_PC32_AND_PLANTED_SEED_CONTROLS: PASS")

if __name__ == "__main__":
    controls()
    first, complete = scan()
    assert first == 6 and complete == 0
