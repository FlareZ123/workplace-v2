#!/usr/bin/env python3
"""POSIX mrand48 whole-packet original-source gate for H-17 K04.

Invert all 2^16 low state bits after the first 32-bit mrand48 output. Test
four consecutive mrand48 outputs for every intact original printer packet,
in both byte endiannesses and four-word directions. Withhold selected ACK2
before parsing its payload. No K04 target commitment or copied ACK2 value is read.
"""
from __future__ import annotations
import argparse, hashlib, pathlib, re, json

SP_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
A=0x5DEECE66D
C=0xB
M=(1<<48)-1
SELECTED=('PS-261003-0417', '2','ACK','RECOVER')

def next_state(s):
    return (A*s+C)&M

def output(s):
    return s>>16

def invert_quad(outputs):
    """Return complete state after first output if 4 consecutive calls fit."""
    head=outputs[0]<<16
    hits=[]
    for lo in range(65536):
        st=head|lo
        s=next_state(st)
        if output(s)!=outputs[1]: continue
        s=next_state(s)
        if output(s)!=outputs[2]: continue
        s=next_state(s)
        if output(s)!=outputs[3]: continue
        hits.append(st)
    return hits

def parse_spool(path):
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SP_SHA, 'original source SHA mismatch'
    out=[]
    excluded=0
    for i,line in enumerate(raw.decode().splitlines()):
        if not line or line.startswith('#'):continue
        fields=dict(re.findall(r'(JOB|ATTEMPT|STATE|CLASS|PAYLOAD)=([^ ]+)',line))
        descriptor=(fields['JOB'],fields['ATTEMPT'],fields['STATE'],fields['CLASS'])
        if descriptor==SELECTED:
            excluded+=1
            continue
        p=bytes.fromhex(fields['PAYLOAD'])
        assert len(p)==16
        out.append((i,fields['JOB'],p))
    assert len(out)==132 and excluded==1,(len(out),excluded)
    return out

def as_words(p,endian,reverse):
    ws=[int.from_bytes(p[4*i:4*(i+1)],endian) for i in range(4)]
    return ws[::-1] if reverse else ws

def controls():
    # Real standard LCG transition including 48-bit state carry.
    states=[0x123456789abc,0x000000000000,0xffffffffffff,0xC0FFEEDEAD00]
    for st0 in states:
        s=st0
        ws=[]
        for _ in range(4):
            s=next_state(s)
            ws.append(output(s))
        assert invert_quad(ws)==[next_state(st0)], (hex(st0),ws)
        assert invert_quad(ws[:-1]+[ws[-1]^1])==[]
    return len(states)

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument('--spool',type=pathlib.Path,
        default=pathlib.Path('resources/evidence/print/spool-reconstruction.log'))
    args=pa.parse_args()
    ctrl=controls()
    observed=parse_spool(args.spool)
    views={}
    two_word_survivors=0
    four_word_survivors=[]
    for endian in ('little','big'):
        for reverse in (False,True):
            first_pair=0
            complete=0
            for idx,job,p in observed:
                w=as_words(p,endian,reverse)
                head=w[0]<<16
                found2=False
                found4=False
                for lo in range(65536):
                    s=head|lo
                    s=next_state(s)
                    if output(s)!=w[1]: continue
                    found2=True
                    s=next_state(s)
                    if output(s)!=w[2]: continue
                    s=next_state(s)
                    if output(s)!=w[3]: continue
                    found4=True
                    four_word_survivors.append({'idx':idx,'job':job,
                        'endian':endian,'reverse':reverse,
                        'state_after_first':f'{head|lo:012x}'})
                first_pair+=found2
                complete+=found4
            views[f'{endian}_{"reverse" if reverse else "forward"}']={
                'two_word_compat_rows':first_pair,
                'whole_packet_compat_rows':complete}
            two_word_survivors+=first_pair
    result={'source_sha256':SP_SHA,'source_intact_rows':len(observed),
        'selected_ack2_excluded_before_hex_parse':True,
        'whole_packet_serializers':4,
        'first_pair_possible_rows':two_word_survivors,
        'complete_16byte_packet_possibilities':four_word_survivors,
        'positive_real_mrand48_states':ctrl,'views':views,
        'original_K04_target_loaded':False}
    print(json.dumps(result,indent=2))
    assert not four_word_survivors,'Unexpected intact mrand48 packet: investigate'

if __name__=='__main__':
    main()
