"""NumPy MT19937 SeedSequence exact source-only arbitrary pool-period sieve.

The NumPy initialized register is periodic in an unknown pool word index n:
S[i] = undo_shift(((pool[i%n]^before_i)*factor_i) mod 2^32), i>0.
This test derives original source-fixed pool word domains for every n=4..623,
without guessing any pool contents or consulting selected K04.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import hashlib
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "resources"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent30"))
from k04_numpy_poolwidth_multilane_sft import (
    mt, source_states, constants, SOURCE_SHA, seeded_key, packets,
)
U = 0xFFFFFFFF


def valid_periods(states: list[tuple[int,int]], lengths=range(4,624)):
    possible = []
    record = {}
    source = []
    for i,(mask,value) in enumerate(states):
        if i==0 or mask.bit_count()<31:
            continue
        b,mul=constants(i)
        inv=pow(mul,-1,1<<32)
        choices=(value,) if mask==U else (value,value|(U^mask))
        options={((((w^(w>>16))*inv)&U)^b) for w in choices}
        source.append((i,options))
    for n in lengths:
        residue={}
        contradictions=0
        for i,options in source:
            j=i%n
            if j not in residue:
                residue[j]=set(options)
            else:
                residue[j].intersection_update(options)
                if not residue[j]:
                    contradictions += 1
        if not contradictions:
            possible.append(n)
        record[n]=(len(source),len(residue),contradictions)
    return possible,record


def run(phase:int):
    raw=(ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    original=[bytes.fromhex(w.decode()) for w in re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)]
    assert len(original)==len(mt.STARTS)==133

    # Genuine seeded 8/16/32/pool-size arbitrary controls from exactly the
    # same printer-layout source reconstruction, withholding selected row129.
    control=[]
    for size in (4,5,7,8,16,32,64,128):
        seq=np.random.SeedSequence(0x1234567890ABCDE123456789,pool_size=size)
        key=seeded_key(tuple(int(x) for x in seq.pool))
        emitter=np.random.MT19937(seq)
        assert np.array_equal(key,emitter.state["state"]["key"])
        outputs=[int(v) for v in emitter.random_raw(phase+max(mt.STARTS)+5)]
        data=packets(outputs,phase)
        states=source_states(phase,data)
        periods,_=valid_periods(states,(size,))
        assert periods==[size], (phase,size,periods)
        control.append(size)
    print("REAL_SEEDED_NUMPY_PERIOD_CONTROL",phase,control,flush=True)

    states=source_states(phase,original)
    possible,record=valid_periods(states)
    s0_valid= ((states[0][1]^0x80000000)&states[0][0])==0
    print("ORIGINAL_PERIOD_SCAN",phase,"S0_possible",s0_valid,
          "possible_count",len(possible),"first_30_possible",possible[:30],
          "last_30_possible",possible[-30:],"max_excluded",
          max((n for n in range(4,624) if n not in possible),default=None),
          "anchored_original_words",record[4][0],
          "periods_4_16_32_64_128",{n:n in possible for n in (4,5,8,16,32,64,128)},
          flush=True)


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("expected output startup offset")
    run(int(sys.argv[1]))
