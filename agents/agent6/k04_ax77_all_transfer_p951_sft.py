"""Original-source AX transfer checkpoint test against hypothetical p951 printer MT.

Run from repository root: python agents/agent6/k04_ax77_all_transfer_p951_sft.py
The disputed selected ACK, commitment, route mask and K08 are excluded.
A score based on zero source-known bits is NOT a positive match.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
FULL = 0xffffffff
MAGIC = 0x9908b0df

def untemper(x):
    for step, left, mask in ((18,False,FULL),(15,True,0xefc60000),
                             (7,True,0x9d2c5680),(11,False,FULL)):
        v = x
        for _ in range(6):
            v = x ^ (((v << step) & mask) if left else (v >> step))
        x = v & FULL
    return x

def twist(x):
    return (x >> 1) ^ (MAGIC if x & 1 else 0)

def inverse_twist(x):
    low = x >> 31
    return (((x ^ (MAGIC if low else 0)) << 1) | low) & FULL

def source_states():
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    packets = [bytes.fromhex(s.decode()) for s in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == len(STARTS) == 133 and STARTS[129] == 951
    origin, n = 2000, 6000
    values, masks = [0] * n, [0] * n
    def add(i, value, mask):
        if not 0 <= i < n:
            return
        assert not ((values[i] ^ value) & masks[i] & mask)
        added = mask & ~masks[i]
        values[i] |= value & added
        masks[i] |= added
    for row, (start, packet) in enumerate(zip(STARTS, packets)):
        if row == 129:
            continue
        for lane in range(4):
            add(origin + start + lane,
                untemper(int.from_bytes(packet[4*lane:4*lane+4], "little")), FULL)
    for _ in range(30):
        before = sum(x.bit_count() for x in masks)
        for i in range(n - 624):
            mask = (masks[i] & 0x80000000) | (masks[i+1] & 0x7fffffff)
            value = (values[i] & 0x80000000) | (values[i+1] & 0x7fffffff)
            if masks[i+397] == masks[i+624] == FULL:
                back = inverse_twist(values[i+397] ^ values[i+624])
                add(i, back, 0x80000000)
                add(i+1, back, 0x7fffffff)
            if mask == FULL:
                if masks[i+397] == FULL:
                    add(i+624, values[i+397] ^ twist(value), FULL)
                if masks[i+624] == FULL:
                    add(i+397, values[i+624] ^ twist(value), FULL)
        if sum(x.bit_count() for x in masks) == before:
            break
    assert sum(x == FULL for x in masks) == 968
    assert sum(0 < x < FULL for x in masks) == 306
    assert not any(masks[origin+951:origin+955])
    return values, masks, origin

def output_high16(values, masks):
    expressions = [1 << i for i in range(32)]
    for i in range(32):
        if i + 11 < 32:
            expressions[i] ^= expressions[i+11]
    for i in range(31,-1,-1):
        if i >= 7 and (0x9d2c5680 >> i) & 1:
            expressions[i] ^= expressions[i-7]
    for i in range(31,-1,-1):
        if i >= 15 and (0xefc60000 >> i) & 1:
            expressions[i] ^= expressions[i-15]
    for i in range(32):
        if i + 18 < 32:
            expressions[i] ^= expressions[i+18]
    answer = []
    for value, known in zip(values, masks):
        target = visible = 0
        for bit in range(16,32):
            if expressions[bit] & ~known:
                continue
            visible |= 1 << (bit-16)
            target |= ((expressions[bit] & value).bit_count() & 1) << (bit-16)
        answer.append((target, visible))
    return answer

def contiguous(trace, samples, origin):
    accepted = []
    for start in range(len(trace) - len(samples) + 1):
        covered = errors = 0
        for offset, observed in enumerate(samples):
            value, mask = trace[start+offset]
            covered += mask.bit_count()
            errors += ((value ^ observed) & mask).bit_count()
        if covered and not errors:
            accepted.append((covered, start-origin))
    return sorted(accepted, reverse=True)

def gapped(trace, samples):
    prior = [None] * len(trace)
    for j, observed in enumerate(samples):
        after = [None] * len(trace)
        for at, (value, mask) in enumerate(trace):
            if (value ^ observed) & mask:
                continue
            gain = mask.bit_count()
            if j == 0:
                after[at] = (gain, int(gain > 0))
                continue
            predecessors = (prior[at-step] for step in range(1,9) if at >= step)
            best = max((p for p in predecessors if p is not None), default=None)
            if best is not None:
                after[at] = (best[0]+gain, best[1]+int(gain>0))
        prior = after
    return max((r for r in prior if r is not None), default=(0,0))

def main():
    values, masks, origin = source_states()
    trace = output_high16(values, masks)
    raw = (ROOT / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
    logs = [json.loads(line) for line in raw.splitlines()]
    for transfer in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        rows = sorted((r for r in logs if r.get("kind") == "CHUNK" and r["transfer"] == transfer),
                      key=lambda x: (x["seq"], x["attempt"]))
        assert len(rows) == 16
        checkpoints = [int(r["checkpoint"],16) for r in rows]
        for encoding in ("display", "swapped"):
            src = checkpoints if encoding == "display" else [((v >> 8) | ((v & 255) << 8)) for v in checkpoints]
            for direction in ("forward", "reverse"):
                samples = src if direction == "forward" else src[::-1]
                complete = contiguous(trace, samples, origin)
                best = gapped(trace, samples)
                if transfer == "AX-7778" and encoding == "swapped" and direction == "forward":
                    assert complete == [(106,-157)] and best == (106,7)
                elif transfer != "AX-7778":
                    assert complete == [] and best[0] <= 16 and best[1] <= 1
                print(transfer, encoding, direction,
                      "nonvacuous_contiguous", complete[:2], "best_gapped_1_to_8", best)
    print("Selected K04 still wholly unconstrained under this conditional state closure")

if __name__ == "__main__":
    main()
