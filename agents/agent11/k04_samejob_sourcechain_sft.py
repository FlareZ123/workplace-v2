"""Read-only same-job printer successor K04 SFT; source-only complete candidates."""
from __future__ import annotations
import hashlib
import hmac
import json
from pathlib import Path
import random
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ZIP = Path('/mnt/data/h17-archive-dump.zip')


def source(path: str) -> bytes:
    direct = ROOT / 'resources' / path
    if direct.is_file():
        return direct.read_bytes()
    with zipfile.ZipFile(ZIP) as archive:
        return archive.read(path)


def records() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for line in source('evidence/print/spool-reconstruction.log').decode('ascii').splitlines():
        if not line or line.startswith('#'):
            continue
        fields = dict(re.findall(r'([A-Z]+)=([^ ]+)', line))
        fields['TIME'] = line.split()[0]
        fields['LINE'] = line
        out.append(fields)
    return out


def metadata(record: dict[str, str]) -> dict[str, str]:
    return {
        'j': record['JOB'], 'c': record['CLASS'],
        'a': record['ATTEMPT'], 's': record['STATE'],
        'd': record['DEST'], 't': record['TIME'],
    }


def messages(old: dict[str, str], new: dict[str, str]):
    o, n = metadata(old), metadata(new)
    raw = bytes.fromhex(old['PAYLOAD'])
    variants = [raw, old['PAYLOAD'].encode(), old['PAYLOAD'].lower().encode()]
    prefixes = ['', n['j'], n['c'], n['a'], n['d'], n['t'],
                n['j'] + '|' + n['c'], n['j'] + '|' + n['a'],
                n['j'] + '|' + n['c'] + '|' + n['a'],
                n['c'] + '|' + n['a'], o['c'], o['a'], o['t'],
                o['c'] + '|' + n['c'], o['a'] + '|' + n['a'],
                o['j'] + '|' + o['c'] + '|' + n['c'] + '|' + n['a'],
                'RECOVER', 'RECOVER:2', 'ESC-N', 'H17-IR-261003']
    suffixes = ['', n['j'], n['c'], n['a'], n['d'], n['t'],
                n['j'] + '|' + n['c'] + '|' + n['a'],
                o['j'] + '|' + o['c'], 'RECOVER', '2', 'ESC-N']
    seen: set[bytes] = set()
    for representation in variants:
        for p in prefixes:
            for s in suffixes:
                for sep in ('', '|', ':', ' ', '\n', '\0'):
                    if not p and not s and sep:
                        continue
                    pre = (p + sep if p else '').encode()
                    suf = (sep + s if s else '').encode()
                    for value in (pre + representation + suf, pre + suf + representation):
                        if value not in seen:
                            seen.add(value)
                            yield value
    for value in (old['LINE'].encode(), old['LINE'].split(' PAYLOAD=')[0].encode() + raw):
        if value not in seen:
            yield value


def derived(message: bytes, keys: list[bytes]):
    for digest_fn in (hashlib.md5, hashlib.sha256, hashlib.sha512,
                      hashlib.blake2s, hashlib.blake2b):
        digest = digest_fn(message).digest()
        if len(digest) >= 16:
            yield digest[:16]
            yield digest[-16:]
            yield digest[:16][::-1]
            yield digest[-16:][::-1]
    for key in keys:
        for fn in (hashlib.sha256, hashlib.sha512):
            digest = hmac.new(key, message, fn).digest()
            yield digest[:16]
            yield digest[-16:]
            yield digest[:16][::-1]
        yield hmac.new(message, key, hashlib.sha256).digest()[:16]
    for seed in (message, message.decode('latin-1'),
                 int.from_bytes(hashlib.sha256(message).digest(), 'big')):
        rng = random.Random(seed)
        yield rng.randbytes(16)
        rng = random.Random(seed)
        value = rng.getrandbits(128)
        yield value.to_bytes(16, 'big')
        yield value.to_bytes(16, 'little')
        rng = random.Random(seed)
        words = [rng.getrandbits(32) for _ in range(4)]
        yield struct.pack('<4I', *words)
        yield struct.pack('>4I', *words)


def candidates(old: dict[str, str], new: dict[str, str], keys: list[bytes]):
    count = 0
    for msg in messages(old, new):
        for value in derived(msg, keys):
            count += 1
            yield count, value


def main() -> None:
    all_records = records()
    original_log = source('evidence/print/spool-reconstruction.log')
    assert hashlib.sha256(original_log).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
    key_source = json.loads(source('evidence/recovery-routing.json'))
    mask = bytes.fromhex(key_source['K04']['masked_component'])
    nonce = bytes.fromhex(key_source['K08']['desk_nonce'])
    keys = [mask, nonce, bytes(16)]
    all_records = [r for r in all_records if r['JOB'] in
                   ('PS-261003-0417', 'PS-261003-0420')]
    def get(job: str, attempt: str, cls: str) -> dict[str, str]:
        return next(r for r in all_records
                    if r['JOB'].endswith(job) and r['ATTEMPT'] == attempt
                    and r['CLASS'] == cls)
    old0420 = get('0420', '1', 'STORES')
    new0420 = get('0420', '2', 'RECOVER')
    actual = bytes.fromhex(new0420['PAYLOAD'])
    checks = 0
    hit = 0
    minbit = 129
    unique0420: set[bytes] = set()
    for checks, value in candidates(old0420, new0420, keys):
        unique0420.add(value)
        hit += value == actual
        minbit = min(minbit,(int.from_bytes(value,'big') ^ int.from_bytes(actual,'big')).bit_count())
    print('0420 known RECOVER holdout: assignments',checks,
          'unique complete candidates',len(unique0420),
          'exact originals',hit,'nearest bit distance',minbit)
    target = json.loads(source('acceptance.json'))['slot_sha256']['K04']
    new0417 = get('0417', '2', 'RECOVER')
    total = hits = 0
    unique0417: set[bytes] = set()
    for predecessor in (get('0417', '1', 'LABEL'), get('0417','1','RECOVER')):
        count = 0
        for count, value in candidates(predecessor, new0417, keys):
            unique0417.add(value)
            component = bytes(a ^ b for a,b in zip(value,mask))
            hits += hashlib.sha256(component).hexdigest() == target
        total += count
        print('0417',predecessor['CLASS'],'-> RECOVER assignments',count)
    baseline = bytes(a ^ b for a,b in zip(bytes.fromhex(new0417['PAYLOAD']),mask))
    assert hashlib.sha256(baseline).hexdigest() != target
    synthetic_msg = b'SOURCE-CHAIN-SYNTHETIC-CONTROL'
    planted = hmac.new(mask,synthetic_msg,hashlib.sha256).digest()[:16]
    assert planted in tuple(derived(synthetic_msg,keys))
    assert (checks,len(unique0420),hit,total,len(unique0417),hits) == (323680,265881,0,630056,517548,0)
    print('Original K04 full checks',total,'unique predicted coupons',len(unique0417),'PASS',hits)
    print('Planted constructor PASS; originals unchanged')


if __name__ == '__main__':
    main()
