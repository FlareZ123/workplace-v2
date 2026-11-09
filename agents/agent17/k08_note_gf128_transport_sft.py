"""Full-known-caption GF(2^128) affine transport with independent original holdouts."""
import itertools
from k08_note_bytechannel_sft import read_original, component

U = (1 << 128) - 1


def multiply(a, b):
    out = 0
    for _ in range(128):
        if b & 1:
            out ^= a
        b >>= 1
        a = ((a << 1) & U) ^ (0x87 if (a >> 127) else 0)
    return out


def inverse(a):
    assert a
    y = 1
    for k in range(127, -1, -1):
        y = multiply(y, y)
        if k:
            y = multiply(y, a)
    assert multiply(a, y) == 1
    return y


def model(notes, spool):
    ids = [2, 6, 13, 17, 18]
    h = {300+i: int.from_bytes(component(notes[i]), "big") for i in ids}
    p = {300+i: int.from_bytes(spool[300+i][2], "big") for i in ids}
    successes = []
    for i, j in itertools.combinations(h, 2):
        a = multiply(p[i] ^ p[j], inverse(h[i] ^ h[j]))
        b = p[i] ^ multiply(a, h[i])
        held = [z for z in h if z not in (i, j)]
        equal = [z for z in held if p[z] == (multiply(a, h[z]) ^ b)]
        if equal:
            successes.append((i, j, equal, a, b))
    return successes


def run():
    assert multiply(0x12345, inverse(0x12345)) == 1
    notes, spool = read_original()
    assert model(notes, spool) == []
    print("ORIGINAL 10 calibrator pairs, 30 full historical 128-bit holdouts, zero passes")
    a = int("F3A4059DE2B6C742B28D890171EE835A", 16)
    b = int("48AAFA5609B0C6FE39D45D1823D12BCD", 16)
    synthetic = dict(spool)
    for i in (2, 6, 13, 17, 18):
        packet = (multiply(a, int.from_bytes(component(notes[i]), "big")) ^ b).to_bytes(16, "big")
        cl, ds, _ = spool[300+i]
        synthetic[300+i] = (cl, ds, packet)
    good = model(notes, synthetic)
    assert len(good) == 10 and all(len(g[2]) == 3 for g in good)
    final = int.from_bytes(component("synthetic final selected line"), "big")
    packet = multiply(a, final) ^ b
    for i, j, held, aa, bb in good:
        assert multiply(inverse(aa), packet ^ bb) == final
    print("SYNTHETIC 10/10 models and 30/30 heldouts PASS; whole unknown recoverable")


if __name__ == "__main__":
    run()
