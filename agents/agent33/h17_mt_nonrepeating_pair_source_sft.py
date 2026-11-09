"""Original H17 MT p951 source-only paired-field screen. Run with python script.py [unpacked_archive_root]."""
from pathlib import Path
from collections import Counter
import hashlib, re, time, sys, json
start = time.perf_counter()
root = (Path(sys.argv[1]).resolve()/'evidence') if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources/evidence'
U=0xffffffff
MAG=0x9908b0df
starts=[0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
def untemper(x):
    for k,left,m in ((18,False,U),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,U)):
        y=x
        for _ in range(6):
            y=x^(((y<<k)&m) if left else y>>k)
        x=y&U
    return x
ORIGIN,LAST=-1100,1040
# An arbitrary 624-word native MT state, with exact 397/624 twist recurrence.
a=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
for i in range(624,LAST-ORIGIN+1):
    t=i-624
    a.append([a[t+397][j]^(a[t][31] if j==30 else (a[t+1][j+1] if j<30 else 0))^(a[t+1][0] if (MAG>>j)&1 else 0) for j in range(32)])
assert len(a)==2141
def sym(stage,tempered=False):
    v=a[stage-ORIGIN]
    if not tempered:return v
    p=[v[j]^(v[j+11] if j+11<32 else 0) for j in range(32)]
    q=[p[j]^(p[j-7] if j>=7 and (0x9d2c5680>>j)&1 else 0) for j in range(32)]
    r=[q[j]^(q[j-15] if j>=15 and (0xefc60000>>j)&1 else 0) for j in range(32)]
    return [r[j]^(r[j+18] if j+18<32 else 0) for j in range(32)]
class Basis:
    def __init__(self):self.rows={}
    def insert(self,v,b):
        v,c=self.reduce(v)
        b^=c
        assert v or not b
        if v:self.rows[v.bit_length()-1]=(v,b)
    def reduce(self,v):
        b=0
        while v:
            p=v.bit_length()-1
            if p not in self.rows:break
            w,c=self.rows[p];v^=w;b^=c
        return v,b
    def fully_reduce(self,v):
        b=0
        while v:
            p=v.bit_length()-1
            if p not in self.rows:
                sub,c=self.fully_reduce(v&((1<<p)-1))
                return (1<<p)|sub,b^c
            w,c=self.rows[p];v^=w;b^=c
        return 0,b
spool=root/'print/spool-reconstruction.log'
assert hashlib.sha256(spool.read_bytes()).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
lines=[line for line in spool.read_text().splitlines() if line.startswith('2026-')]
assert len(lines)==133
route=json.loads((root/'recovery-routing.json').read_text())
assert route['K04']['source'].startswith('escrow coupon')
assert b'ESC-N=PS-261003-0417' in (root/'archive-labels.ini').read_bytes()
assert lines[129].startswith('2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER ')
basis=Basis()
for row,(line,offset) in enumerate(zip(lines,starts)):
    if row==129:continue
    payload=bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})',line).group(1))
    for lane in range(4):
        x=untemper(int.from_bytes(payload[4*lane:4*lane+4],'little'))
        for j,v in enumerate(sym(offset+lane)):
            basis.insert(v,(x>>j)&1)
assert len(basis.rows)==15365
# Nonzero, independently observed source bits must survive equation reduction.
# This control catches accidentally dropping the RHS during basis insertion.
for row in (0, 27, 128, 130, 132):
    payload=bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})',lines[row]).group(1))
    for lane in range(4):
        x=untemper(int.from_bytes(payload[4*lane:4*lane+4],'little'))
        assert all(basis.fully_reduce(v)==(0,(x>>j)&1) for j,v in enumerate(sym(starts[row]+lane)))
print('Original MT source rank',len(basis.rows))
def syndrome(stage,tempered):
    values=sym(stage,tempered)+sym(stage+227,tempered)
    eqs=[basis.fully_reduce(v) for v in values]
    table={}; constraints=[]
    for j,(r,c) in enumerate(eqs):
        mask=1<<j
        while r:
            p=r.bit_length()-1
            if p not in table:
                table[p]=(r,mask,c)
                break
            w,m,z=table[p];r^=w;mask^=m;c^=z
        else:
            constraints.append((mask,c))
    return constraints
def fixed_bits(stage,mode):
    table={}
    for vv in sym(stage,mode):
        rr,_=basis.fully_reduce(vv)
        while rr:
            p=rr.bit_length()-1
            if p not in table:table[p]=rr;break
            rr^=table[p]
    return 32-len(table)
models=[]
for mode in (False,True):
    for t in range(ORIGIN,LAST-226):
        eqs=syndrome(t,mode)
        if len(eqs)>=24 and fixed_bits(t,mode)<=12 and fixed_bits(t+227,mode)<=12:
            models.append((t,mode,eqs))
