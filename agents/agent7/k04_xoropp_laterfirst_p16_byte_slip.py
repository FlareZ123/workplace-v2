#!/usr/bin/env python3
"""LOCAL-ONLY K04 later-first full-coupon byte-slip reconstruction, P16 exact.

The known intact REQUESTED3 two-word packet is the *only* fitted original
observation. A source-free exact first-two-output P16 SMT state partition
recovers candidate generator states; reverse xoroshiro128++ transitions
reconstruct prior serialized packets. Every full 16byte byte-offset coupon
checks the original unchanged K04 SHA **before** any REQUESTED1 diagnostic.
The model is conditional, not historical printer authentication.
Public CI is denied. No original source bytes, coupon values, states, target
digests or verified components are emitted; any exact hit requires out-of-repo
chmod0600 escrow. Quarantined PDFs are never opened.
"""
from __future__ import annotations
import argparse,hashlib,json,multiprocessing as mp,os,random,re,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from agents.agent1.k04_xoropp_laterfirst_backwards_local import (
    output,prev_state,forward_state)
from agents.agent7.k04_xoropp_p16_subcube_source_local import (
    exact_states,P16)
from agents.agent7.k04_xoropp_byte_slip_reducer import (
    pack_packet,escrow_hits)
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream
MASK=(1<<64)-1

def prehistory(state,endian,order):
    """Exactly 12 earlier *aligned* packets, then the fitted later packet."""
    prior=[];s=state
    for _ in range(24):
        s=prev_state(*s)
        prior.append(output(*s))
    words=list(reversed(prior))
    words.extend((output(*state),output(*forward_state(*state))))
    raw=b''.join(pack_packet(tuple(words[i:i+2]),endian,order)
                 for i in range(0,len(words),2))
    assert raw[-16:]==pack_packet(tuple(words[-2:]),endian,order)
    return raw

def full_coupon_scan(state,route_mask,target,endian,order,earlier=None):
    """144 complete candidates, not prefix hashes or copied ACK2 values."""
    assert len(route_mask)==16 and re.fullmatch('[0-9a-f]{64}',target)
    raw=prehistory(state,endian,order);later_start=len(raw)-16
    earlier_packet=(pack_packet(earlier,endian,order)
                    if earlier is not None else None)
    counts={'complete_coupons':0,'accepts':0,'unaligned_accepts':0,
            'earlier_replays':0,'joint':0}
    accepted=[]
    for gap in range(9):
        for slip in range(16):
            begin=later_start-16*(gap+1)-slip
            assert 0<=begin and begin+16<=later_start
            coupon=raw[begin:begin+16]
            comp=bytes(a^b for a,b in zip(coupon,route_mask))
            committed=hashlib.sha256(comp).hexdigest()==target
            counts['complete_coupons']+=1
            counts['accepts']+=int(committed)
            counts['unaligned_accepts']+=int(committed and slip%8!=0)
            replay=(earlier_packet is not None and
                    any(raw[pos:pos+16]==earlier_packet
                        for pos in range(0,begin-15,16)))
            counts['earlier_replays']+=int(replay)
            counts['joint']+=int(committed and replay)
            if committed:accepted.append(comp.hex().upper())
    assert counts['accepts']==len(accepted)
    return counts,accepted

def synthetic():
    # Pure test: 2 states x 4 serializers x 9 whole-packet positions
    # x 16 byte slips, all with full SHA commitment, plus poisoned holdout.
    controls=unaligned=0
    for seed in (20261128,1847):
        r=random.Random(seed)
        s=(r.getrandbits(64),r.getrandbits(64))
        mask=r.randbytes(16)
        for endian in ('big','little'):
            for order in ('ab','ba'):
                b=prehistory(s,endian,order)
                for gap in range(9):
                    for slip in range(16):
                        at=len(b)-16-16*(gap+1)-slip
                        selected=bytes(x^m for x,m in zip(b[at:at+16],mask))
                        target=hashlib.sha256(selected).hexdigest()
                        c,h=full_coupon_scan(s,mask,target,endian,order)
                        assert c['complete_coupons']==144
                        assert c['accepts']==1 and h==[selected.hex().upper()]
                        assert c['unaligned_accepts']==int(slip%8!=0)
                        controls+=1;unaligned+=int(slip%8!=0)
                at=len(b)-16-16*8-5
                selected=bytes(x^m for x,m in zip(b[at:at+16],mask))
                target=hashlib.sha256(selected).hexdigest()
                p=s
                for _ in range(24):p=prev_state(*p)
                first=(output(*p),output(*forward_state(*p)))
                good,h=full_coupon_scan(s,mask,target,endian,order,first)
                bad,h2=full_coupon_scan(s,mask,target,endian,order,
                                      (first[0]^1,first[1]))
                assert good['accepts']==bad['accepts']==1
                assert good['joint']==1 and bad['joint']==0
                assert h==h2==[selected.hex().upper()]
    assert controls==1152 and unaligned==1008
    # A complete candidate state is recovered with exact Boolean carry SMT,
    # not just planted as an external 128bit state oracle.
    rng=random.Random(20261128)
    planted=(rng.getrandbits(64),rng.getrandbits(64))
    y=stream(*planted,2)
    cube=sum(((planted[0]>>p)&1)<<j for j,p in enumerate(P16))
    models,terminal=exact_states(y,cube,10000)
    assert terminal=='unsat' and planted in models
    print(json.dumps({'synthetic_only':True,'full_sha_positives':controls,
        'non_64bit_aligned_sha_positives':unaligned,
        'SMT_true_P16_cube_recovered_complete_128bit_state':True,
        'SMT_terminal':'unsat','poisoned_earlier_not_a_veto':True,
        'original_K04_recovered':False},sort_keys=True))

