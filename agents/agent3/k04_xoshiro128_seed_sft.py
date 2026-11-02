"""Source-only gate for 32-bit splitmix-seeded xoshiro128** spool producers.
For each original intact 16-byte packet reconstruct a 128-bit generator state.
Test whether that state equals four successive outputs of either of two
widely used invertible 32-bit Weyl/mixing families.
Read-only; selected ACK2, mask and K04 target are not accessed.
Run: python agents/agent3/k04_xoshiro128_seed_sft.py resources
"""
import re
import sys
from pathlib import Path
from k04_xoshiro128ss_source_sft import U, fit, stream, table, words

WEYL = 0x9E3779B9

def unxor_right(value, shift):
    size = shift
    while size < 32:
        value ^= value >> size
        size *= 2
    return value & U

def mix(value, family):
    if family == "murmur":
        value ^= value >> 16
        value = (value * 0x85EBCA6B) & U
        value ^= value >> 13
        value = (value * 0xC2B2AE35) & U
        value ^= value >> 16
    else:
        value ^= value >> 16
        value = (value * 0x21F0AAAD) & U
        value ^= value >> 15
        value = (value * 0x735A2D97) & U
        value ^= value >> 15
    return value & U

def unmix(value, family):
    if family == "murmur":
        value = unxor_right(value, 16)
        value = value * pow(0xC2B2AE35, -1, 1 << 32) & U
        value = unxor_right(value, 13)
        value = value * pow(0x85EBCA6B, -1, 1 << 32) & U
        return unxor_right(value, 16)
    value = unxor_right(value, 15)
    value = value * pow(0x735A2D97, -1, 1 << 32) & U
    value = unxor_right(value, 15)
    value = value * pow(0x21F0AAAD, -1, 1 << 32) & U
    return unxor_right(value, 16)

def seeded(seed, family):
    return [mix(seed + WEYL * (i + 1) & U, family) for i in range(4)]

def main(root):
    symbols = table(4)
    for family in ("murmur", "splitmix32"):
        for seed in (0, 1, 20261003, 0xDEADBEEF, U):
            state = seeded(seed, family)
            assert unmix(state[0], family) == (seed + WEYL) & U
            actual = stream(state, 4)
            recovered, rank = fit(symbols, list(enumerate(actual)))
            assert rank == 128
            assert [(recovered >> (i * 32)) & U for i in range(4)] == state
    print("PASS seeded-state and output inversion synthetic controls")
    intact = []
    for line in (root / "evidence/print/spool-reconstruction.log").read_text().splitlines():
        m = re.search(r"JOB=PS-261003-(\d+) ATTEMPT=1 STATE=ACK .*?PAYLOAD=([A-F0-9]{32})", line)
        if m and 300 <= int(m.group(1)) <= 427:
            intact.append(bytes.fromhex(m.group(2)))
    assert len(intact) == 128
    count, hits, one_off = 0, [], []
    for idx, raw in enumerate(intact):
        for endian in ("little", "big"):
            for reverse in (False, True):
                raw_words = words(raw, endian, reverse)
                bits, rank = fit(symbols, list(enumerate(raw_words)))
                assert bits is not None and rank == 128
                state = [(bits >> (i * 32)) & U for i in range(4)]
                for family in ("murmur", "splitmix32"):
                    for shift in range(4):
                        seed = unmix(state[shift], family) - WEYL & U
                        expected = seeded(seed, family)
                        mismatch = sum(a != b for a, b in zip(expected, state[shift:] + state[:shift]))
                        count += 1
                        if mismatch == 0:
                            hits.append((idx, family, endian, reverse, shift, seed))
                        if mismatch <= 1:
                            one_off.append((idx, family, endian, reverse, shift, mismatch))
    assert count == 4096
    print("original intact source rows:", len(intact), "seed alignments:", count)
    print("exact seeded-state matches:", hits)
    print("up to one mismatch in four words:", one_off)
    assert not hits and not one_off
    print("selected ACK2, XOR mask, and acceptance: UNREAD")

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
