"""Conditional K04 first-word parity versus CRC-valid original recorder seq47.

This does not authenticate the recorder's MT output index -523 or reconstruct
the selected ACK. The selected spool row is withheld from source constraints.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
MT_PATH = Path(__file__).resolve().parents[1] / "agent49" / "k04_p951_symbolic_basis.py"
spec = importlib.util.spec_from_file_location("p951_source", MT_PATH)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
forms = mt.words()

spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
recorder = (ROOT / "evidence/recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(recorder).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
packets = [bytes.fromhex(s.decode("ascii")) for s in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
assert len(packets) == len(mt.STARTS) == 133
assert mt.STARTS[129] == 951
assert packets[129] == bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")

seq47 = []
for offset in range(16, len(recorder), 24):
    frame = recorder[offset : offset + 24]
    if len(frame) != 24:
        continue
    stamp, node, event, latch, seq, control, aux, crc = struct.unpack("<IHBBI4sII", frame)
    if node == 50 and seq == 47:
        assert zlib.crc32(frame[:20]) == crc
        assert (stamp, event, latch, aux) == (1791062055, 4, 1, 3075)
        seq47.append(control)
assert seq47 == [bytes.fromhex("98535679")]

native_donor = mt.untemper(int.from_bytes(seq47[0], "little"))
assert native_donor == 0xC7ACBEDA
copied_word = int.from_bytes(packets[129][:4], "little")
copied_parity = ((copied_word >> 30) ^ (copied_word >> 15)) & 1
assert copied_parity == 0

def trial(omit: set[int]):
    source = mt.Basis()
    for row, (packet, pos) in enumerate(zip(packets, mt.STARTS)):
        if row == 129 or row in omit:
            continue
        for lane in range(4):
            native = mt.untemper(int.from_bytes(packet[4 * lane:4 * lane + 4], "little"))
            for bit, eq in enumerate(mt.get(forms, pos + lane)):
                source.insert(eq, (native >> bit) & 1)

    # The K04 tempered word30 XOR word15 equals its native word bit30.
    target_native_bit30 = mt.get(forms, 951)[30]
    assert source.predict(target_native_bit30) is None
    for bit, eq in enumerate(mt.get(forms, -523)):
        source.insert(eq, (native_donor >> bit) & 1)
    return source.rank, source.predict(target_native_bit30)

# The original conditional model and a separate, explicit LABEL-row36 dropout
# both preserve the single target-parity deduction. Dropping the original
# target-ancestry row43 instead destroys it, a negative control.
original_rank, original_p = trial(set())
row36_rank, row36_p = trial({36})
row43_rank, row43_p = trial({43})
assert (original_rank, original_p) == (15396, 1)
assert (row36_rank, row36_p) == (15269, 1)
assert (row43_rank, row43_p) == (15332, None)

print(json.dumps({
    "model": "hypothetical p951 shared MT19937 source and seq47-at-minus523",
    "recorder_seq47_crc_valid": True,
    "original_seq47_native": f"{native_donor:08X}",
    "copied_K04_first_word_parity": copied_parity,
    "hypothetical_source_plus_seq47_first_word_parity": original_p,
    "row36_omitted_first_word_parity": row36_p,
    "row43_omitted_first_word_parity": row43_p,
    "authentic_K04_bits_recovered": 0,
    "historical_seq47_index_authenticated": False
}, indent=2))
