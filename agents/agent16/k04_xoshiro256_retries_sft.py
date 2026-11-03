"""SFT: xoshiro256** reversible-output recovery from the two REQUESTED retry flanks.

Read-only, at repository root: python agents/agent16/k04_xoshiro256_retries_sft.py
The disputed selected ACK attempt-2 payload is omitted before the producer fit.
"""
from pathlib import Path
import hashlib
import itertools
import re

UINT64 = (1 << 64) - 1
INVERSE5 = pow(5, -1, 1 << 64)
INVERSE9 = pow(9, -1, 1 << 64)
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
ORIGINAL_COMMIT = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'


def rotl(value, count):
    return ((value << count) | (value >> (64 - count))) & UINT64


def rotr(value, count):
    return ((value >> count) | (value << (64 - count))) & UINT64


def output(state):
    return (rotl(state[1] * 5 & UINT64, 7) * 9) & UINT64


def unoutput(value):
    return rotr(value * INVERSE9 & UINT64, 7) * INVERSE5 & UINT64


def step(state):
    a, b, c, d = state
    t = b << 17 & UINT64
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    d = rotl(d, 45)
    return a, b, c, d


def symbolic_step(state):
    a, b, c, d = state
    t = [b[j - 17] if j >= 17 else 0 for j in range(64)]
    c = [x ^ y for x, y in zip(c, a)]
    d = [x ^ y for x, y in zip(d, b)]
    b = [x ^ y for x, y in zip(b, c)]
    a = [x ^ y for x, y in zip(a, d)]
    c = [x ^ y for x, y in zip(c, t)]
    d = d[-45:] + d[:-45]
    return a, b, c, d


class BinaryEquations:
    def __init__(self):
        self.rows = {}
        self.conflicts = 0

    def add(self, coeff, value):
        while coeff:
            pivot = coeff.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = (coeff, value)
                return
            other, rhs = self.rows[pivot]
            coeff ^= other
            value ^= rhs
        self.conflicts += bool(value)

    def solutions(self):
        free = [i for i in range(256) if i not in self.rows]
        assert len(free) <= 10, len(free)
        for assignment in range(1 << len(free)):
            value = sum(((assignment >> index) & 1) << bit
                        for index, bit in enumerate(free))
            for pivot in sorted(self.rows):
                coeff, rhs = self.rows[pivot]
                if rhs ^ ((coeff & value).bit_count() & 1):
                    value |= 1 << pivot
            yield tuple((value >> (64 * word)) & UINT64 for word in range(4))


def two_outputs(state, endian, reverse):
    outputs = [output(state), output(step(state))]
    if reverse:
        outputs.reverse()
    return b''.join(x.to_bytes(8, endian) for x in outputs)


