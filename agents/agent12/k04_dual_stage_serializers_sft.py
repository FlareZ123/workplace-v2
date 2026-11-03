"""H-17 K04 dual independent serializer study. Standard library, read-only.

Run from workplace-v2 root: python agents/agent12/k04_dual_stage_serializers_sft.py
Tests 4x4 row/column, 4-word permutation, independent word reversal on both
retained copied P and transcribed M before reduction C = P XOR M.
No missing original physical coupon fidelity is assumed.
"""
from itertools import permutations, product
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
TARGET_SHA = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
EXPECTED_PAYLOAD = 'A9A9DC5731A5E2AE879C47215C2559D5'
EXPECTED_MASK = '8556C8CB6140A7F9A5123AC7571BEE1C'


def source():
    raw = (ROOT / 'resources/evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    matches = [
        re.search(rb'PAYLOAD=([0-9A-F]{32})', line).group(1).decode()
        for line in raw.splitlines()
        if b'JOB=PS-261003-0417 ' in line
        and b'2026-10-03T18:02:00Z ' in line
        and b'ATTEMPT=2 STATE=ACK CLASS=RECOVER ' in line
    ]
    assert matches == [EXPECTED_PAYLOAD]
    route = json.loads((ROOT/'resources/evidence/recovery-routing.json').read_text())
    mask = route['K04']['masked_component']
    assert mask == EXPECTED_MASK
    commitment = json.loads((ROOT/'resources/acceptance.json').read_text())
    assert commitment['slot_sha256']['K04'] == TARGET_SHA
    return bytes.fromhex(matches[0]), bytes.fromhex(mask)


def layouts(original):
    values = []
    for transpose in (False, True):
        matrix = original if not transpose else bytes(
            original[4 * (i % 4) + i // 4] for i in range(16))
        words = [matrix[i:i+4] for i in range(0,16,4)]
        for ordering in permutations(range(4)):
            for reverse in product((False,True),repeat=4):
                values.append(b''.join(words[ordering[j]][::-1] if reverse[j]
                                       else words[ordering[j]] for j in range(4)))
    assert len(values)==768 and len(set(values))==768
    return values


def xor(a,b):
    return bytes(x^y for x,y in zip(a,b))


def main():
    copied,mask=source()
    ps=layouts(copied)
    ms=layouts(mask)
    alone = {xor(p,mask) for p in ps}
    alone.update(xor(copied,m) for m in ms)
    assert len(alone)==1535
    actual=bytes.fromhex(TARGET_SHA)
    planted_p=ps[123]
    planted_m=ms[345]
    assert planted_p!=copied and planted_m!=mask
    planted=hashlib.sha256(xor(planted_p,planted_m)).digest()
    unique=set()
    hits=0
    planted_hits=0
    for p in ps:
        for m in ms:
            candidate=xor(p,m)
            unique.add(candidate)
            digest=hashlib.sha256(candidate).digest()
            hits+=int(digest==actual)
            planted_hits+=int(digest==planted)
    assert len(unique)==589824
    assert len(unique-alone)==588289
    assert hits==0 and planted_hits==1
    print(json.dumps({
        'source_selector':'PS-261003-0417/RECOVER/ACK2/18:02Z',
        'each_stage_layouts':768,'complete_assignments':len(ps)*len(ms),
        'unique_reduced_components':len(unique),
        'one_sided_union':len(alone),
        'new_beyond_one_sided':len(unique-alone),
        'original_K04_matches':hits,'genuinely_two_stage_planted_positive':planted_hits,
        'selected_original_coupon_authenticated_bits':0,
        'archive_status':'INCOMPLETE'},sort_keys=True))


if __name__=='__main__':
    main()
