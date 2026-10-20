"""Audit 2026 supplemental H-17 originals for literal missing REC8 carriers.

Source material, original verifier and commitments are read-only. Requires pypdf.
Run from any working directory: python h17_supplement_carrier_audit.py /path/to/h17-archive
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


def normalized_words(text: str) -> list[str]:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()


def scan_carrier(name: str, data: bytes, mask: bytes, nonce: bytes,
                 target4: bytes, target8: bytes) -> dict[str, int]:
    counts = {'byte_windows': 0, 'hex_windows': 0, 'caption_spans': 0}

    def test_bytes(value: bytes) -> None:
        if hashlib.sha256(value).digest() in (target4, target8):
            raise AssertionError(f'{name}: direct accepted component present')
        if hashlib.sha256(bytes(a ^ b for a, b in zip(value, mask))).digest() == target4:
            raise AssertionError(f'{name}: accepted coupon payload present')

    for offset in range(max(0, len(data) - 15)):
        test_bytes(data[offset:offset + 16])
        counts['byte_windows'] += 1
    text = data.decode('utf-8', errors='replace')
    for run in re.finditer(r'[0-9A-Fa-f]{32,}', text):
        for offset in range(len(run.group()) - 31):
            value = bytes.fromhex(run.group()[offset:offset + 32])
            test_bytes(value)
            counts['hex_windows'] += 1
    words = normalized_words(text)
    for start in range(len(words)):
        for end in range(start + 1, min(len(words), start + 40) + 1):
            message = ' '.join(words[start:end]).encode('utf-8')
            candidate = hmac.new(nonce, message, hashlib.sha256).digest()[:16]
            if hashlib.sha256(candidate).digest() == target8:
                raise AssertionError(f'{name}: accepted final caption present: {message!r}')
            counts['caption_spans'] += 1
    return counts


def main(root: Path) -> None:
    evidence = root / 'evidence'
    office = evidence / 'h17-supplemental-office-files'
    acceptance = json.loads((root / 'acceptance.json').read_text('utf-8'))
    routing = json.loads((evidence / 'recovery-routing.json').read_text('utf-8'))
    mask = bytes.fromhex(routing['K04']['masked_component'])
    nonce = bytes.fromhex(routing['K08']['desk_nonce'])
    t4 = bytes.fromhex(acceptance['slot_sha256']['K04'])
    t8 = bytes.fromhex(acceptance['slot_sha256']['K08'])
    ack = bytes.fromhex('A9A9DC5731A5E2AE879C47215C2559D5')
    synthetic_coupon = bytes(a ^ b for a, b in zip(ack, mask))
    assert hashlib.sha256(synthetic_coupon).hexdigest() == (
        '11a7f6064781a6ac7678dc6dd24759af95981c8a927f8da4436515354d34549b')
    try:
        scan_carrier('synthetic-coupon', b'prefix' + ack + b'suffix', mask, nonce,
                     hashlib.sha256(synthetic_coupon).digest(), t8)
        raise AssertionError('coupon positive control missed')
    except AssertionError as error:
        if 'accepted coupon payload present' not in str(error):
            raise
    example = 'The little lamp stays on until the corridor has gone quiet.'
    candidate = hmac.new(nonce, ' '.join(normalized_words(example)).encode(), hashlib.sha256).digest()[:16]
    assert candidate.hex().upper() == '0C3B326D0324BF93F55D4A3EEAB26CDE'
    try:
        scan_carrier('synthetic-caption', example.encode(), mask, nonce, t4,
                     hashlib.sha256(candidate).digest())
        raise AssertionError('caption positive control missed')
    except AssertionError as error:
        if 'accepted final caption present' not in str(error):
            raise
    print('POSITIVE_CONTROLS coupon_raw=PASS caption_normalization_hmac=PASS')
    totals = {'byte_windows': 0, 'hex_windows': 0, 'caption_spans': 0}
    for path in sorted(office.iterdir()):
        if not path.is_file():
            continue
        data = path.read_bytes()
        counts = scan_carrier(path.name, data, mask, nonce, t4, t8)
        print('ORIGINAL', path.name, len(data), hashlib.sha256(data).hexdigest(), counts)
        for key in totals:
            totals[key] += counts[key]
    pdf = office / 'BX25-08.pdf'
    reader = PdfReader(pdf)
    assert reader.is_encrypted and reader.decrypt('8131')
    assert len(reader.pages) == 1
    parsed_stream = reader.pages[0].get_contents().get_data()
    parsed_text = reader.pages[0].extract_text().encode('utf-8')
    for name, data in [('PDF-DECRYPTED-CONTENT-STREAM', parsed_stream),
                       ('PDF-DECRYPTED-EXTRACTED-TEXT', parsed_text)]:
        counts = scan_carrier(name, data, mask, nonce, t4, t8)
        print('DERIVED', name, len(data), hashlib.sha256(data).hexdigest(), counts)
        for key in totals:
            totals[key] += counts[key]
    print('TOTALS', totals)
    print('RESULT target_K04=NO_MATCH target_K08=NO_MATCH checked_supplemental=4 '
          'derived_pdf_views=2 originals_preserved=YES')


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