def source_brackets(root):
    raw = (root / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    attempts = {}
    for line in raw.decode('ascii').splitlines():
        if 'JOB=PS-261003-0417 ' not in line or 'T18:' not in line:
            continue
        match = re.search(r'ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+)', line)
        assert match
        attempt, state, cls = int(match[1]), match[2], match[3]
        assert cls == 'RECOVER'
        if attempt == 2:
            # Only the ACK route metadata is checked. Disputed payload is
            # withheld even from parsing.
            assert state == 'ACK'
            continue
        assert state == 'REQUESTED' and attempt in (1, 3)
        payload = re.search(r'PAYLOAD=([0-9A-F]{32})', line)
        assert payload
        attempts[attempt] = bytes.fromhex(payload[1])
    assert set(attempts) == {1, 3}
    return attempts[1], attempts[3]


def invert_bracket(before, after, endian, reverse, after_start):
    before_words = [int.from_bytes(before[i:i + 8], endian) for i in (0, 8)]
    after_words = [int.from_bytes(after[i:i + 8], endian) for i in (0, 8)]
    if reverse:
        before_words.reverse()
        after_words.reverse()
    indexed = dict(zip((0, 1, after_start, after_start + 1),
                       [unoutput(v) for v in before_words + after_words]))
    equations = BinaryEquations()
    symbolic = [[1 << (64 * word + bit) for bit in range(64)] for word in range(4)]
    for position in range(after_start + 2):
        if position in indexed:
            observed = indexed[position]
            for bit, coeff in enumerate(symbolic[1]):
                equations.add(coeff, (observed >> bit) & 1)
        symbolic = symbolic_step(symbolic)
    if equations.conflicts:
        return equations, []
    completed = []
    for seed_state in equations.solutions():
        state = seed_state
        native_outputs = []
        for position in range(after_start + 2):
            if position in indexed:
                assert state[1] == indexed[position]
            native_outputs.append(output(state))
            state = step(state)
        completed.append((seed_state, native_outputs))
    return equations, completed


def coupon(outputs, position, endian, reverse):
    words = list(outputs[position:position + 2])
    assert len(words) == 2
    if reverse:
        words.reverse()
    return b''.join(x.to_bytes(8, endian) for x in words)


def matches_original(candidate):
    component = bytes(a ^ b for a, b in zip(candidate, MASK))
    return hashlib.sha256(component).hexdigest() == ORIGINAL_COMMIT


def synthetic_control(after_start, selected_start, endian, reverse):
    actual_state = (0x45A31234562345AD, 0x988767856CFA04B1,
                    0xABBCCDDFF0810AAA, 0xF093847210120DED)
    states = [actual_state]
    for _ in range(after_start + 1):
        states.append(step(states[-1]))
    earlier = two_outputs(states[0], endian, reverse)
    later = two_outputs(states[after_start], endian, reverse)
    desired = two_outputs(states[selected_start], endian, reverse)
    _, solutions = invert_bracket(earlier, later, endian, reverse, after_start)
    assert any(initial == actual_state and
               coupon(ys, selected_start, endian, reverse) == desired
               for initial, ys in solutions)


def main():
    root = Path(__file__).resolve().parents[2] / 'resources'
    before, after = source_brackets(root)
    print('SOURCE: requested attempts 1 and 3 of PS-261003-0417; '
          'selected ACK2 entirely withheld')
    print('SOURCE brackets:', before.hex().upper(), after.hex().upper())

    total_geometries = 0
    consistent_geometries = 0
    state_solutions = 0
    candidate_assignments = 0
    distinct = set()
    hits = []
    rank_counts = {}
    for later_start in range(4, 65):
        for endian, reverse in itertools.product(('little', 'big'), (False, True)):
            eq, initial_states = invert_bracket(before, after, endian, reverse, later_start)
            total_geometries += 1
            rank_counts[len(eq.rows)] = rank_counts.get(len(eq.rows), 0) + 1
            if initial_states:
                consistent_geometries += 1
            state_solutions += len(initial_states)
            for _, outputs in initial_states:
                for selected_start in range(2, later_start - 1):
                    candidate = coupon(outputs, selected_start, endian, reverse)
                    candidate_assignments += 1
                    distinct.add(candidate)
                    if matches_original(candidate):
                        hits.append((later_start, selected_start, endian, reverse,
                                     candidate.hex().upper()))
    print('ORIGINAL bracket:', total_geometries, 'geometries,',
          consistent_geometries, 'consistent,',
          state_solutions, 'compatible generator states')
    print('ORIGINAL candidates:', candidate_assignments, 'complete assignments;',
          len(distinct), 'distinct coupons;', len(hits), 'K04 commitment hits')
    print('ORIGINAL rank counts:', sorted(rank_counts.items()))
    print('ORIGINAL hits:', hits)
    assert total_geometries == 244
    assert consistent_geometries == 143
    assert state_solutions == 248
    assert candidate_assignments == 7454 and len(distinct) == 7454 and not hits

    controls = 0
    for later_start, selected_start in ((4, 2), (7, 3), (18, 13),
                                        (36, 17), (64, 30)):
        for endian, reverse in itertools.product(('little', 'big'), (False, True)):
            synthetic_control(later_start, selected_start, endian, reverse)
            controls += 1
    print('SYNTHETIC actual xoshiro256** missing-coupon recovery:',
          controls, 'PASS controls')
    print('RESULT original conditional xoshiro256** retry producer: NO_MATCH')


if __name__ == '__main__':
    main()
