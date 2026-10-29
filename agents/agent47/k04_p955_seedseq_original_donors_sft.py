"""Read-only conditional original MT19937 seed_seq donor projection, K04 withheld.

Run as a single test file at agents/agent47/ in workplace-v2. Uses exact
original spool and source-consistent p955 alignment. A matching donor value
is conditional source algebra, not an authenticated printer producer or K04 key.
The r132 exclusion is retrospective because the original p955 geometry was itself
chosen using r132 among recurrence witnesses; this is NOT a blind source control.
"""
import hashlib
import re
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
N = 624
A = 0x9908B0DF
raw = (ROOT / 'resources/evidence/print/spool-reconstruction.log').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
rows = []
for line in raw.decode().splitlines():
    if not line.startswith('2026-'):
        continue
    match = re.search(r'PAYLOAD=([0-9A-F]{32})', line)
    assert match
    payload = bytes.fromhex(match.group(1))
    rows.append([int.from_bytes(payload[i:i + 4], 'little') for i in range(0, 16, 4)])
assert len(rows) == 133

# Frozen original-source-compatible chronology, selected index row129=955.
starts = [
    0,7,15,22,30,38,44,51,67,76,84,92,99,112,120,126,132,138,144,151,
    158,165,171,179,186,192,198,205,211,218,224,230,237,243,250,260,
    268,278,285,298,305,311,318,328,339,346,352,358,364,370,376,382,
    388,394,401,407,416,423,429,436,442,456,463,474,481,489,495,507,
    515,522,530,536,543,549,563,569,576,584,590,597,604,610,617,624,
    632,638,644,650,659,665,671,679,689,697,705,714,721,733,740,747,
    753,759,766,772,783,789,796,807,813,820,826,833,839,846,853,861,
    870,876,882,888,896,906,916,922,928,934,940,946,951,955,959,963,967,
]
assert len(starts) == 133 and starts[129] == 955

# Linearized initialized 624-word register. Tempered X[k] is after its first twist.
state = [[1 << (i * 32 + b) for b in range(32)] for i in range(N)]
for k in range(max(starts) + 4):
    left, right, far = state[k], state[k + 1], state[k + 397]
    low = right[0]
    state.append([
        far[b]
        ^ (right[b + 1] if b < 30 else (left[31] if b == 30 else 0))
        ^ (low if (A >> b) & 1 else 0)
        for b in range(32)
    ])

def shift_right(v, n):
    return [v[i + n] if i + n < 32 else 0 for i in range(32)]

def shift_left_mask(v, n, mask):
    return [v[i - n] if i >= n and ((mask >> i) & 1) else 0 for i in range(32)]

def xorv(x, y):
    return [a ^ b for a, b in zip(x, y)]

def temper(v):
    x = xorv(v, shift_right(v, 11))
    x = xorv(x, shift_left_mask(x, 7, 0x9D2C5680))
    x = xorv(x, shift_left_mask(x, 15, 0xEFC60000))
    return xorv(x, shift_right(x, 18))

expr = {
    i: temper(state[624 + i])
    for i in {starts[r] + w for r in range(133) if r != 129 for w in range(4)}
}

def basis_from(exclude, row_values=rows):
    piv = {}
    contradictions = 0
    for r in range(133):
        if r in exclude:
            continue
        for w in range(4):
            bits, value = expr[starts[r] + w], row_values[r][w]
            for b, coeff in enumerate(bits):
                y = (value >> b) & 1
                while coeff:
                    p = coeff.bit_length() - 1
                    if p in piv:
                        coeff ^= piv[p][0]
                        y ^= piv[p][1]
                    else:
                        piv[p] = (coeff, y)
                        break
                else:
                    if y:
                        contradictions += 1
    return piv, contradictions

def source_value(piv, i, b):
    coeff, y = 1 << (i * 32 + b), 0
    while coeff:
        p = coeff.bit_length() - 1
        if p not in piv:
            return None
        coeff ^= piv[p][0]
        y ^= piv[p][1]
    return y

