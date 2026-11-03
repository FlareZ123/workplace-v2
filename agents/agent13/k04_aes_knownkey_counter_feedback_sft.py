"""Source-only AES-128 counter/feedback inversion for archival K04.

Only probes eight source-known keys and 128 ordinary acknowledged printer rows.
Original K04 selected event and all K04/K08 commitments stay excluded.
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'resources/evidence/print/spool-reconstruction.log'
SOURCE_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'


def ecb(key, data, encrypt):
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    context = cipher.encryptor() if encrypt else cipher.decryptor()
    return context.update(data) + context.finalize()


def statistics(ciphertexts, key):
    plaintext = ecb(key, b''.join(ciphertexts), False)
    blocks = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]
    results = {}
    for endian in ('little', 'big'):
        values = [int.from_bytes(block, endian) for block in blocks]
        delta = [(right-left) % (1 << 128)
                 for left, right in zip(values, values[1:])]
        results[endian] = (delta.count(1), Counter(delta).most_common(1)[0][1])
    prefixes = sum(a[:12] == b[:12] for a, b in zip(blocks, blocks[1:]))
    expected = ecb(key, b''.join(ciphertexts[:-1]), True)
    next_blocks = [expected[i:i+16] for i in range(0, len(expected), 16)]
    feedback = sum(a == b for a, b in zip(next_blocks, ciphertexts[1:]))
    return results, prefixes, feedback


def main():
    content = SOURCE.read_bytes()
    assert hashlib.sha256(content).hexdigest() == SOURCE_SHA
    rows = re.findall(
        r'JOB=(\S+) ATTEMPT=1 STATE=ACK .*?PAYLOAD=([0-9A-F]{32})',
        content.decode()
    )
    assert len(rows) == 129 and rows[0][0] == 'PS-261003-0300'
    assert rows[127][0] == 'PS-261003-0427' and rows[128][0] == 'PS-261003-0448'
    source = [bytes.fromhex(payload) for _, payload in rows[:128]]

    keys = {slot: bytes.fromhex(value)
            for slot, value in json.loads((REPO / 'candidate.json').read_text()).items()
            if value is not None}
    assert set(keys) == {'K01', 'K02', 'K03', 'K05', 'K06', 'K07'}
    routing = json.loads((REPO / 'resources/evidence/recovery-routing.json').read_text())
    keys['ROUTE_MASK'] = bytes.fromhex(routing['K04']['masked_component'])
    keys['DESK_NONCE'] = bytes.fromhex(routing['K08']['desk_nonce'])
    assert len(keys) == 8 and all(len(key) == 16 for key in keys.values())

    # Planted genuine AES-ECB counter and output-feedback sources.
    known = keys['K03']
    plaintext = [(0x123456789ABCDEF << 32 | n).to_bytes(16, 'big')
                 for n in range(128)]
    encrypted = ecb(known, b''.join(plaintext), True)
    encrypted = [encrypted[i:i+16] for i in range(0, len(encrypted), 16)]
    deltas, prefixes, feedback = statistics(encrypted, known)
    assert deltas['big'] == (127, 127) and prefixes == 127 and feedback == 0

    chain = [bytes.fromhex('FF8B78200A56E8586DCDA00EF01E4572')]
    for _ in range(127):
        chain.append(ecb(known, chain[-1], True))
    deltas, prefixes, feedback = statistics(chain, known)
    assert feedback == 127 and deltas['big'][0] == 0
    print('CONTROL: planted AES counter and feedback streams PASS')

    steps = fixed_prefixes = feedback_hits = 0
    for name, key in keys.items():
        delta, prefix, fb = statistics(source, key)
        steps += delta['big'][0] + delta['little'][0]
        fixed_prefixes += prefix
        feedback_hits += fb
        print(f'{name}: big={delta["big"]} little={delta["little"]} '
              f'prefix_pairs={prefix} feedback_pairs={fb}')
    print('SOURCE: 8 key candidates, 128 intact regular ACKs each, 127 pairs')
    print(f'unit_steps={steps} fixed_prefixes={fixed_prefixes} '
          f'feedback_pairs={feedback_hits}')
    assert (steps, fixed_prefixes, feedback_hits) == (0, 0, 0)
    print('NO_SOURCE_FIT for the stated models; no K04/K08 component recovered')


if __name__ == '__main__':
    main()
