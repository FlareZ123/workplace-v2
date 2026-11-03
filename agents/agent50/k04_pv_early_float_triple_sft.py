"""Source-only early negative-stage PV float triple from original H17 records.

SFT: run from repository root: python agents/agent50/k04_pv_early_float_triple_sft.py
No selected ESC-N ACK, K04 mask/digest, K08 nonce/digest or candidate is used.
"""
from pathlib import Path
import hashlib
import json
import random
import re

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"
HIST = ROOT / "resources/evidence/telemetry/freeze-export.jsonl"
SPOOL_PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
HIST_PIN = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
ORIGIN, LAST = -2000, 1040
U, MAG = 0xFFFFFFFF, 0x9908B0DF
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]


def untemper(x):
    for k, left, m in ((18, False, U), (15, True, 0xEFC60000),
                       (7, True, 0x9D2C5680), (11, False, U)):
        y = x
        for _ in range(6):
            y = x ^ (((y << k) & m) if left else y >> k)
        x = y & U
    return x


def mt_words():
    a = [[1 << (32*i+j) for j in range(32)] for i in range(624)]
    for i in range(624, LAST - ORIGIN + 1):
        t = i - 624
        a.append([a[t+397][j] ^ (a[t][31] if j == 30 else
                  (a[t+1][j+1] if j < 30 else 0)) ^
                  (a[t+1][0] if (MAG >> j) & 1 else 0) for j in range(32)])
    return a


def temper(v):
    a = [v[j] ^ (v[j+11] if j+11 < 32 else 0) for j in range(32)]
    b = [a[j] ^ (a[j-7] if j >= 7 and (0x9D2C5680 >> j) & 1 else 0) for j in range(32)]
    c = [b[j] ^ (b[j-15] if j >= 15 and (0xEFC60000 >> j) & 1 else 0) for j in range(32)]
    return [c[j] ^ (c[j+18] if j+18 < 32 else 0) for j in range(32)]


class Basis:
    def __init__(self):
        self.rows = {}
        self.rank = 0

    def insert(self, v, bit):
        while v:
            pivot = v.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = (v, bit)
                self.rank += 1
                return
            w, b = self.rows[pivot]
            v ^= w
            bit ^= b
        assert bit == 0, "original intact printer contradiction"

    def predict(self, v):
        bit = 0
        while v:
            pivot = v.bit_length() - 1
            if pivot not in self.rows:
                return None
            w, b = self.rows[pivot]
            v ^= w
            bit ^= b
        return bit


def source_pairs():
    spool = SPOOL.read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_PIN
    packets = [bytes.fromhex(v.decode()) for v in
               re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(packets) == len(STARTS) == 133
    model = mt_words()
    basis = Basis()
    for row, (packet, pos) in enumerate(zip(packets, STARTS)):
        if row == 129:
            continue
        for lane in range(4):
            v = untemper(int.from_bytes(packet[4*lane:4*lane+4], "little"))
            for j, vector in enumerate(model[pos+lane-ORIGIN]):
                basis.insert(vector, (v >> j) & 1)
    assert basis.rank == 15365
    predicted = {}
    for index in range(ORIGIN, 1039):
        words = []
        for stage in (index, index+1):
            value = mask = 0
            for j, vector in enumerate(temper(model[stage-ORIGIN])):
                b = basis.predict(vector)
                if b is not None:
                    mask |= 1 << j
                    value |= b << j
            words.append((value, mask))
        (a, am), (b, bm) = words
        predicted[index] = (((a >> 5) << 26) | (b >> 6),
                            ((am >> 5) << 26) | (bm >> 6))
    return predicted


def interval(q):
    scale = 1 << 53
    den = 152000
    ceildiv = lambda a, b: (a + b - 1) // b
    low = ceildiv((2*q-24001)*scale, den)
    high = ceildiv((2*q-23999)*scale, den) - 1
    return max(0, low), min(scale-1, high)


def count_leq(bound, value, mask):
    if bound < 0:
        return 0
    count = 0
    for j in range(52, -1, -1):
        bit = (value >> j) & 1
        is_fixed = (mask >> j) & 1
        if (bound >> j) & 1:
            if not is_fixed or not bit:
                count += 1 << (((1 << j) - 1 & ~mask).bit_count())
            if is_fixed and not bit:
                return count
        elif is_fixed and bit:
            return count
    return count + 1


def compatible(q, value, mask):
    low, high = interval(q)
    return count_leq(high, value, mask) > count_leq(low-1, value, mask)


def run():
    raw = HIST.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == HIST_PIN
    pv = sorted((r for r in map(json.loads, raw.splitlines())
                 if r["field"] == "PV"), key=lambda r: r["seq"])
    assert len(pv) == 112 and [r["seq"] for r in pv] == list(range(100, 212))
    q = [round(r["value"]*1000) for r in pv]
    pairs = source_pairs()

    # Genuine seeded CPython generator and 64 deliberately withheld stream bytes.
    rng = random.Random(167891)
    stream = [rng.getrandbits(32) for _ in range(500)]
    for i in range(32):
        st = 50 + i*7
        a, b = stream[st:st+2]
        fraction = ((a >> 5) << 26) | (b >> 6)
        observed = round(12000 + 76000 * fraction / (1 << 53))
        assert compatible(observed, fraction, (1 << 53)-1)
    print("synthetic true MT double / exact rounded interval: PASS 32/32")

    high = {st: (mask >> 36).bit_count() for st, (_, mask) in pairs.items()}
    eligible = {stride: [st for st in range(ORIGIN, 1039-2*stride)
               if all(high[st+j*stride] >= 12 for j in range(3))]
               for stride in range(4, 13)}
    stages = {st+j*d for d, starts in eligible.items() for st in starts
              for j in range(3)}
    matches = {}
    for st in stages:
        value, mask = pairs[st]
        matches[st] = [i for i, n in enumerate(q) if compatible(n, value, mask)]
    assert len(stages) == 1169
    assert sum(map(len, matches.values())) == 5

    # Enumerate ALL three-consecutive-value witnesses, with no sequence
    # or stage restricted after looking at the discovered alignment.
    witnesses = []
    for d, starts in eligible.items():
        for st in starts:
            for i in matches[st]:
                for j in matches[st+d]:
                    for k in matches[st+2*d]:
                        if i != j and j != k and i != k:
                            witnesses.append((pv[i]["seq"], pv[j]["seq"],
                                              pv[k]["seq"], st, d))
    assert witnesses == [(175, 176, 177, -1567, 7)], witnesses
    print("original unique PV triple:", witnesses)
    for seq, st in ((175, -1567), (176, -1560), (177, -1553)):
        value, mask = pairs[st]
        n = round(pv[seq-100]["value"]*1000)
        assert compatible(n, value, mask)
        print("PV", seq, "round_milli", n, "stage", st,
              "source_fixed53", mask.bit_count(),
              "source_fixed_top17", (mask >> 36).bit_count())
    print("selected ESC-N source packet withheld, K04/K08 not recovered")


if __name__ == "__main__":
    run()
