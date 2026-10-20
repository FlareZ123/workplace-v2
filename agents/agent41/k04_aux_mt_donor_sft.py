"""Source-only TRP2 auxiliary-reading donor gate; original selected K04 is withheld."""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import re
import struct

SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
KNOWN_CTRL = (12, 17, 26, 28, 40, 45, 72)
TWIST = 0x9908B0DF


def invert_right(x, shift):
    y = x
    for _ in range(6):
        y = x ^ (y >> shift)
    return y


def invert_left(x, shift, mask):
    y = x
    for _ in range(6):
        y = x ^ ((y << shift) & mask)
    return y & 0xffffffff


def untemper(value):
    value = invert_right(value, 18)
    value = invert_left(value, 15, 0xEFC60000)
    value = invert_left(value, 7, 0x9D2C5680)
    return invert_right(value, 11)


def main(source):
    spool = (source / 'print/spool-reconstruction.log').read_bytes()
    assert sha256(spool).hexdigest() == SPOOL_SHA, 'Unexpected input spool'
    rows = []
    for line in spool.decode('utf-8').splitlines():
        found = re.search(r'PAYLOAD=([0-9A-F]{32})', line)
        if found and not ('2026-10-03T18:02:00Z' in line and 'JOB=PS-261003-0417 ' in line):
            rows.append(bytes.fromhex(found.group(1)))
    assert len(rows) == 132
    recorder = (source / 'recorder/trip-recorder.raw').read_bytes()
    assert recorder[:8] == b'TRP2DUMP'
    version, record_size, count = struct.unpack_from('<HHI', recorder, 8)
    assert (version, record_size, count) == (2, 24, 88)
    records = [struct.unpack_from('<IHBBI4sII', recorder, 16 + 24 * i) for i in range(count)]

    printer = [untemper(int.from_bytes(data[i:i + 4], 'little'))
               for data in rows for i in (0, 4, 8, 12)]
    fingerprints = defaultdict(list)
    for i, a in enumerate(printer):
        for j in range(i + 1, len(printer)):
            if i // 4 == j // 4:
                continue
            delta = a ^ printer[j]
            odd = delta >> 31
            low31 = (((delta ^ (TWIST if odd else 0)) << 1) | odd) & 0x7fffffff
            fingerprints[low31].append((i // 4, j // 4))

    def hits(values):
        return [(i, fingerprints[state & 0x7fffffff]) for i, state in enumerate(values)
                if state & 0x7fffffff in fingerprints]

    control = [untemper(int.from_bytes(r[5], 'little')) for r in records]
    aux_le = [untemper(r[6]) for r in records]
    aux_be = [untemper(int.from_bytes(r[6].to_bytes(4, 'little'), 'big')) for r in records]
    ctrl_hits = hits(control)
    aux_le_hits = hits(aux_le)
    aux_be_hits = hits(aux_be)
    print('Original printer rows (target ACK excluded):', len(rows))
    print('Pairwise original printer predecessors:', len(printer) * (len(printer) - 1) // 2 - len(rows) * 6)
    print('Control low31 donor matches:', [(i, pair[:2]) for i, pair in ctrl_hits])
    print('Auxiliary numeric low31 donor matches:', aux_le_hits)
    print('Auxiliary reversed-byte low31 donor matches:', aux_be_hits)
    assert tuple(i for i, _ in ctrl_hits) == KNOWN_CTRL, 'Control positive witness changed'
    assert not aux_le_hits and not aux_be_hits, 'New auxiliary witness needs investigation'
    print('PASS: original control positive witnesses retained; auxiliary direct-word class excluded.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, default=Path(__file__).resolve().parents[2] / 'resources/evidence')
    main(parser.parse_args().evidence)
