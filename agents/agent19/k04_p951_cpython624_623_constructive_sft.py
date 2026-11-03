"""H17 original-source-pinned p951 CPython initializer experiment.

Pure Python stdlib single-file test. Row129 excluded before hex payload decoding.
624-word integer seeds construct all desired selected bytes; 623-word seed
requires a parity identity contradicted by the 132 intact original packets.
The printer's actual generator and physical coupon remain historically unknown.
"""
from __future__ import annotations

import hashlib
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == SHA
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
lines = [line for line in SPOOL.read_text().splitlines() if "PAYLOAD=" in line]
assert len(lines) == len(STARTS) == 133
payloads = [None if i == 129 else bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1)) for i, line in enumerate(lines)]
assert payloads[129] is None and all(p is None or len(p) == 16 for p in payloads)
U = 0xFFFFFFFF
M1, M2 = 1664525, 1566083941


def mix(x, factor):
    return ((x ^ (x >> 30)) * factor) & U


BASE = [19650218]
for i in range(1, 624):
    BASE.append((1812433253 * (BASE[-1] ^ (BASE[-1] >> 30)) + i) & U)


def untemper(x):
    for shift, left, mask in ((18, False, U), (15, True, 0xEFC60000),
                              (7, True, 0x9D2C5680), (11, False, U)):
        y = x
        for _ in range(6):
            y = x ^ (((y << shift) & mask) if left else (y >> shift))
        x = y & U
    return x


def reduce(eq, basis):
    while eq:
        pivot = eq.bit_length() - 1
        if pivot not in basis:
            break
        eq ^= basis[pivot]
    return eq


def symbolic_states():
    states = [[1 << (32 * i + bit) for bit in range(32)] for i in range(624)]
    for i in range(624, 1591):
        p, n, q = states[i - 624], states[i - 623], states[i - 227]
        states.append([
            q[b] ^ (p[31] if b == 30 else n[b + 1] if b < 30 else 0)
            ^ (n[0] if ((0x9908B0DF >> b) & 1) else 0)
            for b in range(32)
        ])
    return states


expressions = symbolic_states()
basis = {}
for index, (payload, start) in enumerate(zip(payloads, STARTS)):
    if payload is None:
        continue
    for lane in range(4):
        value = untemper(int.from_bytes(payload[lane * 4:lane * 4 + 4], "little"))
        for bit, expr in enumerate(expressions[624 + start + lane]):
            rem = reduce((expr << 1) | ((value >> bit) & 1), basis)
            assert rem != 1, ("original-source contradiction", index, lane)
            if rem > 1:
                basis[rem.bit_length() - 1] = rem
assert len(basis) == 15365
for bit in range(32):
    rem = reduce((1 << (bit + 1)) | ((0x80000000 >> bit) & 1), basis)
    assert rem != 1
    if rem > 1:
        basis[rem.bit_length() - 1] = rem
assert len(basis) == 15397
assert 19968 - len(basis) == 4571


def initial_solution(equations):
    value = 0  # all free native state bits zero
    for pivot, row in sorted(equations.items()):
        tail = (row ^ (1 << pivot)) >> 1
        assigned = (row & 1) ^ ((tail & value).bit_count() & 1)
        value |= assigned << (pivot - 1)
    return value


def initialized_register(statebits):
    return tuple((statebits >> (32 * i)) & U for i in range(624))


def actual_register(seed):
    state = random.Random(seed).getstate()
    assert state[0] == 3 and state[1][-1] == 624
    return tuple(state[1][:-1])


def pre_second_register(register):
    x = list(register)
    x[1] = ((register[1] + 1) ^ mix(register[623], M2)) & U
    for i in range(623, 1, -1):
        x[i] = ((register[i] + i) ^ mix(x[i - 1], M2)) & U
    return x


def inverse_seed624(register, first_word=0):
    """Invert both initializer diffusion loops for a 624-word integer seed."""
    assert register[0] == 0x80000000
    x = pre_second_register(register)
    a = (BASE[1] ^ mix(BASE[0], M1)) & U
    keys = [0] * 624
    keys[0] = (first_word - a) & U
    keys[1] = (x[2] - (BASE[2] ^ mix(first_word, M1)) - 1) & U
    for i in range(3, 624):
        keys[i - 1] = (x[i] - (BASE[i] ^ mix(x[i - 1], M1)) - (i - 1)) & U
    keys[623] = (x[1] - (first_word ^ mix(x[623], M1)) - 623) & U
    assert keys[623] != 0
    seed = int.from_bytes(b"".join(k.to_bytes(4, "little") for k in keys), "little")
    assert actual_register(seed) == tuple(register)
    return seed