def required_indexes(s):
    """Existing source-independent sufficient dependency closure, 1..4 seed words."""
    P, Q = 306, 317
    a = [1 << i for i in range(N)]
    for k in range(2 * N - 1, N - 1, -1):
        j, r4 = k % N, a[k % N]
        a[(j + P) % N] |= r4
        a[(j + Q) % N] |= r4
        a[j] = r4 | a[(j + P) % N] | a[(j - 1) % N]
    deps = 0
    for k in range(N - 1, -1, -1):
        j, r2 = k % N, a[k % N]
        r1 = r2 if k > s else a[(j + P) % N]
        if 0 < k <= s:
            deps |= r2 | r1
        a[(j + P) % N] |= r1
        a[(j + Q) % N] |= r2
        a[j] = r1 | a[(j + P) % N] | a[(j - 1) % N]
    return [i for i in range(N) if (deps >> i) & 1]

for name, exclude in [('all_intact', {129}), ('r132_excluded_geometry_preselected', {129, 132})]:
    t = perf_counter()
    piv, bad = basis_from(exclude)
    print(name, 'rank', len(piv), 'contradictions', bad,
          'seconds', round(perf_counter() - t, 3), flush=True)
    assert bad == 0
    assert len(piv) == (15305 if name == 'all_intact' else 15240)
    for s in range(1, 5):
        requested = required_indexes(s)
        full, part_count, partials = {}, 0, []
        for i in requested:
            bits = [source_value(piv, i, b) for b in range(32)]
            part_count += sum(v is not None for v in bits)
            fixed_mask = sum(1 << b for b, v in enumerate(bits) if v is not None)
            fixed_value = sum(v << b for b, v in enumerate(bits) if v is not None)
            if name == 'r132_excluded_geometry_preselected' and s == 1 and fixed_mask:
                partials.append((i, fixed_mask, fixed_value))
            if fixed_mask == 0xFFFFFFFF:
                full[i] = fixed_value
        print(' seedwords', s, 'required', len(requested),
              'fully_known', len(full), 'fixed_bits', part_count,
              'donors', ','.join(f'{i}:{v:08X}' for i, v in full.items()),
              flush=True)
        if partials:
            print(' HELDOUT_ONEWORD_PARTIAL_FIXED_MASKS',
                  ','.join(f'{i}:{mask:08X}:{value:08X}'
                           for i, mask, value in partials), flush=True)

def run_synthetic(seed):
    """Independent seeded MT replay checks every fixed inferred bit."""
    import random
    mt = list(random.Random(seed).getstate()[1][:N])
    src = mt.copy()
    for k in range(max(starts) + 4):
        y = (src[k] & 0x80000000) | (src[k + 1] & 0x7FFFFFFF)
        src.append((src[k + 397] ^ (y >> 1) ^ (A if y & 1 else 0)) & 0xFFFFFFFF)
    def tempered_word(v):
        v ^= v >> 11
        v ^= (v << 7) & 0x9D2C5680
        v ^= (v << 15) & 0xEFC60000
        return (v ^ (v >> 18)) & 0xFFFFFFFF
    simulated = [
        [tempered_word(src[624 + starts[r] + w]) for w in range(4)]
        for r in range(133)
    ]
    piv, bad = basis_from({129, 132}, simulated)
    assert bad == 0 and len(piv) == 15240
    observed = 0
    for s in range(1, 5):
        for index in required_indexes(s):
            for bit in range(32):
                val = source_value(piv, index, bit)
                if val is not None:
                    observed += 1
                    assert val == ((mt[index] >> bit) & 1), (seed, s, index, bit)
    print('SYNTHETIC_SEED_CONTROL_PASS', seed, 'bits', observed, flush=True)

for demo_seed in (0, 8131, 20261029):
    run_synthetic(demo_seed)
print('H17_K04_AUTHENTICATED_SELECTED_BITS 0/128')
