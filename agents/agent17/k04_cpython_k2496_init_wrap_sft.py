"""SFT: CPython init_by_array 624th update and second-pass S6.

Shows why a model using final S1 as the predecessor of S2 is unsound.
The synthetic Python reference state supplies a genuine source positive.
"""
import random

MASK = 0xFFFFFFFF
F1, F2 = 1664525, 1566083941


def mix(v):
    return v ^ (v >> 30)


def first_pass(keys):
    g = [19650218]
    for i in range(1, 624):
        g.append((1812433253 * mix(g[-1]) + i) & MASK)
    a = g.copy()
    n = len(keys)
    for i in range(1, 624):
        j = (i - 1) % n
        a[i] = ((a[i] ^ (F1 * mix(a[i - 1]))) + keys[j] + j) & MASK
    j = 623 % n
    a1_wrapped = ((a[1] ^ (F1 * mix(a[623]))) + keys[j] + j) & MASK
    return a, a1_wrapped


def s6_from(a, predecessor):
    for i in range(2, 7):
        predecessor = ((a[i] ^ (F2 * mix(predecessor))) - i) & MASK
    return predecessor


def test():
    for n in range(1, 5):
        keys = [(0x12345678 + i * 0x30158DA) & MASK for i in range(n)]
        seed = sum(value << (32 * i) for i, value in enumerate(keys))
        actual = random.Random(seed).getstate()[1][:624]
        a, wrapped = first_pass(keys)
        correct = s6_from(a, wrapped)
        # Wrong legacy branch: final S1 is not the input to second-pass S2.
        wrong_s1 = ((a[1] ^ (F2 * mix(actual[623]))) - 1) & MASK
        wrong = s6_from(a, wrong_s1)
        assert correct == actual[6], (n, correct, actual[6])
        assert wrong != actual[6], n
        print(f'n={n} actual_S6={actual[6]:08X} corrected={correct:08X} '
              f'old={wrong:08X} genuine_control=PASS')
    print('PASS 4/4 source-positive controls; 4/4 invalid old-branch predictions')


if __name__ == '__main__':
    test()
