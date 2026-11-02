"""Source-only SplitMix64 seed to xoshiro128** full-state test.
Reconstruct each intact 128-bit generator state, then test whether its four
32-bit words could be two consecutive SplitMix64 outputs under one 64-bit seed.
Selected K04 ACK, mask and commitment are never read.
Run: python agents/agent3/k04_xoshiro128_splitmix64_sft.py resources
"""
import itertools
import re
import sys
from pathlib import Path
from k04_xoshiro128ss_source_sft import U, fit, stream, table, words

U64 = (1 << 64) - 1
WEYL = 0x9E3779B97F4A7C15

def unxor_right(v, k):
    shift = k
    while shift < 64:
        v ^= v >> shift
        shift *= 2
    return v & U64

def mix(z):
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & U64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & U64
    return z ^ (z >> 31)

def unmix(z):
    z = unxor_right(z, 31) * pow(0x94D049BB133111EB, -1, 1 << 64) & U64
    z = unxor_right(z, 27) * pow(0xBF58476D1CE4E5B9, -1, 1 << 64) & U64
    return unxor_right(z, 30)

def seeded(seed):
    return mix(seed + WEYL & U64), mix(seed + 2 * WEYL & U64)

def main(root):
    for seed in (0, 1, 20261003, 0x123456789ABCDEF0, U64):
        a, b = seeded(seed)
        assert unmix(a) == (seed + WEYL) & U64
        state = [a & U, a >> 32, b & U, b >> 32]
        actual = stream(state, 4)
        bits, rank = fit(table(4), list(enumerate(actual)))
        assert bits is not None and rank == 128
        assert [(bits >> (i * 32)) & U for i in range(4)] == state
    print("PASS positive seeded generator and state inversion")

    intact = []
    for line in (root / "evidence/print/spool-reconstruction.log").read_text().splitlines():
        m = re.search(r"JOB=PS-261003-(\d+) ATTEMPT=1 STATE=ACK .*?PAYLOAD=([A-F0-9]{32})", line)
        if m and 300 <= int(m.group(1)) <= 427:
            intact.append(bytes.fromhex(m.group(2)))
    assert len(intact) == 128
    symbols = table(4)
    tested, hits = 0, []
    for idx, raw in enumerate(intact):
        for endian in ("little", "big"):
            for reverse in (False, True):
                observed = words(raw, endian, reverse)
                bits, rank = fit(symbols, list(enumerate(observed)))
                assert bits is not None and rank == 128
                state = [(bits >> (32 * i)) & U for i in range(4)]
                for perm in itertools.permutations(range(4)):
                    a = state[perm[0]] | (state[perm[1]] << 32)
                    b = state[perm[2]] | (state[perm[3]] << 32)
                    seed = (unmix(a) - WEYL) & U64
                    if seeded(seed)[1] == b:
                        hits.append((idx, endian, reverse, perm, hex(seed)))
                    tested += 1
    assert tested == 12288
    print("intact rows:", len(intact), "seed packings:", tested, "matches:", hits)
    assert not hits
    print("K04 selected ACK2, mask and commitment: UNREAD")

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
