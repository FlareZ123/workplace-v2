"""H-17 K04: source-carrier AES keyed-counter producer pilot (read-only SFT).

Checks 128 intact ordinary spool packets against AES-128 using 16-byte keys
extracted from the official source. Both AES operations are inverted;
unknown 128-bit counter origin, increment, endian and fixed nonce are allowed.
Requires cryptography and the unchanged repository resources directory.
Does not inspect K04 acceptance or the disputed selected ACK as a target.
"""
import hashlib
import re
import struct
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[2] / 'resources' / 'evidence'
SPOOL = ROOT / 'print' / 'spool-reconstruction.log'
RECORDER = ROOT / 'recorder' / 'trip-recorder.raw'
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
assert hashlib.sha256(RECORDER.read_bytes()).hexdigest() == '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'

ordinary = []
for line in SPOOL.read_text(encoding='utf-8').splitlines():
    if line.startswith('2026-10-03T') and '+00:00' in line:
        m = re.search(r'PAYLOAD=([0-9A-F]{32})', line)
        if m:
            ordinary.append(bytes.fromhex(m.group(1)))
assert len(ordinary) == 128

keys = {}
def add(value, origin):
    if len(value) == 16:
        keys.setdefault(value, origin)

for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path.suffix.lower() in ('.raw', '.pdf'):
        continue
    for m in re.finditer(r'(?<![0-9A-Fa-f])[0-9A-Fa-f]{32}(?![0-9A-Fa-f])', path.read_text(encoding='utf-8')):
        add(bytes.fromhex(m.group()), 'hex:' + path.relative_to(ROOT).as_posix())

raw = RECORDER.read_bytes()
assert raw[:8] == b'TRP2DUMP'
version, record_size, count = struct.unpack_from('<HHI', raw, 8)
assert record_size == 24 and len(raw) == 16 + count * record_size
for i in range(count):
    record = raw[16 + i * 24:16 + (i + 1) * 24]
    for offset in range(9):
        add(record[offset:offset + 16], f'recorder record={i} offset={offset}')
for offset in (12, 16):
    words = [raw[16 + i * 24 + offset:16 + i * 24 + offset + 4] for i in range(count)]
    for i in range(count - 3):
        add(b''.join(words[i:i + 4]), f'recorder word-offset={offset} window={i}')

# Six source-verified slots, three original prehash blocks, route mask and nonce.
for h in (
    '049AAB2E1CDE7A82CD7C60234303C91A',
    '0D7E3AB56FB75DA3EB0E2E06786D239E',
    'E1A5E474BAD7E853A2E8C71D3317D507',
    '1384AF96E25D6ADA666209CB55E062FA',
    'D7DAD6BC9714519B7DAD0AD4BE8E87FD',
    'FF8B78200A56E8586DCDA00EF01E4572',
    '5DBF40EE52FAAED9A536D3326CF0D95A',
    '93495F5E425AB8E592123DABAEB68545',
    '8947CEDCB9CC73BAB7E87BE63302C5C9',
    '8556C8CB6140A7F9A5123AC7571BEE1C',
    '5F933DA6A1BD03C32DA5CBC25344F497',
):
    add(bytes.fromhex(h), 'source-reduced/recovery-route')

def aes(key, block, decrypt=False):
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    c = cipher.decryptor() if decrypt else cipher.encryptor()
    return c.update(block) + c.finalize()

# Cryptographic known-answer tests, FIPS-197 Appendix C.
plain = bytes.fromhex('00112233445566778899AABBCCDDEEFF')
k128 = bytes(range(16))
k256 = bytes(range(32))
assert aes(k128, plain) == bytes.fromhex('69C4E0D86A7B0430D8CDB78070B4C55A')
assert aes(k256, plain) == bytes.fromhex('8EA2B7CA516745BFEAFC49904B496089')
assert aes(k128, aes(k128, plain), True) == plain
assert aes(k256, aes(k256, plain), True) == plain
print('FIPS197_AES128_256_CONTROLS: PASS')

# An unknown nonce+counter origin is fully absorbed into the first AES input.
# Any constant-stride 128-bit counter must make the first three inverse-AES
# blocks an arithmetic progression (in either endian order). A fixed 8-byte
# nonce, even without a fixed stride, leaves >=8 bytes identical across rows.
progressions = []
most_constant_bytes = 0
for key, origin in keys.items():
    for decrypt in (False, True):
        blocks = [aes(key, packet, decrypt) for packet in ordinary[:3]]
        common = sum(blocks[0][i] == blocks[1][i] == blocks[2][i] for i in range(16))
        most_constant_bytes = max(most_constant_bytes, common)
        for endian in ('little', 'big'):
            a, b, c = (int.from_bytes(x, endian) for x in blocks)
            step = (b - a) % (1 << 128)
            if step == (c - b) % (1 << 128):
                progressions.append((origin, decrypt, endian, step))

# A planted unknown 128-bit starting state and increment are recovered.
key = next(iter(keys))
start = int('FABC015389CDECAB61DA72065B238899', 16)
planted = [aes(key, ((start + 300*i) % (1 << 128)).to_bytes(16, 'big')) for i in range(3)]
readback = [int.from_bytes(aes(key, item, True), 'big') for item in planted]
assert (readback[1] - readback[0]) % (1 << 128) == (readback[2] - readback[1]) % (1 << 128) == 300
print('SYNTHETIC_UNKNOWN_OFFSET_COUNTER_CONTROL: PASS')
print('UNIQUE_SOURCE_CARRIER_KEYS:', len(keys))
print('AES128_MODELS_TESTED:', 2 * len(keys))
print('THREE_ROW_CONSTANT_STRIDE_HITS:', len(progressions))
print('MOST_THREE_ROW_COMMON_NONCE_BYTES:', most_constant_bytes)
assert not progressions and most_constant_bytes < 8
