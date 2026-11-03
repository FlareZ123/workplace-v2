"""K04: source-only n=364 CPython middle-state inversion.

Run: python agents/agent45/k04_middle_inverse_364_sft.py resources
Reads the intact printer spool; withholds selected ACK2 and all REC8 secrets.
Tests p951 first-cycle CPython integer seed, not all producer models.
"""
from pathlib import Path
import sys
import random
import hashlib
import re

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
MASK = (1 << 32) - 1
C1 = 1566083941
C2 = 1664525
B = [19650218]
for i in range(1, 624):
    x = B[-1]
    B.append((1812433253 * (x ^ (x >> 30)) + i) & MASK)


def m(x, multiplier):
    return ((x ^ (x >> 30)) * multiplier) & MASK


def key_term(i, a, b, c):
    left = ((c + i) & MASK) ^ m(b, C1)
    right = B[i] ^ m(((b + i - 1) & MASK) ^ m(a, C1), C2)
    return (left - right) & MASK


def partial_term(i, a, c, low, high_b, high_p):
    b = (high_b << 30) | low
    p = ((b + i - 1) & MASK) ^ m(a, C1)
    left = ((c + i) & MASK) ^ (((b ^ high_b) * C1) & MASK)
    right = B[i] ^ (((p ^ high_p) * C2) & MASK)
    return (left - right) & MASK


def solve_middle(i, a, c, key):
    """Enumerate every 32-bit middle word by exact two-bit-delayed lifting.

    Guess b>>30 and p>>30, where p=(b+i-1)^mix(a). For a fixed pair,
    changing an unknown b bit k toggles both modular odd-multiplier
    terms at bit k; their difference modulo 2**(k+1) is invariant.
    After choosing b's bit k, test through bit k+1. Verify high
    constraints and the complete original equation at the end.
    """
    states = [
        (hb, hp, 0) for hb in range(4) for hp in range(4)
        if (partial_term(i, a, c, 0, hb, hp) & 1) == (key & 1)
    ]
    for k in range(30):
        modulus_mask = (1 << (k + 2)) - 1
        states = [
            (hb, hp, low | (bit << k))
            for hb, hp, low in states for bit in (0, 1)
            if ((partial_term(i, a, c, low | (bit << k), hb, hp) - key)
                & modulus_mask) == 0
        ]
    answer = set()
    for hb, hp, low in states:
        b = (hb << 30) | low
        p = ((b + i - 1) & MASK) ^ m(a, C1)
        if (p >> 30) == hp and key_term(i, a, b, c) == key:
            answer.add(b)
    return sorted(answer)


STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,
    136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,
    237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,
    354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,
    460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,
    582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,
    686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,
    801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,
    912,918,924,930,936,942,947,951,955,959,963]
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def untemper(x):
    for shift, left, mask in ((18, False, MASK), (15, True, 0xefc60000),
                              (7, True, 0x9d2c5680), (11, False, MASK)):
        y = x
        for _ in range(6):
            y = x ^ (((y << shift) & mask) if left else (y >> shift))
        x = y & MASK
    return x


def twist(x):
    return ((x >> 1) ^ (0x9908b0df if x & 1 else 0)) & MASK


def inverse_twist(x):
    return (((x ^ (0x9908b0df if x >> 31 else 0)) << 1) | (x >> 31)) & MASK


