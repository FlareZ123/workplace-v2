"""Noisy-copy classic .NET generator inversion for the selected H-17 printer ACK.
Original spool SHA is pinned; original mask and commitment unchanged.
Tests all filtered complete coupon candidates, both coupon orientations.
The affine positions are empirically sampled, not universally proven.
"""
from __future__ import annotations
import argparse
import hashlib
import random
import re
from pathlib import Path

import numpy as np
from k04_dotnet_seedbyte_inversion_sft import M, SOURCE_SHA256, samples

MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")


def search(packet, phase, bases, slopes, affine, anchors=6):
    positions = [i for i in range(phase, phase+16) if affine[i]]
    threshold = max(3, len(positions)-6)
    candidates = set()
    for anchor in positions[:anchors]:
        observed = packet[anchor-phase]
        end = (M-1-observed)//256+1
        inv = pow(slopes[anchor], -1, M)
        for first in range(0, end, 200000):
            values = observed+256*np.arange(first,min(end,first+200000),dtype=np.int64)
            seeds = ((values-bases[anchor])*inv)%M
            scores = np.ones(len(seeds),dtype=np.uint8)
            for p in positions:
                if p == anchor:continue
                scores += (((bases[p]+slopes[p]*seeds)%M)&255)==packet[p-phase]
            candidates.update(map(int,seeds[scores>=threshold]))
    largest=0
    best=[]
    for seed in candidates | {M}:
        full=bytes(x&255 for x in samples(seed,phase+16)[phase:])
        matching=sum(a==b for a,b in zip(packet,full))
        if matching>largest:
            largest=matching
            best=[(seed,full.hex().upper())]
        elif matching==largest and len(best)<4:
            best.append((seed,full.hex().upper()))
        for name,coupon in (("native",full),("reversed",full[::-1])):
            key=bytes(a^b for a,b in zip(coupon,MASK))
            if hashlib.sha256(key).digest()==TARGET:
                print("ORIGINAL TARGET MATCH",seed,phase,name,key.hex().upper(),flush=True)
                return len(candidates),largest,best,True
    return len(candidates),largest,best,False


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--spool",type=Path,required=True)
    ap.add_argument("--start",type=int,default=0)
    ap.add_argument("--end",type=int,default=64)
    ap.add_argument("--orientation",choices=["forward","reversed","both"],default="both")
    a=ap.parse_args()
    assert 0<=a.start<=a.end<=64
    raw=a.spool.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA256
    selected=next(line for line in raw.decode().splitlines()
                  if "2026-10-03T18:02:00Z" in line and "PS-261003-0417" in line)
    selected_packet=bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",selected).group(1))
    count=a.end+16
    bases=samples(0,count)
    slopes=[(x-y)%M for x,y in zip(samples(1,count),bases)]
    rng=random.Random(20261105)
    affine=[True]*count
    for _ in range(20000):
        seed=rng.randrange(M)
        actual=samples(seed,count)
        for p in range(count):
            affine[p] &= actual[p]==(bases[p]+slopes[p]*seed)%M
    if a.start==0:
        for edits in ([0,2,5,9],[0,2,5,9,12,15]):
            packet=bytearray(x&255 for x in samples(1234567,16))
            for p in edits:packet[p]^=0xAA
            n,score,best,hit=search(bytes(packet),0,bases,slopes,affine)
            assert n==1 and best[0][0]==1234567 and score==16-len(edits)
            print("PLANTED PASS edits",len(edits),"state",best[0][0],flush=True)
    for phase in range(a.start,a.end+1):
        directions=["forward","reversed"] if a.orientation=="both" else [a.orientation]
        for direction in directions:
            packet=selected_packet if direction=="forward" else selected_packet[::-1]
            n,score,best,hit=search(packet,phase,bases,slopes,affine)
            print("ORIGINAL",direction,"phase",phase,"affine",sum(affine[phase:phase+16]),
                  "seeds",n,"best_matching_bytes",score,"K04_PASS",hit,flush=True)


if __name__=="__main__":
    main()
