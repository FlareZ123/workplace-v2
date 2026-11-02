"""SFT: source-only 256-bit xoshiro256** printer producer inversion.

Run with Python 3 and the original case root as argv[1] (or resources/).
No cryptographic commitment, K04 ACK, or candidate is read.
"""
import re
import sys
from pathlib import Path

MASK = (1 << 64) - 1
INV5 = pow(5, -1, 1 << 64)
INV9 = pow(9, -1, 1 << 64)


def rotl(x, n):
    return ((x << n) | (x >> (64 - n))) & MASK


def rotr(x, n):
    return (x >> n) | ((x << (64 - n)) & MASK)


def advance(s):
    a, b, c, d = s
    result = rotl(b * 5 & MASK, 7) * 9 & MASK
    t = (b << 17) & MASK
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    d = rotl(d, 45)
    return result, [a, b, c, d]


def unscramble(x):
    return rotr(x * INV9 & MASK, 7) * INV5 & MASK


def equations(times):
    rows = [0] * (64 * len(times))
    by_time = {time: index for index, time in enumerate(times)}
    for bit in range(256):
        state = [1 << (bit % 64) if k == bit // 64 else 0
                 for k in range(4)]
        for time in range(max(times) + 1):
            if time in by_time:
                mask = state[1]
                index = by_time[time]
                while mask:
                    lowbit = mask & -mask
                    rows[index * 64 + lowbit.bit_length() - 1] |= 1 << bit
                    mask -= lowbit
            _, state = advance(state)
    return rows


def fit(observed, times):
    assert len(observed) == len(times) == 5
    rhs = sum(unscramble(output) << (64 * k)
              for k, output in enumerate(observed))
    rows = [mask | (((rhs >> i) & 1) << 256)
            for i, mask in enumerate(equations(times))]
    rank = 0
    pivots = []
    for col in range(256):
        pivot = next((i for i in range(rank, 320)
                      if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank + 1, 320):
            if (rows[i] >> col) & 1:
                rows[i] ^= rows[rank]
        pivots.append((col, rank))
        rank += 1
    contradictions = sum((row >> 256) & 1 for row in rows[rank:])
    if contradictions or rank < 256:
        return False, rank, contradictions
    statebits = 0
    for col, i in reversed(pivots):
        value = ((rows[i] >> 256) & 1) ^ (
            (rows[i] & statebits).bit_count() & 1
        )
        statebits |= value << col
    state = [(statebits >> (64 * k)) & MASK for k in range(4)]
    predictions = []
    required = dict.fromkeys(times)
    for time in range(max(times) + 1):
        output, state = advance(state)
        if time in required:
            predictions.append(output)
    return predictions == observed, rank, contradictions


def printer_rows(root):
    rows = []
    lines = (root / "evidence" / "print" /
             "spool-reconstruction.log").read_text().splitlines()
    for line in lines:
        if not line.startswith("2026") or "ATTEMPT=1 STATE=ACK" not in line:
            continue
        job = int(re.search(r"JOB=PS-261003-(\d+)", line).group(1))
        if 300 <= job <= 427:
            raw = re.search(r"PAYLOAD=([A-F0-9]{32})", line).group(1)
            rows.append(bytes.fromhex(raw))
    assert len(rows) == 128, len(rows)
    return rows


def main(root):
    seed = [0x0123456789ABCDEF, 0x0FEDCBA987654321,
            0xDEADBEEFCAFE0123, 0xA0B0C0D0E0F00123]
    stream = []
    state = seed
    for _ in range(20):
        value, state = advance(state)
        stream.append(value)
    positives = [
        [0, 1, 2, 3, 4],
        [0, 2, 5, 7, 10],
        [0, 1, 5, 6, 10],
    ]
    for indices in positives:
        ok, rank, contradictions = fit([stream[i] for i in indices], indices)
        assert (ok, rank, contradictions) == (True, 256, 0)
    print("synthetic inversion controls: 3 PASS")

    data = printer_rows(root)
    tested = 0
    survivors = []
    for internal_skip in range(9):
        for external_skip in range(9):
            times = [
                0,
                1 + internal_skip,
                2 + internal_skip + external_skip,
                3 + 2 * internal_skip + external_skip,
                4 + 2 * internal_skip + 2 * external_skip,
            ]
            for order in ("little", "big"):
                for swap in (False, True):
                    observations = []
                    for raw in data[:3]:
                        pair = [int.from_bytes(raw[:8], order),
                                int.from_bytes(raw[8:], order)]
                        if swap:
                            pair.reverse()
                        observations.extend(pair)
                    ok, rank, contradictions = fit(observations[:5], times)
                    tested += 1
                    if ok:
                        survivors.append((internal_skip, external_skip,
                                          order, swap, rank))
    assert tested == 324
    print("original intact printer source / xoshiro256** models:", tested)
    print("full-state-consistent models:", survivors)
    print("selected ACK, mask, K04 commitment: UNREAD")
    assert not survivors


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
