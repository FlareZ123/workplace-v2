"""H-17 K04: source-pinned one-pass legacy code-page copy fault SFT (read-only).

Set H17_ZIP to the original h17-archive-dump.zip path, then run this Python
script. A synthetic >4byte physical-copy recoding positive tests the reducer.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import codecs
import json
import os
import re

SOURCE_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
TARGET = bytes.fromhex('930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0')
CODECS = (
    'latin-1', 'ascii', 'utf-8', 'utf-8-sig', 'utf-16le', 'utf-16be',
    'utf-32le', 'utf-32be', 'cp1250', 'cp1251', 'cp1252', 'cp1253',
    'cp1254', 'cp1257', 'cp437', 'cp720', 'cp737', 'cp775', 'cp850',
    'cp852', 'cp855', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862',
    'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp037',
    'cp500', 'cp1026', 'cp1140', 'mac_roman', 'iso8859_2', 'iso8859_15',
)


def inputs(zip_path):
    with ZipFile(zip_path) as zf:
        spool = zf.read('evidence/print/spool-reconstruction.log')
        route = json.loads(zf.read('evidence/recovery-routing.json'))
    assert sha256(spool).hexdigest() == SOURCE_SHA
    rows = [line for line in spool.splitlines()
            if line.startswith(b'2026-10-03T18:02:00Z')
            and b'JOB=PS-261003-0417' in line and b'ATTEMPT=2' in line
            and b'STATE=ACK' in line and b'CLASS=RECOVER' in line]
    assert len(rows) == 1
    copied = bytes.fromhex(re.search(rb'PAYLOAD=([A-F0-9]{32})', rows[0]).group(1).decode())
    assert copied.hex().upper() == 'A9A9DC5731A5E2AE879C47215C2559D5'
    return copied, bytes.fromhex(route['K04']['masked_component'])


def recode(original, source, destination):
    try:
        output = original.decode(source, errors='strict').encode(destination, errors='strict')
    except (UnicodeError, LookupError):
        return None
    return output if len(output) == 16 else None


def main():
    copied, mask = inputs(Path(os.environ.get('H17_ZIP', 'h17-archive-dump.zip')))
    codepages = tuple(dict.fromkeys(codecs.lookup(x).name for x in CODECS))
    survivors = {}
    hits = []
    valid = 0
    for source in codepages:
        for destination in codepages:
            coupon = recode(copied, source, destination)
            if coupon is None:
                continue
            valid += 1
            survivors.setdefault(coupon, []).append((source, destination))
            component = bytes(x ^ y for x, y in zip(coupon, mask))
            if sha256(component).digest() == TARGET:
                hits.append((source, destination, component.hex().upper()))
    planted_coupon = recode(copied, 'latin-1', 'cp500')
    assert planted_coupon is not None
    assert sum(a != b for a, b in zip(planted_coupon, copied)) == 16
    planted_digest = sha256(bytes(a ^ b for a, b in zip(planted_coupon, mask))).digest()
    planted_matches = [(a, b) for a in codepages for b in codepages
                       if (v := recode(copied, a, b)) is not None and
                       sha256(bytes(x ^ y for x, y in zip(v, mask))).digest() == planted_digest]
    mask_views = {
        v for a in codepages for b in codepages
        if (v := recode(mask, a, b)) is not None
    }
    assert len(mask_views) == 9
    combined = {
        bytes(a ^ b for a, b in zip(p, m))
        for p in survivors for m in mask_views
    }
    assert len(combined) == 99
    joint_hits = [c.hex().upper() for c in combined if sha256(c).digest() == TARGET]
    assert len(codepages) == 39 and len(survivors) == 11 and valid == 64
    assert planted_matches and not hits and not joint_hits
    print('codepage_two_stage_mask_options', len(mask_views),
          'distinct_joint_components', len(combined),
          'original_joint_K04_hits', len(joint_hits))
    print('source_pin PASS')
    print('codec_pairs', len(codepages) ** 2, 'size_preserving', valid,
          'distinct_coupons', len(survivors), 'original_K04_hits', len(hits))
    print('synthetic_positive PASS', len(planted_matches), 'equal presentations')


if __name__ == '__main__':
    main()
