#!/usr/bin/env python3
"""Source-free K04 original-style acceptance-first reducer regression.

Agent37's two xoroshiro128++ 1.0 states have identical intact first-packet
outputs and exactly the same twelve initial-a bits, but different erased
middle and later packets. Exhaustively enumerate BOTH first-packet states
with the existing Agent37 exact model-blocking solver. A synthetic original-
style XOR/SHA256 target is then checked for every predicted middle,
REGARDLESS of whether a separately held-out later packet matches.

Synthetic fixtures only. Reads no H-17 archive, evidence, route, commitment,
real target or PDF. Emits aggregate booleans only, no source or key bytes.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from agents.agent37.k04_xoropp_samebucket_collision_sft import (
    WITNESSES,anchor,independent_forward,query_models,
)


def encode(words: tuple[int,int],endian: str,order: str)->bytes:
    seq=list(words)
    if order=='ba':seq.reverse()
    return b''.join(int(v).to_bytes(8,endian) for v in seq)


def check(models,mask: bytes,target: str,later: tuple[int,int],endian: str,order: str):
    hits=full_replay=joint=0
    for state in models:
        v=independent_forward(*state,6)
        middle=encode(tuple(v[2:4]),endian,order)
        component=bytes(x^y for x,y in zip(middle,mask))
        hit=hashlib.sha256(component).hexdigest()==target
        replay=tuple(v[4:6])==later
        hits+=hit
        full_replay+=replay
        joint+=(hit and replay)
    return hits,full_replay,joint


def run():
    raw=[independent_forward(*s,6) for s in WITNESSES]
    assert raw[0][:2]==raw[1][:2]
    assert raw[0][2:4]!=raw[1][2:4] and raw[0][4:6]!=raw[1][4:6]
    assert anchor(WITNESSES[0][0])==anchor(WITNESSES[1][0])
    models,terminal=query_models(raw[0][:2],anchor(WITNESSES[0][0]),30000)
    assert terminal=='unsat' and len(models)==2 and set(models)==set(WITNESSES)

    mask=bytes(range(16)) # synthetic-only deterministic route mask
    cases=0
    for endian in ('big','little'):
        for order in ('ab','ba'):
            for history in raw:
                mid=encode(tuple(history[2:4]),endian,order)
                target=hashlib.sha256(bytes(x^y for x,y in zip(mid,mask))).hexdigest()
                real_later=tuple(history[4:6])
                fake_later=(0,0) # deliberate independent replacement, not a source observation
                assert fake_later!=real_later
                # The authenticity check must still find the correct selected middle
                # even when the later retry is unrelated.
                assert check(models,mask,target,fake_later,endian,order)==(1,0,0)
                assert check(models,mask,target,real_later,endian,order)==(1,1,1)
                cases+=2
            # A synthetic target never matching the two generated complete outputs
            poison=hashlib.sha256(b'no matching H17 source content').hexdigest()
            assert check(models,mask,poison,tuple(raw[0][4:6]),endian,order)==(0,1,0)
            cases+=1
    print({'synthetic_only':True,
           'exact_firstpacket_models_enumerated':len(models),
           'terminal_proof':terminal,
           'layouts':4,
           'synthetic_tests':cases,
           'unrelated_later_preserves_commitment_hit':True,
           'genuine_later_is_independent_joint_positive':True,
           'synthetic_target_poison_rejected':True,
           'original_K04_recovered':False})

if __name__=='__main__':run()
