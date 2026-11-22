"""Source-pinned H17 K04 MT fullword witness-template lane-mosaic coupon test.

Selected row129 is omitted before PAYLOAD parsing, and original commitments are
unchanged. Every lane receives only source-observed historical witness templates.
"""
import hashlib
import itertools
import json
import re
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / 'resources/evidence/print/spool-reconstruction.log'
ROUTE = ROOT / 'resources/evidence/recovery-routing.json'
ACCEPTANCE = ROOT / 'resources/acceptance.json'
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
ROUTE_SHA = 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
ACCEPT_SHA = '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
TARGET = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
M = (1 << 32) - 1


def undo_right(x, shift):
    y = x
    for _ in range(5):
        y = x ^ (y >> shift)
    return y & M


def undo_left(x, shift, mask):
    y = x
    for _ in range(5):
        y = x ^ ((y << shift) & mask)
    return y & M


def temper(x):
    y = x ^ (x >> 11)
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    return (y ^ (y >> 18)) & M


def untemper(x):
    y = undo_right(x, 18)
    y = undo_left(y, 15, 0xEFC60000)
    y = undo_left(y, 7, 0x9D2C5680)
    return undo_right(y, 11)


def mt_twist_pair(before, now):
    joint = (before & 0x80000000) | (now & 0x7FFFFFFF)
    return (joint >> 1) ^ (0x9908B0DF if now & 1 else 0)


def stage_offsets_right_lane(p, i, q):
    """Offsets when p is the right input lane in twist_pair(x[p-1], x[p])."""
    assert p in (1, 2, 3)
    return 396 + p - i, 623 + p - q


def stage_offsets_left_lane(p0, i, q):
    """Equivalent offsets when p0 is the left input lane (p0 = p - 1)."""
    assert p0 in (0, 1, 2)
    return 397 + p0 - i, 624 + p0 - q


def verify_stage_index_fixture():
    """Seeded MT fixture guards the right/left lane convention against +1 drift."""
    rng = random.Random(0x17A11CE)
    stream = [untemper(rng.getrandbits(32)) for _ in range(1300)]
    for p in (1, 2, 3):
        p0 = p - 1
        i = q = p0
        t = p0
        assert stream[t + 397] == stream[397 + i]
        assert stream[t + 624] == (
            stream[t + 397] ^ mt_twist_pair(stream[t], stream[t + 1])
        )
        right = stage_offsets_right_lane(p, i, q)
        left = stage_offsets_left_lane(p0, i, q)
        assert right == left == (397, 624)
        # Treating the right lane as if it were the left lane is the old +1 bug.
        assert (397 + p - i, 624 + p - q) == (398, 625)


def source_packets():
    assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(ROUTE.read_bytes()).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(ACCEPTANCE.read_bytes()).hexdigest() == ACCEPT_SHA
    assert bytes.fromhex(json.loads(ROUTE.read_text())['K04']['masked_component']) == MASK
    assert json.loads(ACCEPTANCE.read_text())['slot_sha256']['K04'] == TARGET
    rows = [s for s in SPOOL.read_text().splitlines() if s and not s.startswith('#')]
    assert len(rows) == 133
    assert all(s in rows[129] for s in (
        'JOB=PS-261003-0417', 'ATTEMPT=2', 'STATE=ACK', 'CLASS=RECOVER'))
    native = []
    for idx, row in enumerate(rows):
        if idx == 129:
            native.append(None)
            continue
        part = re.search(r'\bPAYLOAD=([0-9A-F]{32})\b', row)
        assert part, idx
        blob = bytes.fromhex(part.group(1))
        native.append(tuple(untemper(int.from_bytes(blob[k:k + 4], 'little')) for k in (0, 4, 8, 12)))
    return native


def witnesses(native):
    by_word = {}
    for r, words in enumerate(native):
        if words is None:
            continue
        for lane, word in enumerate(words):
            by_word.setdefault(word, []).append((r, lane))
    out = []
    for r, words in enumerate(native):
        if words is None:
            continue
        for p in (1, 2, 3):
            patch = mt_twist_pair(words[p - 1], words[p])
            for k in range(r + 1, len(native)):
                if native[k] is None:
                    continue
                for i in range(4):
                    projected = patch ^ native[k][i]
                    for l, q in by_word.get(projected, ()):
                        if l > k:
                            out.append((r, p, k, i, l, q))
    return sorted(out)


