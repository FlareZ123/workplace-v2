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
print('K04_SELECTED_COUPON_AUTHENTICATED_BITS 0/128')
