"""Conditional original-source test of periodic CPython binary MT seed inputs.

Asks whether the 86 source-fixed/one-bit-ambiguous bytes-seed words derived
by Agent15 could belong to a strictly periodic seed B of period 1..2429 bytes.
Original selected printer packet and target commitment are not used.
"""
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

U = (1 << 32) - 1
BASE = [19650218]
for i in range(1, 624):
    BASE.append((1812433253 * (BASE[-1] ^ (BASE[-1] >> 30)) + i) & U)


def mix(x, multiplier):
    return ((x ^ (x >> 30)) * multiplier) & U


def key_term(j, a, b, c):
    i = j + 1
    prior = ((b+i-1) & U) ^ mix(a, 1566083941)
    later = ((c+i) & U) ^ mix(b, 1566083941)
    return (later - (BASE[i] ^ mix(prior, 1664525))) & U


def expressions():
    s = [[1 << (32*i+j) for j in range(32)] for i in range(624)]
    for i in range(624, 1601):
        p, n, q = s[i-624], s[i-623], s[i-227]
        s.append([
            q[j] ^ (p[31] if j == 30 else n[j+1] if j < 30 else 0)
            ^ (n[0] if (mt.MAG >> j) & 1 else 0)
            for j in range(32)
        ])
    return s


def reduce(equation, basis):
    while equation:
        pivot = equation.bit_length()-1
        row = basis.get(pivot)
        if row is None:
            break
        equation ^= row
    return equation


def original_seed_words():
    expr = expressions()
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    )
    tokens = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(tokens) == len(mt.STARTS) == 133
    basis = {}
    for row, pos in enumerate(mt.STARTS):
        if row == 129:
            continue
        data = bytes.fromhex(tokens[row].decode())
        for lane in range(4):
            value = mt.untemper(int.from_bytes(data[lane*4:lane*4+4], "little"))
            for bit, equation in enumerate(expr[624+pos+lane]):
                v = reduce((equation << 1) | ((value >> bit) & 1), basis)
                assert v != 1
                if v > 1:
                    basis[v.bit_length()-1] = v
    assert len(basis) == 15365
    for bit, equation in enumerate(expr[0]):
        v = reduce((equation << 1) | ((0x80000000 >> bit) & 1), basis)
        assert v != 1
        if v > 1:
            basis[v.bit_length()-1] = v
    assert len(basis) == 15397

    words = {}
    for j in range(16, 603):
        vals = []
        missing = []
        for i in (j-1, j, j+1):
            value = known = 0
            for bit, equation in enumerate(expr[i]):
                v = reduce(equation << 1, basis)
                if v <= 1:
                    value |= v << bit
                    known |= 1 << bit
            vals.append(value)
            missing.append(U ^ known)
        if sum(x.bit_count() for x in missing) > 1:
            continue
        options = {(key_term(j, *vals) - j) & U}
        for pos, uncertain in enumerate(missing):
            if uncertain:
                variant = vals.copy()
                variant[pos] |= uncertain
                options.add((key_term(j, *variant) - j) & U)
        words[j] = sorted(options)
    assert len(words) == 86
    assert sum(len(v) == 1 for v in words.values()) == 62
    assert sum(len(v) == 2 for v in words.values()) == 24
    assert words[22] == [0xFD6A4CF7]
    assert words[23] == [0x06EDCDAD]
    return words


def fragments(words):
    result = []
    for index, options in sorted(words.items()):
        byte_options = [v.to_bytes(4, "big") for v in options]
        for k in range(4):
            values = [v[k] for v in byte_options]
            mask = 0xff ^ (values[0] ^ values[-1])
            # Offset is relative to the end of the binary seed B, so unknown
            # absolute seed length does not change residue equalities.
            result.append((-4*(index-15)+k, values[0] & mask, mask))
    assert sum(mask.bit_count() for _, _, mask in result) == 2728
    return result


def compatible(fragments_list, period):
    known = {}
    for offset, value, mask in fragments_list:
        pos = offset % period
        if pos in known:
            prior, prior_mask = known[pos]
            if (value ^ prior) & mask & prior_mask:
                return False
            known[pos] = (value | prior, mask | prior_mask)
        else:
            known[pos] = (value, mask)
    return True


def main():
    # The test correctly recognizes and falsifies genuine 16-byte periodic
    # sources independently of any printer-specific constraints.
    toy = [(i, (i % 16) ^ 0x6a, 0xff) for i in range(-160, 0)]
    assert compatible(toy, 16)
    assert not compatible(toy, 15)
    original = fragments(original_seed_words())
    matches = [p for p in range(1, 2430) if compatible(original, p)]
    assert len(matches) == 203
    assert min(matches) == 1672
    print("ORIGINAL_SEED_WORDS 86; EXACT 62; ONE_BIT_AMBIGUOUS 24")
    print("SOURCE_BITS 2728")
    print("MIN_COMPATIBLE_STRICT_BYTE_PERIOD", min(matches))
    print("COMPATIBLE_PERIODS_1_2429", len(matches))
    print("PERIODS_1_1671_EXCLUDED", 1671)
    print("PERIODS_1_1024_COMPATIBLE", sum(p <= 1024 for p in matches))
    print("SYNTHETIC_PERIODIC_POSITIVE", True)
    print("SELECTED_K04_BIT_AUTHENTICATION", 0)


if __name__ == "__main__":
    main()
