"""Source-only two-pair rejection of original MT_sgenrand 1998 seeding.
Run: python agents/agent33/h17_mt1998_two_pair_source_sft.py original-ZIP
Uses original intact printer source, never selected ACK payload or any target hash.
"""
import hashlib
import re
import secrets
import sys
import zipfile
from pathlib import Path
from h17_r_mt_lcg_firstcycle_sft import STARTS, untemper, MAG, PIN

ORIGIN = -1100
END = max(STARTS)+3
U = 0xffffffff


def lcg(x):
    return (69069*x+1)&U


def old_pair(x):
    """Two adjacent initialized native MT_sgenrand 1998 words."""
    y=lcg(x)
    z=lcg(y)
    w=lcg(z)
    return (x&0xffff0000)|(y>>16),(z&0xffff0000)|(w>>16)


def recover_old_pair(w0,w1):
    """Exhaust all 65536 possible low halves of the preceding LCG word."""
    solutions=[]
    for low in range(65536):
        x=(w0&0xffff0000)|low
        y=lcg(x)
        if y>>16!=(w0&0xffff):continue
        if old_pair(x)[1]==w1:solutions.append(x)
    return solutions


class Basis:
    def __init__(self):
        self.rows={}

    def reduce(self,v):
        b=0
        while v:
            j=v.bit_length()-1
            if j not in self.rows:break
            w,c=self.rows[j];v^=w;b^=c
        return v,b

    def insert(self,v,b):
        v,c=self.reduce(v)
        b^=c
        assert v or not b
        if v:self.rows[v.bit_length()-1]=(v,b)

    def fully(self,v):
        b=0
        while v:
            j=v.bit_length()-1
            if j not in self.rows:
                r,c=self.fully(v&((1<<j)-1))
                return (1<<j)|r,b^c
            w,c=self.rows[j];v^=w;b^=c
        return 0,b


def source_basis(archive):
    with zipfile.ZipFile(archive) as z:
        data=z.read('evidence/print/spool-reconstruction.log')
    assert hashlib.sha256(data).hexdigest()==PIN
    lines=[line for line in data.decode().splitlines() if line.startswith('2026-')]
    assert len(lines)==133
    assert lines[129].startswith('2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER ')

    symbols=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
    for i in range(624,END-ORIGIN+1):
        t=i-624
        symbols.append([
            symbols[t+397][j] ^
            (symbols[t][31] if j==30 else (symbols[t+1][j+1] if j<30 else 0)) ^
            (symbols[t+1][0] if (MAG>>j)&1 else 0)
            for j in range(32)
        ])

    def sym(stage):
        return symbols[stage-ORIGIN]

    basis=Basis()
    for row,(line,first) in enumerate(zip(lines,STARTS)):
        if row==129:continue
        m=re.search(r'PAYLOAD=([0-9A-F]{32})',line)
        assert m
        packet=bytes.fromhex(m.group(1))
        for lane in range(4):
            word=untemper(int.from_bytes(packet[4*lane:4*lane+4],'little'))
            for bit,v in enumerate(sym(first+lane)):
                basis.insert(v,(word>>bit)&1)
    assert len(basis.rows)==15365

    # Nonzero original right-hand-side validation, five complete intact jobs.
    for row in (0,27,128,130,132):
        m=re.search(r'PAYLOAD=([0-9A-F]{32})',lines[row])
        assert m
        packet=bytes.fromhex(m.group(1))
        for lane in range(4):
            word=untemper(int.from_bytes(packet[4*lane:4*lane+4],'little'))
            assert all(basis.fully(v)==(0,(word>>bit)&1)
                       for bit,v in enumerate(sym(STARTS[row]+lane)))

    def exact(stage):
        vals=[basis.fully(v) for v in sym(stage)]
        assert all(v==0 for v,b in vals),('not fixed',stage)
        return sum(b<<i for i,(v,b) in enumerate(vals))

    return exact


def main(archive):
    for _ in range(16):
        x=secrets.randbits(32)
        a,b=old_pair(x)
        assert x in recover_old_pair(a,b)
    print('Generated historical 1998 initializer pair controls: 16/16 PASS')

    exact=source_basis(archive)
    pairs={-852:(exact(-852),exact(-851)),
           -408:(exact(-408),exact(-407))}
    assert pairs=={-852:(0x4efb91af,0xa49a9182),
                   -408:(0xfa497031,0x8fe22d44)}
    assert all(not recover_old_pair(*pair) for pair in pairs.values())

    coverage={phi for phi in range(624)
              if any(-624-phi<=stage and stage+1<=-1-phi for stage in pairs)}
    assert len(coverage)==624
    print('Original source-fixed pairs:',{
        stage:tuple(f'{v:08X}' for v in pair) for stage,pair in pairs.items()})
    print('First-cycle origin phases excluded:',len(coverage),'/624')
    print('Original source-compatible 1998 initialized-state pairs: 0/2')
    print('No physical coupon bytes or author-final words recovered')


if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('Usage: python h17_mt1998_two_pair_source_sft.py original-ZIP')
    main(Path(sys.argv[1]))
