"""Original selected K02 + selected K05 two-donor MT twist-index K04 reconstruction.

Run from repo: python agents/agent34/k04_k02_k05_twist_donor_sft.py
Reads source-only genuine K02/K05 and printer; official K04 hash queried ONLY
for completed, source-compatible 16-byte coupon candidates. Synthetic positive
is derived independently from authentic source-constrained symbolic state.
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'agents/agent49'))
import k04_p951_symbolic_basis as mt

mt.LAST = 2300
orig, symbolic = mt.source(ROOT/'resources')
assert orig.rank == 15365
K02 = bytes.fromhex('E1A5E474BAD7E853A2E8C71D3317D507')
K05 = bytes.fromhex('FF8B78200A56E8586DCDA00EF01E4572')
ROUTE = json.loads((ROOT/'resources/evidence/recovery-routing.json').read_text())
MASK = bytes.fromhex(ROUTE['K04']['masked_component'])
assert MASK.hex().upper() == '8556C8CB6140A7F9A5123AC7571BEE1C'
TARGET = json.loads((ROOT/'resources/acceptance.json').read_text())['slot_sha256']['K04']
STAGES = (1178, 1405)
TWIST_OFFSETS = (97, 170, 227, 397, 454, 624, 851)


def copy_basis(b):
    n = mt.Basis()
    n.rank = b.rank
    n.rows = b.rows.copy()
    return n


def pair_words(source, mode):
    endian, reverse, swap, native = mode
    parts = [source[i:i+4] for i in range(0, 16, 4)]
    if swap:
        parts = [p[2:4] + p[0:2] for p in parts]
    if reverse:
        parts.reverse()
    words = [int.from_bytes(p, endian) for p in parts]
    return words if native else [mt.untemper(w) for w in words]


def k05_words(source, mode):
    endian, reverse, native = mode
    parts = [source[i:i+4] for i in range(0, 16, 4)]
    if reverse:
        parts.reverse()
    words = [int.from_bytes(p, endian) for p in parts]
    return words if native else [mt.untemper(w) for w in words]


def impose(b, stage, words):
    n = copy_basis(b)
    for lane, native in enumerate(words):
        for bit, eq in enumerate(mt.get(symbolic, stage+lane)):
            n.insert(eq, (native >> bit) & 1)
    return n


def fixed_mismatch(b, stage, words):
    known = errors = 0
    for lane, word in enumerate(words):
        for bit, eq in enumerate(mt.get(symbolic, stage + lane)):
            guess = b.predict(eq)
            if guess is not None:
                known += 1
                errors += guess != ((word >> bit) & 1)
                if errors:
                    return known, errors
    return known, errors


def target_affine(b):
    pivots = {}
    coeff = []
    const = []
    for lane in range(4):
        for eq in mt.get(symbolic, 951 + lane):
            v, p = eq, 0
            residual = 0
            while v:
                k = v.bit_length() - 1
                if k in b.rows:
                    w, bit = b.rows[k]
                    v ^= w
                    p ^= bit
                else:
                    residual ^= 1 << k
                    v ^= 1 << k
            tagged = 0
            while residual:
                k = residual.bit_length() - 1
                if k in pivots:
                    row, tag = pivots[k]
                    residual ^= row
                    tagged ^= tag
                else:
                    tag = 1 << len(pivots)
                    pivots[k] = (residual, tag)
                    tagged ^= tag
                    break
            coeff.append(tagged)
            const.append(p)
    assert len(coeff) == len(const) == 128
    dim = len(pivots)
    basewords = [sum(const[32*k+j] << j for j in range(32)) for k in range(4)]
    base = b''.join(sum((mt.temper([(w >> j) & 1 for j in range(32)])[bit] << bit) for bit in range(32)).to_bytes(4,'little') for w in basewords)
    # Separate native target bit effects, with exact MT temper per word.
    deltas = []
    for d in range(dim):
        output = bytearray()
        for k in range(4):
            word = [(coeff[32*k+j] >> d) & 1 for j in range(32)]
            bits = mt.temper(word)
            output.extend(sum(bit << j for j,bit in enumerate(bits)).to_bytes(4, 'little'))
        deltas.append(bytes(output))
    return bytes(a ^ z for a,z in zip(base, MASK)), deltas


def full_candidates(b, limit_dim=16):
    base, deltas = target_affine(b)
    if len(deltas) > limit_dim:
        return len(deltas), 0, ()
    x = bytearray(base)
    found = []
    count = 0
    for k in range(1<<len(deltas)):
        if k:
            j = (k & -k).bit_length()-1
            delta = deltas[j]
            for i in range(16):
                x[i] ^= delta[i]
        count += 1
        if hashlib.sha256(x).hexdigest() == TARGET:
            found.append(bytes(x).hex().upper())
    return len(deltas), count, tuple(found)


def run():
    assert hashlib.sha256((ROOT/'resources/evidence/telemetry/freeze-export.jsonl').read_bytes()).hexdigest() == '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
    assert hashlib.sha256((ROOT/'resources/evidence/recorder/trip-recorder.raw').read_bytes()).hexdigest() == '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
    seen = 0
    compatible = 0
    low_rank = 0
    tested = 0
    hits = []
    minima = {}
    for donor in STAGES:
        for mode in itertools.product(('big','little'), (False, True), (False, True), (False, True)):
            b = impose(orig, donor, pair_words(K02,mode))
            assert b.rank == orig.rank + 128
            for offset in TWIST_OFFSETS:
                k05_stage = donor + offset
                for representation in itertools.product(('big','little'), (False, True), (False,True)):
                    seen += 1
                    words = k05_words(K05,representation)
                    known, errors = fixed_mismatch(b, k05_stage, words)
                    if errors:continue
                    compatible += 1
                    with_k05 = impose(b, k05_stage, words)
                    dim, count, accepted = full_candidates(with_k05, limit_dim=16)
                    minima.setdefault((donor, offset), []).append(dim)
                    if count:
                        low_rank += 1
                        tested += count
                    if accepted:
                        hits.append((donor,mode,k05_stage,representation,dim,accepted))
        print('DONOR',donor,'assigned',seen,'compatible',compatible,'low_rank',low_rank,'full_targets',tested, 'hit', hits, flush=True)
    assert seen == len(STAGES)*16*len(TWIST_OFFSETS)*8
    assert not hits, 'FOUND authentic candidate: ' + repr(hits)
    print('TOTAL', seen,compatible,low_rank,tested,'TARGET_HITS',len(hits))
    print('COMPATIBLE_RANK_SPECTRUM', {str(k):(len(v), min(v),max(v)) for k,v in minima.items()})
    # Independent synthetic bit-identical source-state K05 condition.
    b = impose(orig, 1178, pair_words(K02, ('big',False,False,False)))
    s = 0
    for pivot,(eq,val) in sorted(b.rows.items()):
        if val ^ ((eq&s).bit_count()&1):s |= 1<<pivot
    stage = 1178+397
    words = [sum(((eq&s).bit_count()&1)<<j for j,eq in enumerate(mt.get(symbolic,stage+lane))) for lane in range(4)]
    assert fixed_mismatch(b,stage,words)[1] == 0
    joint = impose(b,stage,words)
    assert joint.rank >= b.rank
    print('SOURCE_PLANTED_K05_NATIVE_POSITIVE',stage,'source_rank',b.rank,'joint_rank',joint.rank,'PASS')
    # A planted selected-stage full quartet collapses the unknown target to one
    # full coupon, confirming the affine reduction and serializer.
    target_words = [sum(((eq&s).bit_count()&1)<<j for j,eq in enumerate(mt.get(symbolic,951+lane))) for lane in range(4)]
    planted = impose(b,951,target_words)
    true_coupon = bytes(a^z for a,z in zip(b''.join(sum(bit<<j for j,bit in enumerate(mt.temper([(w>>i)&1 for i in range(32)]))).to_bytes(4,'little') for w in target_words),MASK))
    base, deltas = target_affine(planted)
    assert not deltas and base == true_coupon
    print('PLANTED_SELECTED_STAGE_COMPLETE_COUPON',true_coupon.hex().upper(),'PASS')
    # Target-adjacent alternative, hypothetical K05 producer copied near 951.
    adjacent = 0
    consistent = []
    for donor in STAGES:
        for mode in itertools.product(('big','little'), (False, True), (False, True), (False, True)):
            source_fit = impose(orig,donor,pair_words(K02,mode))
            for check_stage in range(947, 959):
                for representation in itertools.product(('big','little'), (False, True), (False,True)):
                    adjacent += 1
                    words = k05_words(K05,representation)
                    _,errors = fixed_mismatch(source_fit,check_stage,words)
                    if errors == 0:
                        consistent.append((donor,mode,check_stage,representation))
    assert adjacent == 2 * 16 * 12 * 8
    print('ADJACENT_SELECTED_K05_GROUP',adjacent,'source_compatible',len(consistent),consistent[:5])
    assert not consistent

if __name__=='__main__':run()
