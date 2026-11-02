"""Source-only LT-204 16-bit fixed-pad cross-carrier experiment.

Uses Agent20's original p955 MT symbolic projector without selected spool
row129, coupon, mask or commitment. Only tests intact historical diagnostics.
Run: python agents/agent17/k04_diag_fixedpad_future_sft.py [resources_root]
"""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import hashlib
import json
import runpy
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2] / 'resources'
PRODUCER = Path(__file__).resolve().parents[1] / 'agent20' / 'k04_p955_pv_future_source_only_sft.py'
TELEMETRY = ROOT / 'evidence/telemetry/freeze-export.jsonl'
assert hashlib.sha256(TELEMETRY.read_bytes()).hexdigest() == '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
saved = sys.argv
sys.argv = [str(PRODUCER), str(ROOT)]
with redirect_stdout(StringIO()) as stdout:
    try:
        model = runpy.run_path(str(PRODUCER))
    finally:
        sys.argv = saved
assert 'SOURCE_RANK 15305 SOURCE_CONTRADICTIONS 0' in stdout.getvalue()
full = {i:v for i,(v,mask) in model['fixed'].items() if mask==0xffffffff}
assert len(full) == 318
raw = [json.loads(line) for line in TELEMETRY.read_text().splitlines()]
notes = [x for x in raw if x['field']=='DIAG_WORD' and x['tag']=='LT-204']
series = {r:{x['seq']:x['value'] for x in notes if x['revision']==r and 0<=x['seq']<=7}
          for r in range(1,5)}
assert all(len(series[r])==8 for r in series)

# Four revision-number original series; 1..8 fixed output strides; all epochs
# permitting 3+ projected words; upper/lower/xorfold halves; byte-order
# orientations; unknown 16-bit additive or XOR offset, learned on first word.
best = {'xor':0,'add':0}
eligible = 0
triple = []
for rev,data in series.items():
    for stride in range(1,9):
        for start in range(971-7*stride,2252):
            records = [(s,full[start+stride*s],data[s]) for s in range(8)
                       if start+stride*s in full]
            if len(records) < 3:
                continue
            eligible += 1
            for field in ('upper','lower','xorhalves'):
                for reverse in (False,True):
                    source = [((word>>16) if field=='upper' else word if field=='lower'
                               else (word>>16)^word)&65535 for _,word,_ in records]
                    observed = [((value>>8)|((value&255)<<8)) if reverse else value
                                for _,_,value in records]
                    for family in ('xor','add'):
                        pad = (observed[0]^source[0]) if family=='xor' else (observed[0]-source[0])&65535
                        matches = sum(((a^pad) if family=='xor' else (a+pad)&65535)==b
                                      for a,b in zip(source,observed))
                        best[family] = max(best[family],matches)
                        if matches>=3:
                            triple.append((rev,stride,start,field,reverse,family,pad,matches))

assert eligible==13624 and best=={'xor':2,'add':2} and not triple
# Independently planted 16bit XOR-pad positive, 3 consecutive source-predicted words.
epoch = next(i for i in full if i+1 in full and i+2 in full)
source = [full[i]>>16 for i in range(epoch,epoch+3)]
observed = [v^0x5A5A for v in source]
pad = observed[0]^source[0]
assert pad==0x5A5A and all((a^pad)==b for a,b in zip(source,observed))

print('SOURCE_PIN_PASS original spool/telemetry and p955 projection')
print('COMPLETE_PREDICTABLE_FUTURE_WORDS',len(full))
print('ORIGINAL_SEQUENCES',4,'SOURCE_EPOCH_STRIDE_REV_TRIPLES',eligible)
print('FROZEN_CALIBRATIONS',eligible*3*2*2)
print('MAX_ORIGINAL_MATCHES',best,'THREE_OR_MORE',len(triple))
print('SYNTHETIC_XOR_PAD_CONTROL_PASS',epoch)
print('NO_MATCH; actual K04 selected original bits 0/128, K08 words 0')
