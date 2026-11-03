"""Exact p951/CPython 608-word seed-length exclusion for original H-17 data.

Exhaustively invert all source-possible early register boundaries with C++17.
Then check every survivor against original printer GF(2) source and full
CPython init_by_array wraps. The disputed selected printer row129, K04
acceptance, mask, and K08 text are never used.

Usage: python agents/agent50/k04_n608_full_sft.py
Requires a C++17 compiler (CXX, g++ or clang++), four workers by default.
"""
from __future__ import annotations

import concurrent.futures
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent14"))
import k04_p951_cpython_n609_610_wrap_sft as wrap

gf = wrap.gf
U = 0xFFFFFFFF
A, B = 1664525, 1566083941
IA, IB = pow(A, -1, 1 << 32), pow(B, -1, 1 << 32)
EXPECTED = (
    (5, 0xE415F9C8, 0x04710790),
    (9, 0xA86C6B76, 0x84710790),
    (12, 0xCAE83410, 0x04710790),
)


def mix(x: int, mult: int) -> int:
    return ((x ^ (x >> 30)) * mult) & U


def unmix(x: int, inverse: int) -> int:
    y = (x * inverse) & U
    return y ^ (y >> 30)


def state_a(s: list[int], i: int) -> int:
    return ((s[i] + i) & U) ^ mix(s[i - 1], B)


def initial_base() -> list[int]:
    s = [19650218]
    for i in range(1, 624):
        s.append((1812433253 * (s[-1] ^ (s[-1] >> 30)) + i) & U)
    return s


def middle(s: list[int], base: list[int]) -> list[int]:
    s = s.copy()
    keys = {
        r: (state_a(s, r + 1) - (base[r + 1] ^ mix(state_a(s, r), A)) - r) & U
        for r in range(3, 15)
    }
    next_a = state_a(s, 623)
    for j in range(622, 610, -1):
        residue = j % 608
        previous_a = unmix(
            base[j + 1] ^ ((next_a - keys[residue] - residue) & U), IA
        )
        s[j - 1] = unmix(previous_a ^ ((s[j] + j) & U), IB)
        next_a = previous_a
    return s


def closure_checks(
    s: list[int], base: list[int], values: list[int], masks: list[int]
) -> tuple[int, int, int]:
    a611 = state_a(s, 611)
    a3 = state_a(s, 3)
    key15 = (state_a(s, 16) - (base[16] ^ mix(state_a(s, 15), A)) - 15) & U
    first_a623 = state_a(s, 623)
    counters = [0, 0, 0]
    for high in (0, 0x80000000):
        s[609] = (values[609] & 0x7FFFFFFF) | high
        a610 = state_a(s, 610)
        key2 = (a611 - (base[611] ^ mix(a610, A)) - 2) & U
        a2 = unmix(base[3] ^ ((a3 - key2 - 2) & U), IA)
        a1end = unmix(a2 ^ ((s[2] + 2) & U), IB)
        s1 = ((a1end ^ mix(s[623], B)) - 1) & U
        if ((s1 ^ values[1]) & masks[1]) != 0:
            continue
        counters[0] += 1
        a1first = ((a1end - key15 - 15) & U) ^ mix(first_a623, A)
        key1 = (a2 - (base[2] ^ mix(a1first, A)) - 1) & U
        if (((base[610] ^ mix(state_a(s, 609), A)) + key1 + 1) & U) != a610:
            continue
        counters[1] += 1
        key0 = (a1first - (base[1] ^ mix(base[0], A))) & U
        if (((base[609] ^ mix(state_a(s, 608), A)) + key0) & U) != state_a(s, 609):
            continue
        counters[2] += 1
    return tuple(counters)


def real_seed_controls(base: list[int]) -> None:
    rng = random.Random(0x608BEEF)
    for trial in range(3):
        words = [rng.getrandbits(32) for _ in range(608)]
        words[-1] |= 0x80000000
        seed = sum(x << (32 * j) for j, x in enumerate(words))
        state = list(random.Random(seed).getstate()[1][:624])
        found = middle(state, base)
        assert all(found[i] == state[i] for i in range(610, 624)), trial
        result = closure_checks(state, base, state, [U] * 624)
        assert all(c >= 1 for c in result), (trial, result)
    print("Genuine 608-word CPython integer-seed controls: 3/3 PASS", flush=True)


