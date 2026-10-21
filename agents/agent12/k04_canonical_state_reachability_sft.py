"""Original-source K04 reachable-state GF(2) SFT.

Tests the published, source-consistent 133-row MT chronology at index 955.
No selected 18:02 payload, K04 mask, acceptance digest, or K08 data is read.

Usage: python k04_canonical_state_reachability_sft.py h17-archive-dump.zip
"""
from hashlib import sha256
from pathlib import Path
import random
import sys
from zipfile import ZipFile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STARTS = [
    0, 7, 15, 22, 30, 38, 44, 51, 67, 76, 84, 92, 99, 112, 120, 126,
    132, 138, 144, 151, 158, 165, 171, 179, 186, 192, 198, 205, 211,
    218, 224, 230, 237, 243, 250, 260, 268, 278, 285, 298, 305, 311,
    318, 328, 339, 346, 352, 358, 364, 370, 376, 382, 388, 394, 401,
    407, 416, 423, 429, 436, 442, 456, 463, 474, 481, 489, 495, 507,
    515, 522, 530, 536, 543, 549, 563, 569, 576, 584, 590, 597, 604,
    610, 617, 624, 632, 638, 644, 650, 659, 665, 671, 679, 689, 697,
    705, 714, 721, 733, 740, 747, 753, 759, 766, 772, 783, 789, 796,
    807, 813, 820, 826, 833, 839, 846, 853, 861, 870, 876, 882, 888,
    896, 906, 916, 922, 928, 934, 940, 946, 951, 955, 959, 963, 967,
]
A = 0x9908B0DF
LOW = 0x7FFFFFFF


def temper(value):
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    return (value ^ (value >> 18)) & 0xFFFFFFFF


def untemper(value):
    current = value
    for _ in range(3):
        current = value ^ (current >> 18)
    value, current = current, current
    for _ in range(3):
        current = value ^ ((current << 15) & 0xEFC60000)
    value, current = current, current
    for _ in range(6):
        current = value ^ ((current << 7) & 0x9D2C5680)
    value, current = current, current
    for _ in range(4):
        current = value ^ (current >> 11)
    return current & 0xFFFFFFFF


def twist(value):
    return (value >> 1) ^ (A if value & 1 else 0)


def image_admissible(words):
    assert len(words) == 624
    observed = words[623] ^ words[396]
    return any(twist((bit << 31) | (words[0] & LOW)) == observed
               for bit in (0, 1))


def synthetic_controls():
    for seed in (0, 1, 5489, 20261021, 0xDEADBEEF):
        rng = random.Random(seed)
        words = [untemper(rng.getrandbits(32)) for _ in range(1251)]
        assert image_admissible(words[:624])
        assert image_admissible(words[1:625])
        assert image_admissible(words[627:1251])
        altered = words[:624]
        for index in (104, 332, 333, 334, 335):
            modified = altered.copy()
            modified[index] ^= 0xDEADBEEF
            assert image_admissible(modified)
        bad = altered.copy()
        bad[0] ^= 1
        assert not image_admissible(bad)
    print("synthetic seeded-MT positive/negative image controls 5/5 PASS")


def symbolic_mt(horizon):
    words = [tuple(1 << (32 * i + bit) for bit in range(32))
             for i in range(624)]
    for t in range(horizon - 623):
        prev, adjacent, middle = words[t], words[t + 1], words[t + 397]
        new = []
        for bit in range(32):
            shifted = (adjacent[bit + 1] if bit < 30
                       else prev[31] if bit == 30 else 0)
            expr = middle[bit] ^ shifted
            if (A >> bit) & 1:
                expr ^= adjacent[0]
            new.append(expr)
        words.append(tuple(new))
    return words


def add_equation(basis, vector, rhs):
    while vector:
        pivot = vector.bit_length() - 1
        old = basis.get(pivot)
        if old is None:
            basis[pivot] = (vector, rhs)
            return 1
        vector ^= old[0]
        rhs ^= old[1]
    assert rhs == 0, "original source contradicts the modeled MT/state conditions"
    return 0


def main(archive):
    assert len(STARTS) == 133 and STARTS[129] == 955
    assert all(STARTS[i] + 4 <= STARTS[i + 1] for i in range(132))
    synthetic_controls()
    with ZipFile(archive) as z:
        source = z.read("evidence/print/spool-reconstruction.log")
    assert sha256(source).hexdigest() == SPOOL_SHA
    lines = [line for line in source.decode().splitlines()
             if line.startswith("2026-")]
    assert len(lines) == 133

    source_words = {}
    for index, line in enumerate(lines):
        if index == 129:  # Withhold the selected K04 payload completely.
            continue
        payload = bytes.fromhex(next(field[8:] for field in line.split()
                                     if field.startswith("PAYLOAD=")))
        assert len(payload) == 16
        for word_index in range(4):
            raw = int.from_bytes(payload[4 * word_index:4 * word_index + 4],
                                 "little")
            value = untemper(raw)
            assert temper(value) == raw
            source_words[STARTS[index] + word_index] = value
    assert len(source_words) == 528

    words = symbolic_mt(STARTS[-1] + 3)
    basis = {}
    for position, value in sorted(source_words.items()):
        for bit in range(32):
            add_equation(basis, words[position][bit], (value >> bit) & 1)
    assert len(basis) == 15305, len(basis)
    print("intact original spool equations 16896; source rank", len(basis))

    # Image(T) of the 624-word MT shift-window has codimension 31.
    # X623 xor X396 must equal twist((old_MSB << 31) | X0.low31).
    # The unknown old_MSB changes only bit30, leaving 31 linear equations.
    before = len(basis)
    for bit in range(32):
        if bit == 30:
            continue
        g = (words[0][bit + 1] if bit < 30 else 0)
        if (A >> bit) & 1:
            g ^= words[0][0]
        add_equation(basis, words[623][bit] ^ words[396][bit] ^ g, 0)
    assert len(basis) - before == 31
    print("independent canonical reachable-image equations", len(basis) - before)
    print("original source + reachable-state joint rank", len(basis))

    before = len(basis)
    for position in range(STARTS[129], STARTS[129] + 4):
        for bit in range(32):
            add_equation(basis, words[position][bit], 0)
    assert len(basis) - before == 128
    print("withheld selected K04 128-bit quotient rank", len(basis) - before)
    print("ORIGINAL REC8 target bytes fixed: 0/16")
    print("Scope: conditional common-MT index955 model; no historical producer proof.")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1
         else Path("h17-archive-dump.zip"))
