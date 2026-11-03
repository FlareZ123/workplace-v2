"""Source-pinned, read-only K04 high-arity recovery KDF SFT.

Accepts either the original H-17 ZIP or an unpacked resources directory.
All tested producer hypotheses are speculative; source rules do not attest them.
"""
import hashlib
import hmac
import itertools
import json
import sys
import zipfile
from pathlib import Path

SIX = {
    'K01': '049AAB2E1CDE7A82CD7C60234303C91A',
    'K02': '0D7E3AB56FB75DA3EB0E2E06786D239E',
    'K03': '1384AF96E25D6ADA666209CB55E062FA',
    'K05': 'FF8B78200A56E8586DCDA00EF01E4572',
    'K06': '5DBF40EE52FAAED9A536D3326CF0D95A',
    'K07': '93495F5E425AB8E592123DABAEB68545',
}
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'resources'
if ROOT.is_file():
    with zipfile.ZipFile(ROOT) as z:
        route = json.loads(z.read('evidence/recovery-routing.json'))
        accept = json.loads(z.read('acceptance.json'))
else:
    route = json.loads((ROOT / 'evidence/recovery-routing.json').read_text())
    accept = json.loads((ROOT / 'acceptance.json').read_text())
assert all(hashlib.sha256(bytes.fromhex(v)).hexdigest() == accept['slot_sha256'][k] for k,v in SIX.items())
blocks = {k: bytes.fromhex(v) for k,v in SIX.items()}
blocks['MASK'] = bytes.fromhex(route['K04']['masked_component'])
blocks['NONCE'] = bytes.fromhex(route['K08']['desk_nonce'])
mask, nonce = blocks['MASK'], blocks['NONCE']
target = bytes.fromhex(accept['slot_sha256']['K04'])
order6 = list(SIX)
assert len(blocks) == 8
# Planted target from a frozen nontrivial all-8 HMAC last-half component.
control_message = b'CEG-ARCHIVE-RECOVERY/v1\n' + b'\n'.join(blocks[x] for x in reversed(list(blocks)))
control_component = hmac.digest(nonce, control_message, 'sha256')[16:]
control_target = hashlib.sha256(bytes(a ^ b for a,b in zip(control_component, mask))).digest()

def components(data):
    h = hashlib.sha256(data).digest()
    yield 'sha-first', h[:16]
    yield 'sha-last', h[16:]
    for keyname in ('MASK','NONCE'):
        v = hmac.digest(blocks[keyname], data, 'sha256')
        yield keyname+'-first', v[:16]
        yield keyname+'-last', v[16:]

counts = {'full_candidates':0, 'real_hits':0, 'planted_hits':0}
for labels in (order6, order6+['MASK','NONCE']):
    for perm in itertools.permutations(labels):
        for sep in (b'', b'\n'):
            raw = sep.join(blocks[x] for x in perm)
            for prefix in (b'', b'CEG-ARCHIVE-RECOVERY/v1\n', b'K04\n', b'REC8/1\n'):
                for producer, coupon in components(prefix+raw):
                    for stage, c in (('direct', coupon), ('route', bytes(a ^ b for a,b in zip(coupon,mask)))):
                        digest = hashlib.sha256(c).digest()
                        counts['full_candidates'] += 1
                        if digest == target:
                            counts['real_hits'] += 1
                            print('REAL K04 PASS',producer,stage,perm,sep,prefix,c.hex().upper())
                        if digest == control_target:
                            counts['planted_hits'] += 1
# Six-source XOR/sum directly or through SHA256 digest halves.
ordered = [blocks[x] for x in order6]
xor = bytes(0 for _ in range(16))
for v in ordered:
    xor = bytes(a ^ b for a,b in zip(xor,v))
addition = (sum(int.from_bytes(x,'big') for x in ordered)%(1<<128)).to_bytes(16,'big')
for v in (xor,addition):
    for coupon in (v,hashlib.sha256(v).digest()[:16],hashlib.sha256(v).digest()[16:]):
        for c in (coupon,bytes(a ^ b for a,b in zip(coupon,mask))):
            counts['full_candidates'] += 1
            if hashlib.sha256(c).digest() == target:
                counts['real_hits'] += 1
            if hashlib.sha256(c).digest() == control_target:
                counts['planted_hits'] += 1
assert counts == {'full_candidates':3939852, 'real_hits':0, 'planted_hits':1},counts
print(json.dumps({'result':'NO_MATCH','model':'six/eight-source SHA256/HMAC high-arity KDF',**counts},indent=2))
