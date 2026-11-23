#!/usr/bin/env python3
"""H-17 four-fresh all42 MT chronology: selected cross-carrier source bridge.

Exact source-only negative / positive gate. Withhold disputed PS-0417 ACK2
PAYLOAD before decoding. No original K04 hash, mask or candidate enters fitting.
Run: python agents/agent1/k04_fourfresh_crosscarrier_sft.py [resources_root]
"""
from __future__ import annotations
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent10"))
from k04_all42_wholewindow_sft import (
    ALT_STAGES, SPOOL_SHA, build_basis, project, symbolic_words,
    untemper, temper, U32
)

DELTA = {12:2, 25:-2, 43:2, 47:-2, 66:2,
         79:-2, 96:2, 109:-2, 128:3, 129:-1}
SELECTED_RAW = {
  "K01_WN14": "049AAB2E1CDE7A82CD7C60234303C91A",
  "K02_LT204": "E1A5E474BAD7E853A2E8C71D3317D507",
  "K03_PTWSERIAL_SUFFIXES": "D7DAD6BC9714519B7DAD0AD4BE8E87FD",
  "K05_TRP2": "FF8B78200A56E8586DCDA00EF01E4572",
  "K06_RC17": "5DBF40EE52FAAED9A536D3326CF0D95A",
  "K07_AX7782": "8947CEDCB9CC73BAB7E87BE63302C5C9",
}
EXTRA_PATHS = ("mail/03.eml", "mail/06.eml",
    "maintenance/seal-receipts.jsonl", "procedures/RC-17-scans.txt")

def source_setup(root):
    raw = (root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    lines = re.findall(
      rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
      raw,re.M)
    assert len(lines) == 133
    assert lines[129][:5] == (b"2026-10-03T18:02:00Z",
      b"PS-261003-0417",b"2",b"ACK",b"RECOVER")
    packets = [None if i==129 else tuple(
        untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4*j:4*j+4],"little"))
        for j in range(4)) for i,row in enumerate(lines)]
    assert packets[129] is None
    gaps = [v-u for u,v in zip(ALT_STAGES,ALT_STAGES[1:])]
    for i,d in DELTA.items():gaps[i]+=d
    stages=[0]
    for d in gaps:stages.append(stages[-1]+d)
    assert len(stages)==133 and stages[129]==955 and min(gaps)>=4
    words=symbolic_words(0,2100)
    basis=build_basis(packets,tuple(stages),words,0)
    assert len(basis)==15434
    return stages,words,basis

def known(word,basis):
    mask=value=0
    for i,form in enumerate(word):
        free,rhs=project(form,basis)
        if not free:
            mask |= 1<<i
            value |= rhs<<i
    return mask,value

