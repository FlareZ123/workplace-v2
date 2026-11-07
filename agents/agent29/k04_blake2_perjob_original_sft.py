"""H-17 K04: source-keyed BLAKE2s/BLAKE2b per-job 128-bit coupon issuer.
Selected disputed 18:02 coupon is withheld during source replay. Hypothetical
issuer only, with no historical attribution. Standard-library Python SFT.
Run: python agents/agent29/k04_blake2_perjob_original_sft.py [resources-root]
"""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / 'resources'
SPOOL = ROOT / 'evidence/print/spool-reconstruction.log'
ROUTE = ROOT / 'evidence/recovery-routing.json'
TARGETS = ROOT / 'acceptance.json'
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
route = json.loads(ROUTE.read_text())
targets = json.loads(TARGETS.read_text())
mask = bytes.fromhex(route['K04']['masked_component'])
target = targets['slot_sha256']['K04']
assert mask.hex().upper() == '8556C8CB6140A7F9A5123AC7571BEE1C'
assert target == '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'

KNOWN = {
    'K01': '049AAB2E1CDE7A82CD7C60234303C91A',
    'K02': '0D7E3AB56FB75DA3EB0E2E06786D239E',
    'K03': '1384AF96E25D6ADA666209CB55E062FA',
    'K05': 'FF8B78200A56E8586DCDA00EF01E4572',
    'K06': '5DBF40EE52FAAED9A536D3326CF0D95A',
    'K07': '93495F5E425AB8E592123DABAEB68545',
}
keys = {}
for name, value in KNOWN.items():
    data = bytes.fromhex(value)
    assert hashlib.sha256(data).hexdigest() == targets['slot_sha256'][name]
    keys[name] = data
keys['route_mask'] = mask
keys['desk_nonce'] = bytes.fromhex(route['K08']['desk_nonce'])
assert len(keys) == 8

rows = []
for line in SPOOL.read_text().splitlines():
    if not line.startswith('2026-'):
        continue
    fields = dict(re.findall(r'([A-Z]+)=([^ ]+)', line))
    row = dict(date=line.split()[0], **fields)
    assert len(row['PAYLOAD']) == 32
    rows.append(row)
assert len(rows) == 133
chosen = [r for r in rows if r['JOB'] == 'PS-261003-0417' and r['ATTEMPT'] == '2' and r['STATE'] == 'ACK' and r['CLASS'] == 'RECOVER']
assert len(chosen) == 1 and chosen[0]['date'] == '2026-10-03T18:02:00Z'
assert chosen[0]['PAYLOAD'] == 'A9A9DC5731A5E2AE879C47215C2559D5'
selected = chosen[0]
controls = [r for r in rows if r is not selected]
assert len(controls) == 132

# Canonical metadata fields, subset serializers and domain separators are
# frozen before selected commitment contact. This is a finite model.
PREFIXES = ('', 'K04|', 'H17|', 'REC8|', 'ESC-N|', 'H-17/')
JOINERS = ('', '|', ':', '/', ';', '_', ' ')
ORDERS = (
    ('JOB',), ('ATTEMPT',), ('CLASS',), ('DEST',), ('STATE',), ('date',),
    ('JOB','ATTEMPT'), ('JOB','CLASS'), ('JOB','DEST'), ('JOB','date'),
    ('JOB','ATTEMPT','CLASS'), ('JOB','ATTEMPT','DEST'),
    ('JOB','STATE','CLASS','DEST'), ('date','JOB','ATTEMPT'),
    ('JOB','date','CLASS','DEST'), ('JOB','ATTEMPT','STATE','CLASS','DEST','date'),
)
def messages(row):
    result = set()
    for fields in ORDERS:
        for sep in JOINERS:
            body = sep.join(row[x] for x in fields)
            for prefix in PREFIXES:
                result.add((prefix+body).encode('ascii'))
    result.add(json.dumps({k:row[k] for k in ('JOB','ATTEMPT','STATE','CLASS','DEST','date')},sort_keys=True,separators=(',',':')).encode())
    return sorted(result)

def coupon(digest_kind, key, msg):
    if digest_kind == 'blake2s':
        return hashlib.blake2s(msg, key=key, digest_size=16).digest()
    return hashlib.blake2b(msg, key=key, digest_size=16).digest()

# Synthetic positive: producer and per-row message selector must be
# recovered exclusively from three entire synthetic intact heldout packets.
# No target hash or selected copied packet enters that fit.
positive_key = keys['K06']
positive_messages = [messages(r) for r in controls]
planted = [coupon('blake2s', positive_key, m[0]) for m in positive_messages]
assert len(planted) == 132 and all(len(x) == 16 for x in planted)
heldout_ids = (0, 27, 131)
positive_matches = []
for kind in ('blake2s', 'blake2b'):
    for key_name, key in keys.items():
        for format_idx in range(min(len(positive_messages[i]) for i in heldout_ids)):
            if all(coupon(kind, key, positive_messages[i][format_idx]) == planted[i]
                   for i in heldout_ids):
                positive_matches.append((kind, key_name, format_idx))
assert positive_matches == [('blake2s', 'K06', 0)], positive_matches
kind, key_name, format_idx = positive_matches[0]
positive_coupon = coupon(kind, keys[key_name], messages(selected)[format_idx])
assert positive_coupon == coupon('blake2s', positive_key, messages(selected)[0])
assert len(positive_coupon) == 16

source_checks = 0
source_hits = []
selected_checks = 0
selected_hits = []
for kind in ('blake2s','blake2b'):
    for key_name, key in keys.items():
        for i, (row, candidates) in enumerate(zip(controls, positive_messages)):
            original = bytes.fromhex(row['PAYLOAD'])
            for msg in candidates:
                produced = coupon(kind,key,msg)
                source_checks += 1
                if produced == original:
                    source_hits.append((kind,key_name,i,msg.decode('ascii')))
        for msg in messages(selected):
            produced = coupon(kind,key,msg)
            selected_checks += 1
            component = bytes(a^b for a,b in zip(produced,mask))
            if hashlib.sha256(component).hexdigest() == target:
                selected_hits.append((kind,key_name,msg.decode('ascii'),component.hex().upper()))
print(json.dumps({
    'source': 'ORIGINAL',
    'controls': len(controls),
    'source_complete_packet_checks': source_checks,
    'source_hits': source_hits,
    'selected_complete_component_checks': selected_checks,
    'selected_hits': selected_hits,
    'planted_blake2s_whole_packet_controls': len(planted),
    'planted_source_only_models': positive_matches,
    'planted_blake2s_heldout_coupon': 'PASS',
}, sort_keys=True))
assert source_checks == 965184 and selected_checks == 7312
assert not source_hits and not selected_hits
