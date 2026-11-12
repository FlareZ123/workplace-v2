"""K04 source-pinned complete RS fragment reconstructor. Read-only SFT.

Hypothesis: one 16-byte copied printer field contains (16-p) contiguous
original coupon data bytes and p Reed-Solomon parity bytes. Recover the
remaining p coupon bytes algebraically before trying both literal and
route-mask-reduced original K04 commitments. The transport hypothesis is
exploratory and not asserted to be the actual printer format.

Run with Python 3 standard library:
  python agents/agent3/k04_rs_partial_codeword_sft.py
Or pass the unmodified extracted archive directory as argument.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


class GF:
    def __init__(self, polynomial):
        self.exp = [1] * 510
        self.log = [-1] * 256
        v = 1
        for i in range(255):
            assert self.log[v] == -1
            self.exp[i], self.log[v] = v, i
            v <<= 1
            if v & 256:
                v ^= polynomial
        assert v == 1
        for i in range(255, 510):
            self.exp[i] = self.exp[i - 255]

    def multiply(self, x, y):
        return self.exp[self.log[x] + self.log[y]] if x and y else 0

    def inverse(self, x):
        return self.exp[255 - self.log[x]]

    def power(self, exponent):
        return self.exp[exponent % 255]


def generator(g, parity_count, first_root):
    poly = [1]
    for exponent in range(first_root, first_root + parity_count):
        result = [0] * (len(poly) + 1)
        for j, value in enumerate(poly):
            result[j] ^= value
            result[j + 1] ^= g.multiply(value, g.power(exponent))
        poly = result
    return poly


def parity(data, g, poly):
    count = len(poly) - 1
    state = list(data) + [0] * count
    for i in range(len(data)):
        coefficient = state[i]
        for j, item in enumerate(poly):
            state[i + j] ^= g.multiply(coefficient, item)
    return bytes(state[-count:])


def solve(g, columns, right):
    size = len(right)
    rows = [[columns[j][i] for j in range(size)] + [right[i]] for i in range(size)]
    for j in range(size):
        pivot = next((k for k in range(j, size) if rows[k][j]), None)
        if pivot is None:
            raise ValueError("unexpected singular RS reconstruction")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        reciprocal = g.inverse(rows[j][j])
        rows[j] = [g.multiply(x, reciprocal) for x in rows[j]]
        for i in range(size):
            if i == j:
                continue
            factor = rows[i][j]
            if factor:
                rows[i] = [a ^ g.multiply(factor, b) for a, b in zip(rows[i], rows[j])]
    return bytes(row[size] for row in rows)


def decode(fragment, g, polynomial, first, reverse_data, reverse_parity, swap, columns):
    count = len(polynomial) - 1
    known_length = 16 - count
    if swap:
        checks, known = fragment[:count], fragment[count:]
    else:
        known, checks = fragment[:known_length], fragment[known_length:]
    if reverse_data:
        known = known[::-1]
    if reverse_parity:
        checks = checks[::-1]
    positions = range(first, first + known_length)
    missing = [i for i in range(16) if i not in positions]
    data = bytearray(16)
    for i, index in enumerate(positions):
        data[index] = known[i]
    reference = parity(data, g, polynomial)
    correction = bytes(a ^ b for a, b in zip(checks, reference))
    unknown = solve(g, [columns[index] for index in missing], correction)
    for i, index in enumerate(missing):
        data[index] = unknown[i]
    assert parity(data, g, polynomial) == checks
    return bytes(data)


def main():
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    assert bytes.fromhex(route["K04"]["masked_component"]) == MASK
    assert acceptance["slot_sha256"]["K04"] == TARGET
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    lines = [line for line in raw.splitlines() if b"PAYLOAD=" in line]
    records = [bytes.fromhex(re.search(rb"PAYLOAD=([0-9A-F]{32})", line)[1].decode()) for line in lines]
    assert len(records) == 133
    assert b"PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    assert records[129].hex() == "a9a9dc5731a5e2ae879c47215c2559d5"
    source_indexes = (117, 128, 129, 130, 131, 132)
    checked = 0
    layouts = 0
    planted = bytes((i * 19 + 231) % 256 for i in range(16))
    for primitive in (0x11D, 0x12D):
        gf = GF(primitive)
        for first_root in (0, 1):
            for count in range(1, 17):
                polynomial = generator(gf, count, first_root)
                columns = [
                    parity(bytes(int(i == j) for j in range(16)), gf, polynomial)
                    for i in range(16)
                ]
                for first in range(count + 1):
                    if count == 16 and first != 0:
                        continue
                    for rev_data in (False, True):
                        for rev_parity in (False, True):
                            for swap in (False, True):
                                if count == 16 and (rev_data or swap):
                                    continue
                                original = planted[first:first + 16 - count]
                                first_piece = original[::-1] if rev_data else original
                                ecc = parity(planted, gf, polynomial)
                                last_piece = ecc[::-1] if rev_parity else ecc
                                observed = (last_piece + first_piece) if swap else (first_piece + last_piece)
                                assert decode(observed, gf, polynomial, first, rev_data,
                                              rev_parity, swap, columns) == planted
                                layouts += 1
                                for index in source_indexes:
                                    coupon = decode(records[index], gf, polynomial, first,
                                                    rev_data, rev_parity, swap, columns)
                                    component = bytes(x ^ y for x, y in zip(coupon, MASK))
                                    checked += 1
                                    for stage, value in (("route-xor", component),
                                                         ("already-masked", coupon)):
                                        if hashlib.sha256(value).hexdigest() == TARGET:
                                            print("ORIGINAL K04 PASS", primitive, first_root,
                                                  count, first, rev_data, rev_parity, swap,
                                                  index, stage, value.hex().upper())
                                            return
    assert layouts == 4328 and checked == 25968, (layouts, checked)
    print("synthetic_complete_coupon_controls", layouts, "PASS")
    print("full_source_coupon_presentations", checked)
    print("original_K04_SHA256_comparisons", 2 * checked)
    print("original_K04_hits", 0)
    print("K04 and K08 remain unresolved under this specific physical fragment hypothesis")


if __name__ == "__main__":
    main()
