"""K04 CPython 2-word startup-offset2492 source-only complete inversion.

Run: python agents/agent23/k04_cpython_k2492_n2_inversion_sft.py
Requires g++ with OpenMP and Agent28's existing source projector.
The selected printer ACK2 row129 is removed before original-source fitting.
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent28"))
from k04_cpython_real_output_offset_sft import source_states, mt

SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U = 0xFFFFFFFF
INV_F1 = 0xFEE058C5
CPP = r"""
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <omp.h>
struct Hit {uint32_t k0,k1,s4,s11,s12;};
static inline uint32_t f1(uint32_t v) {return 1664525u*(v^(v>>30));}
static inline uint32_t f2(uint32_t v) {return 1566083941u*(v^(v>>30));}
int main() {
    const uint64_t limit=1ULL<<32;
    uint32_t g[13]{};g[0]=19650218u;
    for(int i=1;i<=12;++i)
        g[i]=1812433253u*(g[i-1]^(g[i-1]>>30))+uint32_t(i);
    const uint32_t S2=0xE403BB7Du,S3=0x1F7B301Fu;
    const uint32_t A3=(S3+3u)^f2(S2);
    std::vector<Hit> hits;
    uint64_t after4=0,after11=0,after12=0;
    #pragma omp parallel reduction(+:after4,after11,after12)
    {
        std::vector<Hit> local;
        #pragma omp for schedule(static)
        for(uint64_t x=0;x<limit;++x) {
            const uint32_t k0=uint32_t(x);
            const uint32_t a1=(g[1]^f1(g[0]))+k0;
            const uint32_t y=0xFEE058C5u*(g[3]^(A3-k0));
            const uint32_t a2=y^(y>>30);
            const uint32_t k1=a2-(g[2]^f1(a1))-1u;
            const uint32_t a4=(g[4]^f1(A3))+k1+1u;
            const uint32_t s4=(a4^f2(S3))-4u;
            if((s4&0x09CC1C00u)!=0x008C1000u)continue;
            ++after4;
            uint32_t a=a4,s=s4,s11=0;
            for(int i=5;i<=12;++i) {
                a=(g[i]^f1(a))+((i&1)?k0:(k1+1u));
                s=(a^f2(s))-uint32_t(i);
                if(i==11) {
                    s11=s;
                    if((s&0xFFu)!=0xB6u)break;
                    ++after11;
                }
                if(i==12) {
                    if((s&0x5398BA7Du)!=0x4010A820u)break;
                    ++after12;
                    local.push_back({k0,k1,s4,s11,s});
                }
            }
        }
        #pragma omp critical
        hits.insert(hits.end(),local.begin(),local.end());
    }
    std::sort(hits.begin(),hits.end(),[](auto a,auto b){return a.k0<b.k0;});
    std::printf("N2_K2492_COMPLETE=%llu S4=%llu S11=%llu S12=%llu\n",
                (unsigned long long)limit,
                (unsigned long long)after4,
                (unsigned long long)after11,
                (unsigned long long)after12);
    for(const Hit &h:hits)
        std::printf("HIT k0=%08X k1=%08X s4=%08X s11=%08X s12=%08X\n",
                    h.k0,h.k1,h.s4,h.s11,h.s12);
}
"""

def f1(v: int) -> int:
    return 1664525 * (v ^ (v >> 30)) & U

def f2(v: int) -> int:
    return 1566083941 * (v ^ (v >> 30)) & U

def controls() -> None:
    g = [19650218]
    for i in range(1, 13):
        g.append((1812433253 * (g[-1] ^ (g[-1] >> 30)) + i) & U)
    for k0, k1 in (
        (0x12345678, 0x23456789), (1, 1), (U, U),
        (8131, 4242), (0, 0x80000000)
    ):
        actual = random.Random((k1 << 32) | k0).getstate()[1][:624]
        s2, s3 = actual[2:4]
        a3 = ((s3 + 3) & U) ^ f2(s2)
        a1 = ((g[1] ^ f1(g[0])) + k0) & U
        y = INV_F1 * (g[3] ^ ((a3 - k0) & U)) & U
        a2 = y ^ (y >> 30)
        recovered_k1 = (a2 - (g[2] ^ f1(a1)) - 1) & U
        assert recovered_k1 == k1
        a = ((g[4] ^ f1(a3)) + k1 + 1) & U
        s = ((a ^ f2(s3)) - 4) & U
        assert s == actual[4]
        for i in range(5, 13):
            a = ((g[i] ^ f1(a)) + (k0 if i & 1 else k1 + 1)) & U
            s = ((a ^ f2(s)) - i) & U
            assert s == actual[i]
    print("GENUINE_CPYTHON_TWO_WORD_CONTROLS=5/5 PASS")

def main() -> None:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    packets = [bytes.fromhex(v.decode("ascii"))
               for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == len(mt.STARTS) == 133 and mt.STARTS[129] == 951
    actual = source_states(2492, packets)
    asserted = {
        2: (U, 0xE403BB7D),
        3: (U, 0x1F7B301F),
        4: (0x09CC1C00, 0x008C1000),
        11: (0x000000FF, 0x000000B6),
        12: (0x5398BA7D, 0x4010A820),
    }
    for i, pair in asserted.items():
        assert actual[i] == pair, (i, actual[i], pair)
    print("ORIGINAL_132_WITHHELD_SELECTED_SOURCE=PASS S2_S3_S4_S11_S12")
    controls()
    with tempfile.TemporaryDirectory(prefix="h17_k2492_n2_") as folder:
        path = Path(folder) / "sieve.cpp"
        staged = path.with_suffix(".new")
        staged.write_text(CPP, encoding="utf-8")
        os.replace(staged, path)
        target = Path(folder) / ("sieve.exe" if os.name == "nt" else "sieve")
        subprocess.run(["g++", "-O3", "-std=c++17", "-fopenmp",
                        str(path), "-o", str(target)], check=True)
        output = subprocess.run([str(target)], check=True, capture_output=True,
                                text=True, env={**os.environ, "OMP_NUM_THREADS": "6"}).stdout
    assert output.strip() == (
        "N2_K2492_COMPLETE=4294967296 S4=8490559 S11=33110 S12=0"
    ), output
    print(output.strip())
    print("ORIGINAL_N2_K2492_EXCLUDED=PASS SELECTED_COUPON_UNRECOVERED")

if __name__ == "__main__":
    main()
