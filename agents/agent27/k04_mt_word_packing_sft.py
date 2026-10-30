"""H-17 printer MT word packing: a selected-coupon-withheld source-only SFT.

Run as one file from the repository checkout.  Uses Python standard library.
This tests hypothetical MT19937 serialization of retained printer records,
not historical producer authenticity, coupon recovery, or K04 acceptance.
"""

from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from random import Random
import re

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / 'resources/evidence/print/spool-reconstruction.log'
SOURCE_SHA256 = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
M32 = 0xFFFFFFFF


def undo_right(y: int, shift: int) -> int:
    x = y
    for _ in range(6):
        x = (y ^ (x >> shift)) & M32
    return x


def undo_left(y: int, shift: int, mask: int) -> int:
    x = y
    for _ in range(6):
        x = (y ^ ((x << shift) & mask)) & M32
    return x


def untemper(y: int) -> int:
    y = undo_right(y, 18)
    y = undo_left(y, 15, 0xEFC60000)
    y = undo_left(y, 7, 0x9D2C5680)
    return undo_right(y, 11)


def twist(a: int, b: int) -> int:
    x = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (x >> 1) ^ (0x9908B0DF if x & 1 else 0)


def unpack(payload: bytes, byteorder: str, reversed_words: bool) -> tuple[int, ...]:
    parts = [payload[i:i + 4] for i in range(0, 16, 4)]
    if reversed_words:
        parts.reverse()
    return tuple(untemper(int.from_bytes(part, byteorder)) for part in parts)


def test_synthetic_controls() -> None:
    rng = Random(7123)
    stream = [rng.getrandbits(32) for _ in range(628)]
    for byteorder in ('little', 'big'):
        for reverse in (False, True):
            def pack(original_words: list[int]) -> bytes:
                blocks = [w.to_bytes(4, byteorder) for w in original_words]
                if reverse:
                    blocks.reverse()
                return b''.join(blocks)

            groups = [unpack(pack(stream[i:i + 4]), byteorder, reverse)
                      for i in (0, 397, 624)]
            assert all(groups[2][j] == (groups[1][j] ^ twist(groups[0][j], groups[0][j + 1]))
                       for j in range(3))
    print('CONTROL: 4/4 word/byte transformations yield all 3/3 seeded MT triples')


def parse_unselected_source() -> dict[int, bytes]:
    data = SPOOL.read_bytes()
    assert sha256(data).hexdigest() == SOURCE_SHA256, 'original source changed'
    lines = [line for line in data.decode().splitlines() if ' PAYLOAD=' in line]
    assert len(lines) == 133
    result = {}
    for index, line in enumerate(lines):
        if index == 129:
            continue  # Disputed 18:02 selected ACK never decoded or used.
        match = re.search(r'PAYLOAD=([0-9A-F]{32})\b', line)
        assert match is not None
        result[index] = bytes.fromhex(match.group(1))
    assert len(result) == 132
    print('SOURCE: expected SHA256, 132 original retained payloads; r129 omitted')
    return result


def fullword_matches(rows: dict[int, tuple[int, ...]]) -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]]:
    by_value: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for row, words in rows.items():
        for word, value in enumerate(words):
            by_value[value].append((row, word))
    ordinary: list[tuple[int, ...]] = []
    late: list[tuple[int, ...]] = []
    for row_a in range(128):
        values_a = rows[row_a]
        for word_a in range(3):
            delta = twist(values_a[word_a], values_a[word_a + 1])
            for row_b in range(row_a + 1, 128):
                for word_b, value_b in enumerate(rows[row_b]):
                    possible_c = (delta ^ value_b) & M32
                    for row_c, word_c in by_value.get(possible_c, ()):
                        if row_c <= row_b:
                            continue
                        hit = (row_a, word_a, row_b, word_b, row_c, word_c)
                        (ordinary if row_c < 128 else late).append(hit)
    return ordinary, late


def main() -> None:
    test_synthetic_controls()
    original = parse_unselected_source()
    counts = {}
    for byteorder in ('little', 'big'):
        for reverse in (False, True):
            rows = {i: unpack(data, byteorder, reverse) for i, data in original.items()}
            ordinary, late = fullword_matches(rows)
            counts[(byteorder, reverse)] = (len(ordinary), len(late))
            print(f'VIEW: {byteorder=} {reverse=} ordinary={len(ordinary)} late={len(late)}')
            if byteorder == 'little' and reverse:
                # These are exactly the two apparent exceptional late matches
                # whose strict MT stream chronology is impossible.
                first = (44, 1, 97, 0, 131, 3)
                second = (44, 2, 97, 1, 130, 0)
                assert first in late and second in late
                for name, hit in [('LATE-A', first), ('LATE-B', second)]:
                    a, aw, b, bw, c, cw = hit
                    reconstructed = (rows[b][bw] ^ twist(rows[a][aw], rows[a][aw + 1])) & M32
                    assert reconstructed == rows[c][cw]
                    print(f'{name}: {hit} -> authentic retained output {rows[c][cw]:08X}')
                d131 = 624 + first[1] - first[5]
                d130 = 624 + second[1] - second[5]
                # Coherent MT would require s131-s44=622,
                # s130-s44=626, thus s131-s130=-4. Chronological
                # 4-word records require s131-s130 >= 4.
                assert (d131, d130, d131 - d130) == (622, 626, -4)
                assert d131 - d130 < 4
                print('CHRONOLOGY CONTRADICTION: s131-s44=622, s130-s44=626, '
                      'thus s131-s130=-4, but row130 precedes row131 by >=4 words')

    assert counts[('little', False)] == (23, 2)
    assert counts[('little', True)] == (19, 4)
    assert counts[('big', False)] == (0, 0)
    assert counts[('big', True)] == (0, 0)
    print('RESULT: reverse-4-word original view is inconsistent under one ordered '
          'MT stream; no selected K04 bytes, mask or acceptance hash were used')


if __name__ == '__main__':
    main()
