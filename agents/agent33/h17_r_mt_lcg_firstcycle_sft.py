"""R RNG_Init LCG to MT19937, source-only first-cycle inversion.

Run: python agents/agent33/h17_r_mt_lcg_firstcycle_sft.py <original-ZIP>
No acceptance hash, route mask or selected ACK payload enters the test.
"""
import hashlib
import re
import secrets
import sys
import time
import zipfile
from pathlib import Path

U = 0xffffffff
A = 69069
MAG = 0x9908b0df
IA = pow(A, -1, 1 << 32)
PIN = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,
          154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,
          272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,
          401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,
          531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,
          658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,
          788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,
          912,918,924,930,936,942,947,951,955,959,963]
assert len(STARTS) == 133


def advance(x, n):
    """LCG affine power f(x)=69069*x+1, including inverse powers."""
    if n < 0:
        a, c, n = IA, (-IA)&U, -n
    else:
        a, c = A, 1
    while n:
        if n & 1: x = (a*x+c)&U
        c = (a*c+c)&U
        a = (a*a)&U
        n >>= 1
    return x


def untemper(x):
    for k, left, mask in ((18,False,U),(15,True,0xefc60000),
                          (7,True,0x9d2c5680),(11,False,U)):
        y = x
        for _ in range(6): y = x ^ (((y<<k)&mask) if left else y>>k)
        x = y&U
    return x


def twist(state):
    """Independent reference in-place MT19937 twist."""
    state = state.copy()
    for j in range(624):
        y = (state[j]&0x80000000)|(state[(j+1)%624]&0x7fffffff)
        state[j] = (state[(j+397)%624]^(y>>1)^(MAG if y&1 else 0))&U
    return state


def first_cycle(seed):
    return twist([advance(seed,j) for j in range(624)])


COEFS = []
a,c = 1,0
for _ in range(1021):
    COEFS.append((a,c))
    a,c = a*A&U,(c*A+1)&U


def native(j,seed):
    """First-cycle native MT state as function of 32bit initial LCG word."""
    def p(k):
        a,c = COEFS[k]
        return (a*seed+c)&U
    def g(k):
        x,y = p(k),p(k+1)
        q = (x&0x80000000)|(y&0x7fffffff)
        return (q>>1)^(MAG if y&1 else 0)
    if j<=226: return p(j+397)^g(j)
    if j<=453: return p(j+170)^g(j-227)^g(j)
    if j<=622: return p(j-57)^g(j-454)^g(j-227)^g(j)
    first = p(397)^g(0)
    q = (p(623)&0x80000000)|(first&0x7fffffff)
    return p(566)^g(169)^g(396)^(q>>1)^(MAG if q&1 else 0)


def recover_low_phase(j,target):
    """Invert a native word at j=0..226, enumerating only its first bit."""
    def f(x):
        nxt = advance(x,1)
        q = (x&0x80000000)|(nxt&0x7fffffff)
        return advance(x,397)^(q>>1)^(MAG if nxt&1 else 0)
    solutions = []
    for first_bit in (0,1):
        x = first_bit
        for bit in range(31):
            if ((f(x)^target)>>bit)&1: x |= 1<<(bit+1)
        if f(x)==target: solutions.append(advance(x,-j))
    return solutions


def invert_firstcycle(obs):
    """Bitwise lift of first-cycle R LCGenerator, all possible 32bit roots."""
    no_wrap = [(j,v) for j,v in obs if j!=623]
    if no_wrap:
        known,offset,stages,roots = no_wrap,1,31,[0,1]
    else:
        known,offset,stages,roots = obs,2,30,[0,1,2,3]
    for bit in range(stages):
        mask = (1<<(bit+1))-1
        roots = [y for x in roots for y in (x,x|(1<<(bit+offset)))
                 if all(((native(j,y)^v)&mask)==0 for j,v in known)]
        if not roots: break
        assert len(roots)<100000
    return [x for x in roots if all(native(j,x)==v for j,v in obs)]


def source_rows(archive):
    with zipfile.ZipFile(archive) as z:
        original = z.read('evidence/print/spool-reconstruction.log')
    assert hashlib.sha256(original).hexdigest()==PIN
    lines = [x for x in original.decode().splitlines() if x.startswith('2026-')]
    assert len(lines)==133
    assert lines[129].startswith('2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER ')
    rows = []
    for index,(line,position) in enumerate(zip(lines,STARTS)):
        if index==129: continue
        m = re.search(r'PAYLOAD=([0-9A-F]{32})',line)
        assert m
        packet = bytes.fromhex(m.group(1))
        for lane in range(4):
            v = untemper(int.from_bytes(packet[4*lane:4*lane+4],'little'))
            rows.append((position+lane,v,index,lane))
    assert len(rows)==528
    return rows


def test_synthetic():
    for trial in range(4):
        seed = secrets.randbits(32)
        first = first_cycle(seed)
        assert all(native(j,seed)==first[j] for j in range(624))
        for phase in (0,7,226,227,452,453,454,553,621,622,623):
            obs = [(phase+s+i,first[phase+s+i]) for s in STARTS for i in range(4)
                   if phase+s+i<624]
            roots = recover_low_phase(*obs[0]) if phase<=226 else invert_firstcycle(obs[:8])
            assert seed in roots,(trial,phase,roots)
    print('Generated R MT controls: 44/44 exact seed/phase recoveries PASS')


def run(archive):
    started = time.perf_counter()
    test_synthetic()
    rows = source_rows(archive)
    survived = []
    initial_roots = 0
    for phase in range(624):
        obs = [(phase+s,v) for s,v,_,_ in rows if phase+s<624]
        assert obs
        roots = recover_low_phase(*obs[0]) if phase<=226 else invert_firstcycle(obs[:8])
        initial_roots += len(roots)
        for root in roots:
            if all(native(j,root)==v for j,v in obs):
                survived.append((phase,root,len(obs)))
    assert not survived,survived
    print('Source original unselected MT observations:',len(rows))
    print('All 624 first-cycle origin phases tested; surviving 32bit seed/phase pairs:',len(survived))
    print('Roots of initial source sample:',initial_roots)
    print('Elapsed:',round(time.perf_counter()-started,3),'sec')
    print('Scope: only R RNG_Init single-seed LCG state, direct 32bit tempered output, p951 placement.')


if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('Usage: python h17_r_mt_lcg_firstcycle_sft.py original-ZIP')
    run(Path(sys.argv[1]))
