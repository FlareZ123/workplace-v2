"""K04: test 128 routine printer packets as degree-127 erasure-code evaluations.

A complete 16-byte K04 payload could be predicted from the 128 retained
routine packets if late packets were successive evaluations of one common
degree <=127 polynomial. Test six GF(2^128) index/clock axes and two
GF(256) per-byte fields against four NONSELECTED late packet controls.
The disputed target (row129) is always withheld from fitting and testing.

python agents/agent1/k04_printer_128codeword_sft.py resources
python agents/agent1/k04_printer_128codeword_sft.py h17-archive-dump.zip

The source checksum and synthetic exact-degree-127 positives are mandatory.
Only the original source data are read, never modified.
"""
from __future__ import annotations
import hashlib
import random
import sys
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
LATE_CONTROL = (128, 130, 131, 132)
M128 = (1 << 128) - 1


def mul(a: int, b: int, polynomial: int, width: int) -> int:
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        if a >> width:
            a ^= (1 << width) | polynomial
        b >>= 1
    return out


def power(a: int, n: int, polynomial: int, width: int) -> int:
    out = 1
    while n:
        if n & 1:
            out = mul(out, a, polynomial, width)
        a = mul(a, a, polynomial, width)
        n >>= 1
    return out


def batch_inverse(values: list[int], polynomial: int, width: int) -> list[int]:
    assert all(values)
    prefix = [1]
    for value in values:
        prefix.append(mul(prefix[-1], value, polynomial, width))
    inverse = power(prefix[-1], (1 << width) - 2, polynomial, width)
    result = [0] * len(values)
    for i in range(len(values) - 1, -1, -1):
        result[i] = mul(inverse, prefix[i], polynomial, width)
        inverse = mul(inverse, values[i], polynomial, width)
    assert inverse == 1
    return result


def barycentric_weights(xs: list[int], polynomial: int, width: int) -> list[int]:
    denominators = []
    for i, xi in enumerate(xs):
        denominator = 1
        for j, xj in enumerate(xs):
            if i != j:
                denominator = mul(denominator, xi ^ xj, polynomial, width)
        denominators.append(denominator)
    return batch_inverse(denominators, polynomial, width)


def interpolate(
    xs: list[int], ys: list[int], weights: list[int],
    x: int, polynomial: int, width: int,
) -> int:
    if x in xs:
        return ys[xs.index(x)]
    differences = [x ^ xi for xi in xs]
    inverses = batch_inverse(differences, polynomial, width)
    product = 1
    for diff in differences:
        product = mul(product, diff, polynomial, width)
    out = 0
    for y, weight, reciprocal in zip(ys, weights, inverses):
        coeff = mul(product, mul(weight, reciprocal, polynomial, width), polynomial, width)
        out ^= mul(y, coeff, polynomial, width)
    return out


def synthetic_positive() -> None:
    rng = random.Random(20261103)
    for polynomial, width in ((0x87, 128), (0x11D, 8), (0x11B, 8)):
        coefficients = [rng.getrandbits(width) for _ in range(128)]
        def evaluate(x: int) -> int:
            y = 0
            for coeff in reversed(coefficients):
                y = mul(y, x, polynomial, width) ^ coeff
            return y
        xs = list(range(128))
        ys = [evaluate(x) for x in xs]
        weights = barycentric_weights(xs, polynomial, width)
        for x in (128, 129, 132):
            assert interpolate(xs, ys, weights, x, polynomial, width) == evaluate(x)
        print(f"POSITIVE degree127 GF2^{width} modulus={polynomial:#x}: 3/3 exact")
        

def read_rows(root: Path) -> list[dict[str, str]]:
    if root.is_file():
        with ZipFile(root) as archive:
            data = archive.read("evidence/print/spool-reconstruction.log")
    else:
        data = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SOURCE_SHA
    rows = []
    for line in data.decode("ascii").splitlines():
        if "PAYLOAD=" not in line:
            continue
        parts = line.split()
        fields = dict(piece.split("=", 1) for piece in parts[1:])
        fields["UTC"] = parts[0]
        rows.append(fields)
    assert len(rows) == 133
    assert [r["JOB"] for r in rows[:128]] == [f"PS-261003-{300+i:04d}" for i in range(128)]
    chosen = rows[129]
    assert (chosen["JOB"], chosen["ATTEMPT"], chosen["STATE"], chosen["CLASS"]) == (
        "PS-261003-0417", "2", "ACK", "RECOVER"
    )
    for i in LATE_CONTROL:
        assert i != 129
    return rows


def main(root: Path) -> None:
    synthetic_positive()
    rows = read_rows(root)
    values = [int(r["PAYLOAD"], 16) for r in rows]
    times = [int(datetime.fromisoformat(r["UTC"].replace("Z", "+00:00")).timestamp()) for r in rows]
    axes = {
        "event-index": [i for i in range(133)],
        "elapsed-seconds": [t - times[0] for t in times],
        "epoch-seconds": times,
        "elapsed-minutes": [(t - times[0]) // 60 for t in times],
        "epoch-minutes": [t // 60 for t in times],
        "UTC-day-seconds": [t % 86400 for t in times],
    }
    for name, xall in axes.items():
        xs = xall[:128]
        assert len(set(xs)) == 128
        weights = barycentric_weights(xs, 0x87, 128)
        match = 0
        for idx in LATE_CONTROL:
            pred = interpolate(xs, values[:128], weights, xall[idx], 0x87, 128)
            same = pred == values[idx]
            match += same
            print(f"GF128 axis={name} nonselected={idx} full-match={int(same)}")
        assert match == 0
        print(f"GF128 axis={name} aggregate={match}/4")
    xs = list(range(128))
    for poly in (0x11D, 0x11B):
        weights = barycentric_weights(xs, poly, 8)
        total_full = 0
        for idx in LATE_CONTROL:
            predicted = bytes(
                interpolate(xs, [bytes.fromhex(r["PAYLOAD"])[pos] for r in rows[:128]],
                            weights, idx, poly, 8)
                for pos in range(16)
            )
            true = bytes.fromhex(rows[idx]["PAYLOAD"])
            num = sum(x == y for x, y in zip(predicted, true))
            total_full += num == 16
            print(f"GF256 modulus={poly:#x} nonselected={idx} byte-match={num}/16")
        assert total_full == 0
        print(f"GF256 modulus={poly:#x} full-controls={total_full}/4")
    print("RESULT: no original nonselected control full-packet matches; target not inferred")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "resources"))
