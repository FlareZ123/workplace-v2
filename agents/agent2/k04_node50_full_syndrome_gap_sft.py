"""H17 conditional source-exact node50 seq64..70 32-bit parity chronology test.

Uses original 132 intact printer packets and seven CRC-valid node50 rows.
The disputed K04 selected printer ACK2, its route mask, K04 acceptance digest
and final K08 caption are never used. No historical shared-generator assertion.
"""
import hashlib
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import source, get, untemper, Basis

REC_HASH = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"


def recorder_controls():
    raw = (ROOT / "resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REC_HASH
    assert raw[:8] == b"TRP2DUMP" and len(raw) == 16 + 88 * 24
    records = {}
    for i in range(88):
        body = raw[16 + i * 24:16 + (i + 1) * 24]
        _, node, _, _, seq, control, _, crc = struct.unpack("<IHBBIIII", body)
        if node == 50:
            assert zlib.crc32(body[:20]) == crc
            records[seq] = control
    assert set(records) == set(range(72))
    return records


def quotient(basis, vector):
    parity = 0
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in basis.rows:
            break
        row, rhs = basis.rows[pivot]
        vector ^= row
        parity ^= rhs
    return vector, parity


def add_equations(pivots, equations):
    inserted = []
    for vector, bit in equations:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (vector, bit)
                inserted.append(pivot)
                break
            previous_vector, previous_bit = pivots[pivot]
            vector ^= previous_vector
            bit ^= previous_bit
        if not vector and bit:
            for pivot in inserted:
                del pivots[pivot]
            return None
    return inserted


def compatible(quotients, native):
    equations = [(vector, rhs ^ ((native >> bit) & 1))
                 for bit, (vector, rhs) in enumerate(quotients)]
    return add_equations({}, equations) is not None


def temper_word(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    x ^= x >> 18
    return x & 0xffffffff


def enumerate_paths(options, originals, quotients, minimum, maximum):
    pivots = {}
    path = []
    complete = []

    def dfs(sequence):
        if sequence == 71:
            complete.append(tuple(path))
            return
        native = untemper(originals[sequence])
        for stage in options[sequence]:
            if path and not minimum <= stage - path[-1] <= maximum:
                continue
            equations = [(v, c ^ ((native >> bit) & 1))
                         for bit, (v, c) in enumerate(quotients[stage])]
            added = add_equations(pivots, equations)
            if added is None:
                continue
            path.append(stage)
            dfs(sequence + 1)
            path.pop()
            for pivot in added:
                del pivots[pivot]

    dfs(64)
    return complete


def target_independent(basis, vectors, originals, path):
    joint = Basis()
    joint.rows = dict(basis.rows)
    joint.rank = basis.rank
    for sequence, stage in zip(range(64, 71), path):
        native = untemper(originals[sequence])
        for bit, equation in enumerate(get(vectors, stage)):
            joint.insert(equation, (native >> bit) & 1)
    augmented = Basis()
    augmented.rows = {p: (equation, 0) for p, (equation, _) in joint.rows.items()}
    augmented.rank = joint.rank
    for stage in range(951, 955):
        for equation in get(vectors, stage):
            augmented.insert(equation, 0)
    return joint.rank, augmented.rank - joint.rank


def main():
    basis, vectors = source(ROOT / "resources")
    assert basis.rank == 15365
    originals = recorder_controls()
    stages = range(-390, -338)
    quotients = {stage: [quotient(basis, vector) for vector in get(vectors, stage)]
                 for stage in stages}
    options = {
        sequence: [stage for stage in stages
                   if compatible(quotients[stage], untemper(originals[sequence]))]
        for sequence in range(64, 71)
    }
    assert -390 in options[64] and -339 in options[70]
    options[64] = [-390]
    options[70] = [-339]

    # Source-positive original and induced source-incompatible one-bit negative.
    native = untemper(originals[64])
    assert compatible(quotients[-390], native)
    bad = [native ^ (1 << bit) for bit in range(32)
           if not compatible(quotients[-390], native ^ (1 << bit))]
    assert bad and not compatible(quotients[-390], bad[0])
    assert temper_word(untemper(originals[64])) == originals[64]

    assert [len(options[i]) for i in range(64, 71)] == [1, 8, 8, 8, 8, 8, 1]
    assert len(enumerate_paths(options, originals, quotients, 1, 26)) == 0
    successful = enumerate_paths(options, originals, quotients, 1, 27)
    assert len(successful) == 8, len(successful)
    assert all(path[0] == -390 and path[-1] == -339 for path in successful)
    assert len(enumerate_paths(options, originals, quotients, 3, 51)) == 0
    distinct = sorted({target_independent(basis, vectors, originals, path)
                       for path in successful})
    assert all(unknown == 128 for _, unknown in distinct), distinct
    print("ORIGINAL CRC/SHA POSITIVE: PASS")
    print("FULL 32-BIT PARITY NEGATIVE CONTROL: PASS")
    print("model conditional: p951/MT19937, native source row129 withheld")
    print("node50 source intervals seq64=-390, seq70=-339 fixed")
    print("valid individual stage counts", [len(options[i]) for i in range(64, 71)])
    print("max gap <=26, min gap=1: 0 joint-compatible stage paths")
    print("max gap 27, min gap=1: 8 joint-compatible stage paths")
    print("min gap >=3, max gap up to 51: 0 joint-compatible stage paths")
    print("eight exact seven-record histories:")
    for path in successful:
        print(" ", path)
    print("joint source rank/selected unknown bits:", distinct)
    print("K04 original recovered: NO; K08 original recovered: NO")


if __name__ == "__main__":
    main()