CPP = r'''
#include <cstdint>
#include <cstdio>
#include <cstdlib>
using u32=uint32_t;using u64=uint64_t;
constexpr u32 A=1664525u,B=1566083941u,IA=0xFEE058C5u,IB=0x6A76AE6Du;
static const u32 EARLY[16][3]={{EARLY}};
static const u32 SRC[32]={{SOURCE}};
static inline u32 mix(u32 x,u32 f){return (x^(x>>30))*f;}
static inline u32 unmix(u32 x,u32 f){u32 y=x*f;return y^(y>>30);}
static inline u32 sa(u32 si,u32 prev,int i){return (si+(u32)i)^mix(prev,B);}
static inline u32 key(const u32*s,const u32*base,int r){
 return sa(s[r+1],s[r],r+1)-(base[r+1]^mix(sa(s[r],s[r-1],r),A))-(u32)r;
}
int main(int argc,char**argv){
 if(argc!=3)return 2;
 int first=atoi(argv[1]),end=atoi(argv[2]);
 if(first<0||end>16||first>=end)return 2;
 u32 base[624]={};base[0]=19650218u;
 for(int i=1;i<624;++i)base[i]=1812433253u*(base[i-1]^(base[i-1]>>30))+(u32)i;
 u64 n=0,s621good=0,s612good=0,s611good=0;
 for(int option=first;option<end;++option){
  u32 s[624]={};
  for(int i=1;i<=16;++i)if(i!=7&&i!=13&&i!=14&&i!=15)s[i]=SRC[i-1];
  for(int i=608;i<624;++i)s[i]=SRC[16+i-608];
  s[7]=EARLY[option][0];s[13]=EARLY[option][1];s[14]=EARLY[option][2];
  u32 keys[15]={};for(int r=3;r<14;++r)keys[r]=key(s,base,r);
  for(u64 v=0;v<(1ull<<30);++v){
   s[15]=0x80000000u|((u32)v<<1);
   keys[14]=key(s,base,14);
   for(int top=0;top<2;++top){
    s[623]=(SRC[31]&0x7fffffffu)|(top?0x80000000u:0u);
    u32 anext=sa(s[623],s[622],623);
    u32 aprev=unmix(base[623]^(anext-keys[14]-14u),IA);
    s[621]=unmix(aprev^(s[622]+622u),IB);
    ++n;
    if(s[621]&0x80000000u)continue;
    ++s621good;anext=aprev;
    for(int j=621;j>=613;--j){
     int r=j%608;
     aprev=unmix(base[j+1]^(anext-keys[r]-(u32)r),IA);
     s[j-1]=unmix(aprev^(s[j]+(u32)j),IB);anext=aprev;
    }
    if((s[612]&0x7fffffffu)!=(SRC[20]&0x7fffffffu))continue;
    ++s612good;
    aprev=unmix(base[613]^(anext-keys[4]-4u),IA);
    s[611]=unmix(aprev^(s[612]+612u),IB);
    if(!(s[611]&0x80000000u))continue;
    ++s611good;
    printf("SURVIVOR %d %08X %08X\n",option,s[15],s[623]);
   }
  }
 }
 printf("COMPLETE %d %d %llu %llu %llu %llu\n",first,end,
     (unsigned long long)n,(unsigned long long)s621good,
     (unsigned long long)s612good,(unsigned long long)s611good);
}
'''


