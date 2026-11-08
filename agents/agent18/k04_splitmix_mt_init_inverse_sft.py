"""Invert direct 64-bit SplitMix64-pair expansion into 624 MT19937 initial words."""
import hashlib
from pathlib import Path
M = (1 << 64)-1
G = 0x9E3779B97F4A7C15
A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB
Ai = pow(A,-1,1<<64)
Bi = pow(B,-1,1<<64)
PIN='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
spool=Path(__file__).resolve().parents[2] / 'resources/evidence/print/spool-reconstruction.log'
assert hashlib.sha256(spool.read_bytes()).hexdigest()==PIN

def xorrshift_inverse(y,k):
    x=y
    for _ in range(7):x=y^(x>>k)
    return x

def mix(x):
    x=((x^(x>>30))*A)&M
    x=((x^(x>>27))*B)&M
    return x^(x>>31)

def unmix(y):
    y=xorrshift_inverse(y,31)
    y=(y*Bi)&M
    y=xorrshift_inverse(y,27)
    y=(y*Ai)&M
    return xorrshift_inverse(y,30)

def words(seed,order):
    s=seed;result=[]
    for _ in range(312):
        s=(s+G)&M;z=mix(s)
        low,high=z&0xffffffff,z>>32
        result.extend([low,high] if order==0 else [high,low])
    return result

def recover(fixed):
    results=[];tested=0
    for order in range(2):
        for phase in range(624):
            i=2 if (2+phase)%2==0 else 3
            lohi=[fixed[i],fixed[i+1]]
            if order==1:lohi.reverse()
            y=(lohi[1]<<32)|lohi[0]
            index=((i+phase)%624)//2
            state=unmix(y)
            seed=(state-((index+1)*G))&M
            output=words(seed,order)
            tested+=1
            if all(output[(phase+k)%624]==v for k,v in fixed.items()):
                results.append((order,phase,seed))
    return results,tested

# SplitMix64 algebraic inversion controls.
for x in (0,1,0x13579BDF2468ACE0,M):assert unmix(mix(x))==x
for seed in (0,1,0x13579BDF2468ACE0,M):
    for order in range(2):
        v=words(seed,order)
        for phase in (0,17,389,623):
            f={i:v[(i+phase)%624] for i in (2,3,4,622)}
            ans,n=recover(f)
            assert (order,phase,seed) in ans,(order,phase,seed,ans)
print('SYNTHETIC_KNOWN_SEED_PHASE_CONTROLS=32/32 PASS')
source={2:0xE32E1557,3:0x3152E7CB,4:0xBBDD46A0,622:0xBBD5A4AB}
ans,n=recover(source)
print('ORIGINAL_CONDITIONAL_STATE=source_S2_S3_S4_S622')
print('PHASE_ENDIAN_CONSTRUCTIONS',n,'FULL_FOURWORD_ORIGINAL_HITS',len(ans),'HITS',ans[:5])

G32=0x9e3779b9
A32=0x85ebca6b
B32=0xc2b2ae35
M32=(1<<32)-1

def mix32(z):
    z=((z^(z>>16))*A32)&M32
    z=((z^(z>>13))*B32)&M32
    return z^(z>>16)

def unmix32(z):
    z=xorrshift_inverse(z,16)
    z=(z*pow(B32,-1,1<<32))&M32
    z=xorrshift_inverse(z,13)
    z=(z*pow(A32,-1,1<<32))&M32
    return xorrshift_inverse(z,16)

def words32(seed):
    s=seed;v=[]
    for _ in range(624):
        s=(s+G32)&M32;v.append(mix32(s))
    return v

def recover32(fixed):
    matches=[]
    for phase in range(624):
        ix=(2+phase)%624
        recovered_state=unmix32(fixed[2])
        seed=(recovered_state-((ix+1)*G32))&M32
        v=words32(seed)
        if all(v[(phase+k)%624]==w for k,w in fixed.items()):
            matches.append((phase,seed))
    return matches

for x in (0,1,0x13579BDF,M32):assert unmix32(mix32(x))==x
for seed in (0,1,0x13579BDF,M32):
    v=words32(seed)
    for phase in (0,17,389,623):
        f={i:v[(i+phase)%624] for i in (2,3,4,622)}
        assert (phase,seed) in recover32(f)
print('SYNTHETIC_32BIT_SPLITMIX_CONTROLS=16/16 PASS')
ans=recover32(source)
print('SPLITMIX32_PHASES_TESTED=624','FULL_FOURWORD_ORIGINAL_HITS',len(ans),'HITS',ans[:5])

def native_coupon(initial, stage=951):
    stream=list(initial)
    for j in range(624,624+stage+4):
        i=j-624
        x=(stream[i]&0x80000000)|(stream[i+1]&0x7fffffff)
        stream.append((stream[i+397]^(x>>1)^(0x9908b0df if x&1 else 0))&0xffffffff)
    def temper(y):
        y^=y>>11;y^=(y<<7)&0x9d2c5680;y^=(y<<15)&0xefc60000
        return (y^(y>>18))&0xffffffff
    return b''.join(temper(x).to_bytes(4,'little') for x in stream[624+stage:624+stage+4])

for seed in (0,1,0x13579BDF2468ACE0, M):
    for order in range(2):
        v=words(seed,order)
        for phase in (0,17,389,623):
            observed={i:v[(phase+i)%624] for i in (2,3,4,622)}
            found,_=recover(observed)
            expected=native_coupon(v[phase:]+v[:phase])
            assert any(native_coupon(words(reseed,ro)[rp:]+words(reseed,ro)[:rp])==expected
                       for ro,rp,reseed in found)
for seed in (0,1,0x13579BDF,M32):
    v=words32(seed)
    for phase in (0,17,389,623):
        observed={i:v[(phase+i)%624] for i in (2,3,4,622)}
        found=recover32(observed)
        expected=native_coupon(v[phase:]+v[:phase])
        assert any(native_coupon(words32(reseed)[rp:]+words32(reseed)[:rp])==expected
                   for rp,reseed in found)
print('BLIND_WHOLE_COUPON_POSITIVES=48/48 PASS')
