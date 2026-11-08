"""Single-file test: reconstruct hypothetical REC8 segments from AX transfer CRC16s.

The eight transfer checkpoints are *opaque 2-byte fields for 1-MiB chunks*, not
attested component CRCs. This explores a complete alternative cross-slot model.
No original files or candidate.json are modified. Pure Python 3 stdlib.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if not (ROOT / 'evidence').is_dir():
    ROOT = ROOT.parent.parent
EVIDENCE = ROOT / 'evidence' if (ROOT / 'evidence').is_dir() else ROOT / 'resources' / 'evidence'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
KNOWN = {
    'K01': '049AAB2E1CDE7A82CD7C60234303C91A',
    'K02': '0D7E3AB56FB75DA3EB0E2E06786D239E',
    'K03': '1384AF96E25D6ADA666209CB55E062FA',
    'K05': 'FF8B78200A56E8586DCDA00EF01E4572',
    'K06': '5DBF40EE52FAAED9A536D3326CF0D95A',
    'K07': '93495F5E425AB8E592123DABAEB68545',
}


def crc16(buf: bytes, poly: int, init: int, xorout: int, reflected: bool) -> int:
    crc = init
    for byte in buf:
        if reflected:
            crc ^= byte
            for _ in range(8):
                crc = ((crc >> 1) ^ (poly if crc & 1 else 0)) & 0xffff
        else:
            crc ^= byte << 8
            for _ in range(8):
                crc = (((crc << 1) & 0xffff) ^ (poly if crc & 0x8000 else 0))
    return crc ^ xorout


CRC_SPECS = {
    'CCITT_FALSE': (0x1021, 0xffff, 0, False, 0x29b1),
    'XMODEM': (0x1021, 0, 0, False, 0x31c3),
    'X25': (0x8408, 0xffff, 0xffff, True, 0x906e),
    'KERMIT': (0x8408, 0, 0, True, 0x2189),
    'ARC': (0xa001, 0, 0, True, 0xbb3d),
    'MODBUS': (0xa001, 0xffff, 0, True, 0x4b37),
    'DNP': (0xa6bc, 0, 0xffff, True, 0xea82),
}


def prefixes(transfer: str, seq: int, attempt: int):
    return {
        'none': b'',
        'seq_u8': bytes([seq]),
        'seq_u16_be': seq.to_bytes(2, 'big'),
        'seq_u16_le': seq.to_bytes(2, 'little'),
        'seq_dec': str(seq).encode(),
        'transfer_seq': f'{transfer}:{seq}'.encode(),
        'seq_attempt': f'{seq}:{attempt}'.encode(),
        'transfer_seq_attempt': f'{transfer}:{seq}:{attempt}'.encode(),
    }


def main() -> None:
    for name, (poly, init, xout, reflected, check) in CRC_SPECS.items():
        assert crc16(b'123456789', poly, init, xout, reflected) == check, name
    transfers: dict[str, dict[int, dict[int, int]]] = defaultdict(lambda: defaultdict(dict))
    source = (EVIDENCE / 'transfers' / 'transfer-audit.jsonl').read_bytes()
    records = [json.loads(line) for line in source.splitlines()]
    for record in records:
        if record['kind'] == 'CHUNK':
            transfers[record['transfer']][record['seq']][record['attempt']] = int(record['checkpoint'], 16)
    assert len(transfers) == 4
    assert all(set(v) == set(range(8)) for v in transfers.values())
    assert all(set(a) == {1, 2} for v in transfers.values() for a in v.values())
    acceptance = json.loads(((ROOT / 'acceptance.json') if (ROOT / 'acceptance.json').exists() else (ROOT / 'resources' / 'acceptance.json')).read_text())['slot_sha256']
    assert all(hashlib.sha256(bytes.fromhex(s)).hexdigest() == acceptance[k] for k, s in KNOWN.items())
    # Build exact inverse of the 16-bit CRC applied to one full 2-byte segment.
    inverse = {}
    zero2 = b'\0\0'
    for name, (poly, init, xout, reflected, _) in CRC_SPECS.items():
        fn = lambda b, poly=poly, init=init, xout=xout, reflected=reflected: crc16(b, poly, init, xout, reflected)
        base = fn(zero2)
        lookup = {fn(i.to_bytes(2, 'big')) ^ base: i.to_bytes(2, 'big') for i in range(65536)}
        assert len(lookup) == 65536, name
        # Independent nonzero-prefix planted control, also exercises concatenation.
        planted = bytes(range(16))
        for style in ['none', 'seq_u8', 'seq_u16_be', 'seq_u16_le', 'seq_dec', 'transfer_seq', 'seq_attempt', 'transfer_seq_attempt']:
            chunks = []
            for seq in range(8):
                pre = prefixes('AX-7782', seq, 2)[style]
                observed = fn(pre + planted[seq * 2:seq * 2 + 2])
                recovered = lookup[observed ^ fn(pre + zero2)]
                chunks.append(recovered)
            assert b''.join(chunks) == planted, (name, style)
        inverse[name] = (fn, lookup)

    results = []
    tested, controls, errors = 0, 0, 0
    control_matches = []
    for transfer, seqmap in sorted(transfers.items()):
        for attempts_mask in range(256):
            attempts = [1 + (attempts_mask >> seq & 1) for seq in range(8)]
            source_checkpoints = [seqmap[seq][attempts[seq]] for seq in range(8)]
            for crc_name, (fn, lookup) in inverse.items():
                for style in prefixes(transfer, 0, 1):
                    precomputed = [fn(prefixes(transfer, seq, attempts[seq])[style] + zero2) for seq in range(8)]
                    for endian in ['big', 'little']:
                        pieces = [lookup[(c if endian == 'big' else ((c & 0xff) << 8 | (c >> 8))) ^ p]
                                  for c, p in zip(source_checkpoints, precomputed)]
                        for order in [False, True]:
                            coupon = b''.join(pieces[::-1] if order else pieces)
                            tested += 1
                            component = bytes(a ^ b for a, b in zip(coupon, MASK))
                            if hashlib.sha256(component).hexdigest() == acceptance['K04']:
                                results.append((transfer, attempts_mask, crc_name, style, endian, order, 'K04', component.hex().upper()))
                            if hashlib.sha256(coupon).hexdigest() == acceptance['K08']:
                                results.append((transfer, attempts_mask, crc_name, style, endian, order, 'K08-direct', coupon.hex().upper()))
                        if attempts_mask in (0, 255):
                            # Independent recorded-slot control: CRC each 2-byte lane of 6 independently recovered components.
                            for label, component_hex in KNOWN.items():
                                comp = bytes.fromhex(component_hex)
                                expect = [fn(prefixes(transfer, seq, attempts[seq])[style] + comp[seq*2:seq*2+2]) for seq in range(8)]
                                observed = [v if endian == 'big' else ((v & 0xff) << 8 | (v >> 8)) for v in source_checkpoints]
                                controls += 1
                                errors += sum(a != b for a, b in zip(expect, observed))
                                for seq, (a, b) in enumerate(zip(expect, observed)):
                                    if a == b:
                                        control_matches.append((transfer, attempts_mask, crc_name, style, endian, label, seq, f"{a:04X}"))
    assert tested == 4 * 256 * 7 * 8 * 2 * 2
    print('TRANSFER_SHA256', hashlib.sha256(source).hexdigest())
    print('INVERSION_CONTROLS', len(CRC_SPECS) * 8, 'PASS')
    print('SOURCE_CHECK', len(transfers), 'transfers; eight sequences; two attempts each')
    print('CANDIDATE_TESTS', tested, 'K04_HITS', len([r for r in results if r[6] == 'K04']),
          'K08_DIRECT_HITS', len([r for r in results if r[6] == 'K08-direct']))
    print('SIX_SLOT_FRAGMENT_CONTROLS', controls, 'byte_lane_crc_mismatches', errors,
          'out_of', 8 * controls)
    for result in results:
        print('MATCH', result)
    for hit in control_matches:
        print('CONTROL_CRC_LANE_MATCH', hit)


if __name__ == '__main__':
    main()
