"""H-17 K04 selected-ACK-withheld seven-future-word source-cohort falsifier.

Conditionally assign three ordered original 16-byte carriers to sufficient
native MT stage groups (1179,1180,1181), (1347,1348), (1574,1575).
Includes a genuine source-compatible synthetic completion to validate projection.
The historic producer and stage links are hypotheses, never attested.
"""
from pathlib import Path
import sys
import hashlib
import itertools
import time

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1] / "agent49"))
import k04_p951_symbolic_basis as mt

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
SOURCE = {k: bytes.fromhex(v) for k, v in SOURCE.items()}
STAGES = [1179, 1180, 1181, 1347, 1348, 1574, 1575]
MASK = SOURCE["K04-ROUTE-MASK"]
K04_TARGET = bytes.fromhex(
    "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
)


class SymbolicDonor:
    def __init__(self, source_basis):
        # Coefficient low bit is the source affine constant; bit j+1 is
        # observed donor bit j. Original source rows have donor mask zero.
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
            eq, coeff = self.rows[pivot]
            state_expr ^= eq
            coefficient ^= coeff
        if coefficient:
            self.syndromes.append(coefficient)

    def reduce(self, state_expr):
        coefficient = 0
        while state_expr:
            pivot = state_expr.bit_length() - 1
            eq, coeff = self.rows[pivot]
            state_expr ^= eq
            coefficient ^= coeff
        return coefficient


def evaluate(donor_bits, coefficient):
    return (((donor_bits << 1) & coefficient).bit_count() & 1) ^ (coefficient & 1)


def native_words(four_word_carrier, encoding):
    # encoding: bit2 reversed four-word order; bit0 big endian; bit1 tempered.
    words = [
        int.from_bytes(four_word_carrier[i : i + 4], "big" if (encoding & 1) else "little")
        for i in (0, 4, 8, 12)
    ]
    if encoding & 4:
        words.reverse()
    if encoding & 2:
        words = [mt.untemper(word) for word in words]
    return words


def temper_number(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & 0xFFFFFFFF


def source_completion(basis):
    # Construct a genuine homogeneous-state completion of the source
    # equations with free initial-register bits set to zero.
    assignment = 0
    for pivot, (expr, constant) in sorted(basis.rows.items()):
        bit = constant ^ ((expr & assignment).bit_count() & 1)
        if bit:
            assignment |= 1 << pivot
    for pivot, (expr, constant) in basis.rows.items():
        assert (expr & assignment).bit_count() & 1 == constant
    return assignment


def run():
    started = time.monotonic()
    mt.LAST = 1578
    basis, symbol = mt.source(ROOT / "resources")
    assert basis.rank == 15365
    source_assignment = source_completion(basis)
    donor = SymbolicDonor(basis)
    for donor_index, stage in enumerate(STAGES):
        for bit, expr in enumerate(mt.get(symbol, stage)):
            donor.insert(expr, 1 << (donor_index * 32 + bit + 1))
    assert len(donor.syndromes) == 31
    targets = [
        donor.reduce(expr)
        for stage in range(951, 955)
        for expr in mt.get(symbol, stage)
    ]
    assert len(targets) == 128

    def evaluate_component(donor_values):
        bits = sum(value << (32 * j) for j, value in enumerate(donor_values))
        if any(evaluate(bits, expr) for expr in donor.syndromes):
            return None
        coupon = b"".join(
            temper_number(sum(
                evaluate(bits, targets[lane * 32 + bit]) << bit
                for bit in range(32)
            )).to_bytes(4, "little")
            for lane in range(4)
        )
        return bytes(x ^ y for x, y in zip(coupon, MASK))

    planted = [
        sum(((expr & source_assignment).bit_count() & 1) << bit
            for bit, expr in enumerate(mt.get(symbol, stage)))
        for stage in STAGES
    ]
    synthetic = evaluate_component(planted)
    actual_native = [
        sum(((expr & source_assignment).bit_count() & 1) << bit
            for bit, expr in enumerate(mt.get(symbol, stage)))
        for stage in range(951, 955)
    ]
    expected = bytes(
        x ^ y for x, y in zip(
            b"".join(temper_number(x).to_bytes(4, "little") for x in actual_native),
            MASK,
        )
    )
    assert synthetic == expected
    altered = planted.copy()
    altered[0] ^= 1 << 15
    assert evaluate_component(altered) is None
    print("Positive test: genuine source-complete seven donors reconstruct withheld synthetic coupon")
    print("Negative test: one-bit donor alteration violates source equations")

    assignments = 0
    source_compatible = 0
    original_matches = 0
    for names in itertools.permutations(SOURCE, 3):
        for encodings in itertools.product(range(8), repeat=3):
            groups = [native_words(SOURCE[name], encoding)
                      for name, encoding in zip(names, encodings)]
            values = groups[0][:3] + groups[1][:2] + groups[2][:2]
            assignments += 1
            component = evaluate_component(values)
            if component is None:
                continue
            source_compatible += 1
            if hashlib.sha256(component).digest() == K04_TARGET:
                original_matches += 1
                print("ORIGINAL K04 MATCH", names, encodings, component.hex().upper())

    assert assignments == 172032
    assert source_compatible == 0
    assert original_matches == 0
    print({
        "source_rank": basis.rank,
        "seven_future_stage": STAGES,
        "source_syndromes": len(donor.syndromes),
        "complete_carrier_assignments": assignments,
        "source_compatible": source_compatible,
        "K04_matches": original_matches,
        "seconds": round(time.monotonic() - started, 2),
    })


if __name__ == "__main__":
    run()
