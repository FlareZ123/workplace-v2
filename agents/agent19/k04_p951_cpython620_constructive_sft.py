"""Source-pinned p951 original H17 CPython 620-word integer seed constructor.

The four repeated first-loop key words are 0,1,2,3 at injections 620..623.
An exact 32-bit one-variable, three-high-pair lowbit inverse constructs an
original 132/132 matching genuine CPython seed. Prescribed K04 bits remain
128/128 independent, under the hypothesized producer only.
"""
import importlib.util
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "agent19_base", ROOT / "k04_p951_cpython624_623_constructive_sft.py"
)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
U = a.U


def unmix(z, m):
    x = (z * pow(m, -1, 1 << 32)) & U
    return x ^ (x >> 30)


def impose(basis, index, value):
    for bit in range(32):
        r = a.reduce((1 << (32*index + bit + 1)) | ((value >> bit) & 1), basis)
        if r == 1:
            return False
        if r > 1:
            basis[r.bit_length() - 1] = r
    return True


def inverse_y(s2, s3, s4, x623, late_key2):
    """Solve last two repeated-index equalities exactly by low-bit lifting.

    key3 has source-known X3,X4; last key3 gives Q=X1 as a function of Y1.
    key2 comparison becomes one 32-bit equation in Y1. Guess high bits of
    Y1,Q,X2 then lift 30 low bits and validate full values.
    """
    x3 = (((s3 + 3) & U) ^ a.mix(s2, a.M2)) & U
    x4 = (((s4 + 4) & U) ^ a.mix(s3, a.M2)) & U
    key3 = (x4 - (a.BASE[4] ^ a.mix(x3, a.M1)) - 3) & U
    b = a.mix(x623, a.M1)
    c = (s2 + 2) & U
    answers = []
    for yhi in range(4):
        for qhi in range(4):
            for x2hi in range(4):
                prefixes = [0]
                for width in range(1, 31):
                    mask = (1 << width) - 1
                    new = []
                    for prefix in prefixes:
                        for ylo in (prefix, prefix | (1 << (width - 1))):
                            y = (yhi << 30) | ylo
                            q = (key3 + (y ^ b) + 3) & U
                            qpartial = (q & mask) | (qhi << 30)
                            x2 = (c ^ a.mix(qpartial, a.M2)) & U
                            x2partial = (x2 & mask) | (x2hi << 30)
                            early = (x3 - (a.BASE[3] ^
                                    a.mix(x2partial, a.M1)) - 2) & U
                            if (early & mask) == (late_key2 & mask):
                                new.append(ylo)
                    prefixes = new
                    assert len(prefixes) <= 20000
                    if not prefixes:
                        break
                for low in prefixes:
                    y = (yhi << 30) | low
                    q = (key3 + (y ^ b) + 3) & U
                    if q >> 30 != qhi:
                        continue
                    x2 = (c ^ a.mix(q, a.M2)) & U
                    if x2 >> 30 != x2hi:
                        continue
                    early = (x3 - (a.BASE[3] ^
                            a.mix(x2, a.M1)) - 2) & U
                    if early == late_key2:
                        answers.append((y, q, key3))
    return answers


def inverse_seed620(register):
    x = a.pre_second_register(register)
    A = a.BASE[1] ^ a.mix(a.BASE[0], a.M1)
    key0 = (x[621] - (a.BASE[621] ^ a.mix(x[620], a.M1))) & U
    y = (key0 + A) & U
    key1 = (x[2] - (a.BASE[2] ^ a.mix(y, a.M1)) - 1) & U
    key2 = (x[3] - (a.BASE[3] ^ a.mix(x[2], a.M1)) - 2) & U
    key3 = (x[4] - (a.BASE[4] ^ a.mix(x[3], a.M1)) - 3) & U
    assert key1 == ((x[622] - (a.BASE[622] ^
                     a.mix(x[621], a.M1)) - 1) & U)
    assert key2 == ((x[623] - (a.BASE[623] ^
                     a.mix(x[622], a.M1)) - 2) & U)
    assert key3 == ((x[1] - (y ^ a.mix(x[623], a.M1)) - 3) & U)
    keys = [0] * 620
    keys[:4] = [key0, key1, key2, key3]
    for j in range(4, 620):
        i = j + 1
        keys[j] = (x[i] - (a.BASE[i] ^
                   a.mix(x[i-1], a.M1)) - j) & U
    assert keys[-1] != 0
    seed = int.from_bytes(b"".join(k.to_bytes(4, "little") for k in keys), "little")
    assert a.actual_register(seed) == tuple(register)
    return seed