def one_cube(job):
    idx,later,first,mask,target,endian,order,ms,retry_ms,cap=job
    states,terminal=exact_states(later,idx,ms,cap)
    first_terminal=terminal
    if terminal=='unknown' and retry_ms>ms:
        extra,terminal=exact_states(later,idx,retry_ms,cap)
        states=list(set(states).union(extra))
    totals=dict(complete_coupons=0,accepts=0,unaligned_accepts=0,
                earlier_replays=0,joint=0)
    components=[]
    for state in states:
        c,h=full_coupon_scan(state,mask,target,endian,order,first)
        for k in totals:totals[k]+=c[k]
        components.extend(h)
    return idx,first_terminal,terminal,len(states),totals,components

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--synthetic',action='store_true')
    ap.add_argument('--start',type=int,default=0)
    ap.add_argument('--count',type=int,default=1)
    ap.add_argument('--parent-major',action='store_true')
    ap.add_argument('--timeout-ms',type=int,default=350)
    ap.add_argument('--retry-timeout-ms',type=int,default=700)
    ap.add_argument('--max-models',type=int,default=32)
    ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--endian',choices=('big','little'),default='big')
    ap.add_argument('--order',choices=('ab','ba'),default='ba')
    ap.add_argument('--local-hit-escrow',type=Path)
    ap.add_argument('--summary-json',type=Path)
    a=ap.parse_args()
    if a.synthetic:return synthetic()
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        ap.error('Historical original source prohibited in public CI')
    if a.local_hit_escrow is None:
        ap.error('out-of-repository private hit escrow required')
    maximum=4096 if a.parent_major else 65536
    if not (0<=a.start<maximum and 1<=a.count<=maximum-a.start and
            100<=a.timeout_ms<=a.retry_timeout_ms<=30000 and
            1<=a.workers<=4 and 1<=a.max_models<=1024):
        ap.error('Invalid bounded search settings')
    escrow=a.local_hit_escrow.expanduser().resolve()
    if escrow==ROOT or ROOT in escrow.parents or not escrow.parent.is_dir():
        ap.error('Verified component escrow must be outside repository')
    if a.summary_json and a.summary_json.resolve()==escrow:
        ap.error('Aggregate output cannot overwrite verified components')
    from agents.agent37.k04_xoropp_acceptance_first_source_local import read_named_sources
    root=ROOT/'resources'
    pins={
      'evidence/print/spool-reconstruction.log':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
      'evidence/recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
      'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'}
    for rel,digest in pins.items():
        fn=root/rel
        if fn.suffix.lower()=='.pdf' or hashlib.sha256(fn.read_bytes()).hexdigest()!=digest:
            ap.error('original source integrity pin mismatch')
    first,later,mask,target=read_named_sources(root,a.endian,a.order)
    if a.parent_major:
        indices=(p+(sub<<12) for p in range(a.start,a.start+a.count)
                 for sub in range(16))
        total=16*a.count
    else:
        indices=range(a.start,a.start+a.count)
        total=a.count
    jobs=((i,later,first,mask,target,a.endian,a.order,a.timeout_ms,
           a.retry_timeout_ms,a.max_models) for i in indices)
    totals=dict(done=0,first_unknown=0,unsat=0,unknown=0,states=0,
                complete_coupons=0,accepts=0,unaligned_accepts=0,
                earlier_replays=0,joint=0)
    started=time.monotonic()
    with mp.Pool(a.workers) as pool:
        for idx,first_status,status,n,c,hits in pool.imap_unordered(
                one_cube,jobs,chunksize=1):
            totals['done']+=1
            totals['first_unknown']+=int(first_status=='unknown')
            totals[status]+=1;totals['states']+=n
            for key in c:totals[key]+=c[key]
            if hits:escrow_hits(escrow,hits)
            if totals['done']%100==0 or totals['done']==total:
                res={'source_safe_aggregate_only':True,
                    'original_bytes_or_components_exposed':False,
                    'conditional_producer':'xoroshiro128++',
                    'fit_only':'intact REQUESTED3',
                    'earlier_REQUESTED1':'independent diagnostic',
                    'layout':a.endian+'/'+a.order,'parent_major':a.parent_major,
                    'range':[a.start,a.start+a.count],
                    'fully_decided':totals['unknown']==0 and totals['done']==total,
                    'elapsed_seconds':round(time.monotonic()-started,2),
                    'totals':totals.copy()}
                print('AGGREGATE_ONLY',json.dumps(res,sort_keys=True),flush=True)
                if a.summary_json:
                    a.summary_json.write_text(json.dumps(res,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':
    main()
