"""Invented fixtures only; no original source paths or recovery material."""
import hashlib
import hmac
import json
from pathlib import Path

NONCE = bytes(range(16))
PHRASE = 'paper boats wait beside the blue cup'
HMAC16 = bytes.fromhex('B49AA9544523119104F4AB7EB21DBAEC')


def write_fixture(resources: Path, phrase: str = PHRASE) -> tuple[dict, bytes]:
    transfer = resources / 'evidence' / 'transfers'
    mail = resources / 'evidence' / 'mail'
    transfer.mkdir(parents=True, exist_ok=True)
    mail.mkdir(parents=True, exist_ok=True)
    checkpoints = [bytes((i, 255 - i)) for i in range(8)]
    rows = []
    for seq, checkpoint in enumerate(checkpoints):
        for attempt, value in ((1, b'\0\0'), (2, checkpoint)):
            rows.append({'kind': 'CHUNK', 'transfer': 'AX-7782', 'seq': seq,
                         'attempt': attempt, 'checkpoint': value.hex(),
                         'bytes': 1048576, 'object': 'IR-261003-H17'})
    rows.append({'kind': 'COMMIT', 'transfer': 'AX-7782', 'dry_run': False,
                 'chunks': 8, 'object': 'IR-261003-H17'})
    (transfer / 'transfer-audit.jsonl').write_text('\n'.join(map(json.dumps, rows)) + '\n')
    (mail / '13.eml').write_text('Synthetic fixture: AX-7782 IR-261003-H17 actual retained copy')
    route = {'K08': {'desk_nonce': NONCE.hex()}}
    (resources / 'evidence' / 'recovery-routing.json').write_text(json.dumps(route))
    chain = b''.join(checkpoints)
    component = hmac.digest(NONCE, phrase.encode('ascii'), 'sha256')[:16]
    acceptance = {'slot_sha256': {
        'K07': hashlib.sha256(hashlib.sha256(chain).digest()[:16]).hexdigest(),
        'K08': hashlib.sha256(component).hexdigest(),
    }}
    (resources / 'acceptance.json').write_text(json.dumps(acceptance))
    return acceptance, chain
