"""H17 target-facing node50 seq47/-523 conditional donor and latch falsifier.
Run at repository root: python agents/agent6/k04_node50_rare_donor_latch_sft.py
Original selected printer ACK row129 is excluded from source fitting.
The p951 common-MT source and seq47 stage proposal are hypotheses.
"""
import hashlib
import json
import random
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, get, source, temper, untemper

REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
ANCHORS = {7:-810, 9:-793, 12:-775, 13:-769, 14:-759,
           24:-683,25:-677,41:-568,43:-552,44:-545,
           45:-540,61:-417,63:-397,64:-390,70:-339}
COPIED_ACK = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")

def recorder():
    raw = (ROOT / "resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REC_SHA
    assert raw[:8] == b"TRP2DUMP" and len(raw) == 16 + 88 * 24
    rows = {}
    for i in range(88):
        block = raw[16+i*24:16+(i+1)*24]
        ts,node,event,latch,seq = struct.unpack_from("<IHBBI", block)
        ctrl,aux,crc = struct.unpack_from("<III", block, 12)
        if node == 50:
            assert zlib.crc32(block[:20]) == crc
            rows[seq] = dict(control=ctrl,latch=latch,aux=aux,event=event,ts=ts)
    assert set(rows) == set(range(72))
    return rows

def projection_rank(basis, state):
    homogeneous = Basis()
    homogeneous.rows = {pivot:(equation,0) for pivot,(equation,_) in basis.rows.items()}
    homogeneous.rank = basis.rank
    for stage in range(951,955):
        for equation in get(state,stage):
            homogeneous.insert(equation,0)
    return homogeneous.rank - basis.rank

def main():
    sample = random.Random(20261103)
    saved = sample.getstate()
    three = sample.getrandbits(3)
    sample.setstate(saved)
    assert sample.getrandbits(32) >> 29 == three

    rows = recorder()
    basis, state = source(ROOT / "resources")
    assert basis.rank == 15365

    for seq,stage in ANCHORS.items():
        native = untemper(rows[seq]["control"])
        for bit,equation in enumerate(get(state,stage)):
            basis.insert(equation,(native>>bit)&1)
    assert basis.rank == 15375

    def masked(stage):
        mask = value = 0
        for bit,equation in enumerate(temper(get(state,stage))):
            known = basis.predict(equation)
            if known is not None:
                mask |= 1<<bit
                value |= known<<bit
        return mask,value

    # The only target-sensitive individual negative native donor site is -523
    # under the original printer-only p951 source quotient (Agent8).
    assert masked(-523) == (0,0)
    before = projection_rank(basis,state)
    assert before == 128
    prev_mask,prev_value = masked(-524)
    fixed_high3_mask = prev_mask >> 29
    fixed_high3_value = prev_value >> 29
    assert (fixed_high3_mask,fixed_high3_value) == (3,0)
    latch47 = rows[47]["latch"]
    assert latch47 == 1
    adjacent_latch_possible = ((latch47 ^ fixed_high3_value) & fixed_high3_mask) == 0
    assert not adjacent_latch_possible

    # Deliberately hypothetical donor: no original source maps seq47 to -523.
    native = untemper(rows[47]["control"])
    for bit,equation in enumerate(get(state,-523)):
        basis.insert(equation,(native>>bit)&1)
    assert basis.rank == 15406
    after = projection_rank(basis,state)
    assert after == 127
    first = temper(get(state,951))
    parity = basis.predict(first[15] ^ first[30])
    copied = int.from_bytes(COPIED_ACK[:4],"little")
    copied_parity = ((copied>>15) ^ (copied>>30)) & 1
    assert (parity,copied_parity) == (1,0)

    print(json.dumps({
      "source_rank":15365,
      "rank_after_15_original_controls":15375,
      "hypothetical_seq47_control_stage":-523,
      "seq47_control":f"{rows[47]['control']:08X}",
      "seq47_original_latch":latch47,
      "preceding_stage_high3_fixed_mask":fixed_high3_mask,
      "preceding_stage_high3_fixed_value":fixed_high3_value,
      "adjacent_latch_before_control_writer": "CONTRADICTED",
      "hypothetical_target_parity":parity,
      "untrusted_copied_ack_parity":copied_parity,
      "target_rank_before":before,
      "target_rank_after_hypothetical_donor":after,
      "historically_authenticated_target_bits":0,
      "recovery":"INCOMPLETE",
      "seeded_bitwidth_control":"PASS"
    },sort_keys=True))

if __name__ == "__main__":
    main()
