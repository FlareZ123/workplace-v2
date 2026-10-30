"""SFT: conditional ACK-only reverse-word MT chronology has a 58-word gauge freedom.

Original K04 selected payload, commitment and mask are never read. Research-only
source equations; this is not proof of a true historical common MT producer.
Run: python agents/agent31/k04_ack_chronology_sliding_certificate_sft.py
"""
import hashlib
from pathlib import Path
from random import Random
import re

SPOOL = Path(__file__).resolve().parents[2] / 'resources/evidence/print/spool-reconstruction.log'
EXPECTED = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK32 = (1 << 32) - 1

# Integer word-start witness for rows r0..r132, with original source r129
# deliberately excluded from all data observations. Obtained by integer
# difference-constraint optimization and checked independently below.
BASE = [
0, 4, 8, 12, 16, 20, 24, 28, 38, 42, 49, 54, 58, 77, 155, 159,
163, 167, 171, 175, 179, 183, 187, 191, 195, 199, 203, 207, 211,
215, 219, 224, 229, 233, 237, 241, 245, 249, 258, 262, 266, 276,
282, 286, 304, 366, 370, 374, 378, 382, 386, 390, 394, 398, 402,
406, 410, 414, 418, 422, 426, 430, 434, 438, 444, 449, 454, 474,
551, 555, 570, 574, 578, 582, 586, 590, 594, 598, 602, 606, 610,
614, 618, 622, 626, 630, 636, 640, 644, 648, 652, 656, 662, 666,
674, 678, 682, 702, 764, 784, 791, 795, 799, 803, 807, 811, 815,
819, 823, 827, 831, 835, 839, 843, 847, 851, 855, 859, 863, 867,
871, 883, 887, 891, 895, 899, 906, 910, 914, 918, 922, 926, 991]
SHIFT_ROWS = frozenset((13, 44, 67, 97, 129, 130, 131))


def untemper(y: int) -> int:
    for shift, left, mask in ((18, False, MASK32), (15, True, 0xEFC60000),
                              (7, True, 0x9D2C5680), (11, False, MASK32)):
        z = y
        for _ in range(6):
            z = (y ^ ((z << shift) & mask if left else z >> shift)) & MASK32
        y = z
    return y


def twist(a: int, b: int) -> int:
    u = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return ((u >> 1) ^ (0x9908B0DF if u & 1 else 0)) & MASK32


def original_hits() -> list[tuple[int, int, int, int, int, int]]:
    raw = SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    lines = [line for line in raw.decode('ascii').splitlines() if ' PAYLOAD=' in line]
    assert len(lines) == 133
    rows = {}
    for index, line in enumerate(lines):
        if index in (128, 129, 130):
            continue  # REQUESTED, disputed selected ACK, REQUESTED
        assert 'STATE=ACK' in line
        payload = bytes.fromhex(re.search(r'PAYLOAD=([A-F0-9]{32})', line).group(1))
        groups = [payload[i:i+4] for i in range(0, 16, 4)][::-1]
        rows[index] = tuple(untemper(int.from_bytes(group, 'little')) for group in groups)
    value_index = {}
    for index, words in rows.items():
        for word, value in enumerate(words):
            value_index.setdefault(value, []).append((index, word))
    hits = []
    for a in range(128):
        for aw in range(3):
            t = twist(rows[a][aw], rows[a][aw+1])
            for b in range(a + 1, 128):
                for bw, val in enumerate(rows[b]):
                    for c, cw in value_index.get((t ^ val) & MASK32, ()):
                        if c > b:
                            hits.append((a, aw, b, bw, c, cw))
    assert len(hits) == 21, ('Unexpected number of original fullword relations', len(hits))
    assert sum(c >= 128 for _, _, _, _, c, _ in hits) == 2
    return hits


def verify(starts: list[int], hits: list[tuple[int, int, int, int, int, int]]) -> None:
    assert len(starts) == 133 and starts[0] == 0 and starts[132] == 991
    assert all(starts[i + 1] - starts[i] >= 4 for i in range(132))
    for a, aw, b, bw, c, cw in hits:
        assert starts[b] + bw - starts[a] - aw == 397
        assert starts[c] + cw - starts[a] - aw == 624


def main() -> None:
    rng = Random(7123)
    w = [untemper(rng.getrandbits(32)) for _ in range(627)]
    assert all(w[624 + i] == (w[397 + i] ^ twist(w[i], w[i + 1])) for i in range(3))
    print('Synthetic seeded-MT fullword recurrence: PASS')
    hits = original_hits()
    print(f'Original fullword source relations: {len(hits)}; target r129 excluded')
    for displacement in range(59):
        starts = [base + (displacement if i in SHIFT_ROWS else 0)
                  for i, base in enumerate(BASE)]
        verify(starts, hits)
        assert starts[129] == 918 + displacement
    print('Source-constraint-compatible historical ordered chronologies: 59/59')
    print('Fixed endpoints: s0=0, s132=991; selected unknown start s129=918..976')
    print('Translation class: r13,r44,r67,r97,r129,r130,r131 each shifted by 0..58 words')
    print('No original selected payload bits, state replay, producer proof or recovery key')


if __name__ == '__main__':
    main()
