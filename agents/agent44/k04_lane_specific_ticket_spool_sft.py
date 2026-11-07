from __future__ import annotations

import csv
import hashlib
import hmac
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'resources' / 'evidence'
SUPPLIER = EVIDENCE / 'h17-supplemental-office-files' / 'supplier-reconciliation-L29.csv'
FLEET = EVIDENCE / 'h17-supplemental-office-files' / 'print-fleet-retirement-note.txt'
SEALS = EVIDENCE / 'maintenance' / 'seal-receipts.jsonl'
SPOOL = EVIDENCE / 'print' / 'spool-reconstruction.log'

SPOOL_RE = re.compile(
    r'^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) '
    r'PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$'
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_supplier() -> list[dict[str, str]]:
    lines = SUPPLIER.read_text(encoding='utf-8').splitlines()
    return list(csv.DictReader(lines[3:]))


def read_spool() -> list[dict]:
    parsed = []
    for line in SPOOL.read_text(encoding='utf-8').splitlines():
        match = SPOOL_RE.match(line)
        if not match:
            continue
        ts, job, attempt, state, job_class, payload, dest = match.groups()
        parsed.append({
            'ts': ts,
            'job': job,
            'suffix': int(job.rsplit('-', 1)[1]),
            'attempt': int(attempt),
            'state': state,
            'class': job_class,
            'payload': bytes.fromhex(payload),
            'dest': dest,
        })
    return parsed


def random_outputs(seed) -> dict[str, bytes]:
    outputs = {}
    rng = random.Random(seed)
    outputs['randbytes'] = rng.randbytes(16)
    for endian in ('big', 'little'):
        rng = random.Random(seed)
        outputs[f'get128_{endian}'] = rng.getrandbits(128).to_bytes(16, endian)
        rng = random.Random(seed)
        words = [rng.getrandbits(32) for _ in range(4)]
        outputs[f'4x32_{endian}'] = b''.join(x.to_bytes(4, endian) for x in words)
        outputs[f'4x32_rev_{endian}'] = b''.join(x.to_bytes(4, endian) for x in reversed(words))
    rng = random.Random(seed)
    outputs['16x8'] = bytes(rng.getrandbits(8) for _ in range(16))
    return outputs


def serial_seed_forms(ptw: int, ps: int, serial: bytes) -> dict[str, object]:
    serial_hex = serial.hex().upper()
    return {
        'raw_bytes': serial,
        'int_be': int.from_bytes(serial, 'big'),
        'int_le': int.from_bytes(serial, 'little'),
        'hex_upper': serial_hex,
        'hex_lower': serial_hex.lower(),
        'sg_upper': 'SG-' + serial_hex,
        'ptw': f'PTW-{ptw}',
        'ps': f'PS-{ps:04d}',
        'serial_ptw': serial_hex + '|PTW-' + str(ptw),
        'serial_ps': serial_hex + '|PS-' + f'{ps:04d}',
        'ptw_serial': 'PTW-' + str(ptw) + '|' + serial_hex,
        'ps_serial': 'PS-' + f'{ps:04d}' + '|' + serial_hex,
    }


def keyed_outputs(ptw: int, ps: int, serial: bytes, row: dict) -> list[tuple[str, bytes]]:
    serial_hex = serial.hex().upper()
    timestamp = row['ts']
    messages = [
        f'SG-{serial_hex}|PS-261003-{ps:04d}|{row["attempt"]}|{row["state"]}|{row["class"]}|{row["dest"]}|{timestamp}'.encode(),
        f'PTW-{ptw}|SG-{serial_hex}|PS-{ps:04d}|{row["class"]}|{row["dest"]}|{row["attempt"]}|{row["state"]}'.encode(),
        serial + ps.to_bytes(2, 'big') + bytes([row['attempt']]) + row['state'].encode() + b'|' + row['class'].encode() + b'|' + row['dest'].encode(),
    ]
    keys = [
        ('serial_raw', serial),
        ('serial_ascii', ('SG-' + serial_hex).encode()),
        ('serial_repeat4', serial * 4),
        ('serial_hash16', hashlib.sha256(serial).digest()[:16]),
    ]
    outputs = []
    for key_name, key in keys:
        for message_index, message in enumerate(messages):
            outputs.append((f'hmac_{key_name}_m{message_index}', hmac.new(key, message, hashlib.sha256).digest()[:16]))
            outputs.append((f'blake2b_{key_name}_m{message_index}', hashlib.blake2b(message, key=key, digest_size=16).digest()))
            outputs.append((f'blake2s_{key_name}_m{message_index}', hashlib.blake2s(message, key=key, digest_size=16).digest()))
    return outputs


def main() -> None:
    supplier = read_supplier()
    fleet_text = FLEET.read_text(encoding='utf-8')
    spool = read_spool()
    seals = [json.loads(line) for line in SEALS.read_text(encoding='utf-8').splitlines()]
    by_job: dict[int, list[dict]] = {}
    for row in spool:
        by_job.setdefault(row['suffix'], []).append(row)

    fleet_jobs = {}
    for match in re.finditer(r'(?m)^PS-261003-(\d{4})\s+(ESC-N|ESC-S)\s+(L-29/[NS])\s+(FA-17|LV-42)\s+([^\s]+)$', fleet_text):
        job_suffix, route, lane_name, account, folio = match.groups()
        fleet_jobs[lane_name] = int(job_suffix)
    tab_index = {}
    for match in re.finditer(r'(?m)^(L-29/[NS])\s+(\d{2})\s+(ST-\d+)\s+', fleet_text):
        lane_name, tab_number, ticket = match.groups()
        tab_index[(lane_name, ticket)] = int(tab_number)
    tab5 = {
        lane_name: next(ticket for (lane, ticket), tab in tab_index.items() if lane == lane_name and tab == 5)
        for lane_name in ('L-29/N', 'L-29/S')
    }
    anchor_offsets = {
        'FA-17': fleet_jobs['L-29/N'] - int(tab5['L-29/N'].split('-')[1]),
        'LV-42': fleet_jobs['L-29/S'] - int(tab5['L-29/S'].split('-')[1]),
    }
    assert anchor_offsets == {'FA-17': 305, 'LV-42': 306}

    predictions = []
    selected_rows = [r for r in supplier if r['run'] == 'R3' and r['posting'] == 'POSTED']
    for ticket in selected_rows:
        suffix = int(ticket['line_ref'].split('-')[1])
        account = ticket['account']
        folio = ticket['folio_or_jacket']
        if account == 'FA-17' and folio in {'H17-POL-17/A3', 'H17-POL-17/A2'}:
            lane_name = 'L-29/N' if folio.endswith('/A3') else None
            lane, offset = ('North L-29/N' if lane_name else 'FA-17 L-28/A2'), anchor_offsets['FA-17']
        elif account == 'LV-42' and folio == 'CS-18/5':
            lane_name = 'L-29/S'
            lane, offset = 'South L-29/S', anchor_offsets['LV-42']
        else:
            continue
        tab_number = tab_index.get((lane_name, ticket['line_ref'])) if lane_name else None
        ps_suffix = suffix + offset
        job_rows = by_job.get(ps_suffix, [])
        same_suffix_rows = by_job.get(suffix + 304, [])
        predictions.append({
            'ticket': ticket['line_ref'],
            'lane': lane,
            'description': ticket['description'],
            'account': account,
            'folio': folio,
            'tab': tab_number,
            'candidate_offset': offset,
            'candidate_ptw': f'PTW-{suffix + 304}',
            'candidate_ps': f'PS-261003-{ps_suffix:04d}',
            'present': bool(job_rows),
            'rows': [f'{r["attempt"]}:{r["state"]}:{r["class"]}/{r["dest"]}' for r in job_rows],
            'same_suffix_ps': f'PS-261003-{suffix + 304:04d}',
            'same_suffix_rows': [f'{r["attempt"]}:{r["state"]}:{r["class"]}/{r["dest"]}' for r in same_suffix_rows],
            'anchor': ticket['line_ref'] in {'ST-112', 'ST-142'},
        })

    predictions.sort(key=lambda p: (
        0 if p['lane'] == 'North L-29/N' else 1 if p['lane'] == 'South L-29/S' else 2,
        p['tab'] if p['tab'] is not None else int(p['ticket'].split('-')[1]),
    ))

    serial_by_permit = {}
    for record in seals:
        serial_by_permit.setdefault(record['permit'], []).append(record['serial'])

    for prediction in predictions:
        prediction['ptw_present'] = len(serial_by_permit.get(prediction['candidate_ptw'], [])) == 1
    ptw_coverage = {}
    for lane in sorted({p['lane'] for p in predictions}):
        lane_rows = [p for p in predictions if p['lane'] == lane]
        ptw_coverage[lane] = {
            'predicted': len(lane_rows),
            'retained_unique_receipts': sum(1 for p in lane_rows if p['ptw_present']),
            'missing': [p['candidate_ptw'] for p in lane_rows if not p['ptw_present']],
        }

    controls = []
    for ticket in selected_rows:
        if ticket['account'] != 'FA-17' or ticket['folio_or_jacket'] not in {'H17-POL-17/A3', 'H17-POL-17/A2'}:
            continue
        st = int(ticket['line_ref'].split('-')[1])
        ptw = st + 304
        serials = serial_by_permit.get(f'PTW-{ptw}', [])
        if len(serials) != 1:
            continue
        ps = ptw + 1
        ack_rows = [r for r in by_job.get(ps, []) if r['state'] == 'ACK']
        if ptw == 416:
            ack_rows = [r for r in ack_rows if r['class'] == 'LABEL']  # withhold selected RECOVER ACK2
        for row in ack_rows:
            controls.append((ptw, ps, bytes.fromhex(serials[0].removeprefix('SG-')), row))

    seed_checks = 0
    mac_checks = 0
    seed_hits = []
    mac_hits = []
    for ptw, ps, serial, row in controls:
        payload = row['payload']
        for seed_name, seed in serial_seed_forms(ptw, ps, serial).items():
            for output_name, output in random_outputs(seed).items():
                seed_checks += 1
                if output == payload:
                    seed_hits.append((ptw, ps, row['class'], seed_name, output_name))
        for output_name, output in keyed_outputs(ptw, ps, serial, row):
            mac_checks += 1
            if output == payload:
                mac_hits.append((ptw, ps, row['class'], output_name))

    result = {
        'source_sha256': {
            str(SUPPLIER.relative_to(ROOT)): sha256(SUPPLIER),
            str(FLEET.relative_to(ROOT)): sha256(FLEET),
            str(SEALS.relative_to(ROOT)): sha256(SEALS),
            str(SPOOL.relative_to(ROOT)): sha256(SPOOL),
        },
        'anchor_offsets_from_fleet_tab05': anchor_offsets,
        'prediction_count': len(predictions),
        'lane_counts': {lane: sum(1 for p in predictions if p['lane'] == lane) for lane in sorted({p['lane'] for p in predictions})},
        'predictions': predictions,
        'ptw_coverage': ptw_coverage,
        'serial_control_count': len(controls),
        'serial_seed_checks': seed_checks,
        'serial_seed_hits': seed_hits,
        'serial_keyed_hash_checks': mac_checks,
        'serial_keyed_hash_hits': mac_hits,
        'selected_ps0417_recover_ack2_withheld': True,
    }
    print(json.dumps(result, indent=2))
    assert len(predictions) == 12
    assert anchor_offsets == {'FA-17': 305, 'LV-42': 306}
    assert len(controls) == 6
    assert ptw_coverage['North L-29/N']['retained_unique_receipts'] == 4
    assert ptw_coverage['South L-29/S']['retained_unique_receipts'] == 0
    assert ptw_coverage['FA-17 L-28/A2']['retained_unique_receipts'] == 2
    assert seed_checks == 576 and not seed_hits
    assert mac_checks == 216 and not mac_hits
    assert all(not (ptw == 416 and row['class'] == 'RECOVER') for ptw, ps, serial, row in controls)


if __name__ == '__main__':
    main()
