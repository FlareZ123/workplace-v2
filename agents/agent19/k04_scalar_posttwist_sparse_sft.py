"""Generate self-contained AVX2/OpenMP C++ exhaustive probes of scalar MT19937 after N twists.

Use original p951 source-only S2/S3/S4/S622 values from Agent39's independent
GF(2) spool reconstruction, not selected K04 bytes or acceptance commitments.
Run depth N=1,2,3,... and compile generated C++ with a C++17 compiler supporting
AVX2 and OpenMP. Providing 'synthetic' as second argument replaces original
source controls with real seed=5489 controls for a positive test.

The generated C++ accepts start/count/thread-count numeric positional arguments.
Count must be divisible by 8. A full exhaustive run covers 0..2^32-1 exactly.
"""
from __future__ import annotations
import sys
from pathlib import Path

SOURCE = (0xE32E1557, 0x3152E7CB, 0xBBDD46A0, 0xBBD5A4AB)


def selected_register(seed: int, count: int) -> tuple[int, int, int, int]:
    mt = [seed]
    for i in range(1, 624):
        mt.append((1812433253 * (mt[-1] ^ (mt[-1] >> 30)) + i) & 0xFFFFFFFF)
    for _ in range(count):
        for k in range(624):
            y = (mt[k] & 0x80000000) | (mt[(k + 1) % 624] & 0x7FFFFFFF)
            mt[k] = mt[(k + 397) % 624] ^ (y >> 1) ^ (0x9908B0DF if y & 1 else 0)
    return tuple(mt[k] for k in (2, 3, 4, 622))


