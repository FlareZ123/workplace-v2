// H-17 Agent25: AVX2 portability rescue for Agent10's source-conditioned two-twist complete-seed sieve.
// Original-source conditional controls from Agent39's p951 intact-spool basis.
// Distinct complete native scalar producer from Agent26's exhaustive one-twist model.
// Selected row129 / K04 mask / K04 commitment are excluded from this test.
// Input: [start,end) unsigned seeds, 8-aligned, 1..8 CPU threads.
// AVX2 supported host required. Compile: g++ -O3 -mavx2 -std=c++17 -pthread file.cpp -o scan
#include <immintrin.h>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <atomic>
#include <thread>
#include <vector>
#include <chrono>
#ifdef H17_SYNTHETIC
// Independent NumPy RandomState(seed=12345): register after 625 draws,
// two full twists, position 1, ring phase17.
constexpr uint32_t K0=0x9CFC7E8Fu,K1=0x6A7CE736u,K2=0x9F82AC37u,K3=0x677D130Du;
#else
// Source-constrained native coordinates S[2],S[3],S[4],S[622].
constexpr uint32_t K0=0xE32E1557u,K1=0x3152E7CBu,K2=0xBBDD46A0u,K3=0xBBD5A4ABu;
#endif
constexpr uint32_t A=0x9908B0DFu,UPPER=0x80000000u,LOWER=0x7fffffffu;
using V=__m256i;
struct Hit { uint32_t seed; unsigned phase; };
inline V shr(V v,int n){return _mm256_srli_epi32(v,n);}
std::vector<Hit> scan(uint64_t start,uint64_t stop,int worker) {
  std::vector<Hit> hits;
  alignas(32) V s[624];
  const V mul=_mm256_set1_epi32(1812433253u);
  const V upper=_mm256_set1_epi32(UPPER),lower=_mm256_set1_epi32(LOWER);
  const V matrix=_mm256_set1_epi32(A),one=_mm256_set1_epi32(1u);
  alignas(32) uint32_t seeds[8];
  for(uint64_t n=start;n<stop;n+=8) {
    for(unsigned lane=0;lane<8;lane++) seeds[lane]=uint32_t(n+lane);
    s[0]=_mm256_load_si256((const V*)seeds);
    for(int i=1;i<624;i++) {
      V prev=s[i-1];
      s[i]=_mm256_add_epi32(_mm256_mullo_epi32(_mm256_xor_si512(prev,shr(prev,30)),mul),_mm256_set1_epi32(i));
    }
    for(int twist=0;twist<2;twist++) {
    for(int i=0;i<227;i++) {
      V y=_mm256_or_si512(_mm256_and_si512(s[i],upper),_mm256_and_si512(s[i+1],lower));
      V magic=_mm256_and_si256(_mm256_sub_epi32(_mm256_setzero_si256(),_mm256_and_si256(y,one)),matrix);
      s[i]=_mm256_xor_si512(_mm256_xor_si512(s[i+397],shr(y,1)),magic);
    }
    for(int i=227;i<623;i++) {
      V y=_mm256_or_si512(_mm256_and_si512(s[i],upper),_mm256_and_si512(s[i+1],lower));
      V magic=_mm256_and_si256(_mm256_sub_epi32(_mm256_setzero_si256(),_mm256_and_si256(y,one)),matrix);
      s[i]=_mm256_xor_si512(_mm256_xor_si512(s[i-227],shr(y,1)),magic);
    }
    {
      V y=_mm256_or_si512(_mm256_and_si512(s[623],upper),_mm256_and_si512(s[0],lower));
      V magic=_mm256_and_si256(_mm256_sub_epi32(_mm256_setzero_si256(),_mm256_and_si256(y,one)),matrix);
      s[623]=_mm256_xor_si512(_mm256_xor_si512(s[396],shr(y,1)),magic);
    }
    }
    for(int idx=0;idx<624;idx++) {
      unsigned phase=(idx+624-2)%624;
      unsigned matching=(unsigned)_mm256_movemask_ps(_mm256_castsi256_ps(_mm256_cmpeq_epi32(s[idx],_mm256_set1_epi32(K0))));
      while(matching) {
        int lane=__builtin_ctz(matching);matching&=matching-1;
        uint32_t s3=((uint32_t*)&s[(idx+1)%624])[lane];
        uint32_t s4=((uint32_t*)&s[(idx+2)%624])[lane];
        uint32_t s622=((uint32_t*)&s[(idx+620)%624])[lane];
        unsigned complete=(s3==K1 && s4==K2 && s622==K3);
        std::printf("THREAD=%d source-S2-hit seed=%u phase=%u S3=%08X S4=%08X S622=%08X complete=%u\n",worker,seeds[lane],phase,s3,s4,s622,complete);
        hits.push_back({seeds[lane],phase});
      }
    }
  }
  return hits;
}
int main(int argc,char** argv) {
  if(argc!=4) {std::fprintf(stderr,"arguments: start end threads\n");return 2;}
  uint64_t begin=std::strtoull(argv[1],nullptr,0),end=std::strtoull(argv[2],nullptr,0);
  int threads=std::atoi(argv[3]);
  if(begin>=end || end>4294967296ull || begin%8 || end%8 || threads<1 || threads>8) return 2;
  auto tick=std::chrono::steady_clock::now();
  std::vector<std::thread> jobs;
  std::vector<std::vector<Hit>> results(threads);
  uint64_t part=((end-begin+threads-1)/threads+7)/8*8;
  for(int k=0;k<threads;k++) {
    uint64_t lo=std::min(end,begin+uint64_t(k)*part),hi=std::min(end,lo+part);
    jobs.emplace_back([&,k,lo,hi]{results[k]=scan(lo,hi,k);});
  }
  for(auto& t:jobs)t.join();
  size_t found=0;for(const auto& h:results)found+=h.size();
  auto ms=std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-tick).count();
  std::printf("SUMMARY start=%llu end=%llu threads=%d firstword_hits=%zu wall_ms=%lld checked=%llu\n",
    (unsigned long long)begin,(unsigned long long)end,threads,found,(long long)ms,(unsigned long long)(end-begin));
}
