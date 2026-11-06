"""H-17 printer/recorder source-only metadata-first MT stage holdout.

Run in checkout: python agents/agent16/k04_recorder_metadata_inverse_holdout_sft.py
Uses original evidence, excluding selected printer ACK2 and acceptance targets.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import random
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent49.k04_p951_symbolic_basis import source, get, temper, untemper

RECORDER_HASH = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
EXPECTED = [(9, -793, 17), (13, -769, 32), (24, -683, 32), (44, -545, 32)]


def full_known_top(basis, symbolic, count):
    bits = [basis.predict(v) for v in symbolic[32-count:]]
    if any(x is None for x in bits):
        return None
    return sum(bit << i for i, bit in enumerate(bits))


def native_known_mask(basis, symbolic):
    predictions = [basis.predict(v) for v in symbolic]
    mask = sum(1 << i for i, bit in enumerate(predictions) if bit is not None)
    value = sum(bit << i for i, bit in enumerate(predictions) if bit is not None)
    return mask, value


def main():
    b, mt = source(ROOT / 'resources')
    recorder = (ROOT / 'resources/evidence/recorder/trip-recorder.raw').read_bytes()
    assert sha256(recorder).hexdigest() == RECORDER_HASH
    assert len(recorder) == 16 + 88*24 and recorder[:8] == b'TRP2DUMP'
    rows = {}
    for record_i in range(88):
        chunk = recorder[16+record_i*24:16+(record_i+1)*24]
        epoch, node, event, latch, seq, control, aux, crc = struct.unpack('<IHBBI4sII',chunk)
        assert ((zlib.crc32(chunk[:20]) & 0xffffffff) == crc) == (
            node == 50 or seq not in (900, 901, 902, 903)
        )
        if node != 50:
            continue
        assert seq not in rows and 2000 <= aux < 8000 and 0 <= latch < 4
        rows[seq] = (aux, latch, untemper(int.from_bytes(control, 'little')))
    assert sorted(rows) == list(range(72))

    # Build stage predictions from the 132 intact printer packets alone.
    # Select recorder records exclusively by their AUX/LATCH, withholding CONTROL.
    signatures = {}
    for q in range(-999, -252):
        latch = full_known_top(b, temper(get(mt, q-1)), 3)
        aux_code = full_known_top(b, temper(get(mt, q+1)), 13)
        if latch is None or aux_code is None or aux_code >= 6000 or latch >= 4:
            continue
        signatures.setdefault((2000+aux_code, latch), []).append(q)

    holdouts = []
    for seq, (aux, latch, original_control) in sorted(rows.items()):
        for q in signatures.get((aux, latch), []):
            mask, value = native_known_mask(b, get(mt, q))
            holdouts.append((seq, q, mask.bit_count(), (original_control & mask) == value, mask, value))
    assert [(seq, q, bits) for seq, q, bits, ok, *_ in holdouts] == EXPECTED
    assert all(ok for _, _, _, ok, *_ in holdouts)

    # Uniformly permute four selected AUX/LATCH pairs among 72 fixed original
    # controls. Same count distribution as a full 72-element pair permutation.
    selected = [(q, mask, value) for _, q, _, _, mask, value in holdouts]
    controls = [rows[i][2] for i in range(72)]
    rng = random.Random(20261106)
    counts = Counter()
    for _ in range(200000):
        sample = rng.sample(range(72), len(selected))
        hits = sum((controls[i] & mask) == value
                   for i, (_, mask, value) in zip(sample, selected))
        counts[hits] += 1
    assert sum(counts.values()) == 200000
    assert counts == Counter({0: 189285, 1: 10494, 2: 219, 3: 2})

    print('RECORDER_METADATA_BLIND_HOLDOUT source_rank', b.rank, 'stage_range=-999..-253',
          'node50_rows', len(rows), 'stage_matches', len(holdouts),
          'heldout_control_bits', sum(x[2] for x in holdouts),
          'independent_wholeword_matches', sum(x[3] for x in holdouts))
    for seq, q, bits, match, _, _ in holdouts:
        print('INVERSE_METADATA_STAGE seq', seq, 'q', q, 'predicted_control_bits', bits, 'match', match)
    print('PAIR_SHUFFLE_200K', dict(sorted(counts.items())))
    print('AUTHENTIC_SELECTED_COUPON_BITS 0; K04/K08 MISSING')


if __name__ == '__main__':
    main()
