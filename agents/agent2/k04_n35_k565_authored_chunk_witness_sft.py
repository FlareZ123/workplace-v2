"""Enumerate whole source-compatible raw seed word patterns at k565/n35/L76.

This is the sole survivor of the frozen author-like writing alphabet screen.
Raw chunks are genuine source-global witnesses, but unknown other bytes and
hypothetical CPython printer/caption link prevent an actual full K08 candidate.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent25"))
from k04_n35_n39_caption_source_sft import (
    OFFSET, mt, words, original_native,
    phase_equations, reduce_source, seed_alphabet_support,
)
import k04_n35_n39_global_source_joint_feasible_sft as joint
from k04_n35_n39_author_orthography_sft import AUTHORED_CAPTION

N=35
K=565
LENGTH=76


def main():
    symbolic=words(OFFSET+623)
    observed=original_native()
    coefficients,constants=reduce_source(phase_equations(
        observed,symbolic,OFFSET+K))
    terms=joint.source_terms(coefficients,constants,N)
    vectors,rank,local,fixed=joint.global_source_basis(
        coefficients,constants,terms)
    print("SOURCE_SELECTED_WITHHELD",N,K,LENGTH,
          "terms",len(terms),"local",local,"global",rank,
          "correlations",local-rank,flush=True)
    rows=[]
    for number,(_,idx,_,_,unique) in enumerate(terms):
        candidates=[]
        for raw,triple in unique.items():
            if not seed_alphabet_support(raw,N,LENGTH,idx,AUTHORED_CAPTION):
                continue
            packed=triple[0] | (triple[1]<<32) | (triple[2]<<64)
            candidates.append((raw,joint.remainder(packed<<(number*96),vectors)))
        assert candidates
        rows.append(candidates)
    suffix=[set() for _ in range(len(rows)+1)]
    suffix[-1].add(0)
    for i in range(len(rows)-1,-1,-1):
        suffix[i]={candidate ^ tail for _,candidate in rows[i]
                   for tail in suffix[i+1]}
    result=[]
    def dfs(index,current,chosen):
        if index==len(rows):
            if current==0:
                result.append(tuple(chosen))
            return
        for raw,component in rows[index]:
            next_state=current^component
            if next_state in suffix[index+1]:
                dfs(index+1,next_state,chosen+[raw])
    dfs(0,joint.remainder(fixed,vectors),[])
    assert len(result)==16,("changed original count",len(result))
    for j,choice in enumerate(result):
        chars=["·"]*LENGTH
        for term,word in zip(terms,choice):
            idx=term[1]
            offset=4*(N-1-idx)
            raw=word.to_bytes(4,"big").decode("ascii")
            for c,value in enumerate(raw):
                chars[offset+c]=value
        print("WHOLE_SOURCE_AUTHOR_RAW_PREFIX_PATTERN",j,
              "".join(chars),flush=True)
    first4=sorted({choice[tuple(t[1] for t in terms).index(34)].to_bytes(4,"big").decode("ascii") for choice in result})
    print("FIRST_FOUR_SOURCE_COMPATIBLE",first4,
          "all_witnesses",len(result),flush=True)

if __name__=="__main__":
    main()
