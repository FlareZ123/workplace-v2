"""Source-only CPython 32-bit seed exclusion, genuine startup offsets 2492..2505.

Run from the repository root: python agents/agent23/k04_cpython_14origins_sft.py
Requires a C++17 compiler with OpenMP support and the existing Agent28 source projector.
Selected printer row129 is excluded before source state reconstruction.
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
U = 0xffffffff
PAIRS = [
    (2492, 0xC9B58006), (2493, 0x23051544), (2494, 0x7FC0F398),
    (2495, 0x62126540), (2496, 0x548F97E6),
    (2497, 0xCFC34245), (2497, 0xE30E4FA7),
    (2500, 0x278B7890), (2500, 0x82AA9709),
    (2500, 0xCBC9C2C1), (2503, 0x9487BC73),
    (2503, 0xED96BBD0), (2504, 0x00727C30),
    (2504, 0xD8CD0235),
]

CPP = r"""
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>
#include <omp.h>
struct Hit {uint32_t key; int index;};
int main() {
    constexpr uint64_t LIMIT=1ULL<<32;
    constexpr uint32_t P=0xE403BB7Du, Q=0x1F7B301Fu;
    uint32_t g[17]{};g[0]=19650218u;
    for(int i=1;i<=16;++i)
        g[i]=1812433253u*(g[i-1]^(g[i-1]>>30))+uint32_t(i);
    uint32_t goal[17]{};
    for(int i=3;i<=16;++i)
        goal[i]=(Q+uint32_t(i))^(1566083941u*(P^(P>>30)));
    std::vector<Hit> hits;
    #pragma omp parallel
    {
        std::vector<Hit> local;
        #pragma omp for schedule(static)
        for(uint64_t x=0;x<LIMIT;++x) {
            uint32_t a=g[0],key=uint32_t(x);
            for(int i=1;i<=16;++i) {
                a=(g[i]^(1664525u*(a^(a>>30))))+key;
                if(i>=3 && a==goal[i])local.push_back({key,i});
            }
        }
        #pragma omp critical
        hits.insert(hits.end(),local.begin(),local.end());
    }
    std::sort(hits.begin(),hits.end(),[](const Hit& a,const Hit& b){
        return a.index==b.index?a.key<b.key:a.index<b.index;
    });
    std::printf("EXHAUSTED=%llu HITS=%zu\n",
                (unsigned long long)LIMIT,hits.size());
    for(auto h:hits)std::printf("HIT %d %08X\n",h.index+2489,h.key);
}
"""

def synthetic_controls() -> None:
    for seed in (0, 1, 8131, 0x12345678, U):
        state = random.Random(seed).getstate()[1][:624]
        g, a = 19650218, 19650218
        for i in range(1, 17):
            g = (1812433253 * (g ^ (g >> 30)) + i) & U
            a = ((g ^ (1664525 * (a ^ (a >> 30)))) + seed) & U
            if i in (3, 7, 16):
                observed = ((state[i] + i) & U) ^ (
                    (1566083941 * (state[i - 1] ^ (state[i - 1] >> 30))) & U)
                assert a == observed
    print("GENUINE_CPYTHON_INITIALIZER_CONTROLS=15/15")

def main() -> None:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    rows = [bytes.fromhex(v.decode("ascii"))
            for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(rows) == len(mt.STARTS) == 133
    assert mt.STARTS[129] == 951
    print("ORIGINAL_SOURCE_SHA256=PASS; selected row129 WITHHELD")
    synthetic_controls()
    offsets = range(2492, 2506) if "--full-source" in sys.argv else (2492, 2496, 2505)
    for offset in offsets:
        state = source_states(offset, rows)
        assert state[offset - 2490] == (U, 0xE403BB7D)
        assert state[offset - 2489] == (U, 0x1F7B301F)
        assert not ((state[0][1] ^ 0x80000000) & state[0][0])
    print("SOURCE_PAIR_OFFSET_CERTIFICATES=", len(offsets))
    with tempfile.TemporaryDirectory(prefix="h17_cp_n1_") as directory:
        script = Path(directory) / "search.cpp"
        stage = script.with_suffix(".new")
        stage.write_text(CPP, encoding="utf-8")
        os.replace(stage, script)
        program = Path(directory) / ("search.exe" if os.name == "nt" else "search")
        subprocess.run(["g++", "-O3", "-std=c++17", "-fopenmp",
                        str(script), "-o", str(program)], check=True)
        output = subprocess.run([str(program)], check=True, capture_output=True,
                                text=True, env={**os.environ, "OMP_NUM_THREADS": "5"}).stdout
    assert "EXHAUSTED=4294967296 HITS=14" in output
    hits = [(int(offset), int(seed, 16))
            for offset, seed in re.findall(r"HIT (\d+) ([0-9A-F]{8})", output)]
    assert hits == PAIRS, (hits, PAIRS)
    for offset, seed in hits:
        i = offset - 2489
        state = random.Random(seed).getstate()[1][:624]
        assert (state[i - 1], state[i]) != (0xE403BB7D, 0x1F7B301F)
    print("COMPLETE_N1_DOMAIN_EXCLUDED_OFFSETS_2492_TO_2505=PASS")
    print("ORIGINAL_K04_BITS_AUTHENTICATED=0 K08_WORDS_AUTHENTICATED=0")

if __name__ == "__main__":
    main()
