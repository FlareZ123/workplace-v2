/*
H-17, Agent 4 (30 Oct 2026): conditional one-32-bit-word C++ seed_seq
initialized MT19937 source experiment.  This test reads NO K04 or K08 target,
mask, nonce, commitment or verifier.  It is not a historical printer claim.

Original source: spool SHA256
7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
V1 Agent22's 128-ordinary-row only GF(2) projection for the retrospective p955
source-consistent MT chronology fixes pre-first-twist S[3]=873F7515 and
S[4]=ADD0D034, with the selected and all five late records excluded.
V1 Agent3 exhausted 0..65535 and stopped with 32-bit relational SMT UNKNOWN.
This program completes all unsigned seed_seq single-word inputs via AVX2,
with a source-independent positive check against native std::seed_seq for
seven seed values.  The p955 chronology and seed_seq producer are HYPOTHESES.

Arguments are COUNT and START, both multiples of 8, satisfying
START+COUNT <= 4294967296. Four exhaustive independent calls use COUNT
1073741824, START 0 / 1073741824 / 2147483648 / 3221225472.
No source result can authenticate the physical ESC-N attempt-2 copied ACK.
*/
#include <immintrin.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <chrono>

constexpr uint32_t originalS3=0x873F7515u, originalS4=0xADD0D034u;
static constexpr int N=624, P=306, Q=317;

struct alignas(32) Vec8 { __m256i x; };

inline __m256i generateT(__m256i x) {return _mm256_xor_si256(x,_mm256_srli_epi32(x,27));}

void batch(uint32_t seedFirst, uint32_t *s3, uint32_t *s4) {
  Vec8 state[N];
  const __m256i init = _mm256_set1_epi32(0x8b8b8b8b);
  for(int j=0;j<N;j++) state[j].x=init;
  const __m256i seeds=_mm256_setr_epi32(seedFirst,seedFirst+1u,seedFirst+2u,seedFirst+3u,seedFirst+4u,seedFirst+5u,seedFirst+6u,seedFirst+7u);
  const __m256i A=_mm256_set1_epi32(1664525);
  for(int k=0;k<N;k++) {
    const int u=(k+P)%N, v=(k+Q)%N;
    __m256i x=_mm256_xor_si256(_mm256_xor_si256(state[k].x,state[u].x),state[(k+N-1)%N].x);
    __m256i r1=_mm256_mullo_epi32(A,generateT(x));
    __m256i r2=_mm256_add_epi32(r1,k==0?_mm256_set1_epi32(1):_mm256_set1_epi32(k));
    if(k==1) r2=_mm256_add_epi32(r2,seeds);
    state[u].x=_mm256_add_epi32(state[u].x,r1);
    state[v].x=_mm256_add_epi32(state[v].x,r2);
    state[k].x=r2;
  }
  const __m256i B=_mm256_set1_epi32(1566083941);
  for(int k=N;k<=946;k++) {
    const int i=k-N, u=(k+P)%N, v=(k+Q)%N;
    __m256i x=_mm256_add_epi32(_mm256_add_epi32(state[i].x,state[u].x),state[(i+N-1)%N].x);
    __m256i r3=_mm256_mullo_epi32(B,generateT(x));
    __m256i r4=_mm256_sub_epi32(r3,_mm256_set1_epi32(i));
    state[u].x=_mm256_xor_si256(state[u].x,r3);
    state[v].x=_mm256_xor_si256(state[v].x,r4);
    state[i].x=r4;
  }
  _mm256_storeu_si256((__m256i*)s3,state[3].x);
  _mm256_storeu_si256((__m256i*)s4,state[4].x);
}

int main(int argc,char**argv) {
  uint64_t count = argc>1 ? strtoull(argv[1],nullptr,10): 1048576ull;
  uint64_t begin = argc>2 ? strtoull(argv[2],nullptr,10): 0ull;
  if(count%8 || begin%8 || count+begin>4294967296ull) return 3;
  std::array<uint32_t,624> output;
  std::seed_seq control{0x8131u};
  control.generate(output.begin(),output.end());
  if(output[3]!=0x66C0E50Eu||output[4]!=0xA2A307BDu) return 4;
  uint32_t control3[8],control4[8];
  batch(0x8130,control3,control4);
  if(control3[1]!=output[3]||control4[1]!=output[4]) {
    printf("CONTROL_MISMATCH vector=%08X/%08X native=%08X/%08X\n",control3[1],control4[1],output[3],output[4]); return 5;
  }
  const uint32_t checkSeeds[]={0u,1u,0x8131u,0x12345678u,0xdeadbeefu,0xffffffffu,123456789u};
  for(const uint32_t check:checkSeeds){
    alignas(32) uint32_t a[8],b[8];
    batch(check&~7u,a,b);
    std::seed_seq native{check};
    native.generate(output.begin(),output.end());
    if(a[check&7u]!=output[3] || b[check&7u]!=output[4]) {
      printf("NATIVE_FAILED_SEED_%08X vector=%08X/%08X native=%08X/%08X\n",check,a[check&7u],b[check&7u],output[3],output[4]);
      return 6;
    }
  }
  printf("NATIVE_S3_S4_POSITIVE_CONTROLS=7\n");
  uint64_t s3hits=0, pairhits=0, nativePos=0;
  auto start=std::chrono::steady_clock::now();
  for(uint64_t k=begin;k<begin+count;k+=8) {
    alignas(32) uint32_t s3[8],s4[8];
    batch((uint32_t)k,s3,s4);
    for(int j=0;j<8;j++) {
      if(s3[j]==originalS3) {s3hits++; printf("S3_MATCH %08X S4=%08X\n",(uint32_t)(k+j),s4[j]);}
      if(s3[j]==originalS3 && s4[j]==originalS4) {pairhits++; printf("FULL_PAIR_MATCH %08X\n",(uint32_t)(k+j));}
      if(s3[j]==0x66C0E50E && s4[j]==0xA2A307BD) nativePos++;
    }
  }
  const double secs=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  printf("START=%llu SEEDS=%llu S3_HITS=%llu PAIR_HITS=%llu CONTROL_PAIRS=%llu SECONDS=%.3f RATE=%.0f seeds/s\n",(unsigned long long)begin,(unsigned long long)count,(unsigned long long)s3hits,(unsigned long long)pairhits,(unsigned long long)nativePos,secs,count/secs);
  return 0;
}
