"""H-17: conditional p951 first-cycle CPython seed-length sieve, K04 withheld.

Run with a repository resources path as the first argument (default resources).
Source-only diagnostic: it never reads recovery commitments or selected ACK2.
"""
import hashlib
import random
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('resources')
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
MASK = 0xffffffff
SOURCE_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'


def untemper(value):
    for shift, left, mask in ((18, False, MASK), (15, True, 0xefc60000), (7, True, 0x9d2c5680), (11, False, MASK)):
        result = value
        for _ in range(6):
            result = value ^ (((result << shift) & mask) if left else (result >> shift))
        value = result & MASK
    return value


def twist(value):
    return ((value >> 1) ^ (0x9908b0df if value & 1 else 0)) & MASK


def untwist(value):
    return (((value ^ (0x9908b0df if value >> 31 else 0)) << 1) | (value >> 31)) & MASK


def closure(native):
    offset, length = 2000, 6000
    value, known = [0] * length, [0] * length

    def add(index, bits, mask):
        if index < 0 or index >= length:
            return 0
        assert ((value[index] ^ bits) & known[index] & mask) == 0
        fresh = mask & ~known[index]
        value[index] = (value[index] & ~fresh) | (bits & fresh)
        known[index] |= fresh
        return fresh.bit_count()

    for row, start in enumerate(STARTS):
        if row == 129:
            continue
        for lane in range(4):
            add(offset + start + lane, untemper(native[row][lane]), MASK)
    for _ in range(30):
        gained = 0
        for p in range(length - 624):
            m = (known[p] & 0x80000000) | (known[p+1] & 0x7fffffff)
            v = (value[p] & 0x80000000) | (value[p+1] & 0x7fffffff)
            if known[p+397] == known[p+624] == MASK:
                prior = untwist(value[p+397] ^ value[p+624])
                gained += add(p, prior, 0x80000000) + add(p+1, prior, 0x7fffffff)
            if m == MASK:
                if known[p+397] == MASK:
                    gained += add(p+624, value[p+397] ^ twist(v), MASK)
                if known[p+624] == MASK:
                    gained += add(p+397, value[p+624] ^ twist(v), MASK)
        if gained == 0:
            break
    assert all(known[offset + STARTS[129] + lane] == 0 for lane in range(4))
    return value[offset-624:offset], known[offset-624:offset]


GENRAND = [19650218]
for j in range(1, 624):
    v = GENRAND[-1]
    GENRAND.append((1812433253 * (v ^ (v >> 30)) + j) & MASK)


def seed_term(i, a, b, c):
    prior = ((b+i-1) & MASK) ^ (1566083941 * (a ^ (a >> 30)) & MASK)
    later = ((c+i) & MASK) ^ (1566083941 * (b ^ (b >> 30)) & MASK)
    return (later - (GENRAND[i] ^ (1664525 * (prior ^ (prior >> 30)) & MASK))) & MASK


def terms(values, masks):
    out = []
    for i in range(4, 624):
        choices = []
        for index in (i-2, i-1, i):
            missing = MASK ^ masks[index]
            if missing.bit_count() > 1:
                break
            choices.append((values[index], values[index] | missing) if missing else (values[index],))
        if len(choices) == 3:
            out.append((i-1, {seed_term(i, a, b, c) for a in choices[0] for b in choices[1] for c in choices[2]}))
    return out


def accepts_length(n, witnesses):
    seen = {}
    for j, candidates in witnesses:
        residue = j % n
        seen[residue] = seen[residue] & candidates if residue in seen else candidates
        if not seen[residue]:
            return False
    return True


# Direct initialized-state controls, and end-to-end MT first-cycle controls.
for n in (1, 2, 4, 16, 80, 128, 249, 256, 623):
    seed = sum((j+1) << (32*j) for j in range(n))
    original = random.Random(seed)
    initialized = list(original.getstate()[1][:624])
    assert accepts_length(n, terms(initialized, [MASK] * 624))
    if n in (1, 249, 623):
        stream = [original.getrandbits(32) for _ in range(967)]
        packets = [stream[start:start+4] for start in STARTS]
        inferred, masks = closure(packets)
        assert all((a ^ b) & mask == 0 for a, b, mask in zip(inferred, initialized, masks))
        assert accepts_length(n, terms(inferred, masks))
print('SYNTHETIC_NINE_SEED_LENGTH_CONTROLS_PASS; THREE_FIRST_CYCLE_CLOSURE_CONTROLS_PASS')

spool = (ROOT / 'evidence/print/spool-reconstruction.log').read_bytes()
assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
payloads = re.findall(rb'PAYLOAD=([0-9A-F]{32})', spool)
assert len(payloads) == len(STARTS) == 133 and STARTS[129] == 951
native = [[int.from_bytes(bytes.fromhex(p.decode())[4*j:4*j+4], 'little') for j in range(4)] for p in payloads]
original, fixed = closure(native)
witnesses = terms(original, fixed)
assert len(witnesses) == 64 and sum(len(v) == 1 for _, v in witnesses) == 24
excluded = [n for n in range(1, 624) if not accepts_length(n, witnesses)]
assert len(excluded) == 479 and excluded[:248] == list(range(1, 249))
print('ORIGINAL_P951_INITIALIZED_STATE_BITS', sum(mask.bit_count() for mask in fixed))
print('ORIGINAL_KEY_RESIDUE_TERMS', len(witnesses), 'EXACT', 24, 'SINGLE_BIT_AMBIGUOUS', 40)
print('P951_LENGTHS_EXCLUDED', len(excluded), 'OF', 623, 'CONTIGUOUS', '1..248')
print('ORIGINAL_K04_SELECTED_OUTPUT_FIXED_BITS', 0)
