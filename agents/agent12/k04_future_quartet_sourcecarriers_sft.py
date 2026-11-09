"""Original-source K04 future-quartet two-carrier inverse, read-only standalone SFT.

Use the actual ZIP, no copied selected ACK2 as a donor. The hypothesized
shared MT19937 future-output stage assignments are NOT source-attested.
"""
import hashlib
import json
from pathlib import Path
import random
import re
import struct
import sys
import zipfile
import zlib
from collections import defaultdict

MASK32 = (1 << 32) - 1
MAG = 0x9908B0DF
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
K04_SHA = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
ZIP_SHA = 'e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7'


def untemper(x):
    for shift, left, mask in ((18,False,MASK32),(15,True,0xEFC60000),
                              (7,True,0x9D2C5680),(11,False,MASK32)):
        value = x
        for _ in range(6):
            value = x ^ (((value << shift) & mask) if left else (value >> shift))
        x = value & MASK32
    return x


def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & MASK32


def twist(a, b):
    y = ((a & 0x80000000) | (b & 0x7fffffff))
    return (y >> 1) ^ (MAG if b & 1 else 0)


def invert_twist(y):
    lowbit = y >> 31
    b = y ^ (MAG if lowbit else 0)
    merged = ((b << 1) | lowbit) & MASK32
    return merged & 0x80000000, merged & 0x7fffffff


def reconstruct(native_a, native_b):
    # X[1574+i] XOR X[1347+i] == twist(X[950+i], X[951+i]); i=0..3
    pairs = [invert_twist(x ^ y) for x, y in zip(native_a, native_b)]
    selected = [(pairs[i-1][1] | pairs[i][0]) for i in range(1, 4)]
    selected.append(pairs[3][1])  # X954 high bit not present in the four pairs.
    assert len(selected) == 4
    return tuple(selected), tuple(selected[:-1] + [selected[-1] | 0x80000000])


def encode(words):
    return b''.join(temper(w).to_bytes(4, 'little') for w in words)


def layouts(block):
    for fmt in ('<4I','>4I'):
        original = struct.unpack(fmt, block)
        for order in (original, original[::-1]):
            yield tuple(order)
            yield tuple(untemper(word) for word in order)


def source_carriers(z):
    carriers = {}

    def add(label, data):
        assert isinstance(data, bytes)
        assert len(data) == 16, (label, len(data))
        carriers.setdefault(data, label)

    spool = z.read('evidence/print/spool-reconstruction.log')
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    packets = re.findall(rb'^2026-[^\n]+', spool, re.M)
    assert len(packets) == 133
    selected = [i for i, x in enumerate(packets) if b'JOB=PS-261003-0417 ' in x and b'ATTEMPT=2 ' in x and b'STATE=ACK ' in x and b'CLASS=RECOVER ' in x]
    assert selected == [129]
    for i, line in enumerate(packets):
        if i != 129:
            add(f'spool[{i}]', bytes.fromhex(re.search(rb'PAYLOAD=([0-9A-F]{32})', line).group(1).decode()))

    route = json.loads(z.read('evidence/recovery-routing.json'))
    add('route K04 XOR mask', bytes.fromhex(route['K04']['masked_component']))
    add('route K08 nonce', bytes.fromhex(route['K08']['desk_nonce']))
    candidate = {
        'K01':'049AAB2E1CDE7A82CD7C60234303C91A',
        'K02':'0D7E3AB56FB75DA3EB0E2E06786D239E',
        'K03':'1384AF96E25D6ADA666209CB55E062FA',
        'K05':'FF8B78200A56E8586DCDA00EF01E4572',
        'K06':'5DBF40EE52FAAED9A536D3326CF0D95A',
        'K07':'93495F5E425AB8E592123DABAEB68545',
    }
    acc = json.loads(z.read('acceptance.json'))
    for key, hex_string in candidate.items():
        val = bytes.fromhex(hex_string)
        assert hashlib.sha256(val).hexdigest() == acc['slot_sha256'][key]
        add(f'accepted {key}', val)

    raw = z.read('evidence/recorder/trip-recorder.raw')
    assert hashlib.sha256(raw).hexdigest() == '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
    assert raw[:8] == b'TRP2DUMP'
    version, size, count = struct.unpack_from('<HHI', raw, 8)
    assert version == 2 and size == 24 and len(raw) == 16 + count * size
    device_words = defaultdict(list)
    for i in range(count):
        frame = raw[16+24*i:16+24*(i+1)]
        if zlib.crc32(frame[:20]) != int.from_bytes(frame[20:], 'little'):
            continue
        _ts, node, event, latch, seq = struct.unpack_from('<IHBBI', frame, 0)
        device_words[(node,event)].append((seq, frame[12:16]))
    for (node,event), pair_list in device_words.items():
        pair_list.sort()
        for idx in range(len(pair_list)-3):
            section = pair_list[idx:idx+4]
            add(f'recorder node{node}/event{event}/seq{section[0][0]}-{section[-1][0]}', b''.join(w for _,w in section))

    raw = z.read('evidence/maintenance/seal-receipts.jsonl')
    receipts = [json.loads(s) for s in raw.splitlines()]
    unique = {}
    for row in receipts:
        if row.get('state') != 'CLOSED' or row.get('fitment') != 'AS_LEFT' or not row.get('signed'): continue
        key = (row['permit'], row['bay'])
        if key not in unique or unique[key]['revision'] < row['revision']:
            unique[key] = row
    seals = [v for _,v in sorted(unique.items())]
    for idx in range(len(seals)-3):
        section = seals[idx:idx+4]
        add(f'seals[{idx}:{idx+4}]', b''.join(bytes.fromhex(r['serial'][3:]) for r in section))
    for permit in sorted({r['permit'] for r in seals}):
        group = {r['bay']: r for r in seals if r['permit'] == permit}
        if len(group) == 4:
            for bay_order in ('ABCD','BDAC'):
                add(f'{permit}/{bay_order}',b''.join(bytes.fromhex(group[b]['serial'][3:]) for b in bay_order))

    sample = [json.loads(line) for line in z.read('evidence/telemetry/freeze-export.jsonl').splitlines()]
    by_seq = {}
    for row in sample:
        if (row.get('tag'),row.get('field'),row.get('quality'),row.get('state')) != ('LT-204','DIAG_WORD','GOOD','HOLD'): continue
        seq = row['seq']
        if seq not in by_seq or by_seq[seq]['revision'] < row['revision']:
            by_seq[seq] = row
    for i in sorted(by_seq):
        if all(j in by_seq for j in range(i, i+8)):
            add(f'telemetry seq{i}..{i+7}', b''.join(by_seq[j]['value'].to_bytes(2,'big') for j in range(i,i+8)))

    transfers = [json.loads(line) for line in z.read('evidence/transfers/transfer-audit.jsonl').splitlines()]
    for transfer in sorted({r['transfer'] for r in transfers}):
        by_seq = {}
        for row in transfers:
            if row['transfer'] != transfer or row['kind']!='CHUNK':continue
            seq=row['seq']
            if seq not in by_seq or by_seq[seq]['attempt'] < row['attempt']:
                by_seq[seq]=row
        if len(by_seq)==8:
            add(f'transfer {transfer}', b''.join(bytes.fromhex(by_seq[i]['checkpoint']) for i in range(8)))

    return carriers


