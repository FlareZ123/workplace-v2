"""H-17 source-only full affine-parity recorder/MT correspondence across stage -1100..11000.

Run from repository root: python agents/agent38/k04_extended_affine_recorder_source_sft.py
The selected physical printer coupon, route mask and target hash are never read.
The conditional p951 printer-stage geometry and native MT source origin are inherited,
not an authenticated physical printer firmware or issuance chronology.
"""
import hashlib
import json
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents' / 'agent49'))
import k04_p951_symbolic_basis as mt

END = 11000
REC_SHA = '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
EXPECTED = [(50,7,-810,32),(50,9,-793,31),(50,12,-775,32),
    (50,13,-769,32),(50,14,-759,30),(50,24,-683,32),
    (50,25,-677,32),(50,41,-568,32),(50,43,-552,30),
    (50,44,-545,32),(50,45,-540,31),(50,61,-417,30),
    (50,63,-397,31),(50,64,-390,30),(50,70,-339,32),
    (49,990,-322,32),(49,201,-321,32),(49,991,-319,30),
    (49,992,-316,32),(49,203,-315,32),(49,993,-313,31)]


def source_controls():
    raw = (ROOT / 'resources' / 'evidence' / 'recorder' / 'trip-recorder.raw').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REC_SHA
    assert len(raw) == 16 + 88 * 24 and raw[:8] == b'TRP2DUMP'
    result = []
    valid_by_node = Counter()
    for i in range(88):
        item = raw[16 + i * 24:16 + (i + 1) * 24]
        time, node, event, latch, seq, word, aux, crc = struct.unpack('<IHBBI4sII', item)
        if zlib.crc32(item[:20]) != crc:
            continue
        valid_by_node[node] += 1
        result.append((node, seq, mt.untemper(int.from_bytes(word, 'little'))))
    assert valid_by_node == {49: 12, 50: 72}
    return result


def parity_constraints(source_rows, native_word):
    """Reduce source MT equations and retain all linear constraints on a 32-bit output.

    (mask, fixed) means parity(native_output & mask) == fixed.
    This includes mixed-bit relations with no individually determined output bits.
    """
    local = {}
    constraints = []
    for j, v in enumerate(native_word):
        mask, fixed = 1 << j, 0
        while v:
            pivot = v.bit_length() - 1
            if pivot in source_rows:
                equation, b = source_rows[pivot]
                v ^= equation
                fixed ^= b
            elif pivot in local:
                equation, b, tag = local[pivot]
                v ^= equation
                fixed ^= b
                mask ^= tag
            else:
                local[pivot] = v, fixed, mask
                break
        if not v:
            assert mask
            constraints.append((mask, fixed))
    return constraints


def matched(controls, constraints, q):
    return [(node, seq, q, len(constraints)) for node, seq, value in controls
            if all(((value & mask).bit_count() & 1) == bit for mask, bit in constraints)]


def main():
    mt.LAST = END
    b, words = mt.source(ROOT / 'resources')
    assert b.rank == 15365
    controls = source_controls()
    assert len(controls) == 84
    assert parity_constraints(b.rows, mt.get(words, 951)) == []
    assert len(parity_constraints(b.rows, mt.get(words, 955))) == 32
    counts = Counter()
    hits = []
    future_hits = []
    for stage in range(mt.ORIGIN, END + 1):
        rules = parity_constraints(b.rows, mt.get(words, stage))
        count = len(rules)
        counts[count] += 1
        if count >= 9:
            found = matched(controls, rules, stage)
            hits.extend(found)
            if stage > 1040:
                future_hits.extend(found)
    assert hits == EXPECTED, (len(hits), hits)
    assert future_hits == []
    assert sum(counts.values()) == END - mt.ORIGIN + 1
    assert counts[0] == 8804 and counts[32] == 1355
    print(json.dumps({
        'independent_original_source_rank': b.rank,
        'original_valid_controls': len(controls),
        'native_stage_window': [mt.ORIGIN, END],
        'stages_with_at_least_nine_original_source_parities': sum(v for k,v in counts.items() if k >= 9),
        'record_stage_assignments': sum(v for k,v in counts.items() if k >= 9) * len(controls),
        'exact_original_correspondences': len(hits),
        'previously_known_original_correspondences': 21,
        'novel_future_correspondences': len(future_hits),
        'stage_951_source_parities': 0,
        'historical_selected_coupon_bits_authenticated': 0,
        'source_control': 'PASS',
        'recovery': 'INCOMPLETE'
    }, sort_keys=True))


if __name__ == '__main__':
    main()
