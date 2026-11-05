"""Source-anchored three-buffer bitwise collision reconstruction for H-17 K04.

Run from an archive checkout or provide H17_RESOURCE_ROOT to the extracted ZIP root.
Historical source is read-only. Original commitments remain unchanged.
"""
import hashlib
import itertools
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get('H17_RESOURCE_ROOT', Path(__file__).resolve().parents[2] / 'resources'))
SPOOL = ROOT / 'evidence/print/spool-reconstruction.log'
ROUTE = ROOT / 'evidence/recovery-routing.json'
ACCEPT = ROOT / 'acceptance.json'
EXPECTED_SPOOL = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
FULL = (1 << 128) - 1


def orient(data: bytes, layout: int) -> bytes:
    if layout == 0:
        return data
    if layout == 1:
        return data[::-1]
    if layout == 2:
        return b''.join(data[i:i + 4] for i in (12, 8, 4, 0))
    return b''.join(data[i:i + 4][::-1] for i in (0, 4, 8, 12))


def parse_spool(path: Path) -> list[dict[str, str]]:
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SPOOL
    result = []
    for line in raw.decode('ascii').splitlines():
        if line.startswith('#'):
            continue
        tokens = line.split()
        fields = dict(token.split('=', 1) for token in tokens[1:])
        fields['UTC'] = tokens[0]
        result.append(fields)
    return result


def pick(rows: list[dict[str, str]], job: str, attempt: str, klass: str, state: str) -> bytes:
    matches = [row for row in rows if row['JOB'] == job and row['ATTEMPT'] == attempt
               and row['CLASS'] == klass and row['STATE'] == state]
    assert len(matches) == 1
    return bytes.fromhex(matches[0]['PAYLOAD'])


def bool_gates(a: bytes, b: bytes, c: bytes) -> list[int]:
    x, y, z = (int.from_bytes(t, 'big') for t in (a, b, c))
    basis = []
    for pattern in range(8):
        mask = FULL
        for bit, input_word in enumerate((x, y, z)):
            mask &= input_word if (pattern >> bit) & 1 else FULL ^ input_word
        basis.append(mask)
    values = [0] * 256
    for table in range(1, 256):
        lowest = table & -table
        values[table] = values[table - lowest] | basis[lowest.bit_length() - 1]
    return values


def main() -> None:
    rows = parse_spool(SPOOL)
    collision = [r for r in rows if r['JOB'] == 'PS-261003-0417' and r['ATTEMPT'] == '1']
    control = [r for r in rows if r['JOB'] == 'PS-261003-0420' and r['ATTEMPT'] == '2']
    assert len(collision) == 2 and {r['CLASS'] for r in collision} == {'LABEL', 'RECOVER'}
    assert len(control) == 1 and control[0]['STATE'] == 'ACK'
    job = 'PS-261003-0417'
    inputs = (pick(rows, job, '1', 'LABEL', 'ACK'),
              pick(rows, job, '1', 'RECOVER', 'REQUESTED'),
              pick(rows, job, '2', 'RECOVER', 'ACK'))
    route = json.loads(ROUTE.read_text(encoding='utf-8'))
    target = json.loads(ACCEPT.read_text(encoding='utf-8'))['slot_sha256']['K04']
    assert route['K04']['source'] == 'escrow coupon / logical printer route ESC-N'
    mask = bytes.fromhex(route['K04']['masked_component'])
    assert len(mask) == 16
    count = 0
    unique = set()
    hits = []
    planted_gate = 0x96  # XOR of the three source bits
    planted_layouts = (0, 2, 3, 1)
    pl_inputs = (orient(x, o) for x, o in zip(inputs, planted_layouts[:3]))
    planted_raw = orient(bool_gates(*pl_inputs)[planted_gate].to_bytes(16, 'big'), planted_layouts[3])
    planted_component = bytes(x ^ y for x, y in zip(planted_raw, mask))
    planted_target = hashlib.sha256(planted_component).digest()
    positives = 0
    for a_layout, b_layout, c_layout in itertools.product(range(4), repeat=3):
        vals = bool_gates(orient(inputs[0], a_layout), orient(inputs[1], b_layout),
                          orient(inputs[2], c_layout))
        for truth_table, value in enumerate(vals):
            if value in (0, FULL):
                continue
            packet = value.to_bytes(16, 'big')
            for output_layout in range(4):
                coupon = orient(packet, output_layout)
                component = bytes(x ^ y for x, y in zip(coupon, mask))
                digest = hashlib.sha256(component).digest()
                if digest == planted_target:
                    positives += 1
                if digest.hex() == target:
                    hits.append((a_layout, b_layout, c_layout, output_layout,
                                 truth_table, coupon.hex().upper(), component.hex().upper()))
                unique.add(component)
                count += 1
    assert count == 65024 and len(unique) == 14456
    assert positives >= 1
    print(f'collision_keys=2 unaffected_0420_ack2=1 candidates={count} distinct={len(unique)}')
    print(f'planted_full_component_hits={positives} original_K04_hits={len(hits)}')
    for hit in hits:
        print('K04_CANDIDATE', hit)


if __name__ == '__main__':
    main()
