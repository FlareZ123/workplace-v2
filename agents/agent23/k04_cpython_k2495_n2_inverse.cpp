#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <omp.h>
static constexpr uint32_t U=0xffffffffu;
static uint32_t g[17];
static inline uint32_t f1(uint32_t x){return 1664525u*(x^(x>>30));}
static inline uint32_t f2(uint32_t x){return 1566083941u*(x^(x>>30));}
static inline uint32_t invf1(uint32_t y){uint32_t q=y*0xfee058c5u;return q^(q>>30);}
static inline uint32_t invf2(uint32_t y){uint32_t q=y*0x6a76ae6du;return q^(q>>30);}
static constexpr uint32_t S5=0xE403BB7Du, S6=0x1F7B301Fu;
static uint32_t A6,EXPECTED_K0=0,EXPECTED_K1=0;
static bool SYN=false;
static uint64_t planted_found=0;
static inline uint32_t a6hat(uint32_t k0,uint32_t k1,uint32_t h){
 uint32_t a=(g[1]^f1(g[0]))+k0;
 a=(g[2]^f1(a))+k1+1u;
 for(int i=3;i<=6;i++)a=(g[i]^(1664525u*(a^((h>>(2*(i-3)))&3u))))+((i&1)?k0:k1+1u);
 return a;
}
static inline bool actual_a6(uint32_t k0,uint32_t k1){
 uint32_t a=(g[1]^f1(g[0]))+k0;
 for(int i=2;i<=6;i++)a=(g[i]^f1(a))+((i&1)?k0:k1+1u);
 return a==A6;
}
static inline uint32_t s4_from_k1(uint32_t k1){
 uint32_t a5=invf1(g[6]^(A6-k1-1u));
 return invf2(a5^(S5+5u));
}
static inline uint32_t s7_from_k0(uint32_t k0){
 uint32_t a7=(g[7]^f1(A6))+k0;
 return (a7^f2(S6))-7u;
}
struct Counts {uint64_t scanned=0,pre7=0,paths=0,roots=0,exact=0,s4=0,s14=0,s15=0,s16=0;};
static void invert(uint32_t k0,Counts& c,std::vector<uint32_t>&curr,std::vector<uint32_t>&next){
 for(uint32_t h=0;h<(1u<<8);h++){
  curr.clear();curr.push_back(0u);
  for(int bit=0;bit<32&&!curr.empty();bit++){
   uint32_t mask=(bit==31)?U:((1u<<(bit+1))-1u),step=1u<<bit;
   next.clear();
   for(uint32_t lo:curr){
    if((a6hat(k0,lo,h)&mask)==(A6&mask))next.push_back(lo);
    uint32_t hi=lo|step;
    if((a6hat(k0,hi,h)&mask)==(A6&mask))next.push_back(hi);
   }
   curr.swap(next);
  }
  c.paths++;
  c.roots+=curr.size();
  for(uint32_t k1:curr){
   if(!actual_a6(k0,k1))continue;
   c.exact++;
   if(SYN){if(k0==EXPECTED_K0&&k1==EXPECTED_K1)planted_found++;continue;}
   if((s4_from_k1(k1)&0x8000001fu)!=0x11u)continue;
   c.s4++;
   uint32_t a=A6,s=S6;
   for(int i=7;i<=16;i++){
    a=(g[i]^f1(a))+((i&1)?k0:k1+1u);
    s=(a^f2(s))-uint32_t(i);
    if(i==14){if((s&0xffu)!=0xb6u)break;c.s14++;}
    if(i==15){if((s&0x5398ba7du)!=0x4010a820u)break;c.s15++;}
    if(i==16){if((s&0x01800800u)!=0x00000800u)break;c.s16++;
     #pragma omp critical(hits)
     printf("SOURCE_FORWARD_SURVIVOR k0=%08X k1=%08X\n",k0,k1);
    }
   }
  }
 }
}
int main(int argc,char**argv){
 g[0]=19650218u;
 for(int i=1;i<17;i++)g[i]=1812433253u*(g[i-1]^(g[i-1]>>30))+uint32_t(i);
 if(argc==4 && std::strcmp(argv[1],"synthetic")==0){
  SYN=true;
  EXPECTED_K0=uint32_t(std::strtoul(argv[2],nullptr,16));
  EXPECTED_K1=uint32_t(std::strtoul(argv[3],nullptr,16));
  uint32_t a=(g[1]^f1(g[0]))+EXPECTED_K0;
  for(int i=2;i<=6;i++)a=(g[i]^f1(a))+((i&1)?EXPECTED_K0:EXPECTED_K1+1u);
  A6=a;
  Counts c;std::vector<uint32_t>curr,next;invert(EXPECTED_K0,c,curr,next);
  printf("GENUINE_SEED_BITLIFT k0=%08X k1=%08X refound=%llu roots=%llu exact=%llu\n",EXPECTED_K0,EXPECTED_K1,
   (unsigned long long)planted_found,(unsigned long long)c.roots,(unsigned long long)c.exact);
  return planted_found==1?0:3;
 }
 if(argc!=3){std::fprintf(stderr,"expected start stop (unsigned 64-bit)\n");return 2;}
 uint64_t begin=std::strtoull(argv[1],nullptr,10),end=std::strtoull(argv[2],nullptr,10);
 if(end>4294967296ull||begin>=end)return 2;
 A6=(S6+6u)^f2(S5);
 if(f1(invf1(0x12345678u))!=0x12345678u||f2(invf2(0x12345678u))!=0x12345678u){std::puts("BAD_INVERSE");return 4;}
 auto t0=std::chrono::steady_clock::now();Counts total;
 #pragma omp parallel
 {
  Counts c;std::vector<uint32_t>curr,next;curr.reserve(128);next.reserve(128);
  #pragma omp for schedule(dynamic,2048)
  for(uint64_t xx=begin;xx<end;xx++){
   uint32_t k0=uint32_t(xx*0x9e3779b9ULL);c.scanned++;
   if((s7_from_k0(k0)&0x09cc1c00u)!=0x008c1000u)continue;
   c.pre7++;invert(k0,c,curr,next);
  }
  #pragma omp critical(counts)
  {
   total.scanned+=c.scanned;total.pre7+=c.pre7;total.paths+=c.paths;total.roots+=c.roots;
   total.exact+=c.exact;total.s4+=c.s4;total.s14+=c.s14;total.s15+=c.s15;total.s16+=c.s16;
  }
 }
 auto secs=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
 printf("K2495_N2_SHARD range=[%llu,%llu) scanned=%llu pre7=%llu geometry=%llu roots=%llu actualA6=%llu sourceS4=%llu sourceS14=%llu sourceS15=%llu sourceS16=%llu seconds=%.3f\n",
  (unsigned long long)begin,(unsigned long long)end,(unsigned long long)total.scanned,(unsigned long long)total.pre7,
  (unsigned long long)total.paths,(unsigned long long)total.roots,(unsigned long long)total.exact,(unsigned long long)total.s4,
  (unsigned long long)total.s14,(unsigned long long)total.s15,(unsigned long long)total.s16,secs);
}
