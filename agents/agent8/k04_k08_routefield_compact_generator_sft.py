"""Source-pinned full-coupon test for a shared issuer of K04's mask and K08's nonce.

Run from repository root as a Python file; optional argument supplies an
unpacked directory containing acceptance.json and evidence/. Read-only.
The issuer is speculative. Neither selected physical copy nor final caption
enters model fitting.
"""
import hashlib
import json
import sys
from collections import deque
from pathlib import Path

U32 = (1 << 32) - 1
U64 = (1 << 64) - 1
HORIZON = 4096
ROUTE_SHA = 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
ACCEPT_SHA = '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'


def rotl(x, n):
    return ((x << n) | (x >> (32 - n))) & U32


def layouts(data, size):
    assert len(data) == 16
    for direction in (False, True):
        for endian in ('little', 'big'):
            chunks = [data[i:i + size] for i in range(0, 16, size)]
            if direction:
                chunks.reverse()
            yield ('reverse' if direction else 'forward') + '-' + endian, tuple(
                int.from_bytes(chunk, endian) for chunk in chunks)


def pack(words, layout, size):
    direction, endian = layout.split('-')
    parts = list(words)
    if direction == 'reverse':
        parts.reverse()
    return b''.join(value.to_bytes(size, endian) for value in parts)


def xorshift_step(words):
    x, y, z, w = words
    t = (x ^ (x << 11)) & U32
    return y, z, w, (w ^ (w >> 19) ^ t ^ (t >> 8)) & U32


def xoshiro_step(s, version):
    a, b, c, d = s
    v = b if version == 11 else a
    out = rotl((v * 5) & U32, 7) * 9 & U32
    t = b << 9 & U32
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    d = rotl(d, 11)
    return (a & U32, b & U32, c & U32, d), out


def undo_xoshiro_output(output):
    value = (output * pow(9, -1, 1 << 32)) & U32
    value = rotl(value, 25)
    return value * pow(5, -1, 1 << 32) & U32


