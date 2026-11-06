// Exact original-source CPython two-word initializer inverse, candidate offset k2494.
// Original selected printer ACK2 is not consulted. Compile C++17 -O3 -fopenmp -mbmi2.
#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <immintrin.h>
#include <omp.h>
using u32 = uint32_t;
using u64 = uint64_t;
constexpr u32 F1=1664525u,F2=1566083941u,F2I=0x6a76ae6du;
constexpr std::array<u32,16> G={0x012bd6aau,0x82d2ab13u,0x342096b7u,0x54846536u,0x2ae75db7u,0x826fe838u,0x2b03a8e8u,0x6c2dcb8fu,0xa8e24d0eu,0xe7d7d1c5u,0x3bd2b928u,0x4f5174d3u,0xac6578e6u,0xcff6b601u,0xe5cae0d8u,0xc55ce976u};
constexpr u32 S4=0xe403bb7du,S5=0x1f7b301fu;
constexpr u32 A5=0x2aed5292u;
constexpr u32 S3_MASK=0x8000001fu, S3_VALUE=0x00000011u;
constexpr u32 S6_MASK=0x09cc1c00u, S6_VALUE=0x008c1000u;
constexpr u32 S13_MASK=0x000000ffu,S13_VALUE=0x000000b6u;
constexpr u32 S14_MASK=0x5398ba7du,S14_VALUE=0x4010a820u;
constexpr u32 S15_MASK=0x01800800u,S15_VALUE=0x00000800u;
static inline u32 t(u32 x) {return x^(x>>30);}
static inline u64 eval5(u32 k0,u32 k1,unsigned guess) {
 u32 a=G[1]^(F1*t(G[0])); a+=k0;
 u32 b=(G[2]^(F1*(a^((guess>>0)&3u))))+k1+1u;
 u32 c=(G[3]^(F1*(b^((guess>>2)&3u))))+k0;
 u32 d=(G[4]^(F1*(c^((guess>>4)&3u))))+k1+1u;
 u32 e=(G[5]^(F1*(d^((guess>>6)&3u))))+k0;
 return (u64(d)<<32)|e;
}
static inline bool forward_checks(u32 k0,u32 k1,u32 s6) {
 u32 a=A5, s=S5;
 for(unsigned i=6;i<=15;i++){
  unsigned j=(i-1)&1u;
  a=(G[i]^(F1*t(a)))+(j?k1:k0)+j;
  s=(a^(F2*t(s)))-i;
  if(i==6 && s!=s6)return false;
  if(i==13 && (s&S13_MASK)!=S13_VALUE)return false;
  if(i==14 && (s&S14_MASK)!=S14_VALUE)return false;
  if(i==15 && (s&S15_MASK)!=S15_VALUE)return false;
 }
 return true;
}
static inline bool source_candidate(u32 k0,u32 k1,unsigned guess,u32 s6){
 const u64 z=eval5(k0,k1,guess);
 const u32 a4=u32(z>>32);
 if(u32(z)!=A5)return false;
 // Guess is exactly the high two bits of first-pass A1..A4.
 u32 a=G[1]^(F1*t(G[0])); a+=k0;
 if((a>>30)!=(guess&3u))return false;
 u32 b=(G[2]^(F1*t(a)))+k1+1u;
 if((b>>30)!=((guess>>2)&3u))return false;
 u32 c=(G[3]^(F1*t(b)))+k0;
 if((c>>30)!=((guess>>4)&3u))return false;
 u32 d=(G[4]^(F1*t(c)))+k1+1u;
 if((d>>30)!=((guess>>6)&3u) || d!=a4)return false;
 const u32 x=(a4^(S4+4u))*F2I;
 const u32 s3=t(x);
 if((s3&S3_MASK)!=S3_VALUE)return false;
 return forward_checks(k0,k1,s6);
}
static inline bool lift(u32 k1,unsigned guess,u32& k0){
 k0=0;
 for(unsigned bit=0;bit<32;bit++){
  const u64 z=eval5(k0,k1,guess);
  const u32 candidate=u32(z);
  k0|=(((candidate^A5)>>bit)&1u)<<bit;
  if(bit==4){
   const u32 a4=u32(eval5(k0,k1,guess)>>32);
   const u32 x=(a4^(S4+4u))*F2I;
   if((x&0x1cu)!=(S3_VALUE&0x1cu))return false;
  }
 }
 return true;
}
int main(int argc,char** argv){
 const u64 bound=(argc>1)?std::strtoull(argv[1],nullptr,10):(1ull<<23);
 const u64 start=(argc>2)?std::strtoull(argv[2],nullptr,10):0;
 if(start+bound>(1ull<<23))return 2;
 // Verify the lift against four genuine CPython first-pass integer keys.
 for(const auto& p: {std::pair<u32,u32>{0x12345678u,0x87654321u},{0x00400000u,0x9fffffffu},{1u,2u},{0xffffffffu,0x12345678u}}){
  u32 a=G[0],last=0;unsigned guess=0;
  for(unsigned i=1;i<=5;i++){
   const unsigned j=(i-1)&1u;
   a=(G[i]^(F1*t(a)))+(j?p.second:p.first)+j;
   if(i<5)guess|=(a>>30)<<(2*(i-1));
   last=a;
  }
  u32 recovered=0;
  for(unsigned bit=0;bit<32;bit++) recovered|=(((u32(eval5(recovered,p.second,guess))^last)>>bit)&1u)<<bit;
  if(recovered!=p.first || u32(eval5(recovered,p.second,guess))!=last){std::puts("FAIL planted n2 inverse");return 3;}
 }
 std::puts("PLANTED_EXACT_N2_BITLIFT=4/4 PASS"); std::fflush(stdout);
 const u32 c6=G[6]^(F1*t(A5));
 const u32 second=F2*t(S5);
 unsigned long long tested_s6=0,guess_assignments=0,early_pass=0,roots=0,s3pass=0,late_pass=0;
 const double now=omp_get_wtime();
 #pragma omp parallel for schedule(dynamic,16384) reduction(+:tested_s6,guess_assignments,early_pass,roots,s3pass,late_pass)
 for(long long index=(long long)start;index<(long long)(start+bound);index++){
  const u32 s6=S6_VALUE|_pdep_u32(u32(index),~S6_MASK);
  const u32 k1=((s6+6u)^second)-c6-1u;
  if(!k1)continue;
  tested_s6++;
  for(unsigned guess=0;guess<256;guess++){
   guess_assignments++;
   u32 k0=0;
   if(!lift(k1,guess,k0))continue;
   early_pass++;
   if(u32(eval5(k0,k1,guess))!=A5)continue;
   roots++;
   if(source_candidate(k0,k1,guess,s6)){
     #pragma omp critical
     {std::printf("ORIGINAL_N2_SOURCE_SURVIVOR K0=%08X K1=%08X S6=%08X\n",k0,k1,s6);std::fflush(stdout);}
     late_pass++;
   }
   const u32 a4=u32(eval5(k0,k1,guess)>>32);
   const u32 s3=t((a4^(S4+4u))*F2I);
   if((s3&S3_MASK)==S3_VALUE)s3pass++;
  }
 }
 std::printf("N2_K2494 range_start=%llu range_end=%llu exact_complete=%s examined_S6=%llu guessed_8bit_topstates=%llu early_lowbit_S3_pass=%llu A5_roots=%llu S3_full_pass=%llu S15_corridor_survivors=%llu elapsed_sec=%.3f\n",
 start,start+bound,start==0 && bound==(1ull<<23)?"YES":"NO",tested_s6,guess_assignments,early_pass,roots,s3pass,late_pass,omp_get_wtime()-now);
 return 0;
}
