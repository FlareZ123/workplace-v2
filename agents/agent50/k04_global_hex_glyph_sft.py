"""Global hex-glyph copy-error H17 K04 complete candidate pilot.

A codebook recoding of up to three *distinct observed hexadecimal characters*
can change numerous positions, unlike a <=3-byte damage model. Test one
transcribed source or both under the same hypothesized recoding. The retained
print spool is explicitly not media-integrity-authenticated, and the route
mask is a transcription. No source directly attests an OCR/glyph recoding.
"""
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2] / 'resources'
EXPECTED_SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
HEX = '0123456789ABCDEF'


def main():
    raw = (ROOT / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SPOOL_SHA
    selected = [line for line in raw.decode('ascii').splitlines()
                if 'JOB=PS-261003-0417 ' in line and 'ATTEMPT=2 ' in line
                and 'STATE=ACK ' in line and 'CLASS=RECOVER ' in line]
    assert len(selected) == 1
    payload_hex = selected[0].split('PAYLOAD=')[1].split()[0]
    assert payload_hex == 'A9A9DC5731A5E2AE879C47215C2559D5'
    route = json.loads((ROOT / 'evidence/recovery-routing.json').read_text())
    acceptance = json.loads((ROOT / 'acceptance.json').read_text())
    mask_hex = route['K04']['masked_component'].upper()
    target = bytes.fromhex(acceptance['slot_sha256']['K04'])
    assert len(payload_hex) == len(mask_hex) == 32 and len(target) == 32

    def get_component(trans, side):
        ph = payload_hex.translate(trans) if side in ('payload','both') else payload_hex
        mh = mask_hex.translate(trans) if side in ('mask','both') else mask_hex
        return bytes(a ^ b for a,b in zip(bytes.fromhex(ph),bytes.fromhex(mh)))

    synthetic_translation = str.maketrans({'9':'B','A':'4'})
    expected_synthetic = {side:hashlib.sha256(get_component(synthetic_translation,side)).digest()
                          for side in ('payload','mask','both')}
    synthetic_seen = {side:False for side in expected_synthetic}
    counts = {}
    hits = []
    t0 = perf_counter()
    for side in ('payload','mask','both'):
        digit_pool = ''.join(sorted(set(payload_hex if side=='payload' else
                                        mask_hex if side=='mask' else HEX)))
        for n in (1,2,3):
            count = 0
            for old in combinations(digit_pool,n):
                options = [tuple(x for x in HEX if x!=char) for char in old]
                for new in product(*options):
                    trans = str.maketrans(dict(zip(old,new)))
                    component = get_component(trans,side)
                    digest = hashlib.sha256(component).digest()
                    count += 1
                    if digest == target:
                        hits.append([side,old,new,component.hex().upper()])
                    if n==2 and digest == expected_synthetic[side]:
                        assert old == ('9','A') and new == ('B','4')
                        synthetic_seen[side] = True
            counts[f'{side}-{n}'] = count
    assert all(synthetic_seen.values())
    assert sum(counts.values()) == 4234245
    print(json.dumps({
        'source_sha256':EXPECTED_SPOOL_SHA,
        'source_model':'up to three global digit replacements (single side or both)',
        'candidate_assignments_by_side_and_glyph_count':counts,
        'total_complete_candidate_assignments':sum(counts.values()),
        'synthetic_two_glyph_positive_for_all_three_stages':synthetic_seen,
        'original_K04_slot_commitment_matches':hits,
        'runtime_seconds':round(perf_counter()-t0,3)},indent=2))


if __name__=='__main__':
    main()
