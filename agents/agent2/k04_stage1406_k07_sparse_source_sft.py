"""K04 selected-withheld K02-stage1406 + K07 sparse halfword source test.

A source-first conditional MT19937 model, never an authentication of printer
firmware. The copied target printer payload and K04 commitment are not input.
Run: python agents/agent2/k04_stage1406_k07_sparse_source_sft.py
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
import k04_p951_symbolic_basis as mt

mt.LAST = 3150
K02 = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
K07 = bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9")
TRANS_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"


def parity(word):
    return word.bit_count() & 1


def source_k07():
    path = ROOT / "resources/evidence/transfers/transfer-audit.jsonl"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == TRANS_SHA
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    winners = {}
    for rec in rows:
        if rec.get("kind") != "CHUNK" or rec.get("transfer") != "AX-7782":
            continue
        seq = rec["seq"]
        if seq not in winners or winners[seq]["attempt"] < rec["attempt"]:
            winners[seq] = rec
    assert set(winners) == set(range(8))
    assert b"".join(bytes.fromhex(winners[k]["checkpoint"]) for k in range(8)) == K07
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())["slot_sha256"]
    assert hashlib.sha256(hashlib.sha256(K02).digest()[:16]).hexdigest() == acceptance["K02"]
    assert hashlib.sha256(hashlib.sha256(K07).digest()[:16]).hexdigest() == acceptance["K07"]


def k02_views():
    for endian in ("big", "little"):
        for reverse, swap, native in itertools.product((False, True), repeat=3):
            words = [K02[4*j:4*j+4] for j in range(4)]
            if swap:
                words = [word[2:] + word[:2] for word in words]
            if reverse:
                words.reverse()
            integers = [int.from_bytes(word, endian) for word in words]
            values = [x if native else mt.untemper(x) for x in integers]
            yield (endian, reverse, swap, native), values


def parity_model(basis, symbolic, start, high):
    pivots, checks = {}, []
    for index in range(8):
        actual = mt.temper(mt.get(symbolic, start + 227*index))
        half = actual[16:32] if high else actual[:16]
        for bit, expression in enumerate(half):
            remainder = 0
            rhs = 0
            while expression:
                p = expression.bit_length()-1
                if p in basis.rows:
                    eq, c = basis.rows[p]
                    expression ^= eq
                    rhs ^= c
                else:
                    remainder ^= 1 << p
                    expression ^= 1 << p
            tag = 1 << (16*index + bit)
            while remainder:
                p = remainder.bit_length()-1
                if p not in pivots:
                    pivots[p] = (remainder, tag, rhs)
                    break
                eq, t, c = pivots[p]
                remainder ^= eq
                tag ^= t
                rhs ^= c
            if not remainder:
                checks.append((tag, rhs))
    assert len(pivots) + len(checks) == 128
    return pivots, checks


def target_rank(basis, pivots, target):
    representatives = {}
    for expression in target:
        remainder = 0
        while expression:
            p = expression.bit_length()-1
            if p in basis.rows:
                expression ^= basis.rows[p][0]
            else:
                remainder ^= 1 << p
                expression ^= 1 << p
        after = 0
        while remainder:
            p = remainder.bit_length()-1
            if p in pivots:
                remainder ^= pivots[p][0]
            else:
                after ^= 1 << p
                remainder ^= 1 << p
        while after:
            p = after.bit_length()-1
            if p not in representatives:
                representatives[p] = after
                break
            after ^= representatives[p]
    return len(representatives)


def checkpoint_word(order, endian_flags):
    word = 0
    for j, index in enumerate(order):
        piece = K07[index*2:index*2+2]
        endian = "little" if (endian_flags >> j)&1 else "big"
        word |= int.from_bytes(piece, endian) << (16*j)
    return word


def main():
    source_k07()
    source, symbolic = mt.source(ROOT / "resources")
    assert source.rank == 15365
    target = [eq for stage in range(951, 955) for eq in mt.get(symbolic, stage)]
    qualified = []
    for view, block in k02_views():
        b = mt.Basis()
        b.rows = source.rows.copy()
        b.rank = source.rank
        try:
            for lane, native in enumerate(block):
                for bit, equation in enumerate(mt.get(symbolic, 1406 + lane)):
                    b.insert(equation, (native >> bit)&1)
        except AssertionError:
            continue
        qualified.append((view, b))
    assert len(qualified) == 10

    # Select geometries by linear rank ONLY, before using K07 values.
    basescan = qualified[0][1]
    low = []
    for start in range(1041, 1552):
        for high in (False, True):
            pivots, checks = parity_model(basescan, symbolic, start, high)
            freedom = target_rank(basescan, pivots, target)
            if freedom < 33:
                low.append((freedom, start, high, len(checks)))
    assert len(low) == 28
    compact = sorted({start for free,start,high,checks in low if free <= 17})
    assert compact == [1062, 1120, 1231, 1289, 1347, 1458, 1516]
    assert all(free == 17 for free,start,high,checks in low if start in compact)

    orders = (tuple(range(8)), tuple(reversed(range(8))),
              (0, 2, 4, 6, 1, 3, 5, 7))
    assignments = hits = 0
    for view, b in qualified:
        for start in compact:
            for high in (False, True):
                pivots, checks = parity_model(b, symbolic, start, high)
                assert target_rank(b, pivots, target) == 17
                for order in orders:
                    for endian_flags in range(256):
                        assignments += 1
                        observed = checkpoint_word(order, endian_flags)
                        if all(parity(observed & tag) == rhs for tag, rhs in checks):
                            hits += 1
                            print("SOURCE_QUALIFIED", view, start, high, order, endian_flags)
    assert assignments == 107520 and hits == 0
    print("K02_STAGE1406_SOURCE_COMPATIBLE_VIEWS", len(qualified))
    print("K07_RANK_FIRST_STAGE_GEOMETRIES", compact)
    print("K04_CONDITIONAL_FREE_BITS", 17)
    print("K07_ORIGINAL_SOURCE_ASSIGNMENTS", assignments)
    print("K07_ORIGINAL_SOURCE_SURVIVORS", hits)
    print("K04_ACCEPTED_NEW_COMPONENTS", 0)


if __name__ == "__main__":
    main()