def run() -> None:
    values, masks, source_basis, expressions = wrap.prior.source_constraints()
    assert len(source_basis) == 15397
    assert masks[15] == 0x80000001 and values[15] == 0x80000000
    assert masks[623] == 0x7FFFFFFF and masks[622] == U
    assert masks[612] == 0x7FFFFFFF and masks[611] == 0x80000000
    assert masks[609] == 0x7FFFFFFF and masks[608] == U
    chosen, options = wrap.joint_domain([7, 13, 14], source_basis, expressions)
    assert len(chosen) == 4 and len(options) == 16
    assert chosen == [(7, 0), (7, 1), (13, 1), (14, 31)]
    early = [(x[7], x[13], x[14]) for x in options]
    base = initial_base()
    real_seed_controls(base)
    comp = os.getenv("CXX") or shutil.which("g++") or shutil.which("clang++")
    assert comp, "C++17 compiler is required for the exact finite scan"
    src = [values[i] for i in list(range(1, 17)) + list(range(608, 624))]
    code = CPP.replace("{{EARLY}}", "{" + ",".join(
        "{" + ",".join(f"0x{v:08X}u" for v in option) + "}" for option in early
    ) + "}").replace("{{SOURCE}}", "{" + ",".join(f"0x{v:08X}u" for v in src) + "}")
    with tempfile.TemporaryDirectory(prefix="h17_n608_") as tmp:
        path = Path(tmp)
        cpp = path / "test.cpp"
        exe = path / ("test.exe" if os.name == "nt" else "test")
        cpp.write_text(code, encoding="utf-8")
        subprocess.run([comp, "-O3", "-std=c++17", str(cpp), "-o", str(exe)], check=True)

        def shard(first: int) -> tuple[int, str]:
            result = subprocess.run([str(exe), str(first), str(first + 4)],
                                    check=True, text=True, capture_output=True)
            return first, result.stdout

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            outputs = sorted(pool.map(shard, (0, 4, 8, 12)))
    survivors = []
    counts = [0, 0, 0, 0]
    for first, output in outputs:
        match = re.search(rf"COMPLETE {first} {first + 4} (\d+) (\d+) (\d+) (\d+)", output)
        assert match, (first, output)
        n, a, b, c = map(int, match.groups())
        assert n == 4 * 2 * (1 << 30)
        for j, value in enumerate((n, a, b, c)):
            counts[j] += value
        survivors += [(int(i), int(s15, 16), int(s623, 16)) for i, s15, s623
                      in re.findall(r"SURVIVOR (\d+) ([0-9A-F]{8}) ([0-9A-F]{8})", output)]
        print(first, "source boundary scans", n, "S621", a, "S612", b, "S611", c, flush=True)
    assert tuple(sorted(survivors)) == EXPECTED, survivors
    assert counts == [16 * 2 * (1 << 30), 16 * (1 << 30), 4, 3], counts
    print("All exact CPython n608 source-boundary survivors:", survivors, flush=True)
    total_s1 = total_s608 = total_s607 = 0
    for idx, s15, s623 in survivors:
        trial = values.copy()
        trial[7], trial[13], trial[14] = early[idx]
        trial[15], trial[623] = s15, s623
        reconstructed = middle(trial, base)
        assert ((reconstructed[621] ^ values[621]) & masks[621]) == 0
        assert ((reconstructed[612] ^ values[612]) & masks[612]) == 0
        assert ((reconstructed[611] ^ values[611]) & masks[611]) == 0
        augmented = source_basis.copy()
        for i in (7, 13, 14, 15, *range(610, 624)):
            for bit, expr in enumerate(expressions[i]):
                rem = gf.reduce((expr << 1) | ((reconstructed[i] >> bit) & 1), augmented)
                assert rem != 1, ("original source contradiction", idx, i, bit)
                if rem > 1:
                    augmented[rem.bit_length() - 1] = rem
        assert len(augmented) == 15783
        n1, n2, n3 = closure_checks(reconstructed, base, values, masks)
        print("survivor", idx, f"S15={s15:08X}", f"S623={s623:08X}",
              "S1/S608/S607 closure", (n1, n2, n3), flush=True)
        total_s1 += n1
        total_s608 += n2
        total_s607 += n3
    assert (total_s1, total_s608, total_s607) == (3, 0, 0)
    print("PASS: exhaustive 34,359,738,368 modeled n608 source assignments,"
          " zero full init_by_array seed-wrap histories", flush=True)
    print("K04 and K08 remain MISSING; unchanged six original slot PASS", flush=True)


if __name__ == "__main__":
    run()
