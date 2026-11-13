#!/usr/bin/env python3
"""Inspect genuine CPython seed residue domains surviving the K04 gap sieve.

Original selected printer packet and acceptance material are never read.
This isolates finite complete-seed reconstructions from vacuous necessary fits.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
from itertools import product
from math import prod
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent40"))
from k04_cpython_midwarmup_n1to24_sft import (
    source_states,term_domains,consistent,observed_packets,seed_domains,
    genuine_full_source_test,
)

PHASES=[
    (768,18),(800,18),(899,18),(1164,24),
    (1554,16),(1600,16),(1729,20),(1790,10),
    (1959,2),(2028,2),(2130,1),(2257,1),(2350,1),(2495,1)
]


def main():
    packets=observed_packets()
    results=[]
    for k,n in PHASES:
        t=time.monotonic()
        states=source_states(k,packets)
        mask,value=states[0]
        s0_ok=not ((value^0x80000000)&mask)
        rows=term_domains(states,0) if s0_ok else []
        r= [set() for _ in range(n)]
        unconstrained=[]
        intersections=[None]*n
        for index,allowed in rows:
            c=index%n
            if intersections[c] is None:
                intersections[c]=set(allowed)
            else:
                intersections[c]&=allowed
        for c,item in enumerate(intersections):
            if item is None:
                unconstrained.append(c)
        complete=all(item is not None and item for item in intersections)
        count=(prod(len(item) for item in intersections) if complete else None)
        finite=genuine_full_source_test(k,packets,n,rows) if s0_ok and consistent(rows,n) else {"status":"SOURCE_CONTRADICTION"}
        row=dict(offset=k,n=n,s0_fixed_bits=mask.bit_count(),
                 s0_possible=s0_ok,source_keyterm_rows=len(rows),
                 observed_key_residues=n-len(unconstrained),
                 unconstrained_key_residues=unconstrained,
                 key_domain_sizes=[len(v) if v is not None else None for v in intersections],
                 fully_bounded_seed_count=count,
                 finite_replay=finite,elapsed_seconds=round(time.monotonic()-t,3))
        results.append(row)
        print(json.dumps(row),flush=True)
    output=ROOT/"artifacts"/"agent40"
    output.mkdir(parents=True,exist_ok=True)
    (output/"midwarmup_residue_diagnostics.json").write_text(json.dumps(results,indent=2)+"\n")


if __name__=="__main__":
    main()
