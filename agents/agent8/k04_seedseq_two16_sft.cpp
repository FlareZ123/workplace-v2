/* H17, original-source conditional C++ seed_seq{uint16,uint16} producer test.
   The selected 18:02 physical coupon and its copied ACK are excluded.
   Required source-only p955 initialized register: S3=873F7515 S4=ADD0D034.
   The 2x16-bit producer assumption is exploratory, not historically attested.
*/
#include <immintrin.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <chrono>
#include <atomic>
#include <algorithm>
#include <omp.h>
constexpr uint32_t S3=0x873F7515u,S4=0xADD0D034u;
static constexpr int N=624,P=306,Q=317;
struct alignas(32) Vec8 { __m256i x; };
static inline __m256i shr27(__m256i x){return _mm256_xor_si256(x,_mm256_srli_epi32(x,27));}
static inline __m256i lane8(uint32_t b){return _mm256_setr_epi32(b,b+1,b+2,b+3,b+4,b+5,b+6,b+7);}
static inline void batch(uint32_t firstPairIndex,uint32_t*s3,uint32_t*s4){
  Vec8 state[N];
  const auto base=_mm256_set1_epi32(0x8b8b8b8b);
  for(auto &v:state)v.x=base;
  // Pair numbering: (seed0=(index & 65535),seed1=(index >>16));
  const auto seed0=_mm256_and_si256(lane8(firstPairIndex),_mm256_set1_epi32(65535));
  const auto seed1=_mm256_set1_epi32(firstPairIndex>>16);
  const auto A=_mm256_set1_epi32(1664525),B=_mm256_set1_epi32(1566083941);
  for(int k=0;k<N;k++){
    const int u=(k+P)%N,v=(k+Q)%N;
    const auto x=_mm256_xor_si256(_mm256_xor_si256(state[k].x,state[u].x),state[(k+N-1)%N].x);
    const auto r1=_mm256_mullo_epi32(A,shr27(x));
    auto r2=_mm256_add_epi32(r1,_mm256_set1_epi32(k==0?2:k));
    if(k==1)r2=_mm256_add_epi32(r2,seed0);
    if(k==2)r2=_mm256_add_epi32(r2,seed1);
    state[u].x=_mm256_add_epi32(state[u].x,r1);
    state[v].x=_mm256_add_epi32(state[v].x,r2);
    state[k].x=r2;
  }
  for(int k=N;k<=946;k++){
    const int i=k-N,u=(k+P)%N,v=(k+Q)%N;
    const auto x=_mm256_add_epi32(_mm256_add_epi32(state[i].x,state[u].x),state[(i+N-1)%N].x);
    const auto r3=_mm256_mullo_epi32(B,shr27(x));
    const auto r4=_mm256_sub_epi32(r3,_mm256_set1_epi32(i));
    state[u].x=_mm256_xor_si256(state[u].x,r3);
    state[v].x=_mm256_xor_si256(state[v].x,r4);
    state[i].x=r4;
  }
  _mm256_storeu_si256((__m256i*)s3,state[3].x);
  _mm256_storeu_si256((__m256i*)s4,state[4].x);
}
int main(int argc,char**argv){
  const uint64_t count=argc>1?std::strtoull(argv[1],nullptr,10):1048576ULL;
  const uint64_t start=argc>2?std::strtoull(argv[2],nullptr,10):0ULL;
  if((count&7)||(start&7)||start+count>4294967296ULL)return 3;
  const std::array<uint32_t,9> examples{0,1,2,7,8131,0x00010001,0x00028131,0xFFFF0000u,0xFFFFFFFFu};
  std::array<uint32_t,N> output;
  for(const uint32_t idx:examples){
    const auto lo=(uint32_t)(idx&65535),hi=idx>>16;
    std::seed_seq seq{lo,hi};seq.generate(output.begin(),output.end());
    alignas(32)uint32_t a[8],b[8];batch(idx&~7u,a,b);
    if(a[idx&7]!=output[3]||b[idx&7]!=output[4]){
      printf("POSITIVE_CONTROL_FAIL index=%08X seeds=%u/%u vector=%08X/%08X standard=%08X/%08X\n",idx,lo,hi,a[idx&7],b[idx&7],output[3],output[4]);return 4;
    }
  }
  printf("NATIVE_STD_SEEDSEQ_TWO_WORD_CONTROLS=%zu PASS\n",examples.size());fflush(stdout);
  unsigned long long h3=0,hpair=0;
  auto t=std::chrono::steady_clock::now();
#pragma omp parallel for schedule(static) reduction(+:h3,hpair)
  for(int64_t k=0;k<(int64_t)(count/8);k++){
    alignas(32)uint32_t a[8],b[8];
    const auto idx=(uint32_t)(start+uint64_t(k)*8);
    batch(idx,a,b);
    for(unsigned j=0;j<8;j++){
      if(a[j]==S3){h3++;
#pragma omp critical
        {printf("S3_MATCH seeds=%u/%u S4=%08X\n",(idx+j)&65535,(idx+j)>>16,b[j]);fflush(stdout);}}
      if(a[j]==S3&&b[j]==S4){hpair++;
#pragma omp critical
        {printf("FULL_PAIR_MATCH seeds=%u/%u\n",(idx+j)&65535,(idx+j)>>16);fflush(stdout);}}
    }
  }
  const double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();
  printf("START=%llu COUNT=%llu S3_HITS=%llu PAIR_HITS=%llu SECONDS=%.3f RATE=%.0f/s THREADS=%d\n",(unsigned long long)start,(unsigned long long)count,h3,hpair,sec,count/sec,omp_get_max_threads());
  return 0;
}
