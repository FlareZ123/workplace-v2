"""Source-pinned rejection of unknown a,c affine MT pre-state initialization.
Run: python agents/agent33/h17_mt_unknown_affine_four_state_sft.py original-ZIP
Historical selected ACK row129 is excluded by source_basis; no target hashes.
"""
import secrets
import sys
from pathlib import Path
from h17_mt1998_two_pair_source_sft import source_basis

MOD = 1<<32
U = MOD-1


def inverse_affine4(v):
    """Solve all modular a,c such that next=(a*previous+c) mod 2**32."""
    d=[(v[i+1]-v[i])&U for i in range(3)]
    eq=[]
    for x,y in ((d[0],d[1]),(d[1],d[2])):
        g=MOD if x==0 else x&-x
        if y%g:return None
        m=MOD//g
        a=0 if m==1 else (y//g)*pow(x//g,-1,m)%m
        eq.append((a,m))
    (a0,m0),(a1,m1)=eq
    if (a0-a1)%min(m0,m1):return None
    a=a0 if m0>=m1 else a1
    c=(v[1]-a*v[0])&U
    assert all((a*v[i]+c)&U==v[i+1] for i in range(3))
    return a,c


def main(archive):
    for _ in range(100):
        a=secrets.randbits(32);c=secrets.randbits(32)
        x=secrets.randbits(32)
        values=[x]
        for _ in range(3):values.append((a*values[-1]+c)&U)
        assert inverse_affine4(values) is not None
    print('Generated arbitrary 32bit affine-state positive controls: 100/100 PASS')

    fixed=source_basis(archive)
    pairs={stage:tuple(fixed(stage+i) for i in range(4))
           for stage in (-685,-622)}
    assert pairs=={
        -685:(0xd045fc16,0x373998d4,0x606fb254,0x57e650e4),
        -622:(0xe32e1557,0x3152e7cb,0xbbdd46a0,0x9027419f)}
    assert all(inverse_affine4(w) is None for w in pairs.values())
    covered={phi for phi in range(624)
             if any(-624-phi<=stage and stage+3<=-1-phi for stage in pairs)}
    assert len(covered)==624
    print('Exact original source-fixed four-word runs:',
          {k:tuple(f'{n:08X}' for n in v) for k,v in pairs.items()})
    print('Conditional unknown-a,c affine native initializers excluded over',
          len(covered),'first-cycle alignments')
    print('No missing recovery component or original selected coupon recovered')


if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('Usage: python h17_mt_unknown_affine_four_state_sft.py original-ZIP')
    main(Path(sys.argv[1]))
