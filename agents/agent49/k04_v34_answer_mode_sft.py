"""K04 original-source exact ITU V.34 answer-mode scrambler test.

The V.34 answer-mode polynomial is 1 + x^-5 + x^-23. N22's fax-machine
remark is an informal analogy, not a documented ESC-N modem specification.
Four exhaustive branches, original unchanged SHA256 commitment, and a
planted full-hash positive. A single invocation may select one branch to
avoid terminal session timeouts. Python standard library only.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if (ROOT / 'resources/evidence').is_dir():
    ROOT = ROOT / 'resources'
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
EXPECT_PAYLOAD = 'A9A9DC5731A5E2AE879C47215C2559D5'
EXPECT_MASK = '8556C8CB6140A7F9A5123AC7571BEE1C'
EXPECT_COMMIT = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
STATES = 1 << 23


def transform(data: bytes, state: int, msb: bool, direction: str) -> bytes:
    order = tuple(range(7, -1, -1)) if msb else tuple(range(8))
    inp = [(b >> k) & 1 for b in data for k in order]
    prior = [(state >> i) & 1 for i in range(23)]
    out = []
    for n, bit in enumerate(inp):
        trail = inp if direction == 'descramble' else out

        def delayed(d):
            t = n - d
            return trail[t] if t >= 0 else prior[t + 23]

        out.append(bit ^ delayed(5) ^ delayed(23))
    result = bytearray(len(data))
    for i, bit in enumerate(out):
        result[i // 8] |= bit << (7 - i % 8 if msb else i % 8)
    return bytes(result)


def basis(data: bytes, msb: bool, direction: str):
    zero = transform(data, 0, msb, direction)
    deltas = [
        bytes(a ^ b for a, b in zip(zero, transform(data, 1 << i, msb, direction)))
        for i in range(23)
    ]
    for state in (0, 1, 2, 3, 0x5A3C12, 0x123456, STATES - 1):
        reconstructed = bytearray(zero)
        for i in range(23):
            if (state >> i) & 1:
                for j in range(16):
                    reconstructed[j] ^= deltas[i][j]
        assert bytes(reconstructed) == transform(data, state, msb, direction)
    return zero, deltas


def search(data, mask, target, msb, direction):
    zero, deltas = basis(data, msb, direction)
    comp = bytearray(a ^ b for a, b in zip(zero, mask))
    old = 0
    hits = []
    t = time.perf_counter()
    for n in range(STATES):
        gray = n ^ (n >> 1)
        if n:
            changed = gray ^ old
            i = (changed & -changed).bit_length() - 1
            for j, value in enumerate(deltas[i]):
                comp[j] ^= value
        old = gray
        if hashlib.sha256(comp).digest() == target:
            hits.append((gray, comp.hex().upper()))
    return hits, time.perf_counter() - t


def main():
    spool = (ROOT / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    rows = [r for r in spool.decode().splitlines()
            if 'JOB=PS-261003-0417' in r and 'ATTEMPT=2' in r
            and 'STATE=ACK' in r and 'CLASS=RECOVER' in r]
    assert len(rows) == 1 and '2026-10-03T18:02:00Z' in rows[0]
    payload = bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})', rows[0]).group(1))
    routing = json.loads((ROOT / 'evidence/recovery-routing.json').read_text())
    acceptance = json.loads((ROOT / 'acceptance.json').read_text())
    mask = bytes.fromhex(routing['K04']['masked_component'])
    target = bytes.fromhex(acceptance['slot_sha256']['K04'])
    assert payload.hex().upper() == EXPECT_PAYLOAD
    assert mask.hex().upper() == EXPECT_MASK
    assert target.hex() == EXPECT_COMMIT
    ctrl = bytes.fromhex('0123456789ABCDEF1032547698BADCFE')
    state = 0x5A3C12
    for msb in (True, False):
        enc = transform(ctrl, state, msb, 'scramble')
        assert transform(enc, state, msb, 'descramble') == ctrl
        assert transform(transform(ctrl, state, msb, 'descramble'), state, msb, 'scramble') == ctrl
    planted_mask = bytes.fromhex('00112233445566778899AABBCCDDEEFF')
    planted = bytes(a ^ b for a, b in zip(ctrl, planted_mask))
    cipher = transform(ctrl, state, True, 'scramble')
    if len(sys.argv) == 1 or sys.argv[1] == 'synthetic':
        hits, seconds = search(cipher, planted_mask, hashlib.sha256(planted).digest(),
                               True, 'descramble')
        assert hits == [(state, planted.hex().upper())], hits
        print('SYNTHETIC_FULL_POSITIVE_PASS state=0x5A3C12 unique=1 sec=%.3f' % seconds,
              flush=True)
        if len(sys.argv) > 1:
            return 0
    total = 0
    count = 0
    for msb, direction in ((True, 'descramble'), (False, 'descramble'),
                           (True, 'scramble'), (False, 'scramble')):
        branch = ('msb' if msb else 'lsb') + '-' + direction
        if len(sys.argv) > 1 and sys.argv[1] != branch:
            continue
        hits, seconds = search(payload, mask, target, msb, direction)
        print('ORIGINAL %s checked=%d hits=%s sec=%.3f'
              % (branch, STATES, hits, seconds), flush=True)
        count += STATES
        total += len(hits)
    print('COMPLETE checked=%d original_hits=%d' % (count, total), flush=True)
    return 0 if total == 0 else 2


if __name__ == '__main__':
    sys.exit(main())