def build(count: int, source: tuple[int, int, int, int] = SOURCE) -> str:
    if count < 1:
        raise ValueError("count must be at least one twist")
    nodes: list[tuple[int, int]] = []
    roots: set[int] = set()
    done: set[tuple[int, int]] = set()

    def visit(n: int, k: int):
        if (n, k) in done:
            return
        if n == 0:
            roots.add(k)
        elif k < 227:
            for p in ((n - 1, k + 397), (n - 1, k), (n - 1, k + 1)):
                visit(*p)
        elif k < 623:
            for p in ((n, k - 227), (n - 1, k), (n - 1, k + 1)):
                visit(*p)
        else:
            for p in ((n, 396), (n - 1, 623), (n, 0)):
                visit(*p)
        done.add((n, k))
        nodes.append((n, k))

    visit(count, 2)

    def var(n, k):
        return f"v{n}_{k}"

    init = "\n".join(f"__m256i {var(0, k)}={{}};" for k in sorted(roots) if k)
    capture = "\n".join(f"if(i=={k}) {var(0, k)}=s;" for k in sorted(roots) if k)
    if 0 in roots:
        init += "\n__m256i v0_0=_mm256_add_epi32(_mm256_set1_epi32(uint32_t(base)),lane);"
    updates = []
    for n, k in nodes:
        if n == 0:
            continue
        if k < 227:
            q, r, t = (n-1, k+397), (n-1, k), (n-1, k+1)
        elif k < 623:
            q, r, t = (n, k-227), (n-1, k), (n-1, k+1)
        else:
            q, r, t = (n, 396), (n-1, 623), (n, 0)
        updates.append(
            f"const __m256i {var(n,k)}=twist_word({var(*q)},{var(*r)},{var(*t)});"
        )

    return f'''// Original-source scalar MT19937 after {count} complete twists.
#include <immintrin.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <chrono>
#include <omp.h>
constexpr uint32_t A=1812433253U, MAGIC=0x9908B0DFU;
constexpr uint32_t SOURCE[4] = {{{','.join('0x%08XU'%x for x in source)}}};
uint32_t full_state(uint32_t seed, uint32_t pos){{
  uint32_t a[624];a[0]=seed;
  for(uint32_t i=1;i<624;i++)a[i]=A*(a[i-1]^(a[i-1]>>30))+i;
  for(int turn=0;turn<{count};turn++){{
    for(int j=0;j<624;j++){{
      uint32_t y=(a[j]&0x80000000U)|(a[(j+1)%624]&0x7FFFFFFFU);
      a[j]=a[(j+397)%624]^(y>>1)^((y&1U)?MAGIC:0U);
    }}
  }}
  return a[pos];
}}
int main(int argc,char**argv){{
  const uint64_t first=argc>1?strtoull(argv[1],nullptr,0):0;
  const uint64_t count=argc>2?strtoull(argv[2],nullptr,0):8000000;
  int threads=argc>3?atoi(argv[3]):4;
  if(first+count>0x100000000ULL || count%8 || threads<1){{
    puts("Invalid range");return 2;
  }}
  omp_set_num_threads(threads);
  const __m256i lane=_mm256_setr_epi32(0,1,2,3,4,5,6,7);
  const __m256i mul=_mm256_set1_epi32(A), target=_mm256_set1_epi32(SOURCE[0]);
  const __m256i top=_mm256_set1_epi32(0x80000000U),
    low=_mm256_set1_epi32(0x7FFFFFFFU),magic=_mm256_set1_epi32(MAGIC);
  uint64_t collisions=0, complete=0;
  auto t0=std::chrono::steady_clock::now();
  #pragma omp parallel for reduction(+:collisions,complete) schedule(static)
  for(uint64_t base=first;base<first+count;base+=8){{
    __m256i s=_mm256_add_epi32(_mm256_set1_epi32(uint32_t(base)),lane);
    {init}
    for(int i=1;i<={max(roots)};i++){{
      s=_mm256_add_epi32(
        _mm256_mullo_epi32(mul,_mm256_xor_si256(s,_mm256_srli_epi32(s,30))),
        _mm256_set1_epi32(i));
      {capture}
    }}
    auto twist_word=[&](__m256i base, __m256i r, __m256i next){{
      __m256i y=_mm256_or_si256(
        _mm256_and_si256(r,top),_mm256_and_si256(next,low));
      return _mm256_xor_si256(
        _mm256_xor_si256(base,_mm256_srli_epi32(y,1)),
        _mm256_and_si256(magic,_mm256_sub_epi32(
          _mm256_setzero_si256(),_mm256_and_si256(y,_mm256_set1_epi32(1)))));
    }};
    {' '.join(updates)}
    int mask=_mm256_movemask_epi8(_mm256_cmpeq_epi32({var(count,2)},target));
    if(mask)for(int j=0;j<8;j++)if(mask&(1<<(4*j))){{
      uint32_t seed=(uint32_t)(base+j);
      bool valid=true;
      for(int q=0;q<4;q++)
        if(full_state(seed,q<3?(q+2):622)!=SOURCE[q])valid=false;
      #pragma omp critical
      printf("T{count} S2_HIT seed=%08X independent_S3_S4_S622=%s\\n",
        seed,valid?"PASS":"FAIL");
      collisions++;
      if(valid)complete++;
    }}
  }}
  const double seconds=std::chrono::duration<double>(
    std::chrono::steady_clock::now()-t0).count();
  printf("T{count} scanned=%llu first=%llu S2_collisions=%llu all4=%llu seconds=%.3f throughput=%.0f/s\\n",
    (unsigned long long)count,(unsigned long long)first,
    (unsigned long long)collisions,(unsigned long long)complete,
    seconds,count/seconds);
}}
'''


if __name__ == "__main__":
    count = int(sys.argv[1])
    synthetic = len(sys.argv) > 2 and sys.argv[2] == "synthetic"
    source = selected_register(5489, count) if synthetic else SOURCE
    path = Path.cwd() / f"k04_scalar_twist{count}{'_synthetic' if synthetic else ''}.cpp"
    tmp = path.with_suffix(".cpp.tmp")
    tmp.write_text(build(count, source), encoding="utf-8")
    tmp.replace(path)
    print(f"Generated {path.name} using {'synthetic' if synthetic else 'source'} target")
