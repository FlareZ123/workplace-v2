#!/usr/bin/env python3
"""Replay source-private P16/P18 xoroshiro states against complete K04 coupon windows.

Zero SMT work: accepts private 0600 resumable producer caches, validates exact
source/serializer/solver families and direct first-packet replay, deduplicates
all recovered states, tests whole 16-byte coupon commitments BEFORE any later
REQUESTED3 comparison, and escrows original hits in 0600 out-of-repo file.
Historical source use is forbidden on public CI. Synthetic mode uses no
historical archive, route, or target data.
"""
from __future__ import annotations
import argparse,hashlib,json,os,random,re,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from agents.agent7.k04_xoropp_byte_slip_reducer import assess_state, serialized_bytes
from agents.agent7.k04_xoropp_p16_subcube_source_local import read_original
PIN='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
P12=(0,1,2,3,22,23,24,25,45,46,47,48)
P16=P12+(4,5,6,7)
SCHEMAS={
 'p16-agent7-firstpair-v1':'p16',
 'p18-agent50-refine-firstpair-v1':'p18',
 'p16-shared-context-parent-v1':'incremental',
}
def private_file(name,create=False):
    p=Path(name).expanduser().absolute()
    if p.is_symlink() or ROOT==p or ROOT in p.parents or not p.parent.is_dir() or p.parent.is_symlink():
        raise ValueError('Private cache must be outside repository and no symlink')
    if p.parent.stat().st_mode&0o077:
        raise ValueError('Private cache parent must be 0700 or stricter')
    if p.exists():
        s=p.stat()
        if not stat.S_ISREG(s.st_mode) or s.st_mode&0o077:
            raise ValueError('Private cache must be regular 0600')
    elif not create:
        raise FileNotFoundError(p)
    return p

def recover_states(ledgers,layout):
    states=set()
    seen=0
    for name in ledgers:
        f=private_file(name)
        for line in f.read_text().splitlines():
            row=json.loads(line)
            kind=SCHEMAS.get(row.get('schema'))
            if not kind or row.get('source_sha256')!=PIN or row.get('layout')!=layout:
                raise ValueError('Different source, serializer or solver schema; cache replay refused')
            if kind=='p16':
                if row.get('anchor_positions')!=list(P16):raise ValueError('P16 anchor mismatch')
                groups=[row['states']]
            elif kind=='p18':
                if row.get('child_positions')!=[8,9]:raise ValueError('P18 anchor mismatch')
                groups=[row['states']]
            else:
                if row.get('anchor_positions')!=list(P16):raise ValueError('Incremental anchor mismatch')
                groups=[c['states'] for c in row['children']]
            for group in groups:
                for value in group:
                    if not re.fullmatch('[0-9a-f]{32}',value):raise ValueError('Invalid cached full state')
                    states.add((int(value[:16],16),int(value[16:],16)))
            seen+=1
    return states,seen

def escrow_components(path,components):
    if not components:return
    flags=os.O_WRONLY|os.O_APPEND|os.O_CREAT|getattr(os,'O_NOFOLLOW',0)
    fd=os.open(path,flags,0o600)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode):raise ValueError('Hit escrow is not regular')
        os.fchmod(fd,0o600)
        for component in components:
            assert re.fullmatch('[0-9A-F]{32}',component)
            os.write(fd,(json.dumps({'verified_K04_component':component})+'\n').encode())
        os.fsync(fd)
    finally:
        os.close(fd)

def test_state(state,first,later,mask,target,endian,order,max_pre,max_later):
    # The whole original first packet is reproduced independently of SMT.
    first_words=first if order=='ab' else first[::-1]
    expected=b''.join(x.to_bytes(8,endian) for x in first_words)
    assert serialized_bytes(state,1,endian,order)==expected
    return assess_state(state,mask,target,endian,order,max_pre,max_later,later)

def synthetic_controls():
    rng=random.Random(20261128)
    total=0
    for endian in ('big','little'):
        for order in ('ab','ba'):
            for _ in range(2):
                state=(rng.getrandbits(64),rng.getrandbits(64))
                from agents.agent7.k04_xoropp_byte_slip_reducer import stream, pack_packet
                words=stream(*state,44)
                first=tuple(words[:2])
                later=tuple(words[24:26])
                mask=rng.randbytes(16)
                raw=serialized_bytes(state,22,endian,order)
                for gap in (0,4,8,16):
                    for slip in (0,7,15):
                        start=16*(gap+1)+slip
                        candidate=bytes(a^b for a,b in zip(raw[start:start+16],mask))
                        sha=hashlib.sha256(candidate).hexdigest()
                        c,h=test_state(state,first,later,mask,sha,endian,order,16,16)
                        assert c['candidates']==272 and c['commit_hits']==1
                        assert h==[candidate.hex().upper()]
                        total+=1
    print(json.dumps({'synthetic_only':True,'complete_K04_style_SHA_positive':total,
                      'layouts':4,'states_per_layout':2,'pre_coupon_gaps':[0,4,8,16],
                      'byte_slips':[0,7,15],'original_material_loaded':False},sort_keys=True))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--synthetic',action='store_true')
    ap.add_argument('--ledger',action='append')
    ap.add_argument('--hit-escrow')
    ap.add_argument('--endian',choices=('big','little'),default='big')
    ap.add_argument('--order',choices=('ab','ba'),default='ab')
    ap.add_argument('--max-pre-packets',type=int,default=8)
    ap.add_argument('--max-later-packets',type=int,default=8)
    ns=ap.parse_args()
    if ns.synthetic:
        synthetic_controls()
        return
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        ap.error('Original source processing forbidden in public CI')
    if not ns.ledger or not ns.hit_escrow:
        ap.error('Source replay requires source-private ledger(s) and hit escrow')
    if not 0<=ns.max_pre_packets<=16 or not 0<=ns.max_later_packets<=16:
        ap.error('Out-of-bounds reducer window')
    escrow=private_file(ns.hit_escrow,create=True)
    if str(escrow) in ns.ledger:
        ap.error('Escrow must differ from every input ledger')
    layout=ns.endian+'/'+ns.order
    states,records=recover_states(ns.ledger,layout)
    first,later,mask,target=read_original(ns.endian,ns.order)
    tally=dict(cache_records=records,unique_states=len(states),
               full_coupon_commitment_checks=0,original_commitment_hits=0,
               later_whole_packet_replays=0)
    for state in states:
        counts,hits=test_state(state,first,later,mask,target,ns.endian,ns.order,
                              ns.max_pre_packets,ns.max_later_packets)
        escrow_components(escrow,hits)
        tally['full_coupon_commitment_checks']+=counts['candidates']
        tally['original_commitment_hits']+=counts['commit_hits']
        tally['later_whole_packet_replays']+=counts['replay_views']
    print('AGGREGATE_ONLY '+json.dumps({
        'method':'producer-state-cache-replay-no-SMT',
        'layout':layout,
        'original_source_or_state_bytes_exposed':False,
        'max_pre_packets':ns.max_pre_packets,
        'max_later_packets':ns.max_later_packets,
        'counts':tally},sort_keys=True))

if __name__=='__main__':
    main()
