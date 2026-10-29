"""CPython init_by_array key-length necessary-condition sieve, original K04 withheld.

The original 128 ordinary print rows alone constrain 190 full initialized
MT-state words only under a *previously published, historically unverified*
p955 common-stream alignment. Consecutive triples of those words yield
key[j]+j terms. Reused residues must be equal for a CPython key array length
n <=624 (the first 624 mixing iterations cover each index once).

This script never reads the disputed selected coupon, route mask, original
slot commitments, nonce, verifier, or the keeper phrase.
"""
from pathlib import Path
import random
import runpy

SOURCE = runpy.run_path(str(Path(__file__).with_name('k04_p955_seedseq_original_donors_sft.py')))
N = 624
MASK = 0xFFFFFFFF

# Reference implementation: CPython Modules/_randommodule.c, init_genrand.
initial = [19650218]
for i in range(1, N):
    w = initial[-1]
    initial.append((1812433253 * (w ^ (w >> 30)) + i) & MASK)


def terms(known):
    """Recover key[j]+j from each three-word initialized-state run.

    Only use index >=4 to avoid the wrapped index-1 double update.
    """
    recovered = []
    for i in range(4, N):
        if not all(j in known for j in (i-2, i-1, i)):
            continue

        def undo_second(j):
            a, preceding = known[j], known[j-1]
            delta = ((preceding ^ (preceding >> 30)) * 1566083941) & MASK
            return ((a + j) & MASK) ^ delta

        earlier = undo_second(i-1)
        later = undo_second(i)
        delta = ((earlier ^ (earlier >> 30)) * 1664525) & MASK
        key_plus_index = (later - (initial[i] ^ delta)) & MASK
        recovered.append((i-1, key_plus_index))
    return recovered


def conflict(witnesses, key_length):
    seen = {}
    for j, term in witnesses:
        residue = j % key_length
        if residue in seen and seen[residue][1] != term:
            return seen[residue], (j, term)
        seen[residue] = (j, term)
    return None


# Independent controls for short and long numeric seed arrays.
for size in (1,2,3,4,5,13,20,31,80,145,256,623):
    numeric_seed = sum((j+1) << (32*j) for j in range(size))
    initialized = dict(enumerate(random.Random(numeric_seed).getstate()[1][:N]))
    term_list = terms(initialized)
    assert len(term_list) == 620
    assert all(((term - j % size) & MASK) == (j % size)+1 for j,term in term_list), size
    assert conflict(term_list, size) is None
print('SYNTHETIC_CPYTHON_KEY_ARRAY_CONTROLS_PASS', 12)

# Omit the selected row and all late exceptional records.
piv, contradictions = SOURCE['basis_from']({128,129,130,131,132})
assert contradictions == 0 and len(piv) == 15014
known = {}
for index in range(N):
    bits = [SOURCE['source_value'](piv, index, b) for b in range(32)]
    if all(x is not None for x in bits):
        known[index] = sum(bit << b for b, bit in enumerate(bits))
assert len(known) == 190
witnesses = terms(known)
assert len(witnesses) == 42

rejected = [n for n in range(1, 624) if conflict(witnesses, n)]
allowed = [n for n in range(1, 624) if not conflict(witnesses, n)]
assert len(rejected) == 395 and len(allowed) == 228
assert rejected[:144] == list(range(1,145)) and allowed[0] == 145
print('ORIGINAL_ORDINARY_ONLY_REGISTER_FULL_WORDS', len(known))
print('ORIGINAL_ORDINARY_ONLY_KEY_RESIDUE_TERMS', len(witnesses))
print('CONDITIONAL_CPYTHON_SEED_ARRAY_LENGTHS_EXCLUDED', len(rejected), 'out_of', 623)
print('ALL_INPUT_ARRAY_LENGTHS_1_THROUGH_144_CONTRADICTED')
for n in (1,5,13,32,64,128,144,145,166,226,256,623):
    pair = conflict(witnesses,n)
    print('length',n,'CONTRADICTION' if pair else 'NOT_EXCLUDED',
          (f'{pair[0][0]}:{pair[0][1]:08X} != {pair[1][0]}:{pair[1][1]:08X}' if pair else ''))

# Extend to initialized-state words with at most one unresolved bit.
# Each missing bit is enumerated independently. This overapproximates
# possible original states, making the resulting contradictions sound.
parts = {}
for index in range(N):
    bits = [SOURCE['source_value'](piv, index, b) for b in range(32)]
    fixed_mask = sum(1 << b for b, v in enumerate(bits) if v is not None)
    fixed_value = sum(v << b for b, v in enumerate(bits) if v is not None)
    parts[index] = (fixed_mask, fixed_value)


def word_options(mask, value):
    if mask.bit_count() < 31:
        return ()
    if mask == MASK:
        return (value,)
    missing = MASK ^ mask
    assert missing.bit_count() == 1
    return (value, value | missing)


def triple_term(index, a, b, c):
    def undo_second(j, later, earlier):
        delta = ((earlier ^ (earlier >> 30)) * 1566083941) & MASK
        return ((later + j) & MASK) ^ delta

    prior = undo_second(index-1, b, a)
    latest = undo_second(index, c, b)
    delta = ((prior ^ (prior >> 30)) * 1664525) & MASK
    return (latest - (initial[index] ^ delta)) & MASK


partial_terms = []
for index in range(4, N):
    values = [word_options(*parts[j]) for j in (index-2, index-1, index)]
    if not all(values):
        continue
    possibilities = {triple_term(index, a, b, c) for a in values[0]
                     for b in values[1] for c in values[2]}
    partial_terms.append((index-1, possibilities))
assert len(partial_terms) == 75
assert sum(len(x) == 1 for _, x in partial_terms) == 42


