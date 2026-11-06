"""K04 exact two-word CPython startup-offset2493 bit-lift source exclusion.

Run: python agents/agent23/k04_cpython_k2493_n2_bitlift_sft.py
Uses the existing exact original source projector and embedded C++17/OpenMP.
Selected printer ACK2 row129 is excluded before source inversion.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent28"))
from k04_cpython_real_output_offset_sft import source_states,mt

SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U=0xffffffff

CPP=r"""
#include <cstdint>
#include <cstdio>
#include <vector>
#include <algorithm>
#include <omp.h>
static inline uint32_t F1(uint32_t x){return 1664525u*(x^(x>>30));}
static inline uint32_t F2(uint32_t x){return 1566083941u*(x^(x>>30));}
struct Hit{uint32_t k0,k1;};
int main(){
 const uint64_t limit=1ULL<<32;
 uint32_t g[14]{};g[0]=19650218u;
 for(int i=1;i<=13;++i)g[i]=1812433253u*(g[i-1]^(g[i-1]>>30))+uint32_t(i);
 const uint32_t S3=0xE403BB7Du,S4=0x1F7B301Fu,A4=(S4+4u)^F2(S3);
 uint64_t pre=0,paths=0,roots=0,high=0,s2good=0,s12good=0,s13good=0,maxbranch=0;
 std::vector<Hit> hits;
 #pragma omp parallel reduction(+:pre,paths,roots,high,s2good,s12good,s13good) reduction(max:maxbranch)
 {
  std::vector<Hit> local;
  std::vector<uint32_t> curr,next;
  #pragma omp for schedule(static)
  for(uint64_t xx=0;xx<limit;xx++){
   // Odd multiplier permutes the entire 32-bit seed domain and samples all high bits early.
   uint32_t k0=uint32_t(xx*0x9e3779b9ULL);
   uint32_t a5=(g[5]^F1(A4))+k0;
   uint32_t s5=(a5^F2(S4))-5u;
   if((s5&0x09CC1C00u)!=0x008C1000u)continue;
   pre++;
   uint32_t a1=(g[1]^F1(g[0]))+k0;
   uint32_t c2=(g[2]^F1(a1))+1u;
   for(uint32_t h2=0;h2<4;h2++)for(uint32_t h3=0;h3<4;h3++){
    curr.clear();curr.push_back(0);
    for(int bit=0;bit<32&&!curr.empty();bit++){
     uint32_t mask=(bit==31)?0xffffffffu:((1u<<(bit+1))-1u);
     uint32_t step=1u<<bit;
     next.clear();
     for(uint32_t lo:curr)for(int b=0;b<2;b++){
      uint32_t k1=lo|(b?step:0u);
      uint32_t a2=c2+k1;
      uint32_t a3=(g[3]^(1664525u*(a2^h2)))+k0;
      uint32_t predicted=(g[4]^(1664525u*(a3^h3)))+k1+1u;
      if((predicted&mask)==(A4&mask))next.push_back(k1);
     }
     curr.swap(next);
     if(curr.size()>maxbranch)maxbranch=curr.size();
    }
    paths++;
    roots+=curr.size();
    for(uint32_t k1:curr){
     uint32_t a2=c2+k1;
     uint32_t a3=(g[3]^F1(a2))+k0;
     if((a2>>30)!=h2||(a3>>30)!=h3)continue;
     high++;
     uint32_t z=0x6A76AE6Du*(a3^(S3+3u));
     uint32_t s2=z^(z>>30);
     if((s2&0x8000001fu)!=0x11u)continue;
     s2good++;
     uint32_t a=A4,s=S4;
     for(int i=5;i<=13;i++){
      a=(g[i]^F1(a))+((i&1)?k0:(k1+1u));
      s=(a^F2(s))-uint32_t(i);
      if(i==12){if((s&0xffu)!=0xb6u)break;s12good++;}
      if(i==13){if((s&0x5398ba7du)!=0x4010a820u)break;
       s13good++;local.push_back({k0,k1});}
     }
    }
   }
  }
  #pragma omp critical
  hits.insert(hits.end(),local.begin(),local.end());
 }
 printf("K2493_N2_LIMIT=%llu PREFILTER=%llu PATHS=%llu ROOTS=%llu HIGHBITS=%llu S2=%llu S12=%llu S13=%llu MAXBRANCH=%llu\n",
  (unsigned long long)limit,(unsigned long long)pre,
  (unsigned long long)paths,(unsigned long long)roots,
  (unsigned long long)high,(unsigned long long)s2good,
  (unsigned long long)s12good,(unsigned long long)s13good,
  (unsigned long long)maxbranch);
 for(auto h:hits)printf("HIT k0=%08X k1=%08X\n",h.k0,h.k1);
}
"""

def f1(v:int)->int:
    return 1664525*(v^(v>>30))&U

def f2(v:int)->int:
    return 1566083941*(v^(v>>30))&U

def seed_controls()->None:
    g=[19650218]
    for i in range(1,14):
        g.append((1812433253*(g[-1]^(g[-1]>>30))+i)&U)
    for k0,k1 in ((0x12345678,0x23456789),(1,1),(U,U),
                  (8131,4242),(0,0x80000000)):
        expected=random.Random((k1<<32)|k0).getstate()[1][:624]
        s3,s4=expected[3:5]
        a4=((s4+4)&U)^f2(s3)
        a1=((g[1]^f1(g[0]))+k0)&U
        a2=((g[2]^f1(a1))+k1+1)&U
        a3=((g[3]^f1(a2))+k0)&U
        assert a4==((g[4]^f1(a3))+k1+1)&U
        high2,high3=a2>>30,a3>>30
        c2=((g[2]^f1(a1))+1)&U
        current=[0]
        for bit in range(32):
            mask=(1<<(bit+1))-1
            nxt=[]
            for low in current:
                for candidate in (low,low|(1<<bit)):
                    b2=(c2+candidate)&U
                    b3=((g[3]^(1664525*(b2^high2)&U))+k0)&U
                    predicted=((g[4]^(1664525*(b3^high3)&U))+candidate+1)&U
                    if (predicted&mask)==(a4&mask):
                        nxt.append(candidate)
            current=nxt
            assert (k1&mask) in current
        assert k1 in current
        v=0x6A76AE6D*(a3^((s3+3)&U))&U
        assert (v^(v>>30))==expected[2]
        a,s=a4,s4
        for i in range(5,14):
            a=((g[i]^f1(a))+(k0 if i&1 else k1+1))&U
            s=((a^f2(s))-i)&U
            assert s==expected[i]
    print("GENUINE_CPYTHON_TWO_WORD_BITLIFT_CONTROLS=5/5 PASS")

def main()->None:
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SHA
    packets=[bytes.fromhex(v.decode("ascii"))
             for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)]
    assert len(packets)==len(mt.STARTS)==133 and mt.STARTS[129]==951
    original=source_states(2493,packets)
    values={2:(0x8000001f,0x11),3:(U,0xE403BB7D),4:(U,0x1F7B301F),
            5:(0x09CC1C00,0x008C1000),12:(0xff,0xb6),
            13:(0x5398BA7D,0x4010A820)}
    for i,v in values.items():assert original[i]==v,(i,original[i],v)
    print("ORIGINAL_SOURCE_132_INTACT_EXCLUDING_SELECTED=PASS")
    seed_controls()
    with tempfile.TemporaryDirectory(prefix="h17_k2493_n2_") as folder:
        path=Path(folder)/"test.cpp"
        stage=path.with_suffix(".new")
        stage.write_text(CPP,encoding="utf-8")
        os.replace(stage,path)
        executable=Path(folder)/("test.exe" if os.name=="nt" else "test")
        subprocess.run(["g++","-O3","-std=c++17","-fopenmp",
                        str(path),"-o",str(executable)],check=True)
        output=subprocess.run([str(executable)],check=True,capture_output=True,
                              text=True,env={**os.environ,"OMP_NUM_THREADS":"6"}).stdout
    assert output.strip()==(
        "K2493_N2_LIMIT=4294967296 PREFILTER=8388608 PATHS=134217728 "
        "ROOTS=184552152 HIGHBITS=11546079 S2=168980 S12=662 S13=0 "
        "MAXBRANCH=232"
    ),output
    print(output.strip())
    print("ORIGINAL_N2_K2493_FULL_SOURCE_EXCLUDED=PASS K04_UNRECOVERED")

if __name__=="__main__":main()
