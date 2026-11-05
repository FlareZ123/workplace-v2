"""H-17 original-source PV175-177 native-MT stride-seven extrapolation falsifier.

Runs against repository resources by default, or H17_ARCHIVE_ZIP original upload.
Uses printer-copy rows except selected row129. Never reads acceptance or masks.
Includes a genuinely generated MT19937 stream positive control.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import random
import re
from time import perf_counter
from zipfile import ZipFile

STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
ORIGIN, LAST, MAG, U = -2092, 970, 0x9908B0DF, 0xFFFFFFFF
SPOOL_HASH = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
PV_HASH = '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'

def read_sources():
    zip_path = os.environ.get('H17_ARCHIVE_ZIP')
    if zip_path:
        with ZipFile(zip_path) as archive:
            spool = archive.read('evidence/print/spool-reconstruction.log')
            pv = archive.read('evidence/telemetry/freeze-export.jsonl')
    else:
        root = Path(os.environ.get('H17_RESOURCE_ROOT', 'resources/evidence'))
        spool = (root / 'print/spool-reconstruction.log').read_bytes()
        pv = (root / 'telemetry/freeze-export.jsonl').read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_HASH
    assert hashlib.sha256(pv).hexdigest() == PV_HASH
    lines = re.findall(rb'PAYLOAD=([0-9A-F]{32})', spool)
    assert len(lines) == len(STARTS) == 133
    packets = [None if row == 129 else bytes.fromhex(raw.decode()) for row, raw in enumerate(lines)]
    values = {int(o['seq']): int(round(float(o['value']) * 1000)) for o in map(json.loads, pv.splitlines()) if o['field'] == 'PV'}
    assert sorted(values) == list(range(100, 212))
    print('SOURCE_PIN_PASS printer 132 intact packets, 1 selected withheld; PV=112', flush=True)
    return packets, values

def untemper(x):
    for k, left, mask in ((18, False, U), (15, True, 0xEFC60000), (7, True, 0x9D2C5680), (11, False, U)):
        y = x
        for _ in range(6):
            y = x ^ (((y << k) & mask) if left else (y >> k))
        x = y & U
    return x

def symbolic_state():
    expressions = [[1 << (32 * i + j) for j in range(32)] for i in range(624)]
    for index in range(624, LAST - ORIGIN + 1):
        t = index - 624
        expressions.append([
            expressions[t + 397][j]
            ^ (expressions[t][31] if j == 30 else (expressions[t + 1][j + 1] if j < 30 else 0))
            ^ (expressions[t + 1][0] if (MAG >> j) & 1 else 0)
            for j in range(32)
        ])
    return expressions

def temper(expressions):
    a = [expressions[j] ^ (expressions[j + 11] if j + 11 < 32 else 0) for j in range(32)]
    b = [a[j] ^ (a[j - 7] if j >= 7 and (0x9D2C5680 >> j) & 1 else 0) for j in range(32)]
    c = [b[j] ^ (b[j - 15] if j >= 15 and (0xEFC60000 >> j) & 1 else 0) for j in range(32)]
    return [c[j] ^ (c[j + 18] if j + 18 < 32 else 0) for j in range(32)]

class Basis:
    def __init__(self):
        self.rows = {}
        self.rank = 0

    def insert(self, vector, bit):
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = (vector, bit)
                self.rank += 1
                return
            previous, previous_bit = self.rows[pivot]
            vector ^= previous
            bit ^= previous_bit
        assert bit == 0, 'contradictory packet source'

    def predict(self, vector):
        bit = 0
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in self.rows:
                return None
            previous, previous_bit = self.rows[pivot]
            vector ^= previous
            bit ^= previous_bit
        return bit

def printer_basis(expressions, packets):
    out = Basis()
    for row, (payload, start) in enumerate(zip(packets, STARTS)):
        if row == 129:
            assert payload is None
            continue
        for lane in range(4):
            word = untemper(int.from_bytes(payload[4 * lane:4 * lane + 4], 'little'))
            for bit, vector in enumerate(expressions[start + lane - ORIGIN]):
                out.insert(vector, (word >> bit) & 1)
    assert out.rank == 15365, out.rank
    return out

def guaranteed_firstword_bits(rounded_milli):
    # True uniform U is constrained to (2*m-24001)/152000 <= U < (2*m-23999)/152000.
    lower = Fraction(2 * rounded_milli - 24001, 152000)
    upper = Fraction(2 * rounded_milli - 23999, 152000)
    assert 0 < lower < upper < 1
    amin = (lower.numerator << 27) // lower.denominator
    amax = ((upper.numerator << 27) + upper.denominator - 1) // upper.denominator - 1
    prefix_length = 27 - (amin ^ amax).bit_length()
    assert 0 <= prefix_length <= 27
    # CPython A = MT32 >> 5, thus A's leading 27 bits equal MT tempered bits 31..5.
    return [(31 - k, (amin >> (26 - k)) & 1) for k in range(prefix_length)]

def check_sequence(expressions, basis, pv_values, log=True):
    records = []
    for seq in range(100, 212):
        index = -1567 + 7 * (seq - 175)
        assert ORIGIN <= index < LAST
        e = temper(expressions[index - ORIGIN])
        bits = guaranteed_firstword_bits(pv_values[seq])
        fixed = [(source_bit, basis.predict(e[pos])) for pos, source_bit in bits]
        fixed = [(source_bit, predicted) for source_bit, predicted in fixed if predicted is not None]
        wrong = sum(predicted != actual for actual, predicted in fixed)
        records.append((seq, index, len(bits), len(fixed), wrong))
    if log:
        for record in records:
            if record[0] in (111, 174, 175, 176, 177, 178, 180, 194):
                print('CHECK_PV seq=%d stage=%d guaranteed_bits=%d printer_fixed=%d mismatched=%d' % record, flush=True)
        print('ALL_PV 112 with_frozen_printer_bits=%d source_conflicting_rows=%d' % (
            sum(r[3] > 0 for r in records), sum(r[4] > 0 for r in records)), flush=True)
        print('HIGHWIDTH_PV >=8_known_match=%d >=8_known_mismatch=%d' % (
            sum(r[3] >= 8 and r[4] == 0 for r in records),
            sum(r[3] >= 8 and r[4] > 0 for r in records)), flush=True)
    return {r[0]: r for r in records}

def synth_source_positive(expressions):
    # Real MT stream, independently seeded. The source copier and PV emitter share it.
    rng = random.Random(20261105)
    stream = [rng.getrandbits(32) for _ in range(LAST - ORIGIN + 1)]
    packets = [None if row == 129 else b''.join(stream[start - ORIGIN + lane].to_bytes(4, 'little') for lane in range(4)) for row, start in enumerate(STARTS)]
    values = {}
    for seq in range(100, 212):
        index = -1567 + 7 * (seq - 175) - ORIGIN
        a = stream[index] >> 5
        b = stream[index + 1] >> 6
        u = (a * (1 << 26) + b) / (1 << 53)
        values[seq] = int(round((12 + 76 * u) * 1000))
    model = printer_basis(expressions, packets)
    tested = check_sequence(expressions, model, values, log=False)
    assert all(entry[4] == 0 for entry in tested.values())
    assert any(entry[3] >= 8 for entry in tested.values())
    print('SYNTHETIC_REAL_MT_AND_PV_POSITIVE_PASS all 112 values source-consistent', flush=True)

def main():
    t = perf_counter()
    packets, values = read_sources()
    expressions = symbolic_state()
    printer = printer_basis(expressions, packets)
    print('ORIGINAL_P951_PRINTER_RANK', printer.rank, flush=True)
    original = check_sequence(expressions, printer, values)
    assert original[111][3:] == (9, 5), original[111]
    assert original[174][3:] == (3, 2), original[174]
    assert [(original[s][3], original[s][4]) for s in (175, 176, 177)] == [(15,0), (11,0), (13,0)]
    assert sum(row[4] > 0 for row in original.values()) == 33
    assert sum(row[3] >= 8 and row[4] == 0 for row in original.values()) == 3
    assert sum(row[3] >= 8 and row[4] > 0 for row in original.values()) == 14
    synth_source_positive(expressions)
    print('RESULT FULL_112_PV_CONSTANT_NATIVE_STRIDE7_REJECTED; selected K04 never evaluated', flush=True)
    print('SECONDS', round(perf_counter() - t, 3), flush=True)

if __name__ == '__main__':
    main()
