"""H-17 p951: CPython integer-seed key-residue inversion and MT-source falsifier.

Reads only the intact original printer payloads (selected ACK2 is withheld).
Does not access REC8 digests, routing mask, or K08. Conditionally excludes
standard CPython first-cycle seed-array lengths, not historical generators.

Usage: python agents/agent45/k04_p951_seed_residue_inverse_sft.py resources
"""
import hashlib
import random
import re
import sys
from pathlib import Path

MASK = 0xffffffff
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
BASE = [19650218]
for i in range(1, 624):
    x = BASE[-1]
    BASE.append((1812433253 * (x ^ (x >> 30)) + i) & MASK)
INV156 = pow(1566083941, -1, 1 << 32)
INV166 = pow(1664525, -1, 1 << 32)


def untemper(x):
    for shift, left, mask in ((18, False, MASK), (15, True, 0xefc60000),
                              (7, True, 0x9d2c5680), (11, False, MASK)):
        y = x
        for _ in range(6):
            y = x ^ (((y << shift) & mask) if left else (y >> shift))
        x = y & MASK
    return x


def twist(x):
    return ((x >> 1) ^ (0x9908b0df if x & 1 else 0)) & MASK


def inverse_twist(x):
    return (((x ^ (0x9908b0df if x >> 31 else 0)) << 1) | (x >> 31)) & MASK


def close(payloads, extra=()):
    """Run exact masked recurrence with selected original packet withheld."""
    offset, size = 2000, 6000
    values, masks = [0] * size, [0] * size

    def add(index, value, mask):
        if not 0 <= index < size:
            return 0
        if ((values[index] ^ value) & masks[index] & mask):
            raise ValueError(f'contradictory native state at {index - offset}')
        fresh = mask & ~masks[index]
        values[index] = (values[index] & ~fresh) | (value & fresh)
        masks[index] |= fresh
        return fresh.bit_count()

    for row, (payload, start) in enumerate(zip(payloads, STARTS)):
        if row == 129:
            continue
        for lane in range(4):
            word = int.from_bytes(payload[lane*4:lane*4+4], 'little')
            add(offset + start + lane, untemper(word), MASK)
    for i, value, mask in extra:
        add(offset - 624 + i, value, mask)
    for _ in range(30):
        gained = 0
        for t in range(size - 624):
            pair_mask = (masks[t] & 0x80000000) | (masks[t+1] & 0x7fffffff)
            pair_value = (values[t] & 0x80000000) | (values[t+1] & 0x7fffffff)
            if masks[t+397] == masks[t+624] == MASK:
                inverse = inverse_twist(values[t+397] ^ values[t+624])
                gained += add(t, inverse, 0x80000000)
                gained += add(t+1, inverse, 0x7fffffff)
            if pair_mask == MASK:
                if masks[t+397] == MASK:
                    gained += add(t+624, values[t+397] ^ twist(pair_value), MASK)
                if masks[t+624] == MASK:
                    gained += add(t+397, values[t+624] ^ twist(pair_value), MASK)
        if not gained:
            break
    return values, masks, offset


def mix(x, multiplier):
    return ((x ^ (x >> 30)) * multiplier) & MASK


def unmix(value, modular_inverse):
    x = (value * modular_inverse) & MASK
    return x ^ (x >> 30)


def key_term(i, a, b, c):
    prior = ((b + i - 1) & MASK) ^ mix(a, 1566083941)
    later = ((c + i) & MASK) ^ mix(b, 1566083941)
    return (later - (BASE[i] ^ mix(prior, 1664525))) & MASK


def recover_first(i, key, b, c):
    later = ((c + i) & MASK) ^ mix(b, 1566083941)
    prior = unmix(((later - key) & MASK) ^ BASE[i], INV166)
    return unmix(prior ^ ((b + i - 1) & MASK), INV156)


def recover_third(i, key, a, b):
    prior = ((b + i - 1) & MASK) ^ mix(a, 1566083941)
    later = (key + (BASE[i] ^ mix(prior, 1664525))) & MASK
    return ((later ^ mix(b, 1566083941)) - i) & MASK


def source_terms(values, masks):
    result = {}
    for i in range(4, 624):
        locations = (i-2, i-1, i)
        if sum((MASK ^ masks[k]).bit_count() for k in locations) > 1:
            continue
        unknown = [k for k in locations if masks[k] != MASK]
        if not unknown:
            result[i-1] = {key_term(i, *values[i-2:i+1])}
        else:
            index = unknown[0]
            options = set()
            for value in (values[index], values[index] | (MASK ^ masks[index])):
                triple = values[i-2:i+1].copy()
                triple[index - (i-2)] = value
                options.add(key_term(i, *triple))
            result[i-1] = options
    return result


