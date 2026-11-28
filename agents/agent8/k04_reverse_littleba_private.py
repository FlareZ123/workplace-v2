#!/usr/bin/env python3
"""Recover K04 from a distinct later-first, little-endian/BA xoroshiro128++ hypothesis.

Only the intact PS-261003-0417 REQUESTED3 print packet is a fitting input.
Predict 24 earlier generator words, serialize under little/BA, and test all 177
complete 16-byte byte-slip coupon windows against original K04 SHA-256 *before*
any independent REQUESTED1 replay. Exact P16 model enumeration + private durable
per-child ledger. CI denied for historical mode; no PDF, no ACK2 payload input.

Synthetic mode reads NO archive, route, acceptance, or source-bearing files.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, stat, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent if (HERE.parent.parent/'resources').is_dir() else HERE
RES=ROOT/'resources' if (ROOT/'resources').is_dir() else ROOT
sp=importlib.util.spec_from_file_location('h17_xoropp_engine',str(HERE/'k04_pruned_native.py'))
e=importlib.util.module_from_spec(sp);sp.loader.exec_module(e)
P12=(0,1,2,3,22,23,24,25,45,46,47,48)
P16=P12+(4,5,6,7)
PINS={'evidence/print/spool-reconstruction.log':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
      'evidence/recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
      'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'}
ENGINE_SHA=hashlib.sha256((HERE/'k04_pruned_native.py').read_bytes()).hexdigest()

def inverse(a,b):
    t=e.ror(b,28)
    olda=e.ror(a ^ t ^ ((t<<21)&e.M),49)
    return olda,olda^t

def output(state):
    a,b=state
    return (e.rol((a+b)&e.M,17)+a)&e.M

def earlier_bytes(state,n=24,endian='little',order='ba'):
    assert n%2==0 and n>=24
    rev=[];p=state
    for _ in range(n):
        p=inverse(*p)
        rev.append(output(p))
    data=bytearray()
    seq=list(reversed(rev))
    for j in range(0,n,2):
        pair=seq[j:j+2]
        if order=='ba':pair.reverse()
        for word in pair:data.extend(word.to_bytes(8,endian))
    return bytes(data)

def full_hits(state,mask,sha,endian='little',order='ba'):
    raw=earlier_bytes(state,24,endian,order)
    hits=[]
    for offset in range(len(raw)-15):
        coupon=raw[offset:offset+16]
        reduced=bytes(a^b for a,b in zip(coupon,mask))
        if hashlib.sha256(reduced).hexdigest()==sha:
            hits.append((offset,reduced))
    assert len(raw)==192
    return hits

def packet_from_output(state,endian='little',order='ba'):
    a,b=e.stream(*state,2)
    seq=[a,b]
    if order=='ba':seq.reverse()
    return b''.join(v.to_bytes(8,endian) for v in seq)

def parse_packet(line,endian='little',order='ba'):
    packet=bytes.fromhex(re.search(r'\bPAYLOAD=([0-9A-F]{32})\b',line).group(1))
    halves=[int.from_bytes(packet[i:i+8],endian) for i in (0,8)]
    if order=='ba':halves.reverse()
    return halves

def source():
    for rel,digest in PINS.items():
        p=RES/rel
        if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            raise ValueError('Original non-PDF file hash does not match pinned export: '+rel)
    spool=(RES/'evidence/print/spool-reconstruction.log').read_text()
    later=[line for line in spool.splitlines() if 'JOB=PS-261003-0417 ' in line and
           'ATTEMPT=3 ' in line and 'STATE=REQUESTED ' in line and 'CLASS=RECOVER ' in line]
    earlier=[line for line in spool.splitlines() if 'JOB=PS-261003-0417 ' in line and
             'ATTEMPT=1 ' in line and 'STATE=REQUESTED ' in line and 'CLASS=RECOVER ' in line]
    assert len(later)==len(earlier)==1
    route=json.loads((RES/'evidence/recovery-routing.json').read_text())
    acc=json.loads((RES/'acceptance.json').read_text())
    return parse_packet(later[0]),parse_packet(earlier[0]),bytes.fromhex(route['K04']['masked_component']),acc['slot_sha256']['K04']

def private_directory(path):
    p=path.expanduser().absolute()
    if p.is_symlink() or not p.is_dir():raise ValueError('Existing non-symlink 0700 private directory required')
    if p.stat().st_mode & 0o077:raise ValueError('Private directory has group/other permission')
    if p.resolve()==ROOT or ROOT in p.resolve().parents:raise ValueError('Private store cannot be within repository')
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):raise ValueError('Historical source scanning forbidden in CI')
    return p

def atomic(path,data):
    temporary=path.with_name(path.name+'.tmp.'+str(os.getpid()))
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(data,f,sort_keys=True,separators=(',',':'))
            f.flush();os.fsync(f.fileno())
        os.replace(temporary,path)
    finally:
        if temporary.exists():temporary.unlink()

def stamp(endian,order,positions=P16):
    obj={'input_sha256':PINS,'engine_sha256':ENGINE_SHA,'source_packet':'PS-261003-0417 REQUESTED3',
         'generator':'xoroshiro128++ 1.0','endianness':endian,'order':order,'P16':tuple(positions),'schema':1}
    return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()

def private_coupon(path,offset,reduced,slot):
    value={'component':'K04','K04':reduced.hex().upper(),'preceding_stream_byte_offset':offset,'source':'later-first local conditional'}
    if path.exists():
        x=json.loads(path.read_text())
        if x['K04']!=value['K04']:raise ValueError('Divergent original K04 hits, inspect privately')
        return
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:json.dump(value,f)

def run(lo,count,store,ms=350,retry_ms=700,max_models=32,endian='little',order='ba',extra_bits=(4,5,6,7)):
    if not (0<=lo<4096 and 1<=count<=4096-lo and 100<=ms<=retry_ms<=30000 and 1<=max_models<=1024):
        raise ValueError('Invalid range/timeout/model parameters')
    folder=private_directory(store)
    extra_bits=tuple(extra_bits)
    if len(extra_bits)!=4 or len(set(extra_bits))!=4 or any(not (0<=p<64) or p in P12 for p in extra_bits):
        raise ValueError('Four distinct additional bits outside P12 required')
    positions=P12+extra_bits
    first,earlier,mask,target=source()
    label=stamp(endian,order,positions)
    obs={0:first[0],1:first[1]}
    counts={'parents':0,'children':0,'cached_complete':0,'terminal_unsat_no_state':0,
            'terminal_with_state':0,'unknown':0,'states_examined':0,'candidate_windows':0,
            'actual_hash_hits':0,'earlier_replay_hits':0,'retry_children':0}
    t0=time.monotonic()
    for parent in range(lo,lo+count):
        counts['parents']+=1
        for child in range(16):
            cube=parent|(child<<12)
            marker='' if extra_bits==(4,5,6,7) else 'extra_'+('_'.join(map(str,extra_bits)))+'_'
            path=folder/f'{marker}cube_{cube:05d}.json'
            rec=None
            if path.exists():
                if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('Unsafe private cube file')
                rec=json.loads(path.read_text())
                if rec.get('stamp')!=label or rec.get('cube')!=cube:raise ValueError('Incompatible cached circuit/source/layout')
                if rec['terminal']=='unsat':counts['cached_complete']+=1
            if rec is None or rec['terminal']=='unknown':
                fixed=sum(((cube>>j)&1)<<bit for j,bit in enumerate(positions))
                states,status=e.solve(obs,fixed,positions,ms,True)
                if status=='unknown' and retry_ms>ms:
                    counts['retry_children']+=1
                    more,new_status=e.solve(obs,fixed,positions,retry_ms,True)
                    states=list(set(states).union(more));status=new_status
                oldstates=[(int(a,16),int(b,16)) for a,b in rec.get('states',[])] if rec else []
                states=sorted(set(states).union(oldstates))
                if status=='unsat' or states:
                    for s in states:assert e.stream(*s,2)==first
                rec={'cube':cube,'stamp':label,'terminal':status,
                     'states':[[f'{a:016X}',f'{b:016X}'] for a,b in states]}
                atomic(path,rec)
            states=[(int(a,16),int(b,16)) for a,b in rec['states']]
            counts['children']+=1
            counts['states_examined']+=len(states)
            if rec['terminal']=='unknown':counts['unknown']+=1
            elif states:counts['terminal_with_state']+=1
            else:counts['terminal_unsat_no_state']+=1
            for state in states:
                hits=full_hits(state,mask,target,endian,order)
                counts['candidate_windows']+=177
                counts['actual_hash_hits']+=len(hits)
                for offset,reduced in hits:
                    private_coupon(folder/'K04_ORIGINAL_HASH_HIT.json',offset,reduced,'K04')
                # A separate generator-continuity diagnostic; never veto target hits.
                rev=[];cur=state
                for j in range(24):
                    cur=inverse(*cur);rev.append(output(cur))
                # A source-requested prior pair may be earlier than our 24-word view.
                chronological=list(reversed(rev))
                counts['earlier_replay_hits']+=int(any(chronological[k:k+2]==earlier for k in range(23)))
    print(json.dumps({'run':'agent8-laterfirst-littleBA','extra_bits':extra_bits,'range':[lo,lo+count],
                      'time_ms':[ms,retry_ms],'elapsed_s':round(time.monotonic()-t0,3),
                      'aggregates':counts,'no_historical_payload_printed':True},sort_keys=True),flush=True)
    return counts

def synthetic():
    import random
    rng=random.Random(202611281035)
    fixtures=0;checked=0
    for endian in ('big','little'):
        for order in ('ab','ba'):
            for k in range(8):
                past=(rng.getrandbits(64),rng.getrandbits(64))
                later=past
                for j in range(24):
                    # advancing from earliest state to later first output state
                    a,b=later;t=a^b
                    later=(e.rol(a,49)^t^((t<<21)&e.M),e.rol(t,28))
                raw=earlier_bytes(later,24,endian,order)
                assert len(raw)==192
                direct=[];s=past
                for _ in range(24):
                    direct.append(output(s))
                    a,b=s;t=a^b
                    s=(e.rol(a,49)^t^((t<<21)&e.M),e.rol(t,28))
                assert s==later
                serialized=bytearray()
                for i in range(0,24,2):
                    pair=direct[i:i+2]
                    if order=='ba':pair.reverse()
                    serialized.extend(b''.join(word.to_bytes(8,endian) for word in pair))
                assert bytes(serialized)==raw
                # Fresh independent state controls both inverse and forward replay.
                assert past==iterative_inverse(later,24)
                mask=rng.randbytes(16)
                positions=(0,1,2,7,16,32,48,64,80,96,112,128,144,160,176)
                for offset in positions:
                    want=bytes(x^y for x,y in zip(raw[offset:offset+16],mask))
                    target=hashlib.sha256(want).hexdigest()
                    hits=full_hits(later,mask,target,endian,order)
                    assert (offset,want) in hits and len(hits)==1
                    checked+=1
                fixtures+=1
    print(json.dumps({'synthetic_fixtures':fixtures,'source_free_original_style_hits':checked,
                      'inverse_roundtrip':True,'historical_key_recovered':False},sort_keys=True),flush=True)

def run_fast_first(lo,count,store,ms=3000,max_models=32,retry_unknown=False):
    """Candidate-latency-first scan of all P12 parent cubes; UNKNOWN remains open."""
    if not(0<=lo<4096 and 1<=count<=4096-lo and 100<=ms<=30000):
        raise ValueError('Invalid P12 coverage')
    folder=private_directory(store)
    first,earlier,mask,target=source()
    base=stamp('little','ba')+'-P12-FASTFIRST-v1'
    label=hashlib.sha256(base.encode()).hexdigest()
    obs={0:first[0],1:first[1]}
    counts={'visited':0,'terminal_no_state_unsat':0,'terminal_state_unsat':0,'unknown':0,
            'states_examined':0,'commitment_windows':0,'original_k04_hits':0,'earlier_holdout_replays':0,'resumed':0}
    start=time.monotonic()
    for parent in range(lo,lo+count):
        path=folder/f'fastfirst_{parent:04d}.json'
        rec=None
        if path.exists():
            if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('Unsafe cache')
            rec=json.loads(path.read_text())
            if rec.get('stamp')!=label or rec.get('parent')!=parent:raise ValueError('Stale incompatible P12 cache')
            counts['resumed']+=1
        if rec is None or (retry_unknown and rec['terminal']=='unknown'):
            fixed=sum(((parent>>j)&1)<<bit for j,bit in enumerate(P12))
            states,status=e.solve(obs,fixed,P12,ms,True)
            old=[(int(a,16),int(b,16)) for a,b in rec['states']] if rec else []
            states=sorted(set(states).union(old))
            rec={'parent':parent,'stamp':label,'terminal':status,
                 'states':[[f'{a:016X}',f'{b:016X}'] for a,b in states]}
            atomic(path,rec)
        states=[(int(a,16),int(b,16)) for a,b in rec['states']]
        counts['visited']+=1
        counts['states_examined']+=len(states)
        if rec['terminal']=='unknown':counts['unknown']+=1
        elif states:counts['terminal_state_unsat']+=1
        else:counts['terminal_no_state_unsat']+=1
        for state in states:
            counts['commitment_windows']+=177
            hits=full_hits(state,mask,target,'little','ba')
            counts['original_k04_hits']+=len(hits)
            for offset,reduced in hits:
                private_coupon(folder/'K04_ORIGINAL_HASH_HIT.json',offset,reduced,'K04')
            p=state;prior=[]
            for j in range(24):p=inverse(*p);prior.append(output(p))
            chronological=list(reversed(prior))
            counts['earlier_holdout_replays']+=int(any(chronological[k:k+2]==earlier for k in range(23)))
        if counts['visited']%50==0 or counts['visited']==count:
            print(json.dumps({'phase':'laterfirst-P12-fastfirst-littleBA','range':[lo,lo+count],
                              'elapsed_s':round(time.monotonic()-start,2),
                              'original_payloads_printed':False,'aggregates':counts},sort_keys=True),flush=True)
    return counts

def ledger_coverage(store,fast_first=False,extra_bits=(4,5,6,7)):
    """Private local ledger summary, no original-source loading or model disclosure."""
    folder=private_directory(store)
    extra_bits=tuple(extra_bits)
    if len(extra_bits)!=4 or len(set(extra_bits))!=4 or any(not (0<=b<64) or b in P12 for b in extra_bits):
        raise ValueError('Four distinct extra state bits required')
    label=hashlib.sha256((stamp('little','ba')+'-P12-FASTFIRST-v1').encode()).hexdigest() if fast_first else stamp('little','ba',P12+extra_bits)
    expected=4096 if fast_first else 65536
    prefix='' if extra_bits==(4,5,6,7) else 'extra_'+('_'.join(map(str,extra_bits)))+'_'
    counts={'expected':expected,'visited':0,'terminal_unsat_empty':0,'terminal_unsat_with_states':0,
            'open_unknown':0,'states_cached':0,'unvisited':0}
    for idx in range(expected):
        path=folder/(f'fastfirst_{idx:04d}.json' if fast_first else f'{prefix}cube_{idx:05d}.json')
        if not path.exists():
            counts['unvisited']+=1;continue
        if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('Unsafe private ledger entry')
        rec=json.loads(path.read_text())
        if rec.get('stamp')!=label or rec.get('parent' if fast_first else 'cube')!=idx:
            raise ValueError('Mismatched ledger source/circuit/layout/coordinate fingerprint')
        counts['visited']+=1
        n=len(rec['states']);counts['states_cached']+=n
        if rec['terminal']=='unknown':counts['open_unknown']+=1
        elif rec['terminal']=='unsat':counts['terminal_unsat_with_states' if n else 'terminal_unsat_empty']+=1
        else:raise ValueError('Invalid terminal status')
    assert counts['visited']+counts['unvisited']==expected
    print(json.dumps({'ledger_scope':'P12 candidate-first' if fast_first else 'P16 disjoint child',
                      'extra_bits':extra_bits if not fast_first else None,
                      'method_only':True,'original_source_or_state_values_printed':False,
                      'aggregate':counts},sort_keys=True),flush=True)
    return counts

def iterative_inverse(state,n):
    for _ in range(n):state=inverse(*state)
    return state

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--synthetic',action='store_true')
    p.add_argument('--coverage',action='store_true',help='aggregate private ledger status without loading historical sources')
    p.add_argument('--fast-first',action='store_true')
    p.add_argument('--retry-unknown',action='store_true',help='explicitly rerun previously UNKNOWN P12 cubes; default first pass skips them')
    p.add_argument('--p16-extra-bits',default='4,5,6,7',help='four extra initial-a0 bit positions for disjoint P16 partition')
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=16)
    p.add_argument('--private-dir',type=Path)
    p.add_argument('--timeout-ms',type=int,default=350)
    p.add_argument('--retry-ms',type=int,default=700)
    args=p.parse_args()
    if args.synthetic:synthetic()
    else:
        if not args.private_dir:p.error('--private-dir required and must be outside repo, mode 0700')
        extra=tuple(int(x) for x in args.p16_extra_bits.split(','))
        if args.coverage:ledger_coverage(args.private_dir,args.fast_first,extra)
        elif args.fast_first:run_fast_first(args.start,args.count,args.private_dir,max(3000,args.timeout_ms),retry_unknown=args.retry_unknown)
        else:run(args.start,args.count,args.private_dir,args.timeout_ms,args.retry_ms,extra_bits=extra)