def inverse_xoshiro_initial(outputs, version):
    """Invert four xoshiro128** words through an exact 128-dimensional GF(2) map."""
    cols = []
    source_lane = 1 if version == 11 else 0
    for bit in range(128):
        state = tuple((1 << (bit % 32)) if lane == bit // 32 else 0 for lane in range(4))
        combined = 0
        for i in range(4):
            combined |= state[source_lane] << (32 * i)
            state, _ = xoshiro_step(state, version)
        cols.append(combined)
    rhs = sum(undo_xoshiro_output(word) << (32 * i) for i, word in enumerate(outputs))
    reduced = {}
    mask = (1 << 128) - 1
    for bit in range(128):
        line = sum(((cols[j] >> bit) & 1) << j for j in range(128))
        line |= ((rhs >> bit) & 1) << 128
        while line:
            low = line & mask
            assert low, 'xoshiro observed packet inconsistent'
            pivot = low.bit_length() - 1
            if pivot not in reduced:
                reduced[pivot] = line
                break
            line ^= reduced[pivot]
    assert len(reduced) == 128
    solved = 0
    for pivot, line in sorted(reduced.items()):
        if ((line >> 128) ^ ((line & solved).bit_count() & 1)) & 1:
            solved |= 1 << pivot
    state = tuple((solved >> (32 * j)) & U32 for j in range(4))
    replay = []
    cur = state
    for _ in range(4):
        cur, output = xoshiro_step(cur, version)
        replay.append(output)
    assert tuple(replay) == tuple(outputs)
    return cur


def undo_right(y, amount):
    value = y
    for _ in range(1 + 64 // amount):
        value = y ^ (value >> amount)
    return value & U64


def mix64(value, family):
    if family == 'stafford':
        value = (value ^ (value >> 30)) * 0xBF58476D1CE4E5B9 & U64
        value = (value ^ (value >> 27)) * 0x94D049BB133111EB & U64
        return value ^ (value >> 31)
    value = (value ^ (value >> 33)) * 0xFF51AFD7ED558CCD & U64
    value = (value ^ (value >> 33)) * 0xC4CEB9FE1A85EC53 & U64
    return value ^ (value >> 33)


def unmix64(value, family):
    if family == 'stafford':
        value = undo_right(value, 31)
        value = value * pow(0x94D049BB133111EB, -1, 1 << 64) & U64
        value = undo_right(value, 27)
        value = value * pow(0xBF58476D1CE4E5B9, -1, 1 << 64) & U64
        return undo_right(value, 30)
    value = undo_right(value, 33)
    value = value * pow(0xC4CEB9FE1A85EC53, -1, 1 << 64) & U64
    value = undo_right(value, 33)
    value = value * pow(0xFF51AFD7ED558CCD, -1, 1 << 64) & U64
    return undo_right(value, 33)


def future(observed, engine):
    if engine == 'xorshift128':
        state = tuple(observed)
        while True:
            state = xorshift_step(state)
            yield state[-1]
    elif engine.startswith('xoshiro'):
        version = int(engine[-2:])
        state = inverse_xoshiro_initial(observed, version)
        while True:
            state, value = xoshiro_step(state, version)
            yield value
    else:
        family = engine.split('-')[1]
        first, second = (unmix64(v, family) for v in observed)
        step = (second - first) & U64
        value = second
        while True:
            value = (value + step) & U64
            yield mix64(value, family)


def controls(mask):
    sample = (0x11223344, 0x99AABBCC, 0x76543210, 0xA5D0C3E7)
    original = sample
    for _ in range(61):
        original = xorshift_step(original)
    f = future(sample, 'xorshift128')
    assert tuple(deque((next(f) for _ in range(61)), maxlen=4)) == original
    for version in (10, 11):
        state = sample
        words = []
        for _ in range(83):
            state, value = xoshiro_step(state, version)
            words.append(value)
        f = future(tuple(words[:4]), f'xoshiro{version}')
        assert [next(f) for _ in range(79)] == words[4:]
    for family in ('stafford', 'murmur'):
        first, step = 0xDEF0ACE710203040, 0x9E3779B97F4A7C15
        outputs = [mix64((first + step * i) & U64, family) for i in range(37)]
        assert all(unmix64(v, family) == ((first + i * step) & U64) for i, v in enumerate(outputs))
        f = future(tuple(outputs[:2]), f'splitmix-{family}')
        assert [next(f) for _ in range(35)] == outputs[2:]
    for size in (4, 8):
        for layout, words in layouts(bytes(range(16)), size):
            assert pack(words, layout, size) == bytes(range(16))
    seed_packet = pack(sample, 'reverse-big', 4)
    seed_words = next(words for layout, words in layouts(seed_packet, 4) if layout == 'reverse-big')
    generator = future(seed_words, 'xorshift128')
    planted = [next(generator) for _ in range(29)]
    full = pack(tuple(planted[-4:]), 'forward-little', 4)
    planted_k04 = hashlib.sha256(bytes(a ^ b for a, b in zip(full, mask))).digest()
    planted_k08 = hashlib.sha256(full).digest()
    reconstructed = deque(maxlen=4)
    generator_again = future(seed_words, 'xorshift128')
    for _ in range(29):
        reconstructed.append(next(generator_again))
    recovered = pack(tuple(reconstructed), 'forward-little', 4)
    assert hashlib.sha256(bytes(a ^ b for a, b in zip(recovered, mask))).digest() == planted_k04
    assert hashlib.sha256(recovered).digest() == planted_k08
    print('SYNTHETIC_FIVE_GENERATORS_LAYOUTS_AND_BOTH_FULL_TARGET_CONTROLS_PASS')


def main(root):
    route_raw = (root / 'evidence/recovery-routing.json').read_bytes()
    accept_raw = (root / 'acceptance.json').read_bytes()
    spool_raw = (root / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(route_raw).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(accept_raw).hexdigest() == ACCEPT_SHA
    assert hashlib.sha256(spool_raw).hexdigest() == SPOOL_SHA
    assert b'2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in spool_raw
    route = json.loads(route_raw)
    accept = json.loads(accept_raw)
    blocks = {
        'route-mask': bytes.fromhex(route['K04']['masked_component']),
        'desk-nonce': bytes.fromhex(route['K08']['desk_nonce']),
    }
    k04mask = blocks['route-mask']
    targets = {slot: bytes.fromhex(accept['slot_sha256'][slot]) for slot in ('K04', 'K08')}
    assert all(len(v) == 16 for v in blocks.values())
    controls(k04mask)
    engines = ('xorshift128', 'xoshiro10', 'xoshiro11', 'splitmix-stafford', 'splitmix-murmur')
    statistics = {}
    for engine in engines:
        size = 8 if engine.startswith('splitmix') else 4
        nwords = 16 // size
        reversed_targets = {name: {words for _, words in layouts(block, size)}
                            for name, block in blocks.items()}
        result = {'source_cross_matches': [], 'K04_matches': [], 'K08_matches': [], 'complete_blocks': 0}
        for origin, original in blocks.items():
            for input_layout, observed in layouts(original, size):
                process = future(observed, engine)
                window = deque(maxlen=nwords)
                for offset in range(HORIZON + nwords - 1):
                    window.append(next(process))
                    if len(window) < nwords:
                        continue
                    w = tuple(window)
                    if w in reversed_targets['desk-nonce' if origin == 'route-mask' else 'route-mask']:
                        result['source_cross_matches'].append((origin, input_layout, offset-nwords+1))
                    for output_layout, _ in layouts(bytes(16), size):
                        predicted = pack(w, output_layout, size)
                        routed = bytes(a ^ b for a, b in zip(predicted, k04mask))
                        if hashlib.sha256(routed).digest() == targets['K04']:
                            result['K04_matches'].append((origin, input_layout, output_layout, offset-nwords+1, routed.hex().upper()))
                        if hashlib.sha256(predicted).digest() == targets['K08']:
                            result['K08_matches'].append((origin, input_layout, output_layout, offset-nwords+1, predicted.hex().upper()))
                        result['complete_blocks'] += 1
        assert result['complete_blocks'] == 2 * 4 * HORIZON * 4
        statistics[engine] = result
        print('ENGINE', engine, 'candidate_blocks', result['complete_blocks'],
              'source_cross_matches', result['source_cross_matches'],
              'K04_matches', result['K04_matches'], 'K08_matches', result['K08_matches'])
    assert sum(x['complete_blocks'] for x in statistics.values()) == 655360
    print(json.dumps({'models': list(statistics), 'full_blocks': 655360,
                      'source_matches': sum(len(v['source_cross_matches']) for v in statistics.values()),
                      'K04_target_hits': sum(len(v['K04_matches']) for v in statistics.values()),
                      'K08_component_target_hits': sum(len(v['K08_matches']) for v in statistics.values()),
                      'interpretation': 'speculative compact-state shared issuer; selected paper and author final unsupplied'}, sort_keys=True))


if __name__ == '__main__':
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'resources'
    main(base)
