"""Read-only H-17 K04 two-step request/ACK source-chain test (Python SFT)."""
import hashlib
import hmac
import json
from pathlib import Path
import random
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2] / 'resources'
ARCHIVE = Path('/mnt/data/h17-archive-dump.zip')


def read(name):
    file = ROOT / name
    if file.is_file():
        return file.read_bytes()
    with zipfile.ZipFile(ARCHIVE) as z:
        return z.read(name)


def transform(value, row, algorithm, tag, placement, sep, view, secret):
    tags = ('', row['ATTEMPT'], row['JOB'], row['CLASS'], row['STATE'],
            row['TIME'], row['JOB'] + ':' + row['ATTEMPT'],
            row['CLASS'] + ':' + row['ATTEMPT'],
            row['JOB'] + ':' + row['CLASS'] + ':' + row['ATTEMPT'])
    salt = tags[tag].encode('ascii')
    separator = sep.encode('ascii') if salt else b''
    msg = salt + separator + value if placement == 0 else value + separator + salt
    if algorithm == 'hmac_secret':
        result = hmac.new(secret, msg, hashlib.sha256).digest()
    elif algorithm == 'hmac_payload':
        result = hmac.new(value, salt, hashlib.sha256).digest()
    elif algorithm == 'random':
        result = random.Random(msg).randbytes(16)
    else:
        result = hashlib.new(algorithm, msg).digest()
    output = result[:16] if view < 2 else result[-16:]
    return output[::-1] if view % 2 else output


def main():
    original = read('evidence/print/spool-reconstruction.log')
    assert hashlib.sha256(original).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
    rows = []
    for line in original.decode('ascii').splitlines():
        if 'JOB=PS-261003-0417' not in line or 'CLASS=RECOVER' not in line:
            continue
        row = dict(re.findall(r'([A-Z]+)=([^ ]+)', line))
        row['TIME'] = line.split()[0]
        rows.append(row)
    by_attempt = {int(row['ATTEMPT']): row for row in rows}
    assert {(int(r['ATTEMPT']), r['STATE']) for r in rows} == {(1,'REQUESTED'),(2,'ACK'),(3,'REQUESTED')}
    first, middle, third = (by_attempt[i] for i in (1,2,3))
    start, finish = bytes.fromhex(first['PAYLOAD']), bytes.fromhex(third['PAYLOAD'])
    route = json.loads(read('evidence/recovery-routing.json'))
    mask = bytes.fromhex(route['K04']['masked_component'])
    nonce = bytes.fromhex(route['K08']['desk_nonce'])
    original_target = json.loads(read('acceptance.json'))['slot_sha256']['K04']
    algorithms = ('md5','sha256','sha512','blake2s','blake2b',
                  'hmac_secret','hmac_payload','random')
    count = matches = key_matches = 0
    best = 129
    for algorithm in algorithms:
        for tag in range(9):
            for place in range(2):
                for sep in ('','|',':','\n','\0'):
                    for view in range(4):
                        secrets = (mask,nonce,bytes(16)) if algorithm == 'hmac_secret' else (mask,)
                        for key in secrets:
                            a = transform(start,middle,algorithm,tag,place,sep,view,key)
                            b = transform(a,third,algorithm,tag,place,sep,view,key)
                            count += 1
                            matches += b == finish
                            best = min(best, (int.from_bytes(b,'big') ^ int.from_bytes(finish,'big')).bit_count())
                            candidate = bytes(x ^ y for x,y in zip(a,mask))
                            key_matches += hashlib.sha256(candidate).hexdigest() == original_target
    known = transform(start,middle,'hmac_secret',6,0,'|',0,mask)
    planted = transform(known,third,'hmac_secret',6,0,'|',0,mask)
    assert any(transform(transform(start,middle,'hmac_secret',6,0,'|',v,mask),third,
                         'hmac_secret',6,0,'|',v,mask) == planted for v in range(4))
    assert count == 3600 and matches == 0 and key_matches == 0
    print('Historical two-step operator assignments',count)
    print('Complete authentic attempt3 matches',matches,'nearest bit distance',best)
    print('Original K04 complete commitment matches',key_matches)
    print('Planted two-step HMAC positive PASS; original files unchanged')


if __name__ == '__main__':
    main()
