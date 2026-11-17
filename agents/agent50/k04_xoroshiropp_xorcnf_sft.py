"""Native-XOR SAT inversion of an H-17 K04 xoroshiro128++ dispatcher hypothesis.

Encoder uses XOR clauses for the generator's GF(2)-linear state transition
and CNF for the two 64-bit modular additions in each scrambler output.
It models a conjectural producer, not authenticated coupon or print media.

Requires pycryptosat for solving. --self-test verifies every emitted clause
against independently simulated state without importing a SAT solver.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

MASK = (1 << 64) - 1
SOURCE_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)
ROOT = Path(__file__).resolve().parents[2] / 'resources'


def rol(value, n):
    return ((value << n) | (value >> (64 - n))) & MASK


def stream(state):
    a, b = state
    words = []
    for _ in range(6):
        words.append((rol((a + b) & MASK, 17) + a) & MASK)
        t = a ^ b
        a, b = (rol(a, 49) ^ t ^ (t << 21)) & MASK, rol(t, 28)
    return words


def decode(payload, view):
    endian = 'little' if view & 1 else 'big'
    words = [int.from_bytes(payload[i:i + 8], endian) for i in (0, 8)]
    return words[::-1] if view & 2 else words


def encode(words, view):
    endian = 'little' if view & 1 else 'big'
    words = words[::-1] if view & 2 else words
    return b''.join(x.to_bytes(8, endian) for x in words)


class XorCnf:
    """Unsigned 64-bit bit-circuit, XOR-native and CNF-majority gates."""

    def __init__(self):
        self.count = 0
        self.clauses = []
        self.xors = []
        self.witness = {}

    def variable(self, value=None):
        self.count += 1
        if value is not None:
            self.witness[self.count] = bool(value)
        return self.count

    def word(self, value=None):
        return [self.variable(None if value is None else (value >> i) & 1)
                for i in range(64)]

    def xor(self, *terms):
        terms = [v for v in terms if v]
        if not terms:
            return 0
        if len(terms) == 1:
            return terms[0]
        known = all(v in self.witness for v in terms)
        out = self.variable(sum(self.witness[v] for v in terms) % 2 if known else None)
        self.xors.append((terms + [out], False))
        return out

    def and2(self, x, y):
        assert x > 0 and y > 0
        known = x in self.witness and y in self.witness
        out = self.variable(self.witness[x] and self.witness[y] if known else None)
        self.clauses.extend(([-x, -y, out], [x, -out], [y, -out]))
        return out

    def majority(self, x, y, z):
        assert all(v > 0 for v in (x, y, z))
        known = all(v in self.witness for v in (x, y, z))
        out = self.variable(sum(self.witness[v] for v in (x, y, z)) >= 2 if known else None)
        self.clauses.extend((
            [-x, -y, out], [-x, -z, out], [-y, -z, out],
            [x, y, -out], [x, z, -out], [y, z, -out],
        ))
        return out

    def add64(self, a, b):
        carry = 0
        out = []
        for i in range(64):
            x, y = a[i], b[i]
            out.append(self.xor(x, y, carry))
            if i < 63:
                carry = self.and2(x, y) if i == 0 else self.majority(x, y, carry)
        return out

    @staticmethod
    def rotated(bits, n):
        return [bits[(i - n) % 64] for i in range(64)]

    def constrain(self, bits, value):
        for i, var in enumerate(bits):
            self.clauses.append([var if value >> i & 1 else -var])

    def build(self, observed, seed=None, prefix_bits=0, prefix=0):
        a = self.word(None if seed is None else seed[0])
        b = self.word(None if seed is None else seed[1])
        initial = (a[:], b[:])
        outputs = []
        for idx in range(6):
            total = self.add64(a, b)
            output = self.add64(self.rotated(total, 17), a)
            outputs.append(output)
            if observed[idx] is not None:
                self.constrain(output, observed[idx])
            if idx != 5:
                t = [self.xor(x, y) for x, y in zip(a, b)]
                rotated_a = self.rotated(a, 49)
                a = [self.xor(rotated_a[i], t[i], t[i - 21] if i >= 21 else 0)
                     for i in range(64)]
                b = self.rotated(t, 28)
        if prefix_bits:
            for i in range(prefix_bits):
                var = initial[0][i]
                self.clauses.append([var if prefix >> i & 1 else -var])
        return initial, outputs

    def validate_witness(self):
        assert len(self.witness) == self.count
        assert all(any(self.witness[abs(v)] == (v > 0) for v in clause)
                   for clause in self.clauses), 'CNF clause mismatch'
        assert all((sum(self.witness[v] for v in terms) % 2 == int(rhs))
                   for terms, rhs in self.xors), 'XOR clause mismatch'

    def emit_to(self, solver):
        for terms, rhs in self.xors:
            solver.add_xor_clause(terms, rhs)
        for clause in self.clauses:
            solver.add_clause(clause)


def parse_source():
    original = (ROOT / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(original).hexdigest() == SOURCE_SHA
    rows = {}
    for line in original.decode('ascii').splitlines():
        if line.startswith('2026-'):
            stamp, *fields = line.split()
            rows[stamp] = dict(s.split('=', 1) for s in fields)
    assert len(rows) == 133
    trio = [rows[f'2026-10-03T18:0{minute}:00Z'] for minute in (1, 2, 3)]
    assert all(r['JOB'] == 'PS-261003-0417' and r['CLASS'] == 'RECOVER'
               for r in trio)
    assert [(r['ATTEMPT'], r['STATE']) for r in trio] == [
        ('1', 'REQUESTED'), ('2', 'ACK'), ('3', 'REQUESTED')]
    return [bytes.fromhex(r['PAYLOAD']) for r in trio]


def bits_to_int(bits, assignment):
    return sum((1 << i) for i, variable in enumerate(bits) if assignment[variable])


def solve(observed, limit, prefix_bits=0, prefix=0, uniqueness=True):
    from pycryptosat import Solver
    builder = XorCnf()
    initial, outputs = builder.build(observed, prefix_bits=prefix_bits, prefix=prefix)
    solver = Solver(time_limit=float(limit), threads=1)
    builder.emit_to(solver)
    start = time.monotonic()
    sat, assignment = solver.solve()
    result = {'status': 'SAT' if sat is True else 'UNSAT' if sat is False else 'UNKNOWN',
              'seconds': round(time.monotonic() - start, 3),
              'variables': builder.count, 'cnf_clauses': len(builder.clauses),
              'xor_clauses': len(builder.xors)}
    if sat is not True:
        return result
    state = tuple(bits_to_int(w, assignment) for w in initial)
    replay = stream(state)
    assert all(x is None or x == y for x, y in zip(observed, replay))
    result['state'] = [f'{w:016X}' for w in state]
    result['middle'] = [f'{w:016X}' for w in replay[2:4]]
    if uniqueness:
        middle_bits = outputs[2] + outputs[3]
        solver.add_clause([-v if assignment[v] else v for v in middle_bits])
        again, _ = solver.solve()
        result['middle_unique'] = True if again is False else False if again is True else None
    return result


def self_test():
    values = stream(SEED)
    builder = XorCnf()
    builder.build(values, seed=SEED, prefix_bits=16, prefix=SEED[0] & 65535)
    builder.validate_witness()
    assert all(encode(decode(bytes(range(16)), v), v) == bytes(range(16))
               for v in range(4))
    print(json.dumps({'self_test': 'PASS', 'variables': builder.count,
                      'cnf_clauses': len(builder.clauses),
                      'xor_clauses': len(builder.xors)}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--view', type=int, choices=range(4), default=0)
    parser.add_argument('--mode', choices=('flanks', 'dispatch'), default='flanks')
    parser.add_argument('--limit-seconds', type=float, default=120)
    parser.add_argument('--control-only', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--prefix-bits', type=int, default=0, choices=range(0, 21))
    parser.add_argument('--prefix', type=lambda x: int(x, 0), default=0)
    args = parser.parse_args()
    self_test()
    if args.self_test:
        return
    sample = stream(SEED)
    control = solve(sample, args.limit_seconds, uniqueness=False)
    print(json.dumps({'experiment': 'unrestricted_synthetic_six_output', **control}), flush=True)
    if control['status'] != 'SAT':
        print(json.dumps({'status': 'CONTROL_BLOCKED', 'source_evaluated': False}), flush=True)
        raise SystemExit(2)
    assert control['state'] == [f'{x:016X}' for x in SEED]
    if args.control_only:
        return
    source = parse_source()
    if args.mode == 'flanks':
        observed = [*decode(source[0], args.view), None, None,
                    *decode(source[2], args.view)]
    else:
        observed = [w for packet in source for w in decode(packet, args.view)]
    result = solve(observed, args.limit_seconds, args.prefix_bits, args.prefix)
    result.update({'experiment': 'original_source', 'mode': args.mode,
                   'view': args.view, 'prefix_bits': args.prefix_bits,
                   'source_sha256': SOURCE_SHA})
    if result['status'] == 'SAT':
        coupon = encode([int(w, 16) for w in result['middle']], args.view)
        if args.mode == 'dispatch':
            assert coupon == source[1]
            result['dispatch_consistency'] = True
        else:
            routing = json.loads((ROOT / 'evidence/recovery-routing.json').read_text())
            mask = bytes.fromhex(routing['K04']['masked_component'])
            component = bytes(x ^ y for x, y in zip(coupon, mask))
            acceptance = json.loads((ROOT / 'acceptance.json').read_text())
            hit = hashlib.sha256(component).hexdigest() == acceptance['slot_sha256']['K04']
            result.update({'coupon_hex': coupon.hex().upper(), 'K04_original_PASS': hit,
                           'component_if_pass': component.hex().upper() if hit else None})
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
