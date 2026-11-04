"""Read-only conditional p951 recorder CONTROL and LATCH bridge.
Original selected spool row129 is withheld. No K04/K08 commitment is used.
"""
import hashlib
import importlib.util
import random
import re
import struct
import sys
import zlib
from pathlib import Path

U = 0xffffffff
MAG = 0x9908b0df
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
AGENT49 = Path(__file__).resolve().parents[1] / "agent49" / "k04_p951_symbolic_basis.py"
EXPECTED = [(7, -810, 32), (9, -793, 17), (12, -775, 32),
            (13, -769, 32), (14, -759, 16), (24, -683, 32),
            (25, -677, 32), (41, -568, 32), (45, -540, 31),
            (61, -417, 16), (63, -397, 17), (64, -390, 16),
            (70, -339, 32)]

def temper_value(y):
    y ^= y >> 11
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 15) & 0xefc60000
    y ^= y >> 18
    return y & U

def checked(path, digest):
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest, path
    return data

def load_recorder(data):
    assert len(data) == 16 + 88 * 24
    controls = {}
    for i in range(88):
        row = data[16 + 24 * i:16 + 24 * (i + 1)]
        timestamp, node, event, latch, seq, control, aux, crc = struct.unpack("<I H B B I 4s I I", row)
        assert zlib.crc32(row[:20]) == crc or node == 49
        if node == 50 and zlib.crc32(row[:20]) == crc:
            assert seq not in controls
            controls[seq] = (int.from_bytes(control, "little"), latch)
    assert len(controls) == 72
    return controls

def closure(packets, positions, untemper):
    lo, hi = -2600, 3000
    n = hi - lo + 1
    mask = [0] * n
    val = [0] * n
    for row, (packet, pos) in enumerate(zip(packets, positions)):
        if row == 129:
            continue
        for j in range(4):
            at = pos + j - lo
            mask[at] = U
            val[at] = untemper(int.from_bytes(packet[j*4:j*4+4], "little"))

    def put(i, bit, b):
        idx = i - lo
        k = 1 << bit
        if mask[idx] & k:
            assert bool(val[idx] & k) == bool(b), (i, bit)
            return 0
        mask[idx] |= k
        if b:
            val[idx] |= k
        return 1

    for pass_no in range(25):
        new = 0
        for iterable in (range(lo, hi - 623), range(hi - 624, lo - 1, -1)):
            for i in iterable:
                a, b, c, d = i-lo, i+1-lo, i+397-lo, i+624-lo
                for bit in range(32):
                    terms = [(c, bit), (d, bit)]
                    if bit == 30:
                        terms.append((a, 31))
                    if bit < 30:
                        terms.append((b, bit + 1))
                    if (MAG >> bit) & 1:
                        terms.append((b, 0))
                    missing = []
                    parity = 0
                    for idx, tbit in terms:
                        if not (mask[idx] >> tbit) & 1:
                            missing.append((idx + lo, tbit))
                        else:
                            parity ^= (val[idx] >> tbit) & 1
                    if not missing:
                        assert parity == 0, (i, bit)
                    elif len(missing) == 1:
                        new += put(missing[0][0], missing[0][1], parity)
        if not new:
            assert pass_no <= 8
            break
    return lo, mask, val

def test():
    spec = importlib.util.spec_from_file_location("p951", AGENT49)
    mt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mt)
    spool = checked(ROOT / "evidence/print/spool-reconstruction.log", SPOOL_SHA)
    rec = checked(ROOT / "evidence/recorder/trip-recorder.raw", REC_SHA)
    packets = [bytes.fromhex(s.decode()) for s in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(packets) == len(mt.STARTS) == 133
    controls = load_recorder(rec)
    lo, mask, val = closure(packets, mt.STARTS, mt.untemper)

    found = []
    heldout_latch = []
    for seq, (word, latch) in controls.items():
        native = mt.untemper(word)
        for stage in range(-1100, 0):
            idx = stage - lo
            nbits = mask[idx].bit_count()
            if nbits < 16:
                continue
            if (native & mask[idx]) == val[idx]:
                found.append((seq, stage, nbits))
                prev = stage - 1 - lo
                if mask[prev] == U:
                    code = temper_value(val[prev]) >> 29
                    heldout_latch.append((seq, stage-1, code, latch, code == latch))
    found.sort()
    assert found == EXPECTED, (found, EXPECTED)
    assert len(heldout_latch) == 9
    assert [seq for seq, _, _, _, good in heldout_latch if not good] == [61]
    print("ORIGINAL_SOURCE_PARTIAL_MATCHES", found, flush=True)
    print("ORIGINAL_SOURCE_LATCH_HELDOUT", sorted(heldout_latch), flush=True)

    basis, sym = mt.source(ROOT)
    assert basis.rank == 15365

    def quotient(b):
        c = mt.Basis()
        c.rows = b.rows.copy()
        c.rank = b.rank
        for t in range(951, 955):
            for vec in mt.get(sym, t):
                c.insert(vec, 0)
        return c.rank - b.rank

    assert quotient(basis) == 128
    for seq, stage, nbits in found:
        native = mt.untemper(controls[seq][0])
        fixed = [basis.predict(bit) for bit in mt.get(sym, stage)]
        # Previously inserted original carriers can add source-fixed bits.
        assert sum(bit is not None for bit in fixed) >= nbits
        assert all(bit is None or bit == ((native >> j) & 1) for j, bit in enumerate(fixed))
        for j, vec in enumerate(mt.get(sym, stage)):
            basis.insert(vec, (native >> j) & 1)
    assert basis.rank == 15373
    assert quotient(basis) == 128
    print("EXACT_SOURCE_RANK=15373 ADDED=8 SELECTED_UNKNOWN=128", flush=True)

    rng = random.Random(20261104)
    simulated = [mt.untemper(rng.getrandbits(32)) for _ in range(1000)]
    for i in range(376):
        y = (simulated[i] & 0x80000000) | (simulated[i+1] & 0x7fffffff)
        assert simulated[i+624] == simulated[i+397] ^ (y >> 1) ^ (MAG if y & 1 else 0)
    for value in simulated[:32]:
        assert mt.untemper(temper_value(value)) == value
    print("SEEDED_MT19937_CONTROLS PASS", flush=True)

if __name__ == "__main__":
    test()
