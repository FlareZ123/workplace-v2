#!/usr/bin/env python3
"""Bounded role-specific ticket→spool suffix frequency screen for H-17 K04.

Locator test only: it does not authenticate a ticket→job foreign key or
establish media integrity. Run with:
  python agents/agent7/k04_role_offset_frequency.py --evidence-root resources/evidence
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

SPOOL_RE = re.compile(
    r'^(\S+) JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) '
    r'PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$'
)
FLEET_JOB_RE = re.compile(
    r'(?m)^PS-261003-(\d{4})\s+(ESC-N|ESC-S)\s+(L-29/[NS])\s+(FA-17|LV-42)\s+([^\s]+)$'
)
TAB_RE = re.compile(r'(?m)^(L-29/[NS])\s+(\d{2})\s+(ST-\d+)\s+')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence-root', type=Path, required=True)
    args = ap.parse_args()
    root = args.evidence_root
    fleet = root / 'h17-supplemental-office-files' / 'print-fleet-retirement-note.txt'
    supplier = root / 'h17-supplemental-office-files' / 'supplier-reconciliation-L29.csv'
    spool = root / 'print' / 'spool-reconstruction.log'

    fleet_text = fleet.read_text(encoding='utf-8')
    fleet_jobs = {}
    for m in FLEET_JOB_RE.finditer(fleet_text):
        suffix, route, lane, account, folio = m.groups()
        fleet_jobs[lane] = int(suffix)
    tabs = {(lane, int(tab)): ticket for lane, tab, ticket in TAB_RE.findall(fleet_text)}
    north_tab5 = int(tabs[('L-29/N', 5)].split('-')[1])
    south_tab5 = int(tabs[('L-29/S', 5)].split('-')[1])
    watch_0420_line = next((line for line in fleet_text.splitlines()
                            if line.startswith('PS-261003-0420 ')), None)

    supplier_rows = list(csv.DictReader(supplier.read_text(encoding='utf-8').splitlines()[3:]))
    fa17_a2 = sorted({int(r['line_ref'].split('-')[1]) for r in supplier_rows
                      if r['account'] == 'FA-17' and r['folio_or_jacket'] == 'H17-POL-17/A2'
                      and r['run'] == 'R3' and r['posting'] == 'POSTED'})
    # ST-121 is the retained non-anchor South observation documented in the
    # lane-specific screen; it is kept separate from tab05 ST-142.
    south_non_anchor = 121
    assert fa17_a2 == [87, 98], fa17_a2
    assert north_tab5 == 112 and south_tab5 == 142
    assert fleet_jobs['L-29/N'] == 417 and fleet_jobs['L-29/S'] == 448

    by_job: dict[int, list[dict]] = collections.defaultdict(list)
    for line in spool.read_text(encoding='utf-8').splitlines():
        m = SPOOL_RE.match(line)
        if not m:
            continue
        ts, suffix, attempt, state, cls, payload, dest = m.groups()
        by_job[int(suffix)].append({'ts': ts, 'attempt': int(attempt), 'state': state,
                                    'class': cls, 'dest': dest, 'payload': payload})

    def rows_for(suffix: int) -> list[dict]:
        return by_job.get(suffix, [])

    def has_recover_ack(suffix: int, *, attempt: int | None = None,
                        dest: str | None = None) -> bool:
        return any(r['class'] == 'RECOVER' and r['state'] == 'ACK'
                   and (attempt is None or r['attempt'] == attempt)
                   and (dest is None or r['dest'] == dest)
                   for r in rows_for(suffix))

    north_full = []
    south_full = []
    north_tab5_ack2_bench = []
    north_l28_both_recover_ack = []
    south_tab5_recover_ack_desk = []
    south_non_anchor_recover_ack_desk = []

    for off in range(200, 401):
        n_target = north_tab5 + off
        n_holdouts = [x + off for x in fa17_a2]
        if has_recover_ack(n_target, attempt=2, dest='bench'):
            north_tab5_ack2_bench.append(off)
        if all(has_recover_ack(x) for x in n_holdouts):
            north_l28_both_recover_ack.append(off)
        if (has_recover_ack(n_target, attempt=2, dest='bench')
                and all(has_recover_ack(x) for x in n_holdouts)):
            north_full.append({'offset': off, 'tab5_job': n_target,
                               'holdout_jobs': n_holdouts})

        s_target = south_tab5 + off
        s_other = south_non_anchor + off
        if has_recover_ack(s_target, dest='desk'):
            south_tab5_recover_ack_desk.append(off)
        if has_recover_ack(s_other, dest='desk'):
            south_non_anchor_recover_ack_desk.append(off)
        if (has_recover_ack(s_target, dest='desk')
                and has_recover_ack(s_other, dest='desk')):
            south_full.append({'offset': off, 'tab5_job': s_target,
                               'non_anchor_job': s_other})

    def describe(suffix: int) -> list[str]:
        return [f"{r['attempt']}:{r['state']}:{r['class']}/{r['dest']}" for r in rows_for(suffix)]

    result = {
        'scope': 'integer suffix offsets 200..400 inclusive (201 offsets)',
        'source_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (fleet, supplier, spool)},
        'anchors': {'north_tab5_ticket': f'ST-{north_tab5:03d}',
                    'north_registered_job': f'PS-261003-{fleet_jobs["L-29/N"]:04d}',
                    'south_tab5_ticket': f'ST-{south_tab5:03d}',
                    'south_registered_job': f'PS-261003-{fleet_jobs["L-29/S"]:04d}',
                    'fa17_l28_holdouts': [f'ST-{x:03d}' for x in fa17_a2],
                    'south_non_anchor': f'ST-{south_non_anchor:03d}'},
        'north_role_predicate': 'tab05 has RECOVER/ACK attempt 2 to bench AND both L28/A2 holdouts have RECOVER/ACK',
        'north_tab5_recover_ack_attempt2_bench_offsets': north_tab5_ack2_bench,
        'north_alternative_308_job_register_line': watch_0420_line,
        'north_l28_both_recover_ack_offsets': north_l28_both_recover_ack,
        'north_role_match_count': len(north_full),
        'north_role_matches': north_full,
        'south_role_predicate': 'tab05 and non-anchor ST-121 both have RECOVER/ACK to desk',
        'south_tab5_recover_ack_desk_offsets': south_tab5_recover_ack_desk,
        'south_non_anchor_recover_ack_desk_offsets': south_non_anchor_recover_ack_desk,
        'south_role_match_count': len(south_full),
        'south_role_matches': south_full,
        'selected_north_job_rows': describe(fleet_jobs['L-29/N']),
        'north_l28_holdout_job_rows': {f'PS-261003-{x+305:04d}': describe(x+305) for x in fa17_a2},
        'selected_south_job_rows': describe(fleet_jobs['L-29/S']),
        'south_non_anchor_job_rows': describe(south_non_anchor+306),
        'interpretation': 'role-specific locator evidence only; no source-authenticated ticket→job foreign key and no coupon/media bytes',
    }
    print(json.dumps(result, indent=2))
    assert north_tab5_ack2_bench == [305, 308]
    assert watch_0420_line and 'WATCH-SPARE' in watch_0420_line
    assert north_l28_both_recover_ack == [220, 231, 242, 252, 278, 289, 298, 305, 309, 319, 322, 329]
    assert len(north_full) == 1 and north_full[0]['offset'] == 305
    assert south_tab5_recover_ack_desk == [250, 259, 268, 271, 285, 306]
    assert south_non_anchor_recover_ack_desk == [216, 217, 218, 219, 271, 280, 289, 292, 306, 327]
    assert len(south_full) == 2 and [x['offset'] for x in south_full] == [271, 306]


if __name__ == '__main__':
    main()
