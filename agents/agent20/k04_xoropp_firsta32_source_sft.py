#!/usr/bin/env python3
"""Local-only exact xoroshiro128++ a0-half source discriminator.

Source is read-only. Never uses the selected damaged ACK2 or original K04
commitment; no actual source words, state values, or candidate coupons are
printed. No PDF or private/ usage. NEVER run source-bearing input in public CI.

Run manually at repo root:
  python agents/agent20/k04_xoropp_firsta32_source_sft.py ptw
  python agents/agent20/k04_xoropp_firsta32_source_sft.py mask
  python agents/agent20/k04_xoropp_firsta32_source_sft.py note947
Requires C++17, g++, OpenMP. Full 64 x 2^32 source checks for PTW/mask;
24 x 2^32 for N09 source-heading anchor.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

REPO=Path(__file__).resolve().parents[2]
SPOOL=REPO/'resources/evidence/print/spool-reconstruction.log'
SEALS=REPO/'resources/evidence/maintenance/seal-receipts.jsonl'
ROUTE=REPO/'resources/evidence/recovery-routing.json'
CODE=REPO/'agents/agent20/k04_xoropp_firsta32_synthetic.cpp'
PINS={
 SPOOL:'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
 SEALS:'c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32',
 ROUTE:'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
}

def source():
    for path,digest in PINS.items():
        assert sha256(path.read_bytes()).hexdigest()==digest, path.name
    lines=[line for line in SPOOL.read_text().splitlines()
      if 'JOB=PS-261003-0417 ' in line
      and 'ATTEMPT=1 ' in line and 'STATE=REQUESTED ' in line
      and 'CLASS=RECOVER ' in line]
    assert len(lines)==1
    packet=bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})',lines[0])[1])
    route=json.loads(ROUTE.read_text())
    mask=bytes.fromhex(route['K04']['masked_component'])
    assert len(packet)==len(mask)==16
    selected={}
    for line in SEALS.read_text().splitlines():
        row=json.loads(line)
        if (row.get('permit')!='PTW-417'
            or row.get('state')!='CLOSED' or row.get('fitment')!='AS_LEFT'
            or row.get('signed') is not True):continue
        bay=row['bay']
        if bay not in selected or row['revision']>selected[bay]['revision']:
            selected[bay]=row
    assert set(selected)==set('ABCD')
    return packet,mask,selected

def scan(binary,mode,packet,mask,seals):
    anchors=[]
    if mode=='ptw':
        for bay in sorted(seals):
            word=bytes.fromhex(seals[bay]['serial'][3:])
            assert len(word)==4
            for endian in ('big','little'):anchors.append(int.from_bytes(word,endian))
    elif mode=='mask':
        for index in (0,4,8,12):
            word=mask[index:index+4]
            for endian in ('big','little'):anchors.append(int.from_bytes(word,endian))
    elif mode=='note947':
        note=REPO/'resources/evidence/crew/noticeboard-and-desk-notes.txt'
        raw=note.read_bytes()
        assert sha256(raw).hexdigest()=='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
        matches=re.findall(r'^N09 /[^\n]*\n([^\n]+)$',raw.decode(),re.M)
        assert len(matches)==1
        line=matches[0]
        heading=line.split(':',1)[0]
        assert len(heading)==28
        def pack(bits):
            return bytes(sum(v<<j for j,v in enumerate(bits[k:k+8]))
                         for k in range(0,len(bits)-7,8))
        assert pack([ord(ch)&1 for ch in heading])==b'3B3'
        prefix=pack([ord(ch)&1 for ch in line[:32]])
        assert len(prefix)==4
        anchors=list(dict.fromkeys((0x3B3,
                        int.from_bytes(prefix,'big'),
                        int.from_bytes(prefix,'little'))))
    else:
        raise ValueError('unsupported mode')
    assert len(anchors)==(3 if mode=='note947' else 8)
    count=0;positive=0
    for endian in ('big','little'):
        values=[int.from_bytes(packet[i:i+8],endian) for i in (0,8)]
        for swap in (False,True):
            y0,y1=values[::-1] if swap else values
            for known in anchors:
                for high in (0,1):
                    args=[str(binary),f'{y0:x}',f'{y1:x}',f'{known:x}',
                          str(high),str(1<<32)]
                    proc=subprocess.run(args,capture_output=True,text=True,
                                        check=True,timeout=180)
                    assert 'synthetic_positive PASS' in proc.stdout
                    assert 'exhaustive_unknown32=1' in proc.stdout
                    found=re.search(r'source_pair_full_match=(\d+)',proc.stdout)
                    assert found, 'Missing complete-search marker'
                    positive+=int(found[1]);count+=1
    assert count==(24 if mode=='note947' else 64)
    return {'model':mode,'source_models':count,'complete_assignments':count*(1<<32),
            'first_packet_pair_fits':positive,'selected_ack2_used':False,
            'K04_target_checked':False,'historical_producer_authenticated':False}

def main():
    if len(sys.argv)!=2 or sys.argv[1] not in ('ptw','mask','note947'):
        raise SystemExit('usage: script.py ptw|mask|note947')
    packet,mask,seals=source()
    with TemporaryDirectory(prefix='h17_agent20_a32_') as temp:
        exe=Path(temp)/'a32'
        subprocess.run(['g++','-std=c++17','-O3','-fopenmp',str(CODE),
                        '-o',str(exe)],check=True)
        # Complete 2^32 planted positive and deliberate wrong-anchor negative.
        control=subprocess.run([str(exe)],capture_output=True,text=True,
                               check=True,timeout=180)
        assert 'full 2^32 planted state + wrong-anchor negative: PASS' in control.stdout
        result=scan(exe,sys.argv[1],packet,mask,seals)
        print('FULL_SYNTHETIC_PASS')
        print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
