"""Enumerate all 16 real source-consistent 53-bit outcomes at PV seq176.

Source-only, never reads the selected ESC-N ACK, K04 acceptance or mask.
Run from repository root: python agents/agent50/k04_pv176_residual_enumeration_sft.py
"""
import hashlib
import json
import re

import k04_pv_early_float_triple_sft as base

SOURCE = base.SPOOL
HIST = base.HIST
STAGE = -1560
FREE = (0, 1, 3, 4)


def build():
    spool = SOURCE.read_bytes()
    assert hashlib.sha256(spool).hexdigest() == base.SPOOL_PIN
    payloads = [bytes.fromhex(x.decode()) for x in
                re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(payloads) == len(base.STARTS) == 133
    state = base.mt_words()
    model = base.Basis()
    for idx, (packet, stage) in enumerate(zip(payloads, base.STARTS)):
        if idx == 129:
            continue
        for lane in range(4):
            value = base.untemper(int.from_bytes(packet[lane*4:lane*4+4],
                                                 "little"))
            for j, vector in enumerate(state[stage+lane-base.ORIGIN]):
                model.insert(vector, (value >> j) & 1)
    assert model.rank == 15365
    return model, state


def output_bit(state, index):
    if index >= 26:
        return base.temper(state[STAGE-base.ORIGIN])[index-21]
    return base.temper(state[STAGE+1-base.ORIGIN])[index+6]


def test():
    raw = HIST.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == base.HIST_PIN
    pv = {r["seq"]: round(r["value"] * 1000)
          for r in map(json.loads, raw.splitlines())
          if r["field"] == "PV"}
    assert len(pv) == 112 and pv[176] == 29968
    model, state = build()
    # Four output bits span the complete original printer-unknown
    # quotient of this particular two-word 53-bit source fraction.
    geom = {p: v for p, (v, _) in model.rows.items()}
    independent = []
    for index in range(53):
        value = output_bit(state,index)
        while value:
            pivot = value.bit_length() - 1
            if pivot in geom:
                value ^= geom[pivot]
            else:
                geom[pivot] = value
                independent.append(index)
                break
    assert independent == list(FREE), independent
    answers = []
    for assignment in range(16):
        sub = base.Basis()
        sub.rows = model.rows.copy()
        sub.rank = model.rank
        for j, index in enumerate(FREE):
            sub.insert(output_bit(state,index), (assignment >> j) & 1)
        assert sub.rank == 15369
        v = 0
        for index in range(53):
            b = sub.predict(output_bit(state,index))
            assert b is not None
            v |= b << index
        milli = (12000*(1<<53) + 76000*v + (1<<52)) >> 53
        answers.append((assignment, milli))

    assert {n for n, q in answers if q == 29968} == {1,2,5,6,8,11,12,15}
    assert {q for n, q in answers} == {29968,65612}
    assert all((n&0b1011).bit_count()%2 == 1
               for n, q in answers if q == 29968)
    print("authentic original source PV176 q=29.968, conditional MT stage",STAGE)
    print("all exact source-consistent values",answers)
    print("source metadata reduces 4 independent float bits to 3; exact one-bit parity")

    augmented = base.Basis()
    augmented.rows = model.rows.copy()
    augmented.rank = model.rank
    augmented.insert(output_bit(state,30),0)
    assert augmented.rank == 15366
    # The new source bit alone does not determine any individual target word bit.
    fixed = [sum(augmented.predict(vector) is not None
                 for vector in state[st-base.ORIGIN])
             for st in range(951,955)]
    assert fixed == [0,0,0,0],fixed
    print("original selected target individual bits remain",fixed)
    print("no K04 authentic coupon bytes recovered; six slots remain PASS")


if __name__ == "__main__":
    test()