def close(payloads):
    """Exact MT recurrence closure, without the selected damaged ACK2."""
    offset, size = 2000, 6000
    values, masks = [0] * size, [0] * size

    def add(index, value, mask):
        if not 0 <= index < size:
            return 0
        if ((values[index] ^ value) & masks[index] & mask):
            raise AssertionError("contradictory native state")
        new = mask & ~masks[index]
        values[index] = (values[index] & ~new) | (value & new)
        masks[index] |= new
        return new.bit_count()

    for row, (payload, start) in enumerate(zip(payloads, STARTS)):
        if row == 129:
            continue
        for lane in range(4):
            word = int.from_bytes(payload[4*lane:4*lane+4], "little")
            add(offset + start + lane, untemper(word), MASK)

    for _ in range(30):
        gained = 0
        for t in range(size - 624):
            pair_mask = (masks[t] & 0x80000000) | (masks[t+1] & 0x7fffffff)
            pair_value = (values[t] & 0x80000000) | (values[t+1] & 0x7fffffff)
            if masks[t+397] == masks[t+624] == MASK:
                inverse = inverse_twist(values[t+397] ^ values[t+624])
                gained += add(t, inverse, 0x80000000)
                gained += add(t+1, inverse, 0x7fffffff)
            if pair_mask == MASK:
                if masks[t+397] == MASK:
                    gained += add(t+624, values[t+397] ^ twist(pair_value), MASK)
                if masks[t+624] == MASK:
                    gained += add(t+397, values[t+624] ^ twist(pair_value), MASK)
        if not gained:
            break
    return values[offset-624:offset], masks[offset-624:offset]


def source_terms(values, masks):
    terms = {}
    for i in range(4, 624):
        positions = (i-2, i-1, i)
        if sum((MASK ^ masks[k]).bit_count() for k in positions) > 1:
            continue
        unknown = [k for k in positions if masks[k] != MASK]
        if not unknown:
            terms[i-1] = {key_term(i, *values[i-2:i+1])}
            continue
        index = unknown[0]
        choices = set()
        for x in (values[index], values[index] | (MASK ^ masks[index])):
            triple = values[i-2:i+1].copy()
            triple[index-(i-2)] = x
            choices.add(key_term(i, *triple))
        terms[i-1] = choices
    return terms


def random_positive_controls():
    rand = random.Random(1729)
    for test_index in range(2048):
        i = rand.randrange(4, 624)
        a, b, c = [rand.getrandbits(32) for _ in range(3)]
        assert b in solve_middle(i, a, c, key_term(i, a, b, c)), test_index
    print("2048/2048 randomized exact inversion positives PASS")


def seeded_positive_controls():
    for case in range(8):
        seed = sum(
            (((0x621902DD + case*0x30303 + j*0x12537) & MASK) << (32*j))
            for j in range(364)
        )
        rng = random.Random(seed)
        truth = list(rng.getstate()[1][:624])
        draws = [rng.getrandbits(32) for _ in range(967)]
        packets = [
            b"".join(x.to_bytes(4, "little") for x in draws[at:at+4])
            for at in STARTS
        ]
        values, masks = close(packets)
        assert all(not ((x ^ v) & mask)
                   for x, v, mask in zip(truth, values, masks))
        source = source_terms(values, masks)
        j, i = 167, 532
        assert key_term(i, *truth[i-2:i+1]) in source[j]
        choices = [
            solve_middle(i, a, c, key)
            for a in (values[i-2], values[i-2] | (MASK ^ masks[i-2]))
            for c in (values[i], values[i] | (MASK ^ masks[i]))
            for key in source[j]
        ]
        assert any(truth[i-1] in answers for answers in choices), case
    print("8/8 genuine CPython 364-word generator controls PASS")


def original_source_test():
    data = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA
    packets = [bytes.fromhex(s.decode())
               for s in re.findall(rb"PAYLOAD=([0-9A-F]{32})", data)]
    assert len(packets) == len(STARTS) == 133 and STARTS[129] == 951
    values, masks = close(packets)
    source = source_terms(values, masks)
    assert len(source) == 64
    j, i = 167, 532
    assert i - 1 - j == 364
    assert len(source[j]) == 2
    assert masks[i-2] == masks[i] == 0x7fffffff
    assert masks[i-1] == 0x80000000
    branch_counts = [
        len(solve_middle(i, a, c, key))
        for a in (values[i-2], values[i-2] | 0x80000000)
        for c in (values[i], values[i] | 0x80000000)
        for key in source[j]
    ]
    assert len(branch_counts) == 8
    assert branch_counts == [0] * 8
    print("Original n364: 8 exact branches, 0 middle-word roots")
    print("Conditional CPython p951 seed length 364 EXCLUDED")


if __name__ == "__main__":
    random_positive_controls()
    seeded_positive_controls()
    original_source_test()
    print("No actual selected K04 bits or K08 words recovered")
