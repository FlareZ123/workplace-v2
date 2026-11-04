"""H-17 source-selected 128-bit GF-affine/GHASH-label emitter SFT, stdlib only."""
import hashlib
from collections import Counter
from itertools import combinations

P = 0xE1000000000000000000000000000000
SRC = [
    ('K01', 'WN-14', 'watch register', '2026-10-02', '049AAB2E1CDE7A82CD7C60234303C91A'),
    ('K02', 'LT-204', 'DIAG_WORD', '2026-10-03', 'E1A5E474BAD7E853A2E8C71D3317D507'),
    ('K05', 'TRP2', 'node49 event82', '2026-10-03', 'FF8B78200A56E8586DCDA00EF01E4572'),
    ('K06', 'RC-17', 'revision C', '2026-10-01', '5DBF40EE52FAAED9A536D3326CF0D95A'),
    ('K07', 'AX-7782', 'COMMIT checkpoint', '2026-10-03', '8947CEDCB9CC73BAB7E87BE63302C5C9'),
]
K04 = ('K04', 'PS-261003-0417', 'RECOVER ACK2', '2026-10-03', '')
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
TARGET = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'


def mul(a, b):
    result = 0
    for shift in range(127, -1, -1):
        if b >> shift & 1:
            result ^= a
        a = (a >> 1) ^ (P if a & 1 else 0)
    return result


def power(a, exponent):
    product = 1 << 127
    while exponent:
        if exponent & 1:
            product = mul(product, a)
        a = mul(a, a)
        exponent >>= 1
    return product


def label(row, mode):
    slot, name, purpose, date, _ = row
    return (
        slot, name, purpose, date + '|' + slot, slot + '|' + name,
        name + '|' + purpose, slot + '|' + name + '|' + date,
        'H17|' + name, 'REC8/1|' + slot,
        'H17-IR-261003|' + slot + '|' + name,
        name + '/' + purpose + '/' + date,
        slot + ':' + name + ':' + purpose + ':' + date,
        'H17:' + name + ':' + date, 'IR-261003-H17:' + slot,
    )[mode]


def encode(value, mode):
    data = value.encode('ascii')
    if mode == 0:
        return int.from_bytes(hashlib.sha256(data).digest()[:16], 'big')
    if mode == 1:
        return int.from_bytes(hashlib.blake2b(data, digest_size=16).digest(), 'big')
    if mode == 2:
        return int.from_bytes(hashlib.md5(data).digest(), 'big')
    if mode == 3:
        return int.from_bytes(data[:16].ljust(16, b'\0'), 'big')
    return int.from_bytes(data[-16:].rjust(16, b'\0'), 'big')


def main():
    assert mul(1 << 127, 0x0123456789abcdef0123456789abcdef) == 0x0123456789abcdef0123456789abcdef
    for x in (1, 2, 0xabcdef12345, (1 << 128)-1):
        assert mul(x, power(x, (1 << 128)-2)) == 1 << 127
    originals = [int(row[-1], 16) for row in SRC]
    observations = Counter()
    attempts = 0
    hits = 0
    for labelmode in range(14):
        for view in range(5):
            x = [encode(label(row, labelmode), view) for row in SRC]
            if len(set(x)) != 5:  # date-only shape has duplicate labels
                continue
            target_x = encode(label(K04, labelmode), view)
            for i, j in combinations(range(5), 2):
                a = mul(originals[i] ^ originals[j], power(x[i] ^ x[j], (1 << 128)-2))
                b = originals[i] ^ mul(a, x[i])
                assert mul(a, x[j]) ^ b == originals[j]
                observations[sum(mul(a, x[k]) ^ b == originals[k] for k in range(5) if k not in (i,j))] += 1
                coupon = (mul(a, target_x) ^ b).to_bytes(16, 'big')
                component = bytes(y ^ m for y, m in zip(coupon, MASK))
                hits += hashlib.sha256(component).hexdigest() == TARGET
                attempts += 1
    assert observations == Counter({0:680}) and attempts == 680 and hits == 0
    print('ORIGINAL_TWO_ANCHOR_MODELS', attempts, 'THREE_HOLDOUT_MATCH_COUNTS', dict(observations), 'K04_SHA_HITS', hits)
    x = [encode(label(row, 7), 0) for row in SRC]
    a0, b0 = 0x76b0f7189bda0a85778ba0946be568a2, 0x139aba9c72719c329472df449d148051
    values = [mul(a0, elt)^b0 for elt in x]
    a = mul(values[0]^values[2], power(x[0]^x[2], (1 << 128)-2))
    b = values[0]^mul(a, x[0])
    assert (a,b) == (a0,b0)
    assert [mul(a, elt)^b for elt in x] == values
    target_x = encode(label(K04, 7), 0)
    assert mul(a, target_x)^b == mul(a0, target_x)^b0
    print('SYNTHETIC_TWO_SELECTED_ANCHORS_THREE_FULL_HOLDOUTS_AND_TARGET PASS')


if __name__ == '__main__':
    main()