def selected_from_actual_seed(seed):
    py = random.Random(seed)
    output = [py.getrandbits(32) for _ in range(max(STARTS) + 4)]
    selected = None
    for i, (source, start) in enumerate(zip(payloads, STARTS)):
        packet = b"".join(w.to_bytes(4, "little") for w in output[start:start + 4])
        if source is None:
            selected = packet
        else:
            assert packet == source, ("original packet mismatch", i)
    return selected


def extend_to_selected(target):
    extended = basis.copy()
    for lane in range(4):
        native = untemper(int.from_bytes(target[lane * 4:lane * 4 + 4], "little"))
        for bit, expr in enumerate(expressions[624 + 951 + lane]):
            rem = reduce((expr << 1) | ((native >> bit) & 1), extended)
            assert rem != 1, "selected packet is independently selectable"
            if rem > 1:
                extended[rem.bit_length() - 1] = rem
    assert len(extended) - len(basis) == 128
    return initialized_register(initial_solution(extended))


def fixed_bit(i, bit):
    residue = reduce(1 << (32 * i + bit + 1), basis)
    assert residue in (0, 1), ("source did not fix", i, bit)
    return residue


def seed623_parity_certificate():
    # A 623-word seed repeats key[0] on the 624th injection at cyclic j=0.
    s1bit = fixed_bit(1, 0)
    s622 = sum(fixed_bit(622, bit) << bit for bit in range(32))
    s623_low31 = sum(fixed_bit(623, bit) << bit for bit in range(31))
    assert s1bit == 1 and s622 == 0xBBD5A4AB and s623_low31 == 0x04710790
    a = BASE[1] ^ mix(BASE[0], M1)
    for high in (0, 1):
        s623 = s623_low31 | (high << 31)
        x623 = (((s623 + 623) & U) ^ mix(s622, M2)) & U
        b = mix(x623, M1)
        x1_low = (s1bit ^ 1) ^ (mix(s623, M2) & 1)
        c_low = x1_low ^ (a & 1)
        assert (b & 1) == 0 and c_low == 1
    print("PASS 623-key impossibility: original fixed bits demand B0=0 and C0=1")


def solve_repeated_first_key(b, c):
    states = {0: 0}  # incoming carry -> low-word candidate
    for bit in range(32):
        nxt = {}
        for carry, y in states.items():
            for xbit in (0, 1):
                s = xbit + (xbit ^ ((b >> bit) & 1)) + carry
                if (s & 1) == ((c >> bit) & 1):
                    nxt[s >> 1] = y | (xbit << bit)
        states = nxt
        if not states:
            return None
    result = next(iter(states.values()))
    assert ((result + (result ^ b)) & U) == c
    return result


def inverse_seed623_test(register):
    x = pre_second_register(register)
    a = BASE[1] ^ mix(BASE[0], M1)
    b = mix(x[623], M1)
    c = (x[1] + a) & U
    first = solve_repeated_first_key(b, c)
    if first is None:
        return None
    keys = [0] * 623
    keys[0] = (first - a) & U
    keys[1] = (x[2] - (BASE[2] ^ mix(first, M1)) - 1) & U
    for i in range(3, 624):
        keys[i - 1] = (x[i] - (BASE[i] ^ mix(x[i - 1], M1)) - (i - 1)) & U
    if not keys[-1]:
        return None
    assert ((x[1] - (first ^ b)) & U) == keys[0]
    seed = int.from_bytes(b"".join(k.to_bytes(4, "little") for k in keys), "little")
    assert actual_register(seed) == tuple(register)
    return seed


def main():
    rng = random.Random(0x484317)
    for i in range(10):
        seed = (1 << (624 * 32 - 1)) | rng.getrandbits(624 * 32 - 1)
        if i & 1:
            original = (0x80000000,) + tuple(rng.getrandbits(32) for _ in range(623))
        else:
            original = actual_register(seed)
        recovered = inverse_seed624(original)
        assert actual_register(recovered) == original
    print("PASS 10/10 original-seeded and arbitrary-register 624-word inverse controls")
    for target in (bytes(16), bytes([0xFF]) * 16, bytes([0xAA]) * 16):
        selected = selected_from_actual_seed(inverse_seed624(extend_to_selected(target)))
        assert selected == target
        print("PASS 624-word target completion", target.hex().upper(), "132/132 original controls")
    seed623_parity_certificate()
    for _ in range(10):
        seed = (1 << (623 * 32 - 1)) | rng.getrandbits(623 * 32 - 1)
        reg = actual_register(seed)
        recovered = inverse_seed623_test(reg)
        assert recovered is not None and actual_register(recovered) == reg
    print("PASS 10/10 independently CPython-seeded 623-word inverse controls")
    print("CONDITIONAL ONLY: actual original K04 selected coupon remains unknown")


if __name__ == "__main__":
    main()
