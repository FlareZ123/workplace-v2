"""Meet-in-middle native XOR SAT for the H17 K04 xoroshiro128++ flank model.

Inverts each known flank's first 64-bit output algebraically and joins
forward/backward GF(2)-linear states at the hidden middle packet.
The disputed attempt-2 ACK is completely withheld from inversion.
"""
import argparse
import hashlib
import json
import time
from k04_xoroshiropp_xorcnf_sft import (
    XorCnf, SEED, ROOT, SOURCE_SHA, decode, encode, parse_source, rol, stream,
)

MASK = (1 << 64) - 1


def states(seed):
    a, b = seed
    result = [(a, b)]
    for _ in range(5):
        t = a ^ b
        a = (rol(a, 49) ^ t ^ (t << 21)) & MASK
        b = rol(t, 28)
        result.append((a, b))
    return result


class MeetCircuit(XorCnf):
    def invert(self, x):
        out = self.variable(not self.witness[x] if x in self.witness else None)
        self.xors.append(([x, out], True))
        return out

    def sub64(self, a, b):
        not_b = [self.invert(x) for x in b]
        carry = self.variable(True)
        self.clauses.append([carry])
        output = []
        for i in range(64):
            output.append(self.xor(a[i], not_b[i], carry))
            if i < 63:
                carry = self.majority(a[i], not_b[i], carry)
        return output

    def get_state_from_output(self, a, y):
        vals = self.word(y)
        self.constrain(vals, y)
        intermediate = self.sub64(vals, a)
        return self.sub64(self.rotated(intermediate, -17), a)

    def step(self, a, b):
        t = [self.xor(x, y) for x, y in zip(a, b)]
        ra = self.rotated(a, 49)
        return ([self.xor(ra[i], t[i], t[i - 21] if i >= 21 else 0)
                 for i in range(64)], self.rotated(t, 28))

    def backward(self, a1, b1):
        t = self.rotated(b1, -28)
        a = self.rotated([
            self.xor(a1[i], t[i], t[i - 21] if i >= 21 else 0)
            for i in range(64)
        ], -49)
        return a, [self.xor(x, y) for x, y in zip(a, t)]

    def constrain_equal(self, x, y):
        for a, b in zip(x, y):
            self.xors.append(([a, b], False))

    def output(self, a, b):
        return self.add64(self.rotated(self.add64(a, b), 17), a)

    def build_meet(self, observed, seed=None, prefix_bits=0, prefix=0):
        assert all(observed[i] is not None for i in (0, 1, 4, 5))
        seeded = states(seed) if seed is not None else None
        a0 = self.word(None if seeded is None else seeded[0][0])
        b0 = self.get_state_from_output(a0, observed[0])
        a4 = self.word(None if seeded is None else seeded[4][0])
        b4 = self.get_state_from_output(a4, observed[4])
        initial = (a0, b0)
        state1 = self.step(*initial)
        state2early = self.step(*state1)
        state3late = self.backward(a4, b4)
        state2late = self.backward(*state3late)
        for x, y in zip(state2early, state2late):
            self.constrain_equal(x, y)
        state5 = self.step(a4, b4)
        self.constrain(self.output(*state1), observed[1])
        self.constrain(self.output(*state5), observed[5])
        middle = [self.output(*state2early), self.output(*state3late)]
        for index, pair in ((2, 0), (3, 1)):
            if observed[index] is not None:
                self.constrain(middle[pair], observed[index])
        for i in range(prefix_bits):
            self.clauses.append([a0[i] if (prefix >> i) & 1 else -a0[i]])
        return initial, middle


def test_circuit():
    outputs = stream(SEED)
    bracket = [*outputs[:2], None, None, *outputs[4:]]
    circuit = MeetCircuit()
    circuit.build_meet(bracket, seed=SEED, prefix_bits=16, prefix=SEED[0] & 65535)
    circuit.validate_witness()
    print(json.dumps({'self_test': 'PASS', 'variables': circuit.count,
                      'cnf_clauses': len(circuit.clauses),
                      'xor_clauses': len(circuit.xors)}), flush=True)


def solve(observed, seconds, prefix_bits=0, prefix=0):
    from pycryptosat import Solver
    circuit = MeetCircuit()
    initial, _ = circuit.build_meet(observed, prefix_bits=prefix_bits, prefix=prefix)
    solver = Solver(time_limit=float(seconds), threads=1)
    circuit.emit_to(solver)
    start = time.monotonic()
    sat, assignment = solver.solve()
    result = {'status': 'SAT' if sat is True else 'UNSAT' if sat is False else 'UNKNOWN',
              'seconds': round(time.monotonic() - start, 3), 'variables': circuit.count,
              'cnf_clauses': len(circuit.clauses), 'xor_clauses': len(circuit.xors)}
    if sat is True:
        state = tuple(sum((1 << i) for i, v in enumerate(word) if assignment[v])
                      for word in initial)
        values = stream(state)
        assert all(x is None or x == y for x, y in zip(observed, values))
        result['state'] = [f'{w:016X}' for w in state]
        result['middle'] = [f'{w:016X}' for w in values[2:4]]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--view', type=int, choices=range(4), default=0)
    parser.add_argument('--limit-seconds', type=float, default=90)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--control-only', action='store_true')
    parser.add_argument('--control-prefix-bits', type=int, choices=range(0, 21), default=16)
    parser.add_argument('--control-negative', action='store_true')
    parser.add_argument('--prefix-bits', type=int, default=0, choices=range(0, 21))
    parser.add_argument('--prefix', type=lambda x: int(x, 0), default=0)
    args = parser.parse_args()
    test_circuit()
    if args.self_test:
        return
    samples = stream(SEED)
    planted = [*samples[:2], None, None, *samples[4:]]
    planted_bits = args.control_prefix_bits
    selected_prefix = (SEED[0] & ((1 << planted_bits) - 1)) ^ int(args.control_negative)
    control = solve(planted, args.limit_seconds, planted_bits, selected_prefix)
    print(json.dumps({'experiment': 'seeded_prefix_negative' if args.control_negative
                      else 'seeded_prefix_positive',
                      'prefix_bits': planted_bits, 'prefix': selected_prefix,
                      **control}), flush=True)
    if args.control_negative:
        if control['status'] != 'UNSAT':
            raise SystemExit(2)
    elif control['status'] != 'SAT' or control['middle'] != [f'{x:016X}' for x in samples[2:4]]:
        raise SystemExit(2)
    if args.control_only:
        return
    rows = parse_source()
    observed = [*decode(rows[0], args.view), None, None,
                *decode(rows[2], args.view)]
    original = solve(observed, args.limit_seconds, args.prefix_bits, args.prefix)
    result = {'experiment': 'original_REQUESTED_flanks', 'view': args.view,
              'prefix_bits': args.prefix_bits, 'prefix': args.prefix,
              'full_domain_tested': args.prefix_bits == 0,
              'source_sha256': SOURCE_SHA, **original}
    if original['status'] == 'SAT':
        payload = encode([int(x, 16) for x in original['middle']], args.view)
        routing = json.loads((ROOT / 'evidence/recovery-routing.json').read_text())
        mask = bytes.fromhex(routing['K04']['masked_component'])
        component = bytes(x ^ y for x, y in zip(payload, mask))
        acceptance = json.loads((ROOT / 'acceptance.json').read_text())
        hit = hashlib.sha256(component).hexdigest() == acceptance['slot_sha256']['K04']
        result.update({'coupon_hex': payload.hex().upper(), 'K04_original_PASS': hit,
                       'component_if_PASS': component.hex().upper() if hit else None})
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
