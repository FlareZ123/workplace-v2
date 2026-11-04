"""H-17 read-only, source-pinned nonprinter MT ancestral seal scan.

Uses Agent49's original p951 conditional symbolic basis, withholding selected
printer row129 entirely. Matches are model-conditioned source coincidences, not
an authenticated generator, a reconstructed selected coupon, or a recovered key.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents/agent49'))
from k04_p951_symbolic_basis import Basis, LAST, ORIGIN, get, source, temper

SEAL_SHA = 'c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32'
EXPECTED = [
    ('PTW-405', 'D', 'F6E935B9', 'little', -964, 32),
    ('PTW-412', 'B', '5AD7D397', 'little', -944, 32),
    ('PTW-414', 'C', '645EB28C', 'little', -937, 32),
]


def main():
    raw = (ROOT / 'resources/evidence/maintenance/seal-receipts.jsonl').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SEAL_SHA
    seals = [json.loads(line) for line in raw.splitlines()]
    assert len(seals) == 44
    basis, symbolic = source(ROOT / 'resources')
    assert basis.rank == 15365
    stages = []
    for stage in range(ORIGIN, LAST + 1):
        mask = value = 0
        for bit, equation in enumerate(temper(get(symbolic, stage))):
            prediction = basis.predict(equation)
            if prediction is not None:
                mask |= 1 << bit
                value |= prediction << bit
        if mask.bit_count() >= 24:
            stages.append((stage, mask, value))
    assert len(stages) == 1117
    assert sum(mask == 0xffffffff for _, mask, _ in stages) == 991

    def scan(transform=lambda x: x):
        hits = []
        for record in seals:
            serial = bytes.fromhex(record['serial'].split('-')[-1])
            for endian in ('little', 'big'):
                word = transform(int.from_bytes(serial, endian))
                for stage, mask, predicted in stages:
                    if (word ^ predicted) & mask == 0:
                        hits.append((record['permit'], record['bay'], serial.hex().upper(),
                                     endian, stage, mask.bit_count()))
        return hits

    hits = sorted(scan())
    assert hits == EXPECTED, hits
    assert scan(lambda x: x ^ 0xffffffff) == [], 'complement negative control'
    selected = Basis()
    selected.rows = {pivot: (equation, 0) for pivot, (equation, _) in basis.rows.items()}
    selected.rank = basis.rank
    for stage in range(951, 955):
        for eq in get(symbolic, stage):
            selected.insert(eq, 0)
    assert selected.rank - basis.rank == 128
    print(json.dumps({'original_seals': 44, 'original_printer_packets': 132,
                      'source_rank': basis.rank, 'source_eligible_stages': len(stages),
                      'source_fullword_stages': 991, 'original_matches': hits,
                      'complement_negative_control': 'PASS',
                      'selected_K04_free_dimensions': 128}, indent=2))


if __name__ == '__main__':
    main()
