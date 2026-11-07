// H17 Agent26: source-only first intact coupon versus every native scalar seed32
// and the first 1872 output offsets, four byte/word layouts, three MT cycles.
// SHA256 original spool: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
// Intact 07:00 JOB0300 ACK: FBBBC54356483F5864BB3F06794518A5
// Withhold selected K04 row129, target hash, route mask, and K08 altogether.
// Requires AVX512F/DQ: g++ -O3 -march=native -std=c++17 -pthread file.cpp -o scan
// Run scan START END THREADS SYNTHETIC(0/1). END<=4294967296, aligned16.
// Synthetic: H17_TEST_OFFSET=623 H17_TEST_VIEW=3 scan 12336 12352 1 1
#include <immintrin.h>
#include <array>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <thread>
#include <vector>
#include <chrono>
using V=__m512i;
inline V shr(V x,int k){return _mm512_srli_epi32(x,k);}
inline V temper(V x){
 x=_mm512_xor_si512(x,shr(x,11));
 x=_mm512_xor_si512(x,_mm512_and_si512(_mm512_slli_epi32(x,7),_mm512_set1_epi32(0x9D2C5680u)));
 x=_mm512_xor_si512(x,_mm512_and_si512(_mm512_slli_epi32(x,15),_mm512_set1_epi32(0xEFC60000u)));
 return _mm512_xor_si512(x,shr(x,18));
}
void twist(V* s){
 const V hi=_mm512_set1_epi32(0x80000000u),lo=_mm512_set1_epi32(0x7fffffffu),a=_mm512_set1_epi32(0x9908B0DFu),one=_mm512_set1_epi32(1u);
 for(int i=0;i<227;i++){
  V y=_mm512_or_si512(_mm512_and_si512(s[i],hi),_mm512_and_si512(s[i+1],lo));
  s[i]=_mm512_xor_si512(_mm512_xor_si512(s[i+397],shr(y,1)),_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,one),a));
 }
 for(int i=227;i<623;i++){
  V y=_mm512_or_si512(_mm512_and_si512(s[i],hi),_mm512_and_si512(s[i+1],lo));
  s[i]=_mm512_xor_si512(_mm512_xor_si512(s[i-227],shr(y,1)),_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,one),a));
 }
 V y=_mm512_or_si512(_mm512_and_si512(s[623],hi),_mm512_and_si512(s[0],lo));
 s[623]=_mm512_xor_si512(_mm512_xor_si512(s[396],shr(y,1)),_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,one),a));
}
using T=std::array<std::array<uint32_t,4>,4>;
T original(){return {{{0x43C5BBFBu,0x583F4856u,0x063FBB64u,0xA5184579u},
{0xFBBBC543u,0x56483F58u,0x64BB3F06u,0x794518A5u},
{0xA5184579u,0x063FBB64u,0x583F4856u,0x43C5BBFBu},
{0x794518A5u,0x64BB3F06u,0x56483F58u,0xFBBBC543u}}};}
T synthetic(){
 const char* po=std::getenv("H17_TEST_OFFSET"),*pv=std::getenv("H17_TEST_VIEW");
 unsigned offset=po?std::strtoul(po,nullptr,0):1200,view=pv?std::strtoul(pv,nullptr,0):0;
 if(offset>1871||view>3){std::fprintf(stderr,"synthetic offset/view invalid\n");std::exit(2);}
 std::mt19937 mt(12345u);mt.discard(offset);
 uint32_t raw[4]{};for(auto& x:raw)x=mt();
 uint8_t buf[16]{};
 for(int i=0;i<4;i++){
  uint32_t w=raw[(view>=2)?3-i:i];
  for(int j=0;j<4;j++)buf[4*i+j]=uint8_t(w>>(8*((view%2)?3-j:j)));
 }
 T out{};
 for(int q=0;q<4;q++)for(int i=0;i<4;i++){
  int p=q>=2?3-i:i;uint32_t w=0;
  if(q%2){for(int j=0;j<4;j++)w=(w<<8)|buf[4*p+j];}
  else {for(int j=3;j>=0;j--)w=(w<<8)|buf[4*p+j];}
  out[q][i]=w;
 }
 return out;
}
struct Stats{std::array<uint64_t,4> first{},full{};};
inline void probe(V a,V b,V c,V d,const T& target,uint64_t base,unsigned offset,Stats& count,int tid){
 for(int k=0;k<4;k++){
  __mmask16 m=_mm512_cmpeq_epi32_mask(a,_mm512_set1_epi32(target[k][0]));
  count.first[k]+=__builtin_popcount((unsigned)m);
  if(!m)continue;
  alignas(64) uint32_t v[4][16];
  _mm512_store_si512((V*)v[0],a);_mm512_store_si512((V*)v[1],b);
  _mm512_store_si512((V*)v[2],c);_mm512_store_si512((V*)v[3],d);
  while(m){int lane=__builtin_ctz((unsigned)m);m&=m-1;
   if(v[1][lane]==target[k][1]&&v[2][lane]==target[k][2]&&v[3][lane]==target[k][3]){
    count.full[k]++;
    std::printf("FULL_PACKET seed=%llu offset=%u orientation=%d words=%08X,%08X,%08X,%08X thread=%d\n",
     (unsigned long long)(base+lane),offset,k,v[0][lane],v[1][lane],v[2][lane],v[3][lane],tid);
    std::fflush(stdout);
   }
  }
 }
}
Stats scan(uint64_t begin,uint64_t end,int tid,const T& target){
 Stats count{};alignas(64) V state[624],words[624],carry[3];
 const V mult=_mm512_set1_epi32(1812433253u);alignas(64) uint32_t seeds[16];
 for(uint64_t n=begin;n<end;n+=16){
  for(int j=0;j<16;j++)seeds[j]=uint32_t(n+j);
  state[0]=_mm512_load_si512((V*)seeds);
  for(int i=1;i<624;i++){
   V p=state[i-1];
   state[i]=_mm512_add_epi32(_mm512_mullo_epi32(_mm512_xor_si512(p,shr(p,30)),mult),_mm512_set1_epi32(i));
  }
  for(int cycle=0;cycle<4;cycle++){
   twist(state);
   for(int i=0;i<624;i++)words[i]=temper(state[i]);
   if(cycle>0){
    unsigned origin=(cycle-1)*624;
    probe(carry[0],carry[1],carry[2],words[0],target,n,origin+621,count,tid);
    probe(carry[1],carry[2],words[0],words[1],target,n,origin+622,count,tid);
    probe(carry[2],words[0],words[1],words[2],target,n,origin+623,count,tid);
   }
   if(cycle<3){
    for(int i=0;i<=620;i++)probe(words[i],words[i+1],words[i+2],words[i+3],target,n,cycle*624+i,count,tid);
    for(int i=0;i<3;i++)carry[i]=words[621+i];
   }
  }
 }
 return count;
}
int main(int argc,char**argv){
 if(argc!=5){std::fprintf(stderr,"arguments: begin end threads synthetic\n");return 2;}
 uint64_t begin=std::strtoull(argv[1],nullptr,0),end=std::strtoull(argv[2],nullptr,0);
 int workers=std::atoi(argv[3]),syn=std::atoi(argv[4]);
 if(begin>=end||end>4294967296ull||begin%16||end%16||workers<1||workers>8||(syn!=0&&syn!=1))return 2;
 T target=syn?synthetic():original();
 auto started=std::chrono::steady_clock::now();
 std::vector<Stats> stats(workers);std::vector<std::thread> threads;
 uint64_t part=((end-begin+uint64_t(workers)-1)/workers+15)/16*16;
 for(int k=0;k<workers;k++){
  uint64_t lo=std::min(end,begin+uint64_t(k)*part),hi=std::min(end,lo+part);
  threads.emplace_back([&,k,lo,hi]{if(lo<hi)stats[k]=scan(lo,hi,k,target);});
 }
 for(auto& t:threads)t.join();
 std::array<uint64_t,4> first{},full{};
 for(const auto& s:stats)for(int j=0;j<4;j++){first[j]+=s.first[j];full[j]+=s.full[j];}
 auto ms=std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-started).count();
 std::printf("SUMMARY begin=%llu end=%llu checked=%llu synthetic=%d first=%llu,%llu,%llu,%llu full=%llu,%llu,%llu,%llu elapsed_ms=%lld\n",
  (unsigned long long)begin,(unsigned long long)end,(unsigned long long)(end-begin),syn,
  (unsigned long long)first[0],(unsigned long long)first[1],(unsigned long long)first[2],(unsigned long long)first[3],
  (unsigned long long)full[0],(unsigned long long)full[1],(unsigned long long)full[2],(unsigned long long)full[3],(long long)ms);
 return 0;
}
