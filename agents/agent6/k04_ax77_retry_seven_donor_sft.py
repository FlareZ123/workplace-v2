"""K04 full-coupon source test: paired attempts from four AX transfers.

Uses Agent39's original-data-checked seven-future-native-donor affine map.
Tests each transfer's chronological (seq,attempt) 16x 16-bit checkpoints
as eight 32-bit attempt-pair words, seven retained; also natural 3+4
consecutive-word mixes across distinct transfers of the same object.
The selected printer ACK is withheld and evidence/commitments remain read-only.
"""
import hashlib
import importlib.util
import itertools
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
file=ROOT/'agents/agent39/k04_p951_seven_donor_affine_sft.py'
spec=importlib.util.spec_from_file_location('affine',file)
affine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(affine)

def key_for(coupon,words,outendian,mask):
    selected=affine.select_native(coupon,words)
    payload=b''.join(affine.temper(v).to_bytes(4,outendian) for v in selected)
    return bytes(x^y for x,y in zip(payload,mask))

def pair_words(original,byteswap,pairreverse,endianness,tempered):
    half=[p[::-1] if byteswap else p for p in original]
    packed=[half[i+1]+half[i] if pairreverse else half[i]+half[i+1]
            for i in range(0,16,2)]
    values=[int.from_bytes(p,endianness) for p in packed]
    return [affine.prior.untemper(v) for v in values] if tempered else values

def main():
    symbols=affine.express()
    affine.positive_controls(symbols)
    original=(ROOT/'resources/evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(original).hexdigest()==affine.SOURCE_SHA
    fields=re.findall(rb'PAYLOAD=([0-9A-F]{32})',original)
    assert len(fields)==len(affine.prior.STARTS)==133
    packets=[b'' if i==129 else bytes.fromhex(x.decode()) for i,x in enumerate(fields)]
    coupon=affine.make_coupon_map(symbols,packets)
    routing=json.loads((ROOT/'resources/evidence/recovery-routing.json').read_text())
    accept=json.loads((ROOT/'resources/acceptance.json').read_text())
    mask=bytes.fromhex(routing['K04']['masked_component'])
    target=bytes.fromhex(accept['slot_sha256']['K04'])
    raw=(ROOT/'resources/evidence/transfers/transfer-audit.jsonl').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'
    entries=[json.loads(x) for x in raw.splitlines()]
    groups={}
    for tag in ('AX-7778','AX-7781','AX-7782','AX-7783'):
        rows=sorted((v for v in entries if v.get('kind')=='CHUNK' and v['transfer']==tag),
                    key=lambda x:(x['seq'],x['attempt']))
        assert len(rows)==16
        groups[tag]=[bytes.fromhex(x['checkpoint']) for x in rows]
    cases=0
    hits=[]
    for tag,original in groups.items():
        for swap,pairreverse,fullreverse,drop,endian,tempered,outend in itertools.product(
                (False,True),(False,True),(False,True),range(8),
                ('little','big'),(False,True),('little','big')):
            values=pair_words(original,swap,pairreverse,endian,tempered)
            if fullreverse:values.reverse()
            candidate=key_for(coupon,values[:drop]+values[drop+1:],outend,mask)
            cases+=1
            if hashlib.sha256(candidate).digest()==target:
                hits.append(('single-transfer',tag,swap,pairreverse,fullreverse,drop,endian,tempered,outend,candidate.hex().upper()))
    assert cases==2048
    print('Single-transfer seven paired-attempt donors:',cases,'matches',len(hits))
    for first,second in itertools.permutations(groups,2):
        for swap,pairreverse,endian,tempered,outend in itertools.product(
                (False,True),(False,True),('little','big'),(False,True),('little','big')):
            left=pair_words(groups[first],swap,pairreverse,endian,tempered)
            right=pair_words(groups[second],swap,pairreverse,endian,tempered)
            for a in range(6):
                for b in range(5):
                    candidate=key_for(coupon,left[a:a+3]+right[b:b+4],outend,mask)
                    cases+=1
                    if hashlib.sha256(candidate).digest()==target:
                        hits.append(('failover',first,second,a,b,swap,pairreverse,endian,tempered,outend,candidate.hex().upper()))
    assert cases==13568
    print('All 13,568 full candidate coupons:',len(hits),'matches')
    assert not hits,hits
    print('Source-based reconstruction hypotheses remain conditional; no seventh authenticated key.')

if __name__=='__main__':main()