def positive():
    for seed in (11,23,99,5489):
        r = random.Random(seed)
        native = [untemper(r.getrandbits(32)) for _ in range(1578)]
        a, b = native[1347:1351], native[1574:1578]
        two = reconstruct(a,b)
        assert tuple(native[951:955]) in two, (seed,two,native[951:955])
        mask = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
        candidate = bytes(a ^ b for a, b in zip(encode(native[951:955]),mask))
        target = hashlib.sha256(candidate).digest()
        assert any(hashlib.sha256(bytes(a ^ b for a, b in zip(encode(choice),mask))).digest() == target for choice in two)
        assert tuple(a) in list(layouts(encode(a)))
        assert tuple(b) in list(layouts(encode(b)))
        for i in range(4):
            assert native[1574+i] ^ native[1347+i] == twist(native[950+i],native[951+i])
    print('Genuine seeded MT19937 positive 4/4 PASS')


class DirectoryReader:
    def __init__(self, root): self.root = Path(root)
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, path): return (self.root / path).read_bytes()


def main(path):
    positive()
    path = Path(path)
    if path.is_file():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == ZIP_SHA
    with (DirectoryReader(path) if path.is_dir() else zipfile.ZipFile(path)) as z:
        carriers=source_carriers(z)
        route=json.loads(z.read('evidence/recovery-routing.json'))
        mask=bytes.fromhex(route['K04']['masked_component'])
        target=bytes.fromhex(json.loads(z.read('acceptance.json'))['slot_sha256']['K04'])
    assert target.hex() == K04_SHA
    categories = defaultdict(int)
    for label in carriers.values():
        categories[label.split('[')[0].split(' ')[0]] += 1
    print('Original carrier classes:',json.dumps(dict(sorted(categories.items())),sort_keys=True))
    items=list(carriers.items())
    encoded=[(name, v, word_view) for v,name in items for word_view in layouts(v)]
    counts={'source_carriers':len(items),'model_views':len(encoded),'pair_views_checked':0,'complete_K04_checks':0,'matches':0}
    source_hits=[]
    for ia,(name_a,block_a,words_a) in enumerate(encoded):
        for name_b,block_b,words_b in encoded:
            if block_a==block_b:continue
            reconstructed=reconstruct(words_a,words_b)
            for native in reconstructed:
                physical=encode(native)
                component=bytes(x^y for x,y in zip(physical,mask))
                if hashlib.sha256(component).digest()==target:
                    source_hits.append((name_a,name_b,words_a,words_b,physical.hex().upper(),component.hex().upper()))
            counts['pair_views_checked']+=1
    counts['complete_K04_checks']=counts['pair_views_checked']*2
    counts['matches']=len(source_hits)
    print(json.dumps(counts,sort_keys=True))
    for hit in source_hits:print('ORIGINAL_K04_HIT',hit)

if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[2] / 'resources')
