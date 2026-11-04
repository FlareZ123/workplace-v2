"""Original H-17 node49 cross-record MT-stage lattice, selected K04 withheld.

Single-file test: python agents/agent6/k04_node49_lattice_sft.py
Requires original resources and existing Agent49 symbolic-source module.
All statements conditional on unverified p951 MT first-cycle geometry.
"""
import hashlib
import random
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, get, source, temper, untemper

REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
ORIGINAL_MATCH = [
    (990, -322, 32), (201, -321, 32), (901, -320, 32),
    (991, -319, 13), (992, -316, 32), (203, -315, 32),
    (903, -314, 32), (993, -313, 26),
]


def read_node49():
    raw = (ROOT / "resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REC_SHA
    assert raw[:8] == b"TRP2DUMP" and len(raw) == 16 + 88 * 24
    data = {}
    for i in range(88):
        packet = raw[16 + 24 * i:16 + 24 * (i + 1)]
        _, node, event, latch, seq = struct.unpack_from("<IHBBI", packet)
        control, aux, crc = struct.unpack_from("<III", packet, 12)
        if node == 49:
            data[seq] = (control, zlib.crc32(packet[:20]) == crc, latch, event, aux)
    assert set(data) == {n + i for n in (200, 300, 900, 990) for i in range(4)}
    assert all(data[seq][2] == seq % 100 for seq in data)
    return data


def slot_projection(basis, symbolic):
    span = Basis()
    span.rows = {pivot: (equation, 0) for pivot, (equation, _) in basis.rows.items()}
    span.rank = basis.rank
    for stage in range(951, 955):
        for equation in get(symbolic, stage):
            span.insert(equation, 0)
    return span.rank - basis.rank


def stage_mask(basis, symbolic, stage):
    mask = value = 0
    for bit, equation in enumerate(temper(get(symbolic, stage))):
        answer = basis.predict(equation)
        if answer is not None:
            mask |= 1 << bit
            value |= answer << bit
    return mask, value


def add_rows(basis, symbolic, rows, include_bad_crc):
    extension = Basis()
    extension.rows = dict(basis.rows)
    extension.rank = basis.rank
    for seq, stage in rows:
        control, crc_ok, _, _, _ = read[seq]
        if not crc_ok and not include_bad_crc:
            continue
        native = untemper(control)
        for bit, equation in enumerate(get(symbolic, stage)):
            extension.insert(equation, (native >> bit) & 1)
    return extension


def main():
    global read
    read = read_node49()
    basis, symbolic = source(ROOT / "resources")
    assert basis.rank == 15365
    rows = [(n + i, -324 + 3 * i + j)
            for i in range(4) for j, n in enumerate((200, 900, 990))]
    masks = [stage_mask(basis, symbolic, stage) for _, stage in rows]
    actual = []
    for (seq, stage), (mask, expected) in zip(rows, masks):
        control, crc_ok, latch, event, aux = read[seq]
        assert event == 82
        assert (crc_ok is False) == (900 <= seq <= 903)
        assert ((control ^ expected) & mask) == 0
        if mask.bit_count() >= 11:
            actual.append((seq, stage, mask.bit_count()))
    assert actual == ORIGINAL_MATCH, actual

    original_controls = [read[seq][0] for seq, _ in rows]
    rng = random.Random(20261104)
    histogram = {}
    for _ in range(10000):
        shuffled = rng.sample(original_controls, len(original_controls))
        count = sum(
            mask.bit_count() >= 11 and (control ^ value) & mask == 0
            for control, (mask, value) in zip(shuffled, masks)
        )
        histogram[count] = histogram.get(count, 0) + 1
    assert histogram == {0: 5039, 1: 3499, 2: 1176, 3: 241, 4: 39, 5: 6}, histogram

    valid = add_rows(basis, symbolic, rows, False)
    all_rows = add_rows(basis, symbolic, rows, True)
    assert (valid.rank, all_rows.rank) == (15432, 15493)
    assert slot_projection(basis, symbolic) == 128
    assert slot_projection(valid, symbolic) == 128
    assert slot_projection(all_rows, symbolic) == 128
    assert all(read[300 + i][1] for i in range(4))
    print("Original 12-node49 cross-record lattice validated")
    print("Stage matches with >=11 source-fixed bits:", actual)
    print("10000 permuted-control label shuffle:", sorted(histogram.items()))
    print("Source rank:", basis.rank, "plus valid node49:", valid.rank,
          "plus CRC-invalid speculative node49:", all_rows.rank)
    print("Selected K04 native bits still unknown:", 128)
    print("Original acceptance unchanged; K04 and K08 remain unresolved")


if __name__ == "__main__":
    main()