def find_source_seed():
    initial = a.initialized_register(a.initial_solution(a.basis))
    assert (initial[2], initial[3], initial[4], initial[622]) == (
        0xE32E1557, 0x3152E7CB, 0xBBDD46A0, 0xBBD5A4AB)
    rng = random.Random(20261103)
    for trial in range(1000):
        s621 = rng.getrandbits(31)
        s623 = 0x04710790 | (rng.getrandbits(1) << 31)
        x623 = (((s623+623)&U) ^ a.mix(initial[622],a.M2)) & U
        x622 = (((initial[622]+622)&U) ^ a.mix(s621,a.M2)) & U
        key2 = (x623 - (a.BASE[623] ^ a.mix(x622,a.M1)) - 2) & U
        b = a.basis.copy()
        assert impose(b,621,s621) and impose(b,623,s623)
        for y,q,_ in inverse_y(initial[2],initial[3],initial[4],x623,key2):
            s1 = ((q ^ a.mix(s623,a.M2)) - 1) & U
            x2 = (((initial[2]+2)&U) ^ a.mix(q,a.M2)) & U
            key1 = (x2 - (a.BASE[2] ^ a.mix(y,a.M1)) - 1) & U
            x621 = unmix(((x622-key1-1)&U) ^ a.BASE[622],a.M1)
            s620 = unmix(x621 ^ ((s621+621)&U),a.M2)
            key0 = (y - (a.BASE[1] ^ a.mix(a.BASE[0],a.M1))) & U
            x620 = unmix(((x621-key0)&U) ^ a.BASE[621],a.M1)
            s619 = unmix(x620 ^ ((s620+620)&U),a.M2)
            extended = b.copy()
            if not impose(extended,1,s1):
                continue
            if not impose(extended,620,s620):
                continue
            if not impose(extended,619,s619):
                continue
            reg = a.initialized_register(a.initial_solution(extended))
            assert reg[1] == s1 and reg[619] == s619
            seed = inverse_seed620(reg)
            assert a.selected_from_actual_seed(seed) is not None
            print("PASS original source132/132 with real 620-word seed trial",trial)
            return extended
    raise AssertionError("No source-compatible 620-word seed in 1000 trials")


def complete_target(basis, target):
    enlarged = basis.copy()
    for lane in range(4):
        native = a.untemper(int.from_bytes(target[4*lane:4*lane+4],"little"))
        for bit, expr in enumerate(a.expressions[624 + 951 + lane]):
            rem = a.reduce((expr << 1) | ((native >> bit) & 1), enlarged)
            assert rem != 1
            if rem > 1:
                enlarged[rem.bit_length() - 1] = rem
    assert len(enlarged) - len(basis) == 128
    register = a.initialized_register(a.initial_solution(enlarged))
    seed = inverse_seed620(register)
    assert a.selected_from_actual_seed(seed) == target


def main():
    rng = random.Random(9620)
    for i in range(10):
        seed = (1 << (620*32-1)) | rng.getrandbits(620*32-1)
        s = a.actual_register(seed)
        x = a.pre_second_register(s)
        late = (x[623] - (a.BASE[623] ^ a.mix(x[622],a.M1)) - 2) & U
        true_y = ((a.BASE[1] ^ a.mix(a.BASE[0],a.M1)) + (seed & U)) & U
        assert any(y == true_y and q == x[1] for y,q,_ in
                   inverse_y(s[2],s[3],s[4],x[623],late))
    print("PASS 10/10 seeded CPython620 inversion positive controls")
    b = find_source_seed()
    for target in (bytes(16),bytes([255])*16,bytes([170])*16):
        complete_target(b,target)
        print("PASS original132/132 and target128/128",target.hex().upper())
    print("CONDITIONAL: n620 fully target ambiguous; historical K04 unknown")


if __name__ == "__main__":
    main()
