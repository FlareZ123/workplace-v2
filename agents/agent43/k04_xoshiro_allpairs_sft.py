"""H17 printer xoshiro128** long-gap, all-intact-pairs source test.

Run: python agents/agent43/k04_xoshiro_allpairs_sft.py resources
Does not read selected ACK2, route mask, or acceptance commitments.
"""
import hashlib
import re
import sys
from pathlib import Path

MASK = 0xffffffff
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
INV5 = pow(5, -1, 2**32)
INV9 = pow(9, -1, 2**32)


def rol(x, n):
    return ((x << n) | (x >> (32 - n))) & MASK


def ror(x, n):
    return ((x >> n) | (x << (32 - n))) & MASK


def output(state):
    return rol((state[1] * 5) & MASK, 7) * 9 & MASK


def decode(value):
    return ror((value * INV9) & MASK, 7) * INV5 & MASK


def step(state):
    a, b, c, d = state
    t = (b << 9) & MASK
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    d = rol(d, 11)
    return a, b, c, d


def linear_masks():
    columns = []
    for index in range(128):
        state = tuple(1 << (index % 32) if i == index // 32 else 0 for i in range(4))
        values = []
        for _ in range(4):
            values.append(state[1])
            state = step(state)
        columns.append(values)
    return [
        sum(((column[t] >> bit) & 1) << k for k, column in enumerate(columns))
        for t in range(4) for bit in range(32)
    ]


def recover(words, masks):
    pivots = {}
    for k, row in enumerate(masks):
        rhs = (decode(words[k // 32]) >> (k % 32)) & 1
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                coeff, value = pivots[p]
                row ^= coeff
                rhs ^= value
            else:
                pivots[p] = (row, rhs)
                break
        if not row and rhs:
            raise AssertionError("inconsistent recovered state")
    assert len(pivots) == 128
    state = 0
    for p in sorted(pivots):
        coeff, rhs = pivots[p]
        state |= (rhs ^ ((coeff & state).bit_count() & 1)) << p
    return tuple((state >> (32 * i)) & MASK for i in range(4))


def scan(states, maximum):
    state_index = {value: i for i, value in enumerate(states)}
    matches = []
    for i, initial in enumerate(states):
        current = initial
        for gap in range(1, maximum + 1):
            current = step(current)
            j = state_index.get(current)
            if j is not None and j != i:
                matches.append((i, j, gap))
    return matches


def run(root):
    spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
    packets = []
    for line in spool.decode("ascii").splitlines():
        m = re.search(r"JOB=(\\S+) ATTEMPT=(\\d+) STATE=(\\S+) CLASS=(\\S+) PAYLOAD=([A-F0-9]{32})", line)
        if not m:
            continue
        job, attempt, state, kind, payload = m.groups()
        if (job, attempt, state, kind) == ("PS-261003-0417", "2", "ACK", "RECOVER"):
            continue
        packets.append(bytes.fromhex(payload))
    assert len(packets) == 132
    masks = linear_masks()
    seed = (0x1a2b3c4d, 0xc0ffee01, 0xdeadbeef, 0xfee1dead)
    after = seed
    for _ in range(378):
        after = step(after)
    assert scan([seed, after], 4096) == [(0, 1, 378)]
    synthetic = []
    current = seed
    for _ in range(4):
        synthetic.append(output(current))
        current = step(current)
    assert recover(synthetic, masks) == seed
    print("SYNTHETIC: 128-bit inversion and 378-step state link PASS")

    for endian in ("little", "big"):
        for reversed_words in (False, True):
            states = []
            for data in packets:
                words = [int.from_bytes(data[k:k + 4], endian) for k in range(0, 16, 4)]
                if reversed_words:
                    words.reverse()
                state = recover(words, masks)
                regenerated = []
                current = state
                for _ in range(4):
                    regenerated.append(output(current))
                    current = step(current)
                assert regenerated == words
                states.append(state)
            links = scan(states, 4096)
            print(f"ORIGINAL: {endian=} {reversed_words=} packets=132 "
                  f"steps=540672 links={len(links)}")
            assert not links
    print("ORIGINAL: 2,162,688 state-successor checks; 0 links")
    print("Selected K04 ACK2, mask, commitment: UNREAD")


if __name__ == "__main__":
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
