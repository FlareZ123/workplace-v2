"""Inverse K04-as-export-shuffle-seed hypothesis. Original evidence read only.

Xorshift128 full initial state (128 bits) is conjectured to be the coupon.
The observed record permutation constrains getrandbits(k) shuffle draws.
For the first seed-identifying prefix, permit 0..1 rejected draws per
accepted swap, at most six total. Validate the entire exact shuffle.
"""
from pathlib import Path
import hashlib
import json
import sys

MASK32 = (1 << 32) - 1
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
RECORDER_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"


def next_xorshift128(state):
    x, y, z, w = state
    t = x ^ ((x << 11) & MASK32)
    new = (w ^ (w >> 19) ^ t ^ (t >> 8)) & MASK32
    return (y, z, w, new), new


def symbolic_outputs(length):
    result = [[0] * 32 for _ in range(length)]
    for variable in range(128):
        state = [0, 0, 0, 0]
        state[variable // 32] = 1 << (variable % 32)
        for step in range(length):
            state, word = next_xorshift128(state)
            while word:
                bit = (word & -word).bit_length() - 1
                result[step][bit] |= 1 << variable
                word &= word - 1
    return result


def actual_swaps(seed, n):
    state = tuple((seed >> (32 * i)) & MASK32 for i in range(4))
    swaps = []
    rejected = []
    for i in range(n - 1, 0, -1):
        bits = (i + 1).bit_length()
        misses = 0
        while True:
            state, word = next_xorshift128(state)
            j = word >> (32 - bits)
            if j < i + 1:
                swaps.append((i, j))
                rejected.append(misses)
                break
            misses += 1
    return swaps, rejected


def inverse_swaps(initial_order):
    working = initial_order[:]
    trace = []
    for i in range(len(working) - 1, 0, -1):
        j = working.index(i, 0, i + 1)
        trace.append((i, j))
        working[i], working[j] = working[j], working[i]
    assert working == list(range(len(working)))
    return trace


def recover_seed(basis):
    seed = 0
    for pivot, value in enumerate(basis):
        assert value is not None
        row, rhs = value
        rhs ^= ((seed & (row ^ (1 << pivot))).bit_count() & 1)
        if rhs:
            seed |= 1 << pivot
    return seed


def inverse(swaps, symbolic, all_seeds=None, max_rejects=6, max_depth=35):
    basis = [None] * 128
    seed_count = 0
    branches = 0
    full_trace_hit = None

    def add_word(step, bits, code, inserted):
        for bit in range(bits):
            row = symbolic[step][32 - bits + bit]
            rhs = (code >> bit) & 1
            while row:
                pivot = row.bit_length() - 1
                known = basis[pivot]
                if known is None:
                    basis[pivot] = (row, rhs)
                    inserted.append(pivot)
                    break
                row ^= known[0]
                rhs ^= known[1]
            else:
                if rhs:
                    return False
        return True

    def search(index, misses, rank):
        nonlocal seed_count, branches, full_trace_hit
        if full_trace_hit is not None:
            return
        branches += 1
        if rank == 128:
            seed = recover_seed(basis)
            seed_count += 1
            if all_seeds is not None:
                all_seeds.add(seed)
            replay, rejection_counts = actual_swaps(seed, len(swaps) + 1)
            if (replay == swaps and max(rejection_counts[:index]) <= 1
                    and sum(rejection_counts[:index]) <= max_rejects):
                full_trace_hit = seed
            return
        if index >= min(len(swaps), max_depth):
            return
        i, code = swaps[index]
        bits = (i + 1).bit_length()
        for extra in (0, 1):
            if misses + extra > max_rejects:
                continue
            inserted = []
            valid = add_word(index + misses + extra, bits, code, inserted)
            if valid:
                search(index + 1, misses + extra, rank + len(inserted))
            for pivot in inserted:
                basis[pivot] = None

    search(0, 0, 0)
    return {"branches": branches, "reconstructed_seed_assignments": seed_count,
            "full_shuffle_seed": full_trace_hit}


def original_swaps(root):
    path = root / "evidence/recorder/trip-recorder.raw"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RECORDER_SHA
    assert len(raw) == 16 + 88 * 24
    rows = [raw[16 + i * 24:16 + (i + 1) * 24] for i in range(88)]

    def indexed_fields(i):
        row = rows[i]
        return (int.from_bytes(row[4:6], "little"),
                int.from_bytes(row[8:12], "little"),
                row[6], row[7], row)

    for mode, ordered in (
        ("raw_asc", sorted(range(88), key=lambda i: rows[i])),
        ("raw_desc", sorted(range(88), key=lambda i: rows[i], reverse=True)),
        ("node_seq_asc", sorted(range(88), key=indexed_fields)),
        ("node_seq_desc", sorted(range(88), key=indexed_fields, reverse=True)),
    ):
        yield mode, inverse_swaps(ordered)


def coupon_views(seed):
    words = [(seed >> (32 * i)) & MASK32 for i in range(4)]
    for byteorder in ("big", "little"):
        for word_order in (words, words[::-1]):
            raw = b"".join(w.to_bytes(4, byteorder) for w in word_order)
            yield raw
            yield raw[::-1]


def main(root):
    assert next_xorshift128((1, 2, 3, 4))[1] == 2061
    masks = symbolic_outputs(88 + 35)
    planted = None
    for counter in range(1000):
        seed = int.from_bytes(hashlib.sha256(str(counter).encode()).digest()[:16], "little")
        swaps, rejected = actual_swaps(seed, 88)
        if max(rejected[:25]) <= 1 and sum(rejected[:25]) <= 6:
            planted = (seed, swaps)
            break
    assert planted is not None
    positive = inverse(planted[1], masks)
    assert positive["full_shuffle_seed"] == planted[0]
    print("SYNTHETIC_SEED_RECOVERY", positive["branches"], "PASS")

    all_seeds = set()
    observations = {}
    for name, swaps in original_swaps(root):
        outcome = inverse(swaps, masks, all_seeds)
        assert outcome["full_shuffle_seed"] is None
        observations[name] = outcome

    candidate_coupons = {coupon for seed in all_seeds for coupon in coupon_views(seed)}
    authentic_hits = [
        coupon.hex().upper()
        for coupon in candidate_coupons
        if hashlib.sha256(bytes(c ^ m for c, m in zip(coupon, MASK))).hexdigest() == TARGET
    ]
    print(json.dumps({"source_models": observations,
                      "distinct_rank128_seed_assignments": len(all_seeds),
                      "unique_complete_coupon_candidates": len(candidate_coupons),
                      "original_K04_hits": authentic_hits}, sort_keys=True))
    assert len(all_seeds) == 1315
    assert len(candidate_coupons) == 5260
    assert not authentic_hits


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
