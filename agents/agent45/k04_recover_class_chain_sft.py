"""K04: class- and destination-specific 128-bit packet-sequence generator controls.

python agents/agent45/k04_recover_class_chain_sft.py <resources-or-ZIP>

Tests GF(2^128) finite-order linear generators and modular 2^128 affine
generators on the original 37 intact RECOVER/ACK coupons and the 3 DEST
subgroups. Disputed original selected 18:02 ACK2 is excluded up front.
No target hash, mask, verifier or candidate accessed. Synthetic positives
verify both distinct producer architectures and blind heldout prediction.
"""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import hashlib
import random
import sys

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MOD = (1 << 128) - 1


def mul(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        if a >> 128:
            a ^= (1 << 128) | 0x87
        b >>= 1
    return out


def power(a, exponent):
    value = 1
    while exponent:
        if exponent & 1:
            value = mul(value, a)
        a = mul(a, a)
        exponent >>= 1
    return value


def bm(sequence):
    """Berlekamp-Massey over the GCM GF(2^128) polynomial 0x87."""
    coeff, previous = [1], [1]
    order, shift, last = 0, 1, 1
    for index, actual in enumerate(sequence):
        discrepancy = actual
        for i in range(1, order + 1):
            discrepancy ^= mul(coeff[i], sequence[index-i])
        if not discrepancy:
            shift += 1
            continue
        old = coeff[:]
        factor = mul(discrepancy, power(last, (1 << 128) - 2))
        coeff.extend([0] * max(0, len(previous) + shift - len(coeff)))
        for j, v in enumerate(previous):
            coeff[j+shift] ^= mul(factor, v)
        if 2 * order <= index:
            order = index + 1 - order
            previous, last, shift = old, discrepancy, 1
        else:
            shift += 1
    return coeff[:order+1], order


def predict(history, coeff, count):
    words = list(history)
    for _ in range(count):
        next_value = 0
        for index in range(1, len(coeff)):
            next_value ^= mul(coeff[index], words[-index])
        words.append(next_value)
    return words[-count:]


def modular_family(states):
    first, second, third = states[:3]
    d1, d2 = (second-first) & MOD, (third-second) & MOD
    if not d1:
        return []
    gcd = d1 & -d1
    if d2 % gcd or gcd > 64:
        return []
    quotient = (MOD+1)//gcd
    base = ((d2//gcd) * pow(d1//gcd, -1, quotient)) % quotient
    return [(a, (second-a*first) & MOD)
            for a in (base+j*quotient for j in range(gcd))]


def positive_controls():
    rng = random.Random(0xA45)
    coeff = [0x45, 0x765, 0xBB3]
    series = [rng.getrandbits(128) for _ in coeff]
    for _ in range(22):
        value = 0
        for i, c in enumerate(coeff, 1):
            value ^= mul(c, series[-i])
        series.append(value)
    for n in (8, 12):
        polynomial, order = bm(series[:n])
        assert order == 3
        assert predict(series[:n], polynomial, 4) == series[n:n+4]
    for a, b, seed in ((3,1,81),(2,1,19),(0,43,121)):
        values = [seed]
        for _ in range(11):
            values.append((a*values[-1]+b) & MOD)
        family = modular_family(values)
        assert (a,b) in family
        assert any(all((u*values[i-1]+v)&MOD == values[i]
                       for i in range(3,len(values))) for u,v in family)
    print("POSITIVE: 2 GF128 recurrence fixtures and 3 modular-affine fixtures PASS")


def source(root):
    if root.is_file():
        with ZipFile(root) as archive:
            data = archive.read("evidence/print/spool-reconstruction.log")
    else:
        data = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == PIN
    rows = [dict(token.split("=",1) for token in line.split()[1:])
            for line in data.decode("ascii").splitlines()
            if "PAYLOAD=" in line]
    assert len(rows) == 133
    assert (rows[129]["JOB"],rows[129]["ATTEMPT"],rows[129]["STATE"],
            rows[129]["CLASS"]) == ("PS-261003-0417","2","ACK","RECOVER")
    kept = [r for i,r in enumerate(rows)
            if i!=129 and r["STATE"]=="ACK" and r["CLASS"]=="RECOVER"]
    assert len(kept)==37
    assert Counter(r["DEST"] for r in kept)=={"bench":12,"desk":13,"store":12}
    return kept


def main(root):
    positive_controls()
    kept = source(root)
    fit_count, heldout_count, full_hits = 0, 0, 0
    for endian in ("big", "little"):
        groups = {"ALL": kept}
        groups.update({d:[r for r in kept if r["DEST"]==d]
                       for d in ("bench","desk","store")})
        for name, group in groups.items():
            values = [int.from_bytes(bytes.fromhex(r["PAYLOAD"]), endian)
                      for r in group]
            # Predictions trained strictly on intact earlier packets.
            for size in (6,8,12,16,24):
                if size+2 > len(values):
                    continue
                polynomial, order = bm(values[:size])
                count = min(4,len(values)-size)
                predicted = predict(values[:size], polynomial, count)
                matches = sum(x == y for x,y in zip(predicted, values[size:size+count]))
                assert matches == 0
                fit_count += 1
                heldout_count += count
                full_hits += matches
                print("GF128", endian, name, "train", size, "order", order,
                      "heldout full-match", matches, "/", count)
            family = modular_family(values)
            exact = [(a,b) for a,b in family
                     if all((a*values[i-1]+b)&MOD == values[i]
                            for i in range(3, min(7,len(values))))]
            assert not exact
            print("MOD128_AFFINE",endian,name,
                  "candidate multipliers",len(family),
                  "4-packet full heldout survivors",len(exact))
    assert fit_count==22 and heldout_count==88 and full_hits==0
    print("NO_SOURCE_PREDICTIVE_CLASS_STREAM",fit_count,
          "models /",heldout_count,"full packet controls; original K04/K08 missing")


if __name__=="__main__":
    main(Path(sys.argv[1] if len(sys.argv)>1 else "resources"))