def direct_source_fields(root,words,basis):
    # Test exact source-selected six raw 16B objects and original standalone
    # historical four-byte fields against ≥29-bit source-predicted native words.
    informative=[]
    for i,word in enumerate(words):
        mask,val=known(word,basis)
        if mask.bit_count()>=29:informative.append((i,mask,val))
    assert len(informative)==1174
    fields=[]
    for name,rawhex in SELECTED_RAW.items():
        buf=bytes.fromhex(rawhex)
        for reversed_words in (False,True):
            chunks=[buf[i:i+4] for i in range(0,16,4)]
            if reversed_words:chunks.reverse()
            for endian in ("little","big"):
                for j,part in enumerate(chunks):
                    for encoding in ("native","untemper"):
                        num=int.from_bytes(part,endian)
                        fields.append((name,encoding,j,
                           untemper(num) if encoding=="untemper" else num))
    for path in EXTRA_PATHS:
        raw=(root/"evidence"/path).read_text()
        for idx,hit in enumerate(re.finditer(
              r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{8}(?![0-9A-Fa-f])",raw)):
            field=bytes.fromhex(hit.group())
            for endian in ("little","big"):
                num=int.from_bytes(field,endian)
                fields.append((path, "native",idx,num))
                fields.append((path, "untemper",idx,untemper(num)))
    counts=collections.Counter()
    matches=[]
    for name,encoding,j,num in fields:
        for phase,mask,predicted in informative:
            counts[mask.bit_count()] += 1
            if ((num^predicted)&mask)==0:
                matches.append([name,encoding,j,phase,mask.bit_count()])
    assert not matches
    assert dict(counts)=={29:1296,30:28080,31:55296,32:422496}
    # Heldout self-contained source-positive: an entire source-fixed original
    # output is interpreted as a synthetic separate raw observed field.
    phase,mask,value=next(x for x in informative if x[1]==U32)
    assert ((value^dict((q,(m,v)) for q,m,v in informative)[phase][1])&mask)==0
    return {"independent_fields":len(fields),"stage_values_ge29bits":len(informative),
      "comparisons_by_known_bits":dict(sorted(counts.items())),
      "original_source_matches":matches,
      "independent_IID32_expected_matches":sum(c*2.0**-n for n,c in counts.items()),
      "planted_exact_fullword_positive":"PASS"}

def temperforms(word):
    a=word.copy()
    a=[v^(word[i+11] if i+11<32 else 0) for i,v in enumerate(a)]
    old=a
    a=[v^(old[i-7] if i>=7 and (0x9D2C5680>>i)&1 else 0) for i,v in enumerate(a)]
    old=a
    a=[v^(old[i-15] if i>=15 and (0xEFC60000>>i)&1 else 0) for i,v in enumerate(a)]
    old=a
    return [v^(old[i+18] if i+18<32 else 0) for i,v in enumerate(a)]

def scan8(originals,catalog):
    hits=[];maxbits=(0,None);tests=0
    for label,buf in originals.items():
        for reverse in (False,True):
            parts=[buf[i:i+2] for i in range(0,16,2)]
            if reverse:parts.reverse()
            for endian in ("big","little"):
                items=[int.from_bytes(x,endian) for x in parts]
                for variant in ("native","tempered"):
                    for half in (0,1):
                        data=catalog[(variant,half)]
                        for stride in range(1,13):
                            for phase in range(2100-7*stride):
                                tests+=1
                                bits=0;match=True
                                for i,val in enumerate(items):
                                    mask,pred=data[phase+i*stride]
                                    if ((val^pred)&mask):
                                        match=False;break
                                    bits+=mask.bit_count()
                                if not match:continue
                                if bits>maxbits[0]:
                                    maxbits=(bits,(label,reverse,endian,variant,half,stride,phase))
                                if bits>=48:hits.append((label,reverse,endian,variant,half,stride,phase,bits))
    return hits,maxbits,tests

def eight_halfwords(words,basis):
    views={}
    for variant in ("native","tempered"):
        expressions = words if variant=="native" else [temperforms(w) for w in words]
        full=[known(w,basis) for w in expressions]
        for half in (0,1):
            views[(variant,half)]=[((m>>(16*half))&65535,(v>>(16*half))&65535)
                                   for m,v in full]
    originals={
       "K02_LT204":bytes.fromhex(SELECTED_RAW["K02_LT204"]),
       "K07_AX7782":bytes.fromhex(SELECTED_RAW["K07_AX7782"]),
    }
    hits,maxbits,tests=scan8(originals,views)
    assert tests==788928 and hits==[] and maxbits[0]==16
    phase=120
    synthetic=b"".join(views[("native",0)][phase+i][1].to_bytes(2,"big")
                       for i in range(8))
    planted,maxplant,_=scan8({"planted8":synthetic},views)
    assert any(row[5]==1 and row[6]==phase and row[7]==112 for row in planted)
    return {"complete_eightword_models":tests,"original_48plus_bit_matches":hits,
      "max_compatible_fixed_bits":maxbits[0],
      "synthetic_112bit_8word_control":"PASS"}

if __name__=="__main__":
    root=Path(sys.argv[1]) if len(sys.argv)==2 else Path(__file__).resolve().parents[2]/"resources"
    stages,words,basis=source_setup(root)
    result={"spool_sha256":SPOOL_SHA,"copied_ACK2_payload_loaded":False,
       "fourfresh_selected_stage":stages[129],"source_rank":len(basis),
       "direct":direct_source_fields(root,words,basis),
       "halfword":eight_halfwords(words,basis),
       "k04_original_commitment":"NOT_EVALUATED"}
    print(json.dumps(result,sort_keys=True,indent=2))
