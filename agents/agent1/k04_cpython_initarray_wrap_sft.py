"""Single-file test of CPython MT19937 init_by_array index-1 double visit.

Separates first-pass A1 from wrapped B1 and final S1. No K04 coupon,
acceptance digest, or secret candidate is used in any computation.
"""
import hashlib
import random
from pathlib import Path

U = 0xFFFFFFFF
F1 = 1664525
F2 = 1566083941
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def t(x):
    return x ^ (x >> 30)


def direct_initialized(keys):
    """Compute complete state, retaining first and wrapped first-pass states."""
    length = len(keys)
    assert 1 <= length <= 624 and all(0 <= x <= U for x in keys)
    g = [19650218]
    for index in range(1, 624):
        g.append((1812433253 * t(g[-1]) + index) & U)
    a = [g[0]]
    for index in range(1, 624):
        j = (index - 1) % length
        a.append(((g[index] ^ (F1 * t(a[-1]))) + keys[j] + j) & U)
    j = 623 % length
    b1 = ((a[1] ^ (F1 * t(a[623]))) + keys[j] + j) & U
    s = [0] * 624
    s[1] = b1
    for index in range(2, 624):
        s[index] = ((a[index] ^ (F2 * t(s[index - 1]))) - index) & U
    s[1] = ((b1 ^ (F2 * t(s[623]))) - 1) & U
    s[0] = 0x80000000
    return a, b1, s


def reference_initialized(keys):
    """Independent loop-form replay of CPython's two initialization passes."""
    s = [19650218]
    for index in range(1, 624):
        s.append((1812433253 * t(s[-1]) + index) & U)
    i, j = 1, 0
    for _ in range(max(624, len(keys))):
        s[i] = ((s[i] ^ (F1 * t(s[i - 1]))) + keys[j] + j) & U
        i += 1
        j += 1
        if i == 624:
            s[0] = s[623]
            i = 1
        if j == len(keys):
            j = 0
    for _ in range(623):
        s[i] = ((s[i] ^ (F2 * t(s[i - 1]))) - i) & U
        i += 1
        if i == 624:
            s[0] = s[623]
            i = 1
    s[0] = 0x80000000
    return s


def control():
    count = 0
    old_s1_fail = old_s2_fail = 0
    for n in (1, 2, 3, 4, 5, 8, 16):
        for trial in range(12):
            keys = [((0x12345678 + 0x30158DA * j + 0x4F89D7 * trial) & U)
                    for j in range(n)]
            seed = sum(k << (32 * j) for j, k in enumerate(keys))
            a, b1, s = direct_initialized(keys)
            assert s == reference_initialized(keys)
            assert s == list(random.Random(seed).getstate()[1][:624])
            assert s[2] == ((a[2] ^ (F2 * t(b1))) - 2) & U
            assert s[7] == ((a[7] ^ (F2 * t(s[6]))) - 7) & U
            wrong_s1 = ((a[1] ^ (F2 * t(s[623]))) - 1) & U
            wrong_s2 = ((a[2] ^ (F2 * t(wrong_s1))) - 2) & U
            old_s1_fail += wrong_s1 != s[1]
            old_s2_fail += wrong_s2 != s[2]
            count += 1
    assert old_s1_fail == old_s2_fail == count
    known_s6, known_s7 = 0xE403BB7D, 0x1F7B301F
    calculated_a7 = ((known_s7 + 7) & U) ^ (F2 * t(known_s6) & U)
    assert calculated_a7 == 0x2AED5290
    spool = (Path(__file__).resolve().parents[2] /
             "resources/evidence/print/spool-reconstruction.log")
    assert hashlib.sha256(spool.read_bytes()).hexdigest() == SPOOL_SHA
    print(f"GENUINE_CPYTHON_INITIALIZER_CONTROLS={count}/{count} PASS")
    print(f"OLD_S1_MISMATCHES={old_s1_fail}/{count}; OLD_S2_MISMATCHES={old_s2_fail}/{count}")
    print("CORRECT_A7_ORIGINAL_SOURCE=2AED5290, independent of wrapped-S1 correction")
    print("NO_ACCEPTANCE_OR_SELECTED_SOURCE_READ; K04 K08 UNRECOVERED")


if __name__ == "__main__":
    control()
