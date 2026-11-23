"""H17: genuine NumPy MT19937 default SeedSequence pool4, all42 source inversion.

python agents/agent1/k04_numpy_pool4_all42_source_sft.py
Requires NumPy and sibling K04 source projector. Selected ACK2 never decoded.
"""
import json
import time
import numpy as np
import k04_all42_cpython_n98_extended_sft as base

U = 0xFFFFFFFF
MOD = 1 << 32
INIT_B = 0x8B51F9DD
MULT_B = 0x58F38DED
SOURCE_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'

def pool_word(i, stateword):
    before = INIT_B * pow(MULT_B, i, MOD) & U
    factor = before * MULT_B & U
    raw = stateword ^ (stateword >> 16)
    return ((raw * pow(factor, -1, MOD)) & U) ^ before

def seedseq_state(pool):
    arr = [0x80000000]
    for i in range(1, 624):
        before = INIT_B * pow(MULT_B, i, MOD) & U
        factor = before * MULT_B & U
        v = (pool[i % 4] ^ before) * factor & U
        arr.append(v ^ (v >> 16))
    return arr

def native_stream(initial, length):
    words = list(initial)
    for k in range(624, length):
        a, b = words[k-624], words[k-623]
        v = (a & 0x80000000) | (b & 0x7FFFFFFF)
        words.append((words[k-227] ^ (v >> 1) ^
                      (base.MAG if v & 1 else 0)) & U)
    return words

def temper(v):
    v ^= v >> 11
    v ^= (v << 7) & 0x9D2C5680
    v ^= (v << 15) & 0xEFC60000
    v ^= v >> 18
    return v & U

def genuine_planted(offset, seed):
    mt = np.random.MT19937(np.random.SeedSequence(seed))
    initial = [int(x) for x in mt.state['state']['key']]
    assert mt.state['state']['pos'] == 623 and initial[0] == 0x80000000
    pool = [0] * 4
    for i in range(1, 5):
        pool[i % 4] = pool_word(i, initial[i])
    assert all(pool_word(i, initial[i]) == pool[i % 4] for i in range(1, 624))
    assert seedseq_state(pool) == initial
    words = native_stream(initial, 624 + offset + base.S[-1] + 4)
    packets = [
        None if r == 129 else b''.join(
            temper(words[624+offset+stage+j]).to_bytes(4, 'little')
            for j in range(4))
        for r, stage in enumerate(base.S)
    ]
    return initial, tuple(pool), packets

def infer_source(states):
    if (states[0][1] ^ 0x80000000) & states[0][0]:
        return 'bad_init0', None
    possible = {j: set() for j in range(4)}
    for i, (mask, value) in enumerate(states):
        if i and mask == U:
            possible[i % 4].add(pool_word(i, value))
            if len(possible[i % 4]) > 1:
                return 'contradiction', i
    if not all(len(v) == 1 for v in possible.values()):
        return 'insufficient', None
    pool = tuple(next(iter(possible[i])) for i in range(4))
    initialized = seedseq_state(pool)
    for i, (mask, value) in enumerate(states):
        if initialized[i] & mask != value:
            return 'mismatch', i
    return 'complete', pool

def main():
    for offset, seed in ((0, 2026), (616, 0xA17E8BC0), (93, 0xCAFEBABE)):
        initialized, pool, packets = genuine_planted(offset, seed)
        states = base.projection(offset, packets)
        assert all(initialized[i] & m == v for i, (m, v) in enumerate(states))
        assert infer_source(states) == ('complete', pool)
        print('GENUINE_NUMPY_POOL4_PASS', offset, seed, flush=True)
    original = base.source()
    results = {}
    started = time.monotonic()
    for offset in range(624):
        states = base.projection(offset, original)
        outcome, detail = infer_source(states)
        results[outcome] = results.get(outcome, 0) + 1
        if offset % 100 == 0:
            print('ORIGINAL_PROGRESS', offset, results,
                  round(time.monotonic()-started, 1), flush=True)
    assert results == {'contradiction': 499, 'bad_init0': 125}, results
    print('ORIGINAL_RESULT', json.dumps({
        'source_sha256': SOURCE_SHA,
        'offsets_tested': 624,
        'source_incompatible_offsets': 624,
        'initial_state_bit_incompatible': 125,
        'pool4_residue_incompatible': 499,
        'genuine_numpy_planted_passes': 3,
        'complete_original_pool4_models': 0,
        'selected_ACK2_payload_decoded': False,
        'original_K04_recovered': False,
    }, sort_keys=True), flush=True)

if __name__ == '__main__':
    main()
