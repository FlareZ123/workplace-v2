"""Original H-17 K04: per-32-bit-word mixed endian and packet-word order MT witnesses.

The selected original ACK2 payload is excluded before its bytes are decoded.
All complete source-template coupons are checked against unchanged K04 SHA256.
Run from any working directory: python agents/agent1/k04_mixedendian_source_sft.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
U = 0xFFFFFFFF
MAG = 0x9908B0DF


def untemper(value: int) -> int:
    for shift, left, mask in ((18, False, U), (15, True, 0xEFC60000),
                              (7, True, 0x9D2C5680), (11, False, U)):
        prior = value
        for _ in range(6):
            value = prior ^ (((value << shift) & mask) if left else (value >> shift))
        value &= U
    return value


def temper(value: int) -> int:
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    value ^= value >> 18
    return value & U


def twist(a: int, b: int) -> int:
    pair = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return ((pair >> 1) ^ (MAG if pair & 1 else 0)) & U


def words_from_packet(packet: tuple[bytes, ...], perm: tuple[int, ...], flags: int):
    return tuple(untemper(int.from_bytes(packet[perm[j]],
                                           'big' if (flags >> j) & 1 else 'little'))
                 for j in range(4))


def packet_from_words(native: tuple[int, ...], perm: tuple[int, ...], flags: int) -> bytes:
    blocks = [b''] * 4
    for j, word in enumerate(native):
        blocks[perm[j]] = temper(word).to_bytes(
            4, 'big' if (flags >> j) & 1 else 'little')
    return b''.join(blocks)


def witnesses(native: list[tuple[int, ...] | None]):
    inverse: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for row, packet in enumerate(native):
        if packet is not None:
            for lane, value in enumerate(packet):
                inverse[value].append((row, lane))
    result = []
    for r, first in enumerate(native):
        if first is None:
            continue
        for p in range(1, 4):
            correction = twist(first[p-1], first[p])
            for k in range(r + 1, len(native)):
                second = native[k]
                if second is None:
                    continue
                for i in range(4):
                    for l, q in inverse.get(second[i] ^ correction, ()):
                        if l > k:
                            result.append((r, p, k, i, l, q))
    return result


def options_for_target(native, selected, found):
    options = [set() for _ in range(4)]
    for r, p, k, i, l, q in found:
        prior = selected - (l - r)
        middle = prior + k - r
        if not (0 <= prior < middle < selected):
            continue
        first = native[prior]
        second = native[middle]
        if first is not None and second is not None:
            options[q].add(second[i] ^ twist(first[p-1], first[p]))
    return options


def read_source():
    raw = (ROOT / 'resources/evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    records = re.findall(
        rb'^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) '
        rb'PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$', raw, re.M)
    assert len(records) == 133
    assert records[129][:5] == (
        b'2026-10-03T18:02:00Z', b'PS-261003-0417', b'2', b'ACK', b'RECOVER')
    return [None if r == 129 else
            tuple(bytes.fromhex(entry[5].decode())[j:j+4] for j in (0,4,8,12))
            for r, entry in enumerate(records)]


def seeded_control():
    """Genuine Python MT stream with mixed serialization and an erased row."""
    passes = 0
    for perm, flags in (((2,0,3,1), 0b0101),
                        ((3,1,0,2), 0b1010),
                        ((0,1,2,3), 0)):
        generator = random.Random(0xA17E8BC0 + flags)
        outputs = [generator.getrandbits(32) for _ in range(935)]
        source = []
        target = b''
        for row in range(133):
            native_words = tuple(untemper(w) for w in outputs[7*row:7*row+4])
            packet = packet_from_words(native_words, perm, flags)
            assert words_from_packet(tuple(packet[j:j+4] for j in (0,4,8,12)),
                                     perm, flags) == native_words
            if row == 129:
                target = packet
                source.append(None)
            else:
                source.append(words_from_packet(tuple(packet[j:j+4]
                                                      for j in (0,4,8,12)), perm, flags))
        found = witnesses(source)
        predicted = options_for_target(source, 129, found)
        true_words = words_from_packet(tuple(target[j:j+4] for j in (0,4,8,12)),
                                       perm, flags)
        assert len(found) == 43
        assert [len(v) for v in predicted] == [0, 0, 0, 1]
        assert true_words[3] in predicted[3]
        passes += 1
    assert passes == 3
    print('SYNTHETIC_GENUINE_MT_MIXED_ENDIAN', passes, 'PASS', flush=True)


def main():
    seeded_control()
    source = read_source()
    route = json.loads((ROOT/'resources/evidence/recovery-routing.json').read_text())
    acceptance = json.loads((ROOT/'resources/acceptance.json').read_text())
    mask = bytes.fromhex(route['K04']['masked_component'])
    digest = acceptance['slot_sha256']['K04']
    counts = {'views':0, 'mixed_views':0, 'mixed_max_witnesses':0,
              'mixed_complete_views':0, 'mixed_complete_coupons':0,
              'uniform_complete_views':0, 'uniform_complete_coupons':0,
              'original_K04_hits':0}
    for perm in itertools.permutations(range(4)):
        for flags in range(16):
            counts['views'] += 1
            mixed = flags not in (0, 15)
            if mixed:
                counts['mixed_views'] += 1
            native = [None if row is None else words_from_packet(row, perm, flags)
                      for row in source]
            found = witnesses(native)
            if perm == (0,1,2,3) and flags == 0:
                assert len(found) == 25
            if mixed:
                counts['mixed_max_witnesses'] = max(
                    counts['mixed_max_witnesses'], len(found))
            options = options_for_target(native, 129, found)
            if any(not v for v in options):
                continue
            n = 1
            for v in options:
                n *= len(v)
            prefix = 'mixed' if mixed else 'uniform'
            counts[f'{prefix}_complete_views'] += 1
            counts[f'{prefix}_complete_coupons'] += n
            for candidate in itertools.product(*options):
                coupon = packet_from_words(candidate, perm, flags)
                key = bytes(a ^ b for a,b in zip(coupon, mask))
                if hashlib.sha256(key).hexdigest() == digest:
                    counts['original_K04_hits'] += 1
                    print('ORIGINAL_K04_PASS', coupon.hex().upper(), key.hex().upper())
    assert counts == {
        'views':384, 'mixed_views':336, 'mixed_max_witnesses':14,
        'mixed_complete_views':0, 'mixed_complete_coupons':0,
        'uniform_complete_views':24, 'uniform_complete_coupons':16189,
        'original_K04_hits':0}
    print('RESULT', json.dumps(counts, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
