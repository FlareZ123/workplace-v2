"""Test source-indexed HST PV + ordinary-printer 624-word interleaved MT completion."""
import hashlib
import itertools
import json
import struct
import re
import random
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'resources' / 'evidence'
MAG=0x9908B0DF


def untemper(x):
    x ^= x >> 18
    x ^= (x << 15) & 0xEFC60000
    original=x
    for _ in range(6): x = original ^ ((x << 7) & 0x9D2C5680)
    original=x
    for _ in range(6): x = original ^ (x >> 11)
    return x & 0xffffffff


def temper(v):
    v ^= v >> 11
    v ^= (v << 7) & 0x9D2C5680
    v ^= (v << 15) & 0xEFC60000
    v ^= v >> 18
    return v & 0xffffffff


def continuation(state, n=1024):
    native = list(state)
    for t in range(n):
        a,b,c=native[t],native[t+1],native[t+397]
        m=(a&0x80000000)|(b&0x7fffffff)
        native.append(c ^ (m >> 1) ^ (MAG if b & 1 else 0))
    return native[624:]


def pvword(v,codec):
    if codec=='float32':return struct.unpack('<I',struct.pack('<f',v))[0]
    if codec=='milli':return round(1000*v)
    if codec=='round':return round(v)
    raise AssertionError(codec)


def main():
    raw = (EVIDENCE / 'print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
    spool = [line for line in raw.decode('ascii').splitlines() if line.startswith('2026-')]
    assert len(spool) == 133
    assert all('ATTEMPT=1 STATE=ACK' in line for line in spool[:128])
    assert '0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in spool[129]
    packets = [bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})', line).group(1)) for line in spool]
    historian_bytes = (EVIDENCE / 'telemetry/freeze-export.jsonl').read_bytes()
    assert hashlib.sha256(historian_bytes).hexdigest() == '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
    pv = [json.loads(line) for line in historian_bytes.splitlines() if line.strip()]
    pv = [r for r in pv if r['field'] == 'PV']
    assert len(pv) == 112
    assert {r['seq'] for r in pv} == set(range(100, 212))
    routing_bytes = (EVIDENCE / 'recovery-routing.json').read_bytes()
    acceptance_bytes = (ROOT / 'resources/acceptance.json').read_bytes()
    assert hashlib.sha256(routing_bytes).hexdigest() == 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
    assert hashlib.sha256(acceptance_bytes).hexdigest() == '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'
    route=json.loads(routing_bytes)
    acceptance=json.loads(acceptance_bytes)
    expected=acceptance['slot_sha256']['K04']
    assert expected == '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
    mask=bytes.fromhex(route['K04']['masked_component'])
    assert mask.hex().upper() == '8556C8CB6140A7F9A5123AC7571BEE1C'
    record_pv={row['seq']:row['value'] for row in pv}
    all_pv={'seq': [record_pv[i] for i in range(100,212)],
            'record': [r['value'] for r in pv],
            'acquisition': [r['value'] for r in sorted(pv,key=lambda r:(r['ts'],r['seq']))]}
    assert len({r['seq'] for r in pv})==112
    controls=[packets[j] for j in (128,130,131,132)]
    # Independent true-MT stream, split into a five-word HST/print interleave,
    # is reassembled by the same float32 codec as the historical test.
    generator = random.Random(683255)
    synthetic = [generator.getrandbits(32) for _ in range(624 + 20)]
    synthetic_pv = []
    synthetic_packets = []
    cursor = 0
    for row in range(128):
        batch = synthetic[cursor:cursor + (5 if row < 112 else 4)]
        cursor += len(batch)
        if row < 112:
            pv_native = batch[2]
            pv_value = struct.unpack('<f', pv_native.to_bytes(4, 'little'))[0]
            assert math.isfinite(pv_value) and pvword(pv_value, 'float32') == pv_native
            synthetic_pv.append(pv_value)
            batch = batch[:2] + batch[3:]
        synthetic_packets.append(b''.join(w.to_bytes(4, 'little') for w in batch))
    assert cursor == 624
    state = []
    for row in range(128):
        batch = [int.from_bytes(synthetic_packets[row][j:j + 4], 'little')
                 for j in range(0, 16, 4)]
        if row < 112:
            batch.insert(2, pvword(synthetic_pv[row], 'float32'))
        state.extend(batch)
    assert state == synthetic[:624]
    predicted = [temper(w) for w in continuation([untemper(w) for w in state], 20)]
    assert predicted == synthetic[624:]
    synthetic_coupon = b''.join(w.to_bytes(4, 'little') for w in predicted[9:13])
    planted = hashlib.sha256(bytes(x ^ y for x,y in zip(synthetic_coupon, mask))).digest()
    assert sum(hashlib.sha256(bytes(x ^ y for x,y in zip(
        b''.join(w.to_bytes(4, 'little') for w in predicted[i:i+4]), mask))).digest() == planted
        for i in range(17)) == 1
    tested=0; hits=[]; full_controls=[]
    for (pvorder,pvv),(codec,endian,reverse,position) in itertools.product(all_pv.items(),itertools.product(('float32','milli','round'),('little','big'),(False,True),range(5))):
        words=[]
        for row in range(128):
            sample=[int.from_bytes(packets[row][i*4:i*4+4],endian) for i in range(4)]
            if reverse:sample.reverse()
            if row<112:sample.insert(position,pvword(pvv[row],codec))
            words.extend(sample)
        assert len(words)==624
        future=[temper(x) for x in continuation([untemper(w) for w in words])]
        # Same printer-word presentation, with 4 possible whole-packet views for target.
        control_matches=[]
        for start in range(len(future)-3):
            window=future[start:start+4]
            raw4=b''.join(x.to_bytes(4,endian) for x in (window[::-1] if reverse else window))
            for ctrl in controls:
                if raw4==ctrl: control_matches.append((controls.index(ctrl),start))
            for byteorder in ('little','big'):
                for wordreverse in (False,True):
                    buf=b''.join(w.to_bytes(4,byteorder) for w in (window[::-1] if wordreverse else window))
                    component=bytes(x^y for x,y in zip(buf,mask))
                    tested+=1
                    if hashlib.sha256(component).hexdigest()==expected:
                        hits.append((pvorder,codec,endian,reverse,position,start,byteorder,wordreverse,component.hex().upper()))
        if control_matches:full_controls.append(((pvorder,codec,endian,reverse,position),control_matches))
    assert tested == 180 * 1021 * 4
    assert not hits and not full_controls
    print(json.dumps({'models':180, 'complete_original_K04_commitment_checks':tested,
                      'original_K04_hits':hits, 'original_late_source_holdouts':full_controls,
                      'true_MT_interleaved_624_word_predictor': 'PASS',
                      'planted_complete_coupon_recovery': 'PASS',
                      'selected_disputed_ACK2_used':False}, indent=2))

if __name__=='__main__':main()
