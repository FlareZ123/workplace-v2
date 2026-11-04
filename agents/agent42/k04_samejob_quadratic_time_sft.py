"""H-17 K04 same-job quadratic timestamp interpolation; source-only inputs.

Run: python agents/agent42/k04_samejob_quadratic_time_sft.py [resources_dir]
Original 18:02 ACK2 copied payload is never read into a candidate.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import itertools
import json
import re
import sys

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
FORM = re.compile(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$")


def multiply(a, b, bits, poly):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & (1 << bits):
            a ^= (1 << bits) | poly
    return out


def inverse(value, bits, poly):
    exponent = (1 << bits) - 2
    out = 1
    while exponent:
        if exponent & 1:
            out = multiply(out, value, bits, poly)
        value = multiply(value, value, bits, poly)
        exponent >>= 1
    return out


def lagrange(xs, ys, t, bits, poly):
    result = 0
    for i in range(3):
        num = den = 1
        for j in range(3):
            if i != j:
                num = multiply(num, t ^ xs[j], bits, poly)
                den = multiply(den, xs[i] ^ xs[j], bits, poly)
        assert den and multiply(den, inverse(den, bits, poly), bits, poly) == 1
        result ^= multiply(ys[i], multiply(num, inverse(den, bits, poly), bits, poly), bits, poly)
    return result


def reconstruct(xs, source, t, bits, poly, endian):
    width = bits // 8
    return b"".join(lagrange(xs, [int.from_bytes(v[i:i + width], endian) for v in source],
                             t, bits, poly).to_bytes(width, endian)
                    for i in range(0, 16, width))


def indices(times, bits, unit, relative):
    vals = [int(t.timestamp()) // unit for t in times]
    return [((v - vals[0]) if relative else v) % (1 << bits) for v in vals]


def run(root):
    for bits, poly in ((8, 0x1b), (8, 0x1d), (128, 0x87)):
        f = lambda t: 0x5a ^ multiply(0xa5, t, bits, poly) ^ multiply(0x3f, multiply(t, t, bits, poly), bits, poly)
        assert lagrange([1, 76, 79], [f(x) for x in (1, 76, 79)], 77, bits, poly) == f(77)
    source = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(source).hexdigest() == PIN
    rows = []
    for line in source.decode().splitlines():
        if line.startswith("#"):
            continue
        m = FORM.fullmatch(line)
        assert m
        time, job, attempt, state, kind, raw, dest = m.groups()
        rows.append((datetime.fromisoformat(time.replace("Z", "+00:00")), job, int(attempt), state, kind, raw, dest))
    assert len(rows) == 133
    same = [r for r in rows if r[1] == "PS-261003-0417"]
    assert [(r[2], r[3], r[4]) for r in same] == [(1,"ACK","LABEL"),
        (1,"REQUESTED","RECOVER"),(2,"ACK","RECOVER"),(3,"REQUESTED","RECOVER")]
    # Deliberately exclude same[2][5], the disputed copied target payload.
    known = [same[i] for i in (0, 1, 3)]
    times = [r[0] for r in known] + [same[2][0]]
    payloads = [bytes.fromhex(r[5]) for r in known]
    models, candidates, hits = 0, set(), []
    controls = {}
    for bits, poly, label in ((8,0x1b,"AES-GF256"),(8,0x1d,"RS-GF256"),(128,0x87,"GCM-GF128")):
        correct = 0
        for i in range(125):
            four = rows[i:i + 4]
            x = indices([four[j][0] for j in (0,1,3,2)], bits, 60, True)
            got = reconstruct(x[:3], [bytes.fromhex(four[j][5]) for j in (0,1,3)],
                              x[3],bits,poly,"big")
            correct += got == bytes.fromhex(four[2][5])
        controls[label] = correct
        for unit, relative, endian in itertools.product((60,1),(True,False),
                                                         (("big","little") if bits == 128 else ("big",))):
            x = indices(times,bits,unit,relative)
            coupon = reconstruct(x[:3],payloads,x[3],bits,poly,endian)
            candidates.add(coupon)
            key = bytes(a ^ b for a,b in zip(coupon,MASK))
            models += 1
            if sha256(key).hexdigest() == TARGET:
                hits.append((label,unit,relative,endian,key.hex().upper()))
    assert models == 16 and len(candidates) == 16 and controls == {
        "AES-GF256":0,"RS-GF256":0,"GCM-GF128":0}
    print(json.dumps({"synthetic_controls":"PASS","original_sha256":PIN,
          "model":"three-source same-job quadratic timestamp interpolation",
          "target_copy_payload_used":False,"complete_models":models,
          "distinct_coupon_candidates":len(candidates),"original_K04_hits":hits,
          "ordinary_heldout_windows_per_field":125,"ordinary_exact_predictions":controls},indent=2))


if __name__ == "__main__":
    run(Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "resources")
