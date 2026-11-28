#!/usr/bin/env python3
"""Read-only K04 AX-7782 mixed-retry AES/SHA/AES source-coupling test.

Exploratory source-based relation, NOT a documented historic printer producer.
Only aggregate outcomes are printed. Never reads the hash-only BX25-08 PDF.
Requires cryptography: python k04_axmixed_aes_sha_aes_sft.py /path/to/export
"""
import argparse, configparser, hashlib, json, re
from collections import defaultdict
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def load(root):
    route=json.loads((root/'evidence/recovery-routing.json').read_text())
    acceptance=json.loads((root/'acceptance.json').read_text())
    ini=configparser.ConfigParser()
    ini.read(root/'evidence/archive-labels.ini')
    job=ini['printer_routes_2026-09-01_to_2026-10-03']['ESC-N']
    rows=[]
    for line in (root/'evidence/print/spool-reconstruction.log').read_text().splitlines():
        fields=dict(re.findall(r'\b([A-Z]+)=([^\s]+)',line))
        if fields.get('JOB')==job:
            rows.append((int(fields['ATTEMPT']),fields['STATE'],fields['CLASS'],bytes.fromhex(fields['PAYLOAD'])))
    assert len(rows)==4 and len({x[3] for x in rows})==4
    selected=[x for x in rows if x[0]==2 and x[1]=='ACK' and x[2]=='RECOVER']
    assert len(selected)==1
    chunks=defaultdict(dict)
    for line in (root/'evidence/transfers/transfer-audit.jsonl').read_text().splitlines():
        rec=json.loads(line)
        if rec['kind']=='CHUNK':
            chunks[rec['transfer']][(rec['seq'],rec['attempt'])]=bytes.fromhex(rec['checkpoint'])
    return route,acceptance,rows,selected[0],chunks

def mixed_key(chunks,transfer):
    src=chunks[transfer]
    assert len(src)==16
    assert all(len(src[s,a])==2 for s in range(8) for a in (1,2))
    return b''.join(src[s,1 if s%2==0 else 2] for s in range(8))

def parity_check(key):
    bits=[b&1 for b in key]
    packed=bytes(sum(bits[i+j]<<j for j in range(8)) for i in (0,8))
    assert packed==bytes.fromhex('50D4')
    assert all(x.bit_count()%2==0 for x in packed)
    assert bytes(x&0x7f for x in packed)==b'PT'

def aes(k,block):
    assert len(k)==len(block)==16
    return Cipher(algorithms.AES(k),modes.ECB()).encryptor().update(block)

def source_pipeline(k,block):
    # Predeclared one-direction AES / SHA / AES on a complete 16-byte block.
    return aes(k,hashlib.sha256(aes(k,block)).digest()[:16])

def accepts_k04(producer_output,route,acceptance):
    mask=bytes.fromhex(route['K04']['masked_component'])
    component=bytes(x^y for x,y in zip(producer_output,mask))
    return hashlib.sha256(component).hexdigest()==acceptance['slot_sha256']['K04']

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path)
    route,acceptance,rows,selected,chunks=load(ap.parse_args().root)
    key=mixed_key(chunks,'AX-7782')
    parity_check(key)
    print('AX_MIXED_PTPARITY=PASS')
    # Independent AES-128 known answer vector.
    assert aes(bytes.fromhex('000102030405060708090A0B0C0D0E0F'),
               bytes.fromhex('00112233445566778899AABBCCDDEEFF'))==bytes.fromhex('69C4E0D86A7B0430D8CDB78070B4C55A')
    synthetic=b'\x10'*16
    mask=bytes.fromhex(route['K04']['masked_component'])
    good=hashlib.sha256(bytes(a^b for a,b in zip(synthetic,mask))).hexdigest()
    bad=hashlib.sha256(bytes(a^b for a,b in zip(synthetic[:-1]+b'\x11',mask))).hexdigest()
    assert good!=bad
    print('SYNTHETIC_GATES=PASS')
    for transfer in ('AX-7778','AX-7781','AX-7782','AX-7783'):
        key=mixed_key(chunks,transfer)
        outputs=[source_pipeline(key,row[3]) for row in rows]
        hits=sum(accepts_k04(x,route,acceptance) for x in outputs)
        readable=sum(all(32<=b<=126 for b in x) for x in outputs)
        if transfer=='AX-7782':
            selected_output=source_pipeline(key,selected[3])
            selected_hit=int(accepts_k04(selected_output,route,acceptance))
            assert selected_hit==int(accepts_k04(outputs[rows.index(selected)],route,acceptance))
            print('SELECTED_SOURCE_PIPELINE original_K04_hit=%d all_four_source_blocks_hits=%d all_printable=%d'%(selected_hit,hits,readable))
        else:
            print('CONTROL_TRANSFER '+transfer+' all_four_source_blocks_hits=%d all_printable=%d'%(hits,readable))
    print('HISTORICAL_COMPLETE_RECOVERY=NO')

if __name__=='__main__':main()
