"""H17 source-only 53-bit fractional PV <-> intact spool coincidence SFT.

Run: python agents/agent20/k04_pv_rounded_spool_overlap_sft.py [resources-dir]
No selected printer coupon, route mask, verifier, or target acceptance is read.
A negative result excludes only these *hypothesized* directly aligned float channels.
"""
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]/'resources'
PRINTER = ROOT/'evidence/print/spool-reconstruction.log'
PV = ROOT/'evidence/telemetry/freeze-export.jsonl'
assert hashlib.sha256(PRINTER.read_bytes()).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
assert hashlib.sha256(PV.read_bytes()).hexdigest() == '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'

coupons = [bytes.fromhex(re.search(r'PAYLOAD=([A-F0-9]{32})', line).group(1))
           for line in PRINTER.read_text().splitlines() if 'PAYLOAD=' in line][:128]
assert len(coupons) == 128
pv = {row['seq']: row['value'] for line in PV.read_text().splitlines()
      if (row := json.loads(line))['field'] == 'PV'}
assert sorted(pv) == list(range(100,212))
pv_index = defaultdict(list)
for seq, value in pv.items():
    pv_index[value].append(seq)


def raw_to_pv(a, b, low=12, high=88):
    """Standard CPython random.random() 53-bit word-pair construction."""
    fraction = ((a >> 5) * (1 << 26) + (b >> 6))/(1 << 53)
    return round(low + (high-low)*fraction, 3)

for byteorder in ('little','big'):
    for reversed_words in (False,True):
        offsets = (12,8,4,0) if reversed_words else (0,4,8,12)
        words = [int.from_bytes(coupon[offset:offset+4],byteorder)
                 for coupon in coupons for offset in offsets]
        assert len(words) == 512
        for low,high in ((12,88),(10,90),(0,100),(15,85),(12,90)):
            values = [raw_to_pv(words[i],words[i+1],low,high) for i in range(511)]
            single = [(i,val,pv_index[val]) for i,val in enumerate(values) if val in pv_index]
            # Two original PV values with consecutive seq numbers cannot simply
            # be two back-to-back float draws from this intact spool alignment.
            paired = [(i, s) for i in range(509) for s in pv_index.get(values[i], ())
                      if (s+1 in pv and pv[s+1] == values[i+2])]
            assert not paired, (byteorder,reversed_words,low,high,paired)
            print('ORIGINAL',byteorder,'reverse' if reversed_words else 'natural',
                  f'range={low}:{high}','one_value_intersections',len(single),
                  'two_consecutive_source_values',len(paired))

# An independent simulated adjacent two-PV source pair must pass the exact
# matcher; does not imply historical generator identity.
source = [int.from_bytes(coupons[0][i:i+4],'little') for i in range(0,16,4)]
control = [raw_to_pv(source[0],source[1]),raw_to_pv(source[2],source[3])]
assert control == [raw_to_pv(source[i],source[i+1]) for i in (0,2)]
syn_index = {control[0]: [500], control[1]: [501]}
assert [(i, s) for i in (0,2) for s in syn_index.get(raw_to_pv(source[i],source[i+1]), ())
        if s==500 and raw_to_pv(source[i+2],source[i+3]) == control[1]] == [(0,500)]
print('SYNTHETIC_TWO_FLOAT_SOURCE_CONTROL_PASS',control)
print('CONCLUSION: no consecutive exact PV pair directly reconstructed in 20 bounded original word/order/range views')
