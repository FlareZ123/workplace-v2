"""Original-source node49 CRC-rejected CONTROL stride prediction; K04 withheld.

Run: python agents/agent10/k04_node49_crc_stride_sft.py
Requires existing Agent49 p951 symbolic basis and original resources/evidence.
"""
from pathlib import Path
import hashlib
import struct
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
from k04_p951_symbolic_basis import Basis, get, source, untemper

ROOT = Path(__file__).resolve().parents[2] / "resources"
RECORDER_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"


def recorder_node49():
    data = (ROOT / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(data).hexdigest() == RECORDER_SHA
    result = {}
    for i in range(88):
        off = 16 + 24 * i
        _, node, _, _, seq, control, _, crc = struct.unpack_from("<IHBBI4sII", data, off)
        if node != 49:
            continue
        syndrome = zlib.crc32(data[off:off + 20]) ^ crc
        result[seq] = (untemper(int.from_bytes(control, "little")), control, syndrome)
    assert len(result) == 16
    assert all(result[s][2] == 0x100 for s in range(900, 904))
    assert all(result[s][2] == 0 for s in tuple(range(200, 204)) + tuple(range(990, 994)))
    return result


def fixed_native(basis, state, index):
    value = mask = 0
    for bit, expr in enumerate(get(state, index)):
        predicted = basis.predict(expr)
        if predicted is not None:
            mask |= 1 << bit
            value |= predicted << bit
    return value, mask


def target_quotient(basis, state):
    extra = {}
    for pos in range(951, 955):
        for expr in get(state, pos):
            value = expr
            while value:
                pivot = value.bit_length() - 1
                if pivot in basis.rows:
                    value ^= basis.rows[pivot][0]
                elif pivot in extra:
                    value ^= extra[pivot]
                else:
                    extra[pivot] = value
                    break
    return len(extra)


def main():
    printer, state = source(ROOT)  # Built without selected spool payload row129.
    assert printer.rank == 15365
    records = recorder_node49()
    # Freeze the 3-step interleave using only CRC-valid row identities and words.
    anchors = {990: -322, 991: -319, 992: -316, 993: -313,
               201: -321, 203: -315}
    for seq, pos in anchors.items():
        value, mask = fixed_native(printer, state, pos)
        assert mask.bit_count() >= 16
        assert ((value ^ records[seq][0]) & mask) == 0, (seq, pos)
        # Independently locate each intact anchor without using any bad-CRC words.
        matches = []
        for test in range(-1100, -1):
            test_value, test_mask = fixed_native(printer, state, test)
            if test_mask.bit_count() >= 16 and ((test_value ^ records[seq][0]) & test_mask) == 0:
                matches.append(test)
        assert matches == [pos], (seq, matches)

    # These four row positions are predictions from the intact 3-step layout.
    # The failed-CRC control values did not select or alter the positions.
    fixed_counts = []
    for latch in range(4):
        seq = 900 + latch
        pos = -323 + 3 * latch
        value, mask = fixed_native(printer, state, pos)
        assert ((value ^ records[seq][0]) & mask) == 0
        fixed_counts.append(mask.bit_count())
        if mask == 0xffffffff:
            repaired_control = bytes(a ^ b for a, b in zip(records[seq][1], bytes.fromhex("3F9B320D")))
            alternative = untemper(int.from_bytes(repaired_control, "little"))
            assert ((value ^ alternative) & mask).bit_count() == 14
            print(f"CRC-bad seq{seq}: {mask.bit_count()}/32 native bits predict original {records[seq][1].hex().upper()}, repaired-control alternative disagrees at 14 bits")
        else:
            print(f"CRC-bad seq{seq}: {mask.bit_count()}/32 native bits predict retained CONTROL")
    assert fixed_counts == [2, 32, 1, 32]
    assert sum(fixed_counts) == 67

    # Additional source equations if all twelve interleaved original raw controls
    # are trusted and the inferred stage layout is the historical one.
    joint = Basis()
    joint.rows = printer.rows.copy()
    joint.rank = printer.rank
    for latch in range(4):
        for offset, seq in enumerate((200 + latch, 900 + latch, 990 + latch)):
            pos = -324 + 3 * latch + offset
            for bit, expr in enumerate(get(state, pos)):
                joint.insert(expr, (records[seq][0] >> bit) & 1)
    assert joint.rank == 15493
    assert target_quotient(printer, state) == target_quotient(joint, state) == 128
    print("PASS: six intact anchor positions; four CRC-bad retained controls agree at 67/67 source-fixed bits")
    print("Conditional 12-word interleave: rank +128; selected K04 quotient 128/128 still unknown")
    print("No K04/K08 commitment or disputed ACK payload was used")


if __name__ == "__main__":
    main()