def infer(n, observed_values, observed_masks):
    """Conservative domain propagation; excluded means no possible seed."""
    values, masks = observed_values.copy(), observed_masks.copy()
    for iteration in range(30):
        residue_domains = {}
        for j, candidates in source_terms(values, masks).items():
            residue = j % n
            residue_domains[residue] = (
                residue_domains[residue] & candidates if residue in residue_domains
                else candidates
            )
            if not residue_domains[residue]:
                return False, values, masks, f'key residue at {j} iteration {iteration}'
        fresh = 0
        for i in range(4, 624):
            keys = residue_domains.get((i-1) % n)
            if keys is None:
                continue
            positions = (i-2, i-1, i)
            for unknown_offset in (0, 2):
                index = positions[unknown_offset]
                if masks[index] == MASK or any(
                    masks[positions[k]] != MASK for k in range(3) if k != unknown_offset
                ):
                    continue
                possible = (
                    {recover_first(i, key, values[i-1], values[i]) for key in keys}
                    if unknown_offset == 0 else
                    {recover_third(i, key, values[i-2], values[i-1]) for key in keys}
                )
                possible = {x for x in possible if not ((x ^ values[index]) & masks[index])}
                if not possible:
                    return False, values, masks, f'inverted state at {index} iteration {iteration}'
                pivot = next(iter(possible))
                consensus = MASK
                for x in possible:
                    consensus &= (~(x ^ pivot)) & MASK
                new = consensus & ~masks[index]
                if new:
                    values[index] = (values[index] & ~new) | (pivot & new)
                    masks[index] |= new
                    fresh += new.bit_count()
        if not fresh:
            return True, values, masks, 'stable'
    raise AssertionError('propagation did not converge')


def screen(payloads):
    source, known, offset = close(payloads)
    original, masks = source[offset-624:offset], known[offset-624:offset]
    original_terms = source_terms(original, masks)
    base_survivors = []
    for n in range(1, 624):
        seen = {}
        for j, options in original_terms.items():
            residue = j % n
            seen[residue] = seen[residue] & options if residue in seen else options
            if not seen[residue]:
                break
        else:
            base_survivors.append(n)
    inverse_survivors = []
    final_survivors = []
    inverse_only = {}
    recurrence_exclusions = {}
    target_masks = {}
    for n in base_survivors:
        valid, values, filled, reason = infer(n, original, masks)
        if not valid:
            inverse_only[n] = reason
            continue
        inverse_survivors.append(n)
        additions = [(i, values[i], filled[i] & ~masks[i]) for i in range(624)
                     if filled[i] & ~masks[i]]
        try:
            updated, updated_masks, off = close(payloads, additions)
        except ValueError as error:
            recurrence_exclusions[n] = str(error)
            continue
        final_survivors.append(n)
        target_masks[n] = updated_masks[off+951:off+955]
    return base_survivors, inverse_survivors, final_survivors, inverse_only, recurrence_exclusions, target_masks


def main(root):
    for trial in range(128):
        r = random.Random(trial)
        a, b, c = [r.getrandbits(32) for _ in range(3)]
        i = r.randrange(4,624)
        key = key_term(i,a,b,c)
        assert recover_first(i,key,b,c) == a
        assert recover_third(i,key,a,b) == c
    print('256 random mathematical inversion controls PASS', flush=True)
    raw = (root / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    payloads = [bytes.fromhex(x.decode()) for x in re.findall(rb'PAYLOAD=([0-9A-F]{32})',raw)]
    assert len(payloads) == len(STARTS) == 133 and STARTS[129] == 951
    base, inverse, surviving, first_bad, second_bad, target = screen(payloads)
    assert len(base) == 144 and len(inverse) == 118 and len(surviving) == 85
    assert min(surviving) == 364
    assert 249 in first_bad and 307 in first_bad and 392 in second_bad
    assert all(all(word == 0 for word in mask) for mask in target.values())
    print('Original source 64 exact/onebit seed terms; 144 survivors of lengths 1..623')
    print('New inversion contradictions',len(first_bad),'new MT recurrence contradictions',len(second_bad))
    print('Survivors',len(surviving),'first allowed length',min(surviving))
    print('Conditional selected K04 source bits recovered',0,'of 128')
    for n in (249,307,364,392,509,623):
        for variant in (0,1):
            seed = sum((((0x621902dd + variant*0x30303 + j*0x12537) & MASK) << (j*32)) for j in range(n))
            rng = random.Random(seed)
            initialized = list(rng.getstate()[1][:624])
            draws = [rng.getrandbits(32) for _ in range(967)]
            generated = [b''.join(x.to_bytes(4,'little') for x in draws[at:at+4]) for at in STARTS]
            stream, masks, offset = close(generated)
            original, initial_masks = stream[offset-624:offset],masks[offset-624:offset]
            assert all(not ((a ^ b) & m) for a,b,m in zip(initialized,original,initial_masks))
            ok, inferred, inferred_masks, reason = infer(n,original,initial_masks)
            assert ok, (n,variant,reason)
            assert all(not ((a ^ b) & m) for a,b,m in zip(initialized,inferred,inferred_masks))
            extras = [(j,inferred[j],inferred_masks[j] & ~initial_masks[j]) for j in range(624)
                      if inferred_masks[j] & ~initial_masks[j]]
            again,known,off=close(generated,extras)
            selected=[untemper(draws[951+j]) for j in range(4)]
            assert all(not ((selected[j]^again[off+951+j]) & known[off+951+j]) for j in range(4))
            print('Synthetic seeded source',n,variant,'PASS',flush=True)
    print('12/12 genuine-seeded controls PASS, no historical K04 recovery')

if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('resources'))
