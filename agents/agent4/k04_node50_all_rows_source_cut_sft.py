"""H-17 source-only node50 chronology cut; read-only, Python 3 stdlib.

Requires the unchanged original resources and Agent49's exact p951 MT basis.
Run: python agents/agent4/k04_node50_all_rows_source_cut_sft.py
"""
import hashlib
import random
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents' / 'agent49'))
from k04_p951_symbolic_basis import source, get, untemper

LO, HI = -810, -339
A, B = 4, 11
REC_SHA = '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'


def recorder():
    raw = (ROOT / 'resources/evidence/recorder/trip-recorder.raw').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REC_SHA
    assert raw[:8] == b'TRP2DUMP' and len(raw) == 16 + 88*24
    records = {}
    for i in range(88):
        row = raw[16+24*i:16+24*(i+1)]
        _, node, _, _, seq, control, _, crc = struct.unpack('<IHBBIIII', row)
        if node == 50:
            assert zlib.crc32(row[:20]) == crc
            records[seq] = untemper(control)
    assert set(records) == set(range(72))
    return records


def source_fixed(basis, vectors):
    data = {}
    for stage in range(LO, HI+1):
        mask = value = 0
        for bit, equation in enumerate(get(vectors, stage)):
            predicted = basis.predict(equation)
            if predicted is not None:
                mask |= 1 << bit
                value |= predicted << bit
        data[stage] = (mask, value)
    return data


def matches(data, observation, stage):
    mask, value = data[stage]
    return ((observation ^ value) & mask) == 0


def full_chain_failure(data, observations, check_source=False):
    frontier = {LO}
    for seq in range(8, 71):
        frontier = {
            at for at in range(LO+4*(seq-7), min(HI, LO+11*(seq-7))+1)
            if matches(data, observations[seq], at)
            and any(A <= at-prev <= B for prev in frontier)
        }
        if seq == 33:
            assert not check_source or frontier == {-630, -629}
        if not frontier:
            return seq
    return None


def best_subset(data, records):
    paths = {(7, LO): (1, ((7, LO),))}
    for seq in range(8, 71):
        for stage in range(LO, HI+1):
            if seq == 70 and stage != HI:
                continue
            if not matches(data, records[seq], stage):
                continue
            prev = max((item for (s, p), item in paths.items()
                        if s < seq and A*(seq-s) <= stage-p <= B*(seq-s)),
                       key=lambda item: item[0], default=None)
            if prev:
                paths[seq,stage] = (prev[0]+1, prev[1]+((seq,stage),))
    return paths.get((70,HI))


def main():
    basis, vectors = source(ROOT / 'resources')
    assert basis.rank == 15365
    original = recorder()
    fixed = source_fixed(basis, vectors)
    assert matches(fixed, original[7], LO)
    assert matches(fixed, original[70], HI)

    # Fully observed planted 64-row producer, plus a flipped held-out row.
    rng = random.Random(0xA170)
    planted = {p: (0xffffffff, rng.getrandbits(32)) for p in range(LO,HI+1)}
    index = [LO+7*i+(30*i//63) for i in range(64)]
    assert index[0] == LO and index[-1] == HI
    sample = {seq: planted[index[seq-7]][1] for seq in range(7,71)}
    assert full_chain_failure(planted, sample) is None
    assert best_subset(planted, sample)[0] == 64
    sample[34] ^= 1
    assert full_chain_failure(planted, sample) == 34

    assert full_chain_failure(fixed, original, check_source=True) == 34
    assert original[34] == 0x3096c886
    assert fixed[-623] == (0x80000001, 0x00000001)
    # Seq33's only surviving positions are -630/-629; next gap requires
    # seq34 to be one of -626..-618, all incompatible with printer bits.
    mismatch = {p: ((original[34]^fixed[p][1])&fixed[p][0]).bit_count()
                for p in range(-626,-617)}
    assert mismatch == {-626:16,-625:12,-624:5,-623:1,-622:19,
                        -621:13,-620:15,-619:12,-618:18}
    # Stronger frozen-56-row-source geometry cut: seq33=-630 and seq36=-609.
    # Any source-faithful, monotonically advancing recorder emitter must
    # place seq34 strictly in the 20 native stages between them. Every
    # such position contradicts at least one original printer-fixed bit,
    # irrespective of the number of skipped/rejected intermediate draws.
    open_window = range(-629, -609)
    interior_mismatches = {
        p: ((original[34] ^ fixed[p][1]) & fixed[p][0]).bit_count()
        for p in open_window
    }
    assert len(interior_mismatches) == 20
    assert min(interior_mismatches.values()) == 1
    assert not any(matches(fixed, original[34], p) for p in open_window)
    # Plant a source-compatible control at the closest stage to distinguish
    # genuine model contradiction from an impossible visibility criterion.
    planted_34 = (original[34] & ~fixed[-623][0]) | fixed[-623][1]
    assert matches(fixed, planted_34, -623)
    assert not matches(fixed, original[34], -623)
    maximum = best_subset(fixed, original)
    assert maximum and maximum[0] == 60
    omissions = sorted(set(range(7,71))-{s for s,_ in maximum[1]})
    assert omissions == [30,36,67,68]
    print('Original printer/recorder SHA, CRC and rank: PASS')
    print('Synthetic 64-row positive and flipped-row negative: PASS')
    print('seq33 source-only stage frontier: -630,-629')
    print('seq34 -626..-618 fixed-bit mismatches:', mismatch)
    print('all-64 prefix first impossible at seq34; endpoint70 not required')
    print('even with UNBOUNDED gaps between fixed seq33=-630/seq36=-609,')
    print('  seq34 has zero source-compatible native stages in -629..-610')
    print('  minimum original conflict:', min(interior_mismatches.values()), 'of 20 positions')
    print('max source-only subsequence with 7/70 endpoints: 60/64')
    print('one optimal omission set:', omissions)
    print('K04/K08 recovery status: INCOMPLETE')


if __name__ == '__main__':
    main()