def lane_candidates(native, templates, dest):
    candidates = [set() for _ in range(4)]
    for dk, dl, p, i, q in templates:
        r = dest - dl
        k = r + dk
        if r < 0 or k <= r or k >= dest or native[r] is None or native[k] is None:
            continue
        candidates[q].add(native[k][i] ^ mt_twist_pair(native[r][p - 1], native[r][p]))
    return candidates


def candidate_coupon(native_words):
    return b''.join(temper(w).to_bytes(4, 'little') for w in native_words)


def main():
    verify_stage_index_fixture()
    native = source_packets()
    observed = witnesses(native)
    assert len(observed) == 25, len(observed)
    assert all(
        stage_offsets_right_lane(p, i, q) == stage_offsets_left_lane(p - 1, i, q)
        for r, p, k, i, l, q in observed
    )
    print('seeded MT stage-index fixture=PASS; all 25 source tuples use equivalent right/left lane offsets')
    signatures = sorted({(k-r, l-r, p, i, q) for r, p, k, i, l, q in observed})
    assert Counter(l-r for r, p, k, i, l, q in observed) == Counter({83: 6, 84: 17, 87: 2})
    assert {((k-r), (l-r)) for r, p, k, i, l, q in observed} == {(52,83),(53,83),(53,84),(54,84),(53,87)}
    selected = lane_candidates(native, signatures, 129)
    sizes = tuple(map(len, selected))
    assert sizes == (4, 5, 6, 8), sizes
    # Target-blind syntax in raw payload lane order; mixed witnesses may use
    # different native source rows for each of the four target lanes.
    positives = []
    for words in itertools.product(*(sorted(v) for v in selected)):
        coupon = candidate_coupon(words)
        component = bytes(a ^ b for a,b in zip(coupon,MASK))
        if hashlib.sha256(component).hexdigest() == TARGET:
            positives.append((coupon.hex().upper(),component.hex().upper()))
    checked = 1
    for x in sizes: checked *= x
    assert checked == 960
    print(f'original witnesses={len(observed)} distinct_templates={len(signatures)} raw_row_offset_pairs={sorted({(k-r,l-r) for r,p,k,i,l,q in observed})}')
    print(f'original selected row129 lane choices={sizes} complete coupon candidates={checked} K04_SHA256_matches={len(positives)}')
    for coupon,component in positives:
        print('ORIGINAL_MATCH',coupon,component)

    # Strict source-blind intact holdouts: remove *every* witness containing
    # the held-out row before selecting source-level templates for that row.
    intact_tested = 0
    all_lanes_present = 0
    full_words = 0
    full_packets = 0
    for h in range(133):
        if h == 129: continue
        train = {(k-r,l-r,p,i,q) for r,p,k,i,l,q in observed if h not in (r,k,l)}
        guess = lane_candidates(native, train, h)
        # h is never accessed as a source row because r<k<h above.
        if not any(guess): continue
        intact_tested += 1
        full_words += sum(native[h][q] in guess[q] for q in range(4))
        if all(guess):
            all_lanes_present += 1
            if all(native[h][q] in guess[q] for q in range(4)):
                full_packets += 1
    print(f'source-blind intact holdouts attempted={intact_tested} with all four lanes covered={all_lanes_present} matched native words={full_words} entire packets={full_packets}')

    # A separate planted physical coupon is built by this exact producer:
    # each target lane uses one different historical source-derived template,
    # with its other source packets frozen. The synthetic target is inserted
    # only after every lane is computed; derive using the identical constructor.
    pick = [next((t for t in signatures if t[-1] == q and (129-t[1]) > 0), None) for q in range(4)]
    assert all(pick)
    planted = tuple(next(iter(lane_candidates(native, [t], 129)[q])) for q,t in enumerate(pick))
    regenerated = [lane_candidates(native, [t],129)[q] for q,t in enumerate(pick)]
    assert all(planted[q] in regenerated[q] for q in range(4))
    planted_coupon = candidate_coupon(planted)
    planted_digest = hashlib.sha256(bytes(a ^ b for a,b in zip(planted_coupon,MASK))).digest()
    assert any(hashlib.sha256(bytes(a^b for a,b in zip(candidate_coupon(words), MASK))).digest() == planted_digest
               for words in itertools.product(*(sorted(v) for v in selected)))
    assert hashlib.sha256(bytes(a^b for a,b in zip(planted_coupon[:-1]+bytes([planted_coupon[-1]^1]), MASK))).digest() != planted_digest
    print('synthetic full selected coupon and 256-bit commitment positive: PASS')
    assert not positives

if __name__ == '__main__':
    main()