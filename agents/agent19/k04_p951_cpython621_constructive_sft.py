"""H-17 p951 conditional original-source CPython integer 621-word constructor.

Uses exact full CPython initializer reversal and source GF2 basis of Agent19
companion. The 624 first-loop injections repeat key0,key1,key2 at indices
621,622,623. Never use selected source row129 or H17 acceptance in fitting.
"""
import importlib.util
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "agent19_source", ROOT / "k04_p951_cpython624_623_constructive_sft.py"
)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
U = a.U


def unmix(z, m):
    x = (z * pow(m, -1, 1 << 32)) & U
    return x ^ (x >> 30)


def impose(basis, index, word):
    for bit in range(32):
        r = a.reduce((1 << (32 * index + bit + 1)) | ((word >> bit) & 1), basis)
        if r == 1:
            return False
        if r > 1:
            basis[r.bit_length() - 1] = r
    return True


def lift_first_two(s2, s3, x623, k622):
    """Solve two 32-bit exact repeats via 64 guessed upper-bit configurations."""
    c = (s2 + 2) & U
    x3 = (((s3 + 3) & U) ^ a.mix(s2, a.M2)) & U
    b = a.mix(x623, a.M1)
    result = []
    for ytop in range(4):
        for qtop in range(4):
            for x2top in range(4):
                yh, qh = ytop << 30, qtop << 30
                prefixes = [(0, 0)]
                for width in range(1, 31):
                    mask = (1 << width) - 1
                    nxt = []
                    for low_y, low_q in prefixes:
                        for yi in (low_y, low_y | (1 << (width - 1))):
                            y = yh | yi
                            rhs = (k622 + (a.BASE[2] ^ a.mix(y, a.M1)) + 1) & U
                            for qi in (low_q, low_q | (1 << (width - 1))):
                                q = qh | qi
                                x2 = (c ^ a.mix(q, a.M2)) & U
                                if (x2 ^ rhs) & mask:
                                    continue
                                surrogate = (x2 & mask) | (x2top << 30)
                                key2 = (x3 - (a.BASE[3] ^
                                        a.mix(surrogate, a.M1)) - 2) & U
                                last = (q - (y ^ b) - 2) & U
                                if ((key2 ^ last) & mask) == 0:
                                    nxt.append((yi, qi))
                    prefixes = nxt
                    assert len(prefixes) <= 20000
                    if not prefixes:
                        break
                for yi, qi in prefixes:
                    y, q = yh | yi, qh | qi
                    x2 = (c ^ a.mix(q, a.M2)) & U
                    if (x2 >> 30) != x2top:
                        continue
                    key1 = (x2 - (a.BASE[2] ^ a.mix(y, a.M1)) - 1) & U
                    key2 = (x3 - (a.BASE[3] ^ a.mix(x2, a.M1)) - 2) & U
                    last = (q - (y ^ b) - 2) & U
                    if key1 == k622 and key2 == last:
                        result.append((y, q))
    return result


def inverse_seed621(register):
    x = a.pre_second_register(register)
    A = a.BASE[1] ^ a.mix(a.BASE[0], a.M1)
    key0 = (x[622] - (a.BASE[622] ^ a.mix(x[621], a.M1))) & U
    y = (key0 + A) & U
    key1 = (x[2] - (a.BASE[2] ^ a.mix(y, a.M1)) - 1) & U
    key2 = (x[3] - (a.BASE[3] ^ a.mix(x[2], a.M1)) - 2) & U
    assert key1 == ((x[623] - (a.BASE[623] ^
                     a.mix(x[622], a.M1)) - 1) & U)
    assert key2 == ((x[1] - (y ^ a.mix(x[623], a.M1)) - 2) & U)
    keys = [0] * 621
    keys[0], keys[1], keys[2] = key0, key1, key2
    for j in range(3, 621):
        i = j + 1
        keys[j] = (x[i] - (a.BASE[i] ^
                   a.mix(x[i - 1], a.M1)) - j) & U
    assert keys[-1] != 0
    seed = int.from_bytes(b"".join(k.to_bytes(4, "little") for k in keys), "little")
    assert a.actual_register(seed) == tuple(register)
    return seed


def original_witness():
    sample = a.initialized_register(a.initial_solution(a.basis))
    assert sample[2] == 0xE32E1557 and sample[3] == 0x3152E7CB
    assert sample[622] == 0xBBD5A4AB
    rng = random.Random(20261103)
    for trial in range(1000):
        s621 = rng.getrandbits(31)
        s623 = 0x04710790 | (rng.getrandbits(1) << 31)
        x623 = (((s623 + 623) & U) ^ a.mix(sample[622], a.M2)) & U
        x622 = (((sample[622] + 622) & U) ^ a.mix(s621, a.M2)) & U
        key1 = (x623 - (a.BASE[623] ^ a.mix(x622, a.M1)) - 1) & U
        b = a.basis.copy()
        assert impose(b, 621, s621) and impose(b, 623, s623)
        for y, q in lift_first_two(sample[2], sample[3], x623, key1):
            s1 = ((q ^ a.mix(s623, a.M2)) - 1) & U
            key0 = (y - (a.BASE[1] ^ a.mix(a.BASE[0], a.M1))) & U
            x621 = unmix(((x622 - key0) & U) ^ a.BASE[622], a.M1)
            s620 = unmix(x621 ^ ((s621 + 621) & U), a.M2)
            extended = b.copy()
            if not impose(extended, 1, s1):
                continue
            if not impose(extended, 620, s620):
                continue
            register = a.initialized_register(a.initial_solution(extended))
            assert register[1] == s1 and register[620] == s620
            seed = inverse_seed621(register)
            assert a.selected_from_actual_seed(seed) is not None
            print("PASS first original-compatible 621-word seed", trial)
            return extended
    raise AssertionError("No 621-word source-compatible seed in 1000 trials")


def enforce_selected(basis, target):
    enlarged = basis.copy()
    for lane in range(4):
        native = a.untemper(int.from_bytes(target[4*lane:4*lane+4], "little"))
        for bit, expr in enumerate(a.expressions[624 + 951 + lane]):
            rem = a.reduce((expr << 1) | ((native >> bit) & 1), enlarged)
            assert rem != 1
            if rem > 1:
                enlarged[rem.bit_length() - 1] = rem
    assert len(enlarged) - len(basis) == 128
    register = a.initialized_register(a.initial_solution(enlarged))
    seed = inverse_seed621(register)
    assert a.selected_from_actual_seed(seed) == target


def main():
    rng = random.Random(921)
    for index in range(10):
        seed = (1 << (621 * 32 - 1)) | rng.getrandbits(621 * 32 - 1)
        s = a.actual_register(seed)
        x = a.pre_second_register(s)
        k622 = (x[623] - (a.BASE[623] ^ a.mix(x[622], a.M1)) - 1) & U
        true_y = ((a.BASE[1] ^ a.mix(a.BASE[0], a.M1)) + (seed & U)) & U
        assert (true_y, x[1]) in lift_first_two(s[2], s[3], x[623], k622)
    print("PASS 10/10 genuine CPython 621-word seed inversion controls")
    b = original_witness()
    for target in (bytes(16), bytes([0xFF]) * 16, bytes([0xAA]) * 16):
        enforce_selected(b, target)
        print("PASS original132/132, target128/128", target.hex().upper())
    print("CONDITIONAL: n621 seed is source-feasible and K04 fully ambiguous")


if __name__ == "__main__":
    main()
