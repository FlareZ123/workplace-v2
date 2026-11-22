"""Bounded 193-bit future-donor carrier search for H-17 K04.

Conditional p951 MT19937 geometry. Uses the 132 intact original spool
packets only; selected ACK2 row129 is withheld. Searches the eight original
16-byte source families from the prior seven-word carrier test, using the
six-full-words-plus-one-bit sufficient donor set.
"""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "mt_source", ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
mt.LAST = 1578
basis, states = mt.source(ROOT / "resources")
assert basis.rank == 15365

SOURCE = {
    "K01-WN14": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K05-TRP2": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06-RC17": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K04-ROUTE-MASK": "8556C8CB6140A7F9A5123AC7571BEE1C",
    "K08-DESK-NONCE": "5F933DA6A1BD03C32DA5CBC25344F497",
    "K02-LT204-HASH": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03-PTW-HASH": "1384AF96E25D6ADA666209CB55E062FA",
    "K07-AX-HASH": "93495F5E425AB8E592123DABAEB68545",
}
SOURCE = {name: bytes.fromhex(value) for name, value in SOURCE.items()}
MASK = SOURCE["K04-ROUTE-MASK"]
K04_TARGET = bytes.fromhex(
    "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
)
FULL_STAGES = (1180, 1181, 1347, 1348, 1574, 1575)
PARTIAL_BITS = ("native31", "temp2", "temp9", "temp13",
                "temp20", "temp27", "temp31")


class DonorMap:
    def __init__(self, source_basis):
        # Coefficient bit 0 is the affine constant; bits 1..193 are
        # the six complete donor words followed by the partial donor bit.
        self.rows = {
            pivot: (expr, constant)
            for pivot, (expr, constant) in source_basis.rows.items()
        }
        self.syndromes = []

    def insert(self, state_expr, coefficient):
        while state_expr:
            pivot = state_expr.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = (state_expr, coefficient)
                return
            equation, coeff = self.rows[pivot]
            state_expr ^= equation
            coefficient ^= coeff
        if coefficient:
            self.syndromes.append(coefficient)

    def reduce(self, state_expr):
        coefficient = 0
        while state_expr:
            pivot = state_expr.bit_length() - 1
            equation, coeff = self.rows[pivot]
            state_expr ^= equation
            coefficient ^= coeff
        return coefficient


def evaluate(donor_bits, coefficient):
    return (((donor_bits << 1) & coefficient).bit_count() & 1) ^ (coefficient & 1)


def temper_number(value):
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    value ^= value >> 18
    return value & 0xFFFFFFFF


def native_words(carrier, encoding):
    # bit 0: big-endian words; bit 1: carrier words are tempered;
    # bit 2: reverse the four-word order.
    words = [
        int.from_bytes(carrier[i:i + 4], "big" if encoding & 1 else "little")
        for i in (0, 4, 8, 12)
    ]
    if encoding & 4:
        words.reverse()
    if encoding & 2:
        words = [mt.untemper(word) for word in words]
    return words


def build_map(partial):
    donor = DonorMap(basis)
    for donor_index, stage in enumerate(FULL_STAGES):
        for bit, expr in enumerate(mt.get(states, stage)):
            donor.insert(expr, 1 << (donor_index * 32 + bit + 1))
    if partial == "native31":
        expression = mt.get(states, 1179)[31]
    else:
        bit = int(partial[4:])
        expression = mt.temper(mt.get(states, 1179))[bit]
    donor.insert(expression, 1 << (192 + 1))
    targets = [
        donor.reduce(expr)
        for stage in range(951, 955)
        for expr in mt.get(states, stage)
    ]
    assert len(targets) == 128
    assert len(donor.syndromes) == 1
    return donor, targets


def component_from_bits(donor_bits, targets):
    coupon = b"".join(
        temper_number(sum(
            evaluate(donor_bits, targets[lane * 32 + bit]) << bit
            for bit in range(32)
        )).to_bytes(4, "little")
        for lane in range(4)
    )
    return bytes(left ^ right for left, right in zip(coupon, MASK))


def source_completion():
    assignment = 0
    for pivot, (expr, constant) in sorted(basis.rows.items()):
        if constant ^ ((expr & assignment).bit_count() & 1):
            assignment |= 1 << pivot
    return assignment


def run():
    started = time.monotonic()
    maps = {partial: build_map(partial) for partial in PARTIAL_BITS}
    assert all(len(d.syndromes) == 1 for d, _ in maps.values())

    # Positive control: a genuine source-compatible synthetic state must
    # reconstruct the exact withheld synthetic coupon from the 193-bit view.
    assignment = source_completion()

    def native(stage):
        return sum(
            ((expr & assignment).bit_count() & 1) << bit
            for bit, expr in enumerate(mt.get(states, stage))
        )

    for partial, (donor_map, targets) in maps.items():
        full = [native(stage) for stage in FULL_STAGES]
        word1179 = native(1179)
        partial_value = (
            (word1179 >> 31) & 1 if partial == "native31"
            else (temper_number(word1179) >> int(partial[4:])) & 1
        )
        donor_bits = sum(value << (32 * i) for i, value in enumerate(full))
        donor_bits |= partial_value << 192
        assert all(evaluate(donor_bits, row) == 0
                   for row in donor_map.syndromes)
        recovered = component_from_bits(donor_bits, targets)
        actual_coupon = b"".join(
            temper_number(native(stage)).to_bytes(4, "little")
            for stage in range(951, 955)
        )
        expected = bytes(a ^ b for a, b in zip(actual_coupon, MASK))
        assert recovered == expected
    print("193-bit synthetic positive controls: PASS (7/7 partial-bit views)")

    views = {
        (name, encoding): native_words(value, encoding)
        for name, value in SOURCE.items()
        for encoding in range(8)
    }
    assignments = 0
    source_compatible = 0
    matches = []
    for names in itertools.permutations(SOURCE, 3):
        for encodings in itertools.product(range(8), repeat=3):
            left, middle, right = (
                views[(name, encoding)]
                for name, encoding in zip(names, encodings)
            )
            full = (
                left[1], left[2],
                middle[0], middle[1],
                right[0], right[1],
            )
            for partial in PARTIAL_BITS:
                donor_map, targets = maps[partial]
                partial_value = (
                    (left[0] >> 31) & 1 if partial == "native31"
                    else (temper_number(left[0]) >> int(partial[4:])) & 1
                )
                donor_bits = sum(
                    value << (32 * index)
                    for index, value in enumerate(full)
                ) | (partial_value << 192)
                assignments += 1
                if any(evaluate(donor_bits, row)
                       for row in donor_map.syndromes):
                    continue
                source_compatible += 1
                component = component_from_bits(donor_bits, targets)
                if hashlib.sha256(component).digest() == K04_TARGET:
                    matches.append({
                        "sources": names,
                        "encodings": encodings,
                        "partial_bit": partial,
                        "component": component.hex().upper(),
                    })
                    print("ORIGINAL K04 COMMITMENT MATCH", matches[-1])

    assert assignments == 1_204_224
    assert source_compatible == 610_176
    assert len(matches) == 0
    print({
        "source_rank": basis.rank,
        "full_donor_stages": FULL_STAGES,
        "partial_donor_stage": 1179,
        "partial_bit_views": PARTIAL_BITS,
        "distinct_source_families_per_assignment": 3,
        "word_views_per_source": 8,
        "assignments": assignments,
        "source_compatible": source_compatible,
        "K04_commitment_matches": len(matches),
        "elapsed_seconds": round(time.monotonic() - started, 2),
    })


if __name__ == "__main__":
    run()
