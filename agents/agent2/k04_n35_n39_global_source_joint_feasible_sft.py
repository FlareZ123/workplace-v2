"""Exact joint printable caption-key feasibility under original printer-source affine state.

n35/n39 residual phase test, conditional on p951 and genuine CPython
Random(bytes, version=2). Each preimage group is enumerated from the original
132 intact printer packets; disputed physical K04 row129 is never observed.
Instead of independent printable per-key checks, this enforces one globally
consistent original native MT source state by XOR-state-syndrome DP.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent25"))
from k04_n35_n39_caption_source_sft import (
    OFFSET, PRINTABLE, U, mt, words, original_native,
    source_group, key_term, reduce_source, phase_equations, source_dimension,
    seed_alphabet_support,
)


def reduced_basis(expressions):
    basis = {}
    for value in expressions:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    ordered = sorted(basis, reverse=True)
    return [basis[pivot] for pivot in ordered], len(ordered)


def remainder(value, vectors):
    for vector in vectors:
        if value & (1 << (vector.bit_length() - 1)):
            value ^= vector
    return value


def source_terms(coefficients, constants, n):
    terms = []
    for at in range(4, 624):
        idx = (at - 1) % n
        if idx < 16:
            continue
        indices = tuple(32 * word + bit
                        for word in (at - 2, at - 1, at)
                        for bit in range(32))
        free = source_dimension(coefficients[index] for index in indices)
        if free > 9:
            continue
        triples = source_group(coefficients, constants, at)
        assert len(triples) == 1 << free
        unique = {}
        for triple in triples:
            raw = ((key_term(at, triple) - idx) & U)
            assert raw not in unique
            unique[raw] = triple
        terms.append((at, idx, free, indices, unique))
    return terms


def global_source_basis(coefficients, constants, terms):
    columns = defaultdict(int)
    offset = 0
    fixed = 0
    for _, _, _, indices, _ in terms:
        for localbit, row in enumerate(indices):
            targetbit = offset + localbit
            fixed |= constants[row] << targetbit
            expression = coefficients[row]
            while expression:
                bit = expression & -expression
                columns[bit.bit_length()-1] |= (1 << targetbit)
                expression ^= bit
        offset += 96
    vectors, rank = reduced_basis(columns.values())
    total_local = sum(term[2] for term in terms)
    assert rank <= total_local
    return vectors, rank, total_local, fixed


def solve_terms(terms, vectors, fixed, n, length):
    candidates = []
    for number, (_, idx, _, _, unique) in enumerate(terms):
        row = []
        for raw, triple in unique.items():
            if not seed_alphabet_support(raw, n, length, idx, PRINTABLE):
                continue
            packed = triple[0] | (triple[1] << 32) | (triple[2] << 64)
            row.append((raw, remainder(packed << (96*number), vectors)))
        if not row:
            return {"local_feasible": False, "joint_feasible": False,
                    "local_counts": [len(r) for r in candidates]+[0]}
        candidates.append(row)

    # State is the exact quotient-space syndrome. A zero syndrome is one
    # globally consistent native-state assignment for all printable chunks.
    ways = {remainder(fixed, vectors): (1, tuple())}
    sizes = []
    for row in candidates:
        nextways = {}
        for syndrome, (count, witness) in ways.items():
            for raw, component in row:
                new_syndrome = syndrome ^ component
                if new_syndrome not in nextways:
                    nextways[new_syndrome] = (count, witness + (raw,))
                else:
                    old_count, old_witness = nextways[new_syndrome]
                    nextways[new_syndrome] = (old_count + count, old_witness)
        ways = nextways
        sizes.append(len(ways))
    matches, chosen = ways.get(0, (0, tuple()))
    return {"local_feasible": True, "joint_feasible": matches>0,
            "joint_assignments": matches, "local_counts": [len(r) for r in candidates],
            "dp_state_counts": sizes,
            "witness_words": [(terms[i][1], chosen[i].to_bytes(4,"big").hex(),
                               chosen[i].to_bytes(4,"big").decode("ascii","replace"))
                              for i in range(len(chosen))]}


def analyze(native, symbolic, n, k, lengths=None):
    coefficients, constants = reduce_source(
        phase_equations(native, symbolic, OFFSET+k))
    terms = source_terms(coefficients, constants, n)
    vectors, rank, local, fixed = global_source_basis(
        coefficients, constants, terms)
    results = {}
    selected_lengths = (lengths if lengths is not None else
                        range(4*(n-1)-63, 4*n-63))
    for length in selected_lengths:
        results[length] = solve_terms(terms, vectors, fixed, n, length)
    return {"n":n, "k":k, "terms":len(terms), "local_rank_sum":local,
            "global_joint_rank":rank, "cross_term_correlations":local-rank,
            "by_length":results}


def genuine_control(symbolic, n, k, length):
    raw = (b"After the late watch, there is still room by the window for "
           b"one more cup, and a little light across the sea. " * 3)[:length]
    assert len(raw)==length and all(v in PRINTABLE for v in raw)
    key = int.from_bytes(raw + hashlib.sha512(raw).digest(),"big")
    assert (key.bit_length()+31)//32 == n
    rng = random.Random(raw)
    stream = [rng.getrandbits(32)
              for _ in range(OFFSET+k+mt.STARTS[-1]+4)]
    native = [[mt.untemper(stream[OFFSET+k+start+lane])
               for lane in range(4)] for start in mt.STARTS]
    result = analyze(native, symbolic, n, k, (length,))
    row=result["by_length"][length]
    assert row["joint_feasible"], (n,k,length,row)
    assert row["joint_assignments"] > 0
    print("GENUINE_WHOLE_PRINTER_KEY_SOURCE_JOINT=PASS",n,k,length,
          "joint_assignments",row["joint_assignments"],
          "correlations",result["cross_term_correlations"],flush=True)


def run(n, shard):
    phases=(tuple(range(504,624)) if n==35
            else tuple(range(309,338)))[shard::8]
    symbolic=words(OFFSET+623)
    genuine_control(symbolic,n,phases[0],4*n-64)
    genuine_control(symbolic,n,phases[0],4*(n-1)-63)
    native=original_native()
    totals={length:{"local":0,"joint":0,"witnesses":[]}
            for length in range(4*(n-1)-63,4*n-63)}
    for k in phases:
        result=analyze(native,symbolic,n,k)
        for length,row in result["by_length"].items():
            if row["local_feasible"]:
                totals[length]["local"]+=1
                if row["joint_feasible"]:
                    totals[length]["joint"]+=1
                    totals[length]["witnesses"].append(k)
                    print("SOURCE_JOINT_PRINTABLE_WITNESS",n,k,length,
                          "assignments",row["joint_assignments"],
                          "printable_words",row["witness_words"],flush=True)
                else:
                    print("SOURCE_GLOBAL_JOINT_REJECTION",n,k,length,
                          "term_count",result["terms"],
                          "local_rank",result["local_rank_sum"],
                          "joint_rank",result["global_joint_rank"],
                          "local_domains",row["local_counts"],
                          "dp_syndrome_counts",row["dp_state_counts"],flush=True)
    print("ORIGINAL_SOURCE_GLOBAL_JOINT_SHARD",n,shard,
          "phases",list(phases),"totals",totals,flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--n",type=int,choices=(35,39),required=True)
    parser.add_argument("--shard",type=int,choices=range(8),required=True)
    args=parser.parse_args()
    run(args.n,args.shard)


if __name__=="__main__":
    main()
