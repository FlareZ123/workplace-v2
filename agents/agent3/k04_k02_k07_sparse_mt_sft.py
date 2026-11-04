"""Read-only original K02+K07 hypothetical MT donor to K04 complete candidates.

Run on repository root:
    python agents/agent3/k04_k02_k07_sparse_mt_sft.py 0
    python agents/agent3/k04_k02_k07_sparse_mt_sft.py 1
    python agents/agent3/k04_k02_k07_sparse_mt_sft.py 2
    python agents/agent3/k04_k02_k07_sparse_mt_sft.py 3
Each shard checks a disjoint 64 of 256 complete 17-bit coupon cosets.
"""
from pathlib import Path
from collections import Counter
import sys
import itertools
import json
import hashlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

mt.LAST = 5200
SOURCE = ROOT / "resources"
SPOOL = SOURCE / "evidence/print/spool-reconstruction.log"
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
base, symbolic = mt.source(SOURCE)
assert base.rank == 15365
k02 = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
k07 = bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9")
route = json.loads((SOURCE / "evidence/recovery-routing.json").read_text())
mask = int.from_bytes(bytes.fromhex(route["K04"]["masked_component"]), "little")
target = bytes.fromhex(
    json.loads((SOURCE / "acceptance.json").read_text())["slot_sha256"]["K04"]
)
assert target.hex() == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
target_eqs = [
    v
    for stage in range(951, 955)
    for v in mt.temper(mt.get(symbolic, stage))
]


def insert_k02(basis, stage, endian, native, reverse, pairflip):
    chunks = [k02[i:i+4] for i in range(0, 16, 4)]
    if reverse:
        chunks.reverse()
    for j, word in enumerate(chunks):
        if pairflip:
            word = word[2:4] + word[0:2]
        value = int.from_bytes(word, "big" if endian else "little")
        if not native:
            value = mt.untemper(value)
        for bit, equation in enumerate(mt.get(symbolic, stage+j)):
            basis.insert(equation, (value >> bit) & 1)


def insert_k07(basis, half, endian, reverse):
    chunks = [k07[i:i+2] for i in range(0, 16, 2)]
    if reverse:
        chunks.reverse()
    for seq, word in enumerate(chunks):
        value = int.from_bytes(word, "big" if endian else "little")
        bits = mt.temper(mt.get(symbolic, 951 + 397 * seq))
        for i, equation in enumerate(bits[16*half:16*half+16]):
            basis.insert(equation, (value >> i) & 1)


def affine_image(basis):
    constant = 0
    columns = {}
    for outbit, original in enumerate(target_eqs):
        equation = original
        rhs = 0
        while equation:
            pivot = equation.bit_length() - 1
            row = basis.rows.get(pivot)
            if row is None:
                columns[pivot] = columns.get(pivot, 0) ^ (1 << outbit)
                equation ^= 1 << pivot
            else:
                dependency, bit = row
                equation ^= dependency
                rhs ^= bit
        constant |= rhs << outbit
    independent = {}
    effects = []
    for effect in columns.values():
        v = effect
        while v:
            pivot = v.bit_length() - 1
            if pivot not in independent:
                independent[pivot] = v
                effects.append(effect)
                break
            v ^= independent[pivot]
    return constant, effects


def canonical(constant, effects):
    basis = {}
    for effect in effects:
        while effect:
            pivot = effect.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = effect
                break
            effect ^= basis[pivot]
    for pivot in sorted(basis, reverse=True):
        if (constant >> pivot) & 1:
            constant ^= basis[pivot]
    return constant, tuple(sorted(basis.items()))


def main(shard):
    assert 0 <= shard < 4
    hist = Counter()
    cosets = {}
    for donor in (1178, 1405):
        for endian, native, reverse, pairflip in itertools.product(range(2), repeat=4):
            basis = mt.Basis()
            basis.rows = base.rows.copy()
            basis.rank = base.rank
            try:
                insert_k02(basis, donor, endian, native, reverse, pairflip)
            except AssertionError:
                hist["k02_inconsistent"] += 1
                continue
            for half, h_endian, h_reverse in itertools.product(range(2), repeat=3):
                extended = mt.Basis()
                extended.rows = basis.rows.copy()
                extended.rank = basis.rank
                try:
                    insert_k07(extended, half, h_endian, h_reverse)
                except AssertionError:
                    hist["k07_inconsistent"] += 1
                    continue
                constant, effects = affine_image(extended)
                assert len(effects) == 17
                hist["k07_consistent"] += 1
                fingerprint = canonical(constant, effects)
                cosets.setdefault(fingerprint, (constant, effects))
    assert hist["k07_consistent"] == 256
    assert len(cosets) == 256
    print("SOURCE_CONSISTENT", dict(hist), "DISTINCT_COSETS", len(cosets))

    matches = []
    total = 0
    synthetic_positive = False
    for constant, effects in list(cosets.values())[shard*64:(shard+1)*64]:
        planted = constant ^ effects[0] ^ effects[-1]
        synthetic = hashlib.sha256((planted ^ mask).to_bytes(16, "little")).digest()
        value = constant
        old_gray = 0
        for i in range(1 << len(effects)):
            gray = i ^ (i >> 1)
            if i:
                value ^= effects[(gray ^ old_gray).bit_length()-1]
            old_gray = gray
            digest = hashlib.sha256((value ^ mask).to_bytes(16, "little")).digest()
            if digest == target:
                matches.append(value.to_bytes(16, "little").hex().upper())
            if digest == synthetic:
                synthetic_positive = True
            total += 1
    assert total == 8_388_608 and synthetic_positive
    print("SHARD", shard, "COMPLETE_CANDIDATES", total,
          "ORIGINAL_K04_MATCHES", matches, "SYNTHETIC_PASS", synthetic_positive)


if __name__ == "__main__":
    main(int(sys.argv[1]))
