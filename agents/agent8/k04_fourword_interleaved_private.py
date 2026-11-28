#!/usr/bin/env python3
"""K04 full-component four-word copy-stage reducer; source-compatible state PRIVATE.

Exploratory conditional printer interpretation: contiguous or regularly strided
four 32-bit words, all 24 word orders, and all 16 combinations of individual
four-byte word reversals. Source-free synthetic positive controls; original
mode checks the original K04 full SHA after route XOR, before optional holdouts.
No copied ACK2, PDF, or original source bytes/state in stdout or public CI.
"""
import argparse, hashlib, itertools, json, os, random
from pathlib import Path

PERM=tuple(itertools.permutations(range(4)))

def layouts(raw):
    assert len(raw)==192
    for offset in range(len(raw)-15):
        yield ('contiguous',offset,tuple(raw[offset+j:offset+j+4] for j in (0,4,8,12)))
    words=tuple(raw[j:j+4] for j in range(0,len(raw),4))
    for stride in range(2,9):
        for first in range(len(words)-3*stride):
            yield ('stride',(stride,first),tuple(words[first+j*stride] for j in range(4)))

def emit(words,perm,reversals):
    return b''.join((words[p][::-1] if (reversals>>j)&1 else words[p])
                    for j,p in enumerate(perm))

def exhaustive(raw,mask,target):
    counts={'contiguous_layouts':0,'strided_layouts':0,'complete_SHA256_checks':0,
            'original_commitment_hits':0}
    hits=[]
    for kind,loc,words in layouts(raw):
        counts['contiguous_layouts' if kind=='contiguous' else 'strided_layouts']+=1
        for perm in PERM:
            for flip in range(16):
                coupon=emit(words,perm,flip)
                component=bytes(x^y for x,y in zip(coupon,mask))
                counts['complete_SHA256_checks']+=1
                if hashlib.sha256(component).hexdigest()==target:
                    counts['original_commitment_hits']+=1
                    hits.append((kind,loc,perm,flip,component.hex().upper()))
    assert counts['complete_SHA256_checks']==156672
    return counts,hits

def synthetic():
    # Pure stream functions import mathematical generator code; no originals
    # are opened by forward_bytes or the source-free fixture generator.
    from k04_bigba_forward177_replay import forward_bytes
    rng=random.Random(202611281158)
    total=0
    for case in range(6):
        raw=forward_bytes((rng.getrandbits(64),rng.getrandbits(64)))
        candidates=tuple(layouts(raw))
        for idx in (case*29,177+case*14,180+case*22):
            kind,loc,words=candidates[idx]
            perm=PERM[(case*5+total)%24];rev=(case*7+total)%16
            coupon=emit(words,perm,rev)
            mask=rng.randbytes(16)
            component=bytes(a^b for a,b in zip(coupon,mask))
            target=hashlib.sha256(component).hexdigest()
            counts,hits=exhaustive(raw,mask,target)
            assert len(hits)==counts['original_commitment_hits']==1
            assert hits[0]==(kind,loc,perm,rev,component.hex().upper())
            total+=1
    print(json.dumps({'synthetic_only':True,'complete_full_SHA256_positive_controls':total,
                      'historical_source_read':False},sort_keys=True))

def original(statefile,private_dir):
    if os.environ.get('GITHUB_ACTIONS') or os.environ.get('GITHUB_REPOSITORY'):
        raise RuntimeError('Historical data forbidden in public GitHub Actions')
    if statefile.is_symlink() or not statefile.is_file() or statefile.stat().st_mode&0o077:
        raise ValueError('Expect private nonsymlink 0600 state cache')
    if private_dir.is_symlink() or not private_dir.is_dir() or private_dir.stat().st_mode&0o077:
        raise ValueError('Expect private nonsymlink 0700 output directory')
    from k04_bigba_forward177_replay import forward_bytes,source
    from k04_reverse_littleba_private import e
    first,mask,target=source()  # source hashes pinned; REQUESTED1 only
    src=json.loads(statefile.read_text())
    if len(src)!=1 or len(src[0])!=2:raise ValueError('Expected one complete source-compatible state')
    s=tuple(int(x,16) if isinstance(x,str) else int(x) for x in src[0])
    assert e.stream(*s,2)==first
    counts,hits=exhaustive(forward_bytes(s),mask,target)
    if hits:
        out=private_dir/'K04_wordlane_original_hits.json'
        fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'w') as f:
            json.dump({'conditional_model':'firstpacket big/BA','hits':hits},f)
    print(json.dumps({'source':'firstpacket big/BA parent1371',
          'model':'contiguous or stride2..8 32bit 4word copies, permutations/reversals',
          'original_bytes_or_states_printed':False,'counters':counts},sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--synthetic',action='store_true')
    p.add_argument('--state-file',type=Path)
    p.add_argument('--private-dir',type=Path)
    a=p.parse_args()
    if a.synthetic:synthetic()
    else:
        if not a.state_file or not a.private_dir:p.error('Private state and output paths required')
        original(a.state_file,a.private_dir)