def partial_conflict(key_length, candidates=partial_terms):
    seen = {}
    for j, choices in candidates:
        residue = j % key_length
        if residue in seen:
            previous_j, previous_values = seen[residue]
            surviving = previous_values & choices
            if not surviving:
                return (previous_j, previous_values), (j, choices)
            seen[residue] = (previous_j, surviving)
        else:
            seen[residue] = (j, choices)
    return None


# Positive controls use independent real CPython states with the original
# partial-source mask positions applied to each synthetic state.
for size in (1,2,4,13,20,80,145,256,623):
    numeric_seed = sum((j+1) << (32*j) for j in range(size))
    state = random.Random(numeric_seed).getstate()[1][:N]
    candidate_terms = []
    for j, original_set in partial_terms:
        index = j+1
        values = [word_options(parts[k][0], state[k] & parts[k][0])
                  for k in (index-2, index-1, index)]
        actual = triple_term(index, *state[index-2:index+1])
        possibilities = {triple_term(index,a,b,c) for a in values[0]
                         for b in values[1] for c in values[2]}
        assert actual in possibilities
        assert ((actual - (j % size)) & MASK) == (j % size)+1
        candidate_terms.append((j, possibilities))
    assert len(candidate_terms) == 75
    assert partial_conflict(size, candidate_terms) is None
print('SYNTHETIC_PARTIAL_MASK_CPYTHON_CONTROLS_PASS', 9)

excluded_partial = [n for n in range(1,624) if partial_conflict(n)]
remaining_partial = [n for n in range(1,624) if not partial_conflict(n)]
assert len(excluded_partial) == 554 and len(remaining_partial) == 69
assert excluded_partial[:378] == list(range(1,379))
assert remaining_partial[0] == 379
assert set(rejected).issubset(excluded_partial)
print('ORIGINAL_ORDINARY_ONLY_PARTIAL_31BIT_KEY_TERMS', len(partial_terms))
print('PARTIAL_TERM_CHOICE_COUNTS', {size:sum(len(v)==size for _,v in partial_terms)
                                    for size in (1,2,4)})
print('CONDITIONAL_PARTIAL_SIEVE_EXCLUDED', len(excluded_partial), 'of', 623)
print('EVERY_CPYTHON_KEY_ARRAY_LENGTH_1_THROUGH_378_CONTRADICTED')
for n in (145,256,378,379,400,623):
    print('PARTIAL_LENGTH', n,
          'CONTRADICTION' if partial_conflict(n) else 'NOT_EXCLUDED')
# CHRONOLOGY SENSITIVITY: a second v1 Agent5 source-compatible p955
# vector, distinct from Agent11's printer-only p955 vector. Both models were
# preselected using late records, so this is not an independent event witness.
alt_starts = [
    0,7,14,22,30,46,52,58,68,76,84,92,99,112,120,126,132,138,
    144,150,156,162,168,174,180,189,199,205,211,218,224,230,237,243,
    250,256,262,272,288,298,305,311,318,328,339,346,352,358,364,370,
    376,382,388,394,401,407,416,423,430,437,451,458,464,474,481,489,
    495,507,515,522,530,542,548,554,560,566,572,579,585,591,604,610,
    617,624,632,638,644,650,658,664,673,682,690,697,705,714,721,733,
    740,747,753,759,765,771,777,786,793,802,808,816,822,833,839,846,
    853,861,870,881,891,897,903,909,916,922,928,934,940,946,951,955,
    959,963,967
]
assert len(alt_starts) == 133 and alt_starts[129] == 955
# runpy returns a namespace snapshot. Update the function-global namespace.
internal = SOURCE['basis_from'].__globals__
internal['starts'] = alt_starts
internal['expr'] = {
    i: SOURCE['temper'](SOURCE['state'][N+i])
    for i in {alt_starts[r]+w for r in range(133) if r!=129 for w in range(4)}
}
alt_piv, alt_bad = SOURCE['basis_from']({128,129,130,131,132})
assert alt_bad == 0 and len(alt_piv) == 15078
alt_parts = {}
for index in range(N):
    bits = [SOURCE['source_value'](alt_piv, index, b) for b in range(32)]
    m = sum(1<<b for b,v in enumerate(bits) if v is not None)
    v = sum(bit<<b for b,bit in enumerate(bits) if bit is not None)
    alt_parts[index] = (m,v)
assert sum(m == MASK for m,v in alt_parts.values()) == 207
alt_terms = []
for index in range(4,N):
    vals = [word_options(*alt_parts[j]) for j in (index-2,index-1,index)]
    if not all(vals):
        continue
    possibilities = {triple_term(index,a,b,c) for a in vals[0]
                     for b in vals[1] for c in vals[2]}
    alt_terms.append((index-1,possibilities))
assert len(alt_terms) == 90
alt_excluded = {n for n in range(1,624) if partial_conflict(n,alt_terms)}
shared_excluded = alt_excluded & set(excluded_partial)
assert len(alt_excluded) == 561 and len(shared_excluded) == 525
assert all(n in shared_excluded for n in range(1,350))
assert 350 not in shared_excluded
print('ALTERNATE_V1_AGENT5_P955_ORDINARY_FULL_REGISTERS',207,'partial_terms',90)
print('ALTERNATE_P955_EXCLUDED',len(alt_excluded),'of',623)
print('TWO_PRESELECTED_GEOMETRIES_SHARED_EXCLUSIONS',len(shared_excluded),'of',623)
print('TWO_PRESELECTED_GEOMETRIES_SHARED_EXCLUDED_PREFIX_1_THROUGH_349')
print('K04_SELECTED_COUPON_AUTHENTICATED_BITS 0/128')
