/* H17 original-source K04: all two-uint16 C++ seed_seq MT19937 streams at startup origin0.
   Source-only first original intact ordinary spool ACK: FBBBC54356483F5864BB3F06794518A5.
   Exact direct first four MT words as 16 bytes under LE or BE word serialization.
   Selected disputed 18:02 ACK, original commitments and route mask excluded.
*/
#include <immintrin.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <chrono>
#include <omp.h>
constexpr int N=624,P=306,Q=317;
static constexpr uint32_t sourceLE[4]={0x43c5bbfbu,0x583f4856u,0x063fbb64u,0xa5184579u};
static constexpr uint32_t sourceBE[4]={0xfbbbc543u,0x56483f58u,0x64bb3f06u,0x794518a5u};
struct alignas(32) Vec8 { __m256i x; };
static inline __m256i sh27(__m256i x){return _mm256_xor_si256(x,_mm256_srli_epi32(x,27));}
static inline __m256i lane8(uint32_t b){return _mm256_setr_epi32(b,b+1,b+2,b+3,b+4,b+5,b+6,b+7);}
static inline __m256i temper(__m256i x){
  x=_mm256_xor_si256(x,_mm256_srli_epi32(x,11));
  x=_mm256_xor_si256(x,_mm256_and_si256(_mm256_slli_epi32(x,7),_mm256_set1_epi32(0x9D2C5680u)));
  x=_mm256_xor_si256(x,_mm256_and_si256(_mm256_slli_epi32(x,15),_mm256_set1_epi32(0xEFC60000u)));
  return _mm256_xor_si256(x,_mm256_srli_epi32(x,18));
}
static inline void batch(uint32_t firstPairIndex,uint32_t*out0,uint32_t*out1,uint32_t*out2,uint32_t*out3){
  Vec8 state[N];
  const auto base=_mm256_set1_epi32(0x8b8b8b8b);
  for(auto &v:state)v.x=base;
  const auto seed0=_mm256_and_si256(lane8(firstPairIndex),_mm256_set1_epi32(65535));
  const auto seed1=_mm256_set1_epi32(firstPairIndex>>16);
  const auto A=_mm256_set1_epi32(1664525),B=_mm256_set1_epi32(1566083941);
  for(int k=0;k<N;k++){
    const int u=(k+P)%N,v=(k+Q)%N;
    const auto x=_mm256_xor_si256(_mm256_xor_si256(state[k].x,state[u].x),state[(k+N-1)%N].x);
    const auto r1=_mm256_mullo_epi32(A,sh27(x));
    auto r2=_mm256_add_epi32(r1,_mm256_set1_epi32(k==0?2:k));
    if(k==1)r2=_mm256_add_epi32(r2,seed0);
    if(k==2)r2=_mm256_add_epi32(r2,seed1);
    state[u].x=_mm256_add_epi32(state[u].x,r1);
    state[v].x=_mm256_add_epi32(state[v].x,r2);
    state[k].x=r2;
  }
  for(int k=N;k<2*N;k++){
    const int i=k-N,u=(k+P)%N,v=(k+Q)%N;
    const auto x=_mm256_add_epi32(_mm256_add_epi32(state[i].x,state[u].x),state[(i+N-1)%N].x);
    const auto r3=_mm256_mullo_epi32(B,sh27(x));
    const auto r4=_mm256_sub_epi32(r3,_mm256_set1_epi32(i));
    state[u].x=_mm256_xor_si256(state[u].x,r3);
    state[v].x=_mm256_xor_si256(state[v].x,r4);
    state[i].x=r4;
  }
  alignas(32) uint32_t*outs[4]={out0,out1,out2,out3};
  const auto upper=_mm256_set1_epi32(0x80000000u),lower=_mm256_set1_epi32(0x7FFFFFFFu);
  for(int i=0;i<4;i++){
    const auto y=_mm256_or_si256(_mm256_and_si256(state[i].x,upper),_mm256_and_si256(state[i+1].x,lower));
    const auto bit=_mm256_and_si256(y,_mm256_set1_epi32(1));
    const auto twist=_mm256_xor_si256(state[i+397].x,_mm256_xor_si256(_mm256_srli_epi32(y,1),_mm256_and_si256(_mm256_sub_epi32(_mm256_setzero_si256(),bit),_mm256_set1_epi32(0x9908B0DFu))));
    _mm256_storeu_si256((__m256i*)outs[i],temper(twist));
  }
}
int main(int argc,char**argv){
  const uint64_t count=argc>1?strtoull(argv[1],nullptr,10):1048576ull,start=argc>2?strtoull(argv[2],nullptr,10):0ull;
  if((start&7)||(count&7)||start+count>4294967296ull)return 3;
  constexpr std::array<uint32_t,9> examples{0u,1u,7u,8131u,0x00010001u,0x00028131u,0x7fffffff,0xffff0000u,0xffffffffu};
  for(uint32_t idx:examples){
    uint32_t a[8] __attribute__((aligned(32))),b[8] __attribute__((aligned(32))),c[8] __attribute__((aligned(32))),d[8] __attribute__((aligned(32)));
    batch(idx&~7u,a,b,c,d);
    std::seed_seq seq{idx&65535,idx>>16};std::mt19937 gen(seq);
    if(a[idx&7]!=gen()||b[idx&7]!=gen()||c[idx&7]!=gen()||d[idx&7]!=gen()){
      printf("NATIVE_MT_CONTROL_FAIL seed=%u/%u\n",idx&65535,idx>>16);return 4;
    }
  }
  printf("NATIVE_CXX_SEEDSEQ_TWO16_MT_OUTPUT_CONTROLS=9 PASS\n");fflush(stdout);
  unsigned long long first=0,full=0;
  auto starttime=std::chrono::steady_clock::now();
#pragma omp parallel for schedule(static) reduction(+:first,full)
  for(int64_t k=0;k<(int64_t)(count/8);k++){
    alignas(32)uint32_t a[8],b[8],c[8],d[8];
    const uint32_t idx=(uint32_t)(start+uint64_t(k)*8);
    batch(idx,a,b,c,d);
    for(int j=0;j<8;j++){
      if(a[j]==sourceLE[0]||a[j]==sourceBE[0]){
        const bool le=a[j]==sourceLE[0],f=(le?b[j]==sourceLE[1]&&c[j]==sourceLE[2]&&d[j]==sourceLE[3]:b[j]==sourceBE[1]&&c[j]==sourceBE[2]&&d[j]==sourceBE[3]);
        first++;if(f)full++;
#pragma omp critical
        {printf("FIRST_MATCH seed=%u/%u endian=%s words=%08X,%08X,%08X,%08X full=%d\n",(idx+j)&65535,(idx+j)>>16,le?"LE":"BE",a[j],b[j],c[j],d[j],f?1:0);fflush(stdout);}
      }
    }
  }
  const double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-starttime).count();
  printf("START=%llu COUNT=%llu FIRST_WORD_HITS=%llu FULL_16BYTE_HITS=%llu SECONDS=%.3f RATE=%.0f/s THREADS=%d\n",(unsigned long long)start,(unsigned long long)count,first,full,sec,count/sec,omp_get_max_threads());
  return 0;
}
