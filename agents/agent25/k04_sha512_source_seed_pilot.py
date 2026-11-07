"""Original H17 source-derived SHA512/CPython64 issuer against intact spool word.

Run in repository checkout; requires only Python standard library. Read-only.
"""
import hashlib
import random
import re
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'resources'
PRIOR, LAST = 2496, 3119
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
KNOWN = {
    'K01':'049AAB2E1CDE7A82CD7C60234303C91A',
    'K02':'0D7E3AB56FB75DA3EB0E2E06786D239E',
    'K03':'1384AF96E25D6ADA666209CB55E062FA',
    'K05':'FF8B78200A56E8586DCDA00EF01E4572',
    'K06':'5DBF40EE52FAAED9A536D3326CF0D95A',
    'K07':'93495F5E425AB8E592123DABAEB68545',
    'K04_route_mask':'8556C8CB6140A7F9A5123AC7571BEE1C',
    'K08_desk_nonce':'5F933DA6A1BD03C32DA5CBC25344F497',
}
IDENTITIES = ('H17-IR-261003','PS-261003-0417','ESC-N','L-29/N','FA-17',
              'H17-POL-17/A3','IR-261003-H17','8131','REC8/1',
              '2026-10-03T18:02:00Z')


def inputs():
    raw = (R / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    packet_hex = re.findall(rb'PAYLOAD=([0-9A-F]{32})', raw)
    assert len(packet_hex) == 133
    # Physical selected row129 never decoded, and never enters source seeds.
    early = [bytes.fromhex(x.decode('ascii')) for x in packet_hex[:128]]
    first = early[0]
    assert first.hex().upper() == 'FBBBC54356483F5864BB3F06794518A5'
    corpus = {}
    for p in sorted((R / 'evidence').rglob('*')):
        if p.is_file() and p.name != 'spool-reconstruction.log':
            corpus['file:' + p.relative_to(R).as_posix()] = p.read_bytes()
    for i, row in enumerate(early):
        corpus[f'early_row_raw:{i}'] = row
        corpus[f'early_row_hex:{i}'] = row.hex().upper().encode('ascii')
    lines = raw.splitlines()[1:129]
    assert len(lines) == 128
    corpus.update({f'early_line:{i}':line for i,line in enumerate(lines)})
    corpus.update({f'known:{k}':bytes.fromhex(v) for k,v in KNOWN.items()})
    corpus.update({f'identity:{s}':s.encode('ascii') for s in IDENTITIES})
    corpus['preack_binary'] = b''.join(early)
    corpus['preack_hex'] = b''.join(x.hex().upper().encode('ascii') for x in early)
    return first, corpus


def scan(words, first_word):
    return [p for p in range(PRIOR, LAST+1) if words[p] == first_word]


def run():
    first, source = inputs()
    positive = random.Random(hashlib.sha512(b'SYNTHETIC_FILE').digest())
    sample = [positive.getrandbits(32) for _ in range(LAST+4)]
    assert scan(sample, sample[PRIOR+174]) == [PRIOR+174]
    complete = []
    words_hit = []
    seen = set()
    wanted = int.from_bytes(first[:4], 'little')
    for name, payload in source.items():
        digest = hashlib.sha512(payload).digest()
        if digest in seen:continue
        seen.add(digest)
        rng = random.Random(digest)
        generated = [rng.getrandbits(32) for _ in range(LAST+4)]
        phases = scan(generated, wanted)
        if phases:words_hit.append(name)
        if any(b''.join(v.to_bytes(4,'little') for v in generated[p:p+4]) == first
               for p in phases):complete.append(name)
    print('SOURCE_SHA256', SPOOL_SHA)
    print('SYNTHETIC_POSITIVE', PRIOR+174)
    print('SOURCE_INPUTS',len(source),'DISTINCT_SEEDS',len(seen),'PHASES',LAST-PRIOR+1)
    print('ORIGINAL_WORD_HITS',len(words_hit),'ORIGINAL_PACKET_HITS',len(complete))
    assert not words_hit and not complete


if __name__ == '__main__':
    run()
