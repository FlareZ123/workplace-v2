#!/usr/bin/env python3
"""H-17 K04/K08 missing-source intake; implements only the route-sheet rules."""
from pathlib import Path
import hashlib
import hmac
import re
import argparse
import sys

K04_MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
K08_NONCE = bytes.fromhex('5F933DA6A1BD03C32DA5CBC25344F497')
K04_COMMIT = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
K08_COMMIT = '285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747'
K04_JOB = 'PS-261003-0417'


def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9\s]', ' ', s.lower())).strip()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def print_rows(p):
    """Return matching records with source provenance preserved."""
    try:
        lines = p.read_text(errors='ignore').splitlines()
    except Exception:
        return []
    out = []
    for line_no, line in enumerate(lines, 1):
        if f'JOB={K04_JOB}' not in line or 'PAYLOAD=' not in line:
            continue
        tokens = line.split()
        timestamp = tokens[0] if tokens and re.match(r'^\d{4}-\d\d-\d\dT', tokens[0]) else ''
        f = {k: v for k, v in (tok.split('=', 1) for tok in tokens if '=' in tok)}
        try:
            attempt = int(f['ATTEMPT'])
        except (KeyError, ValueError):
            continue
        payload = f.get('PAYLOAD', '').upper()
        if not re.fullmatch(r'[0-9A-F]{32}', payload):
            continue
        out.append({
            'path': str(p),
            'line': line_no,
            'timestamp': timestamp,
            'job': f.get('JOB', ''),
            'class': f.get('CLASS', ''),
            'dest': f.get('DEST', ''),
            'attempt': attempt,
            'state': f.get('STATE', f.get('STATUS', '')),
            'payload': payload,
        })
    return out


def select_k04_ack(rows):
    """Select a unique highest-attempt ACK or fail closed on ambiguity."""
    acks = [r for r in rows if r['state'] == 'ACK']
    if not acks:
        raise LookupError('no ACK rows for the exact K04 job')
    highest = max(r['attempt'] for r in acks)
    top = [r for r in acks if r['attempt'] == highest]
    nonrecover = [r for r in top if r['class'] != 'RECOVER']
    if nonrecover:
        details = '; '.join(
            f"{r['path']}:{r['line']} {r['timestamp']} class={r['class']!r} dest={r['dest']!r} payload={r['payload']}"
            for r in nonrecover
        )
        raise ValueError(f'highest ACK attempt {highest} contains non-RECOVER row(s): {details}')
    payloads = {r['payload'] for r in top}
    if len(payloads) != 1:
        details = '; '.join(
            f"{r['path']}:{r['line']} {r['timestamp']} class={r['class']} dest={r['dest']} payload={r['payload']}"
            for r in top
        )
        raise ValueError(f'conflicting payloads at highest ACK attempt {highest}: {details}')
    # Deterministic tie handling for identical duplicate rows; retain every source in output.
    selected = max(top, key=lambda r: (r['timestamp'], r['path'], r['line']))
    return selected, top, acks


def k04(root):
    rows = []
    for p in root.rglob('*'):
        if p.is_file() and ('0417' in p.name.upper() or p.name.lower() in {
            'spool-reconstruction.log', 'queue.log', 'queue.journal', 'queue-export.txt'
        }):
            rows.extend(print_rows(p))
    acks = [r for r in rows if r['state'] == 'ACK']
    print('K04 carriers:', len(rows), 'ACKs:', len(acks))
    if not acks:
        print('K04: no ACK rows found')
        return
    try:
        selected, top, _ = select_k04_ack(rows)
    except (LookupError, ValueError) as exc:
        print('K04 FAIL-CLOSED:', exc)
        raise SystemExit(2)
    print(f"K04 highest ACK attempt {selected['attempt']}: {len(top)} row(s), 1 distinct payload")
    for r in top:
        print('K04 source:', r['path'], 'line', r['line'], 'timestamp', r['timestamp'],
              'class', r['class'], 'dest', r['dest'], 'attempt', r['attempt'], 'payload', r['payload'])
    payload = bytes.fromhex(selected['payload'])
    c = bytes(a ^ b for a, b in zip(payload, K04_MASK))
    print('K04 component', c.hex().upper(), 'commit', sha(c), 'match', sha(c) == K04_COMMIT)


def k08(root):
    hits = []
    files = 0
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        low = str(p).lower()
        if not any(x in low for x in ('wn-14', 'desk', 'caption', 'galley', 'noticeboard', 'crew')):
            continue
        try:
            words = re.findall(r'[a-z0-9]+', p.read_text(errors='ignore').lower())
        except Exception:
            continue
        files += 1
        for i in range(len(words)):
            s = ''
            for n in range(1, min(64, len(words) - i) + 1):
                s = words[i] if n == 1 else s + ' ' + words[i + n - 1]
                h = hmac.new(K08_NONCE, s.encode(), hashlib.sha256).digest()[:16]
                if sha(h) == K08_COMMIT:
                    hits.append((p, s))
    print('K08 text carriers:', files, 'contiguous commitment hits:', len(hits))
    for p, s in hits:
        print(p, repr(s))


def main(argv=None):
    ap = argparse.ArgumentParser(description='H-17 K04/K08 missing-source intake; implements only the route-sheet rules.')
    ap.add_argument('root', type=Path)
    args = ap.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        ap.error('root must be a directory')
    k04(root)
    k08(root)
    return 0


if __name__ == '__main__':
    sys.exit(main())