assert len(models)==286
print('Original pair systems',len(models),'native/tempered',Counter(mode for _,mode,_ in models))
sourcefiles=[]
for p in sorted(root.rglob('*')):
    if not p.is_file() or p.suffix.lower()=='.pdf':continue
    data=p.read_bytes()
    if p==spool:data='\n'.join(line for i,line in enumerate(lines) if i!=129).encode()
    sourcefiles.append((p.relative_to(root).as_posix(),'raw',data))
    for m in re.finditer(rb'(?<![0-9a-fA-F])[0-9a-fA-F]{16,}(?![0-9a-fA-F])',data):
        h=m.group()
        sourcefiles.append((p.relative_to(root).as_posix(),f'hex@{m.start()}',bytes.fromhex(h[:len(h)//2*2].decode())))
fragments={}
for name,fmt,data in sourcefiles:
    if name=='print/spool-reconstruction.log':continue
    for i in range(len(data)-7):
        word=data[i:i+8]
        if word[:4]==word[4:]:continue
        if word not in fragments:fragments[word]=(name,fmt,i)
assert len(fragments)==34717,len(fragments)
variants=[]
for frag,(name,fmt,offset) in fragments.items():
    for endian in ('little','big'):
        w0=int.from_bytes(frag[:4],endian);w1=int.from_bytes(frag[4:],endian)
        variants.append((w0|(w1<<32),name,fmt,offset,endian,'raw'))
        variants.append((untemper(w0)|(untemper(w1)<<32),name,fmt,offset,endian,'untempered'))
assert len(variants)==138868
print('Original nonrepeating eightbyte fragments',len(fragments),'four views',len(variants))
hits=[];screens=0
for ti,(stage,mode,eqs) in enumerate(models):
    for value,name,fmt,offset,endian,encoding in variants:
        screens+=1
        if all((value&mask).bit_count()%2==bit for mask,bit in eqs):
            hits.append((stage,mode,name,fmt,offset,endian,encoding))
    if ti%80==0:print('Stage progress',ti,'/',len(models),'matches',len(hits),flush=True)
assert screens==39716248,screens
assert not hits,hits[:5]
print('Original source exact pair tests',screens,'hits',len(hits),'elapsed',round(time.perf_counter()-start,2))
def plant_valid(eqs):
    table={}
    for mask,bit in eqs:
        while mask:
            p=mask.bit_length()-1
            if p not in table:table[p]=(mask,bit);break
            v,c=table[p];mask^=v;bit^=c
        else:assert bit==0
    selected=sum(1<<p for p in table)
    value=0x6a2bd20e95e13c7f&~selected
    for p in sorted(table):
        mask,bit=table[p]
        value|=(bit^((value&(mask^(1<<p))).bit_count()&1))<<p
    assert all((value&mask).bit_count()%2==bit for mask,bit in eqs)
    return value
chosen=next(x for x in models if x[1] and sum((mask&U)==(mask>>32) and bit==0 for mask,bit in x[2])<24)
t,mode,eqs=chosen
planted=plant_valid(eqs)
assert (planted&U)!=(planted>>32)
flip=(eqs[0][0]&-eqs[0][0]).bit_length()-1
assert any(((planted^(1<<flip))&mask).bit_count()%2 != bit for mask,bit in eqs)
print('Synthetic nonrepeating paired-state positive PASS at stage',t,'value',planted.to_bytes(8,'little').hex())
print('No source field recovered the K04 original physical coupon.')

# Target relevance gate: a source-fitting donor need not constrain the K04 gap.
def matrix_rank(rows):
    piv={}
    for v in rows:
        while v:
            j=v.bit_length()-1
            if j not in piv:
                piv[j]=v
                break
            v^=piv[j]
    return len(piv)
target=[basis.fully_reduce(v)[0] for stage in (951,952,953,954) for v in sym(stage)]
assert matrix_rank(target)==128
all_pair_rows=[]
for stage,mode,_ in models:
    all_pair_rows.extend(basis.fully_reduce(v)[0] for v in sym(stage,mode)+sym(stage+227,mode))
rank_all=matrix_rank(all_pair_rows)
overlap=128+rank_all-matrix_rank(target+all_pair_rows)
assert (rank_all,overlap)==(2886,0),(rank_all,overlap)
print('Original 286 pair models combined donor rank',rank_all,'K04 target overlap',overlap)
# Directly inspect future target-bearing stages beyond the earlier -1100..1040 window.
for i in range(len(a),1806-ORIGIN+1):
    t=i-624
    a.append([a[t+397][j]^(a[t][31] if j==30 else (a[t+1][j+1] if j<30 else 0))^(a[t+1][0] if (MAG>>j)&1 else 0) for j in range(32)])
target_witness_stages=[]
for stage in range(700,1579):
    donor=[basis.fully_reduce(v)[0] for v in sym(stage)+sym(stage+227)]
    rank_d=matrix_rank(donor)
    overlap=128+rank_d-matrix_rank(target+donor)
    if overlap>0 and 64-rank_d>=24:
        target_witness_stages.append(stage)
assert target_witness_stages==[952,953,954,1179,1180,1181,1351,1406,1578]
target_witness_matches=[]
for stage in target_witness_stages:
    constraints=syndrome(stage,False)
    for value,name,kind,offset,endian,encoding in variants:
        if all((value&mask).bit_count()%2==bit for mask,bit in constraints):
            target_witness_matches.append((stage,name,kind,offset,endian,encoding))
assert not target_witness_matches,target_witness_matches[:5]
print('Original K04 target-relevant 227-step models',len(target_witness_stages),
      'complete candidate comparisons',len(target_witness_stages)*len(variants),
      'exact witness matches',len(target_witness_matches))
