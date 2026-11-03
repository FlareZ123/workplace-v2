/* H-17 K04: entire uint32 std::mt19937 seed space, 15 prospective pre-spool
 * generator origins. Each origin is a fully source-determined native p951 MT
 * state. Selected disputed ACK, K04 mask and commitments are never read.
 * Source origin choice remains a conditional hypothesis, not an attested epoch.
 *
 * Build: g++ -O3 -std=c++17 -mavx2 -fopenmp agents/agent3/k04_native_pre_spool_seed_sft.cpp -lcrypto -o native_seed_test
 * Run four disjoint shards: ./native_seed_test 0 1073741824 etc
 */
#include <immintrin.h>
#include <openssl/sha.h>
#include <omp.h>
#include <random>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cassert>
#include <inttypes.h>

struct Witness{int index;uint32_t output;};
static const Witness w[]={
 {-1081,0x1cc39602U},{-999,0xbe48792fU},{-964,0xb935e9f6U},
 {-938,0x44744295U},{-904,0xc1968864U},{-810,0x7a906f32U},
 {-775,0x99e65dd9U},{-769,0xf9ce04eaU},{-761,0xf1399ce6U},
 {-754,0x2a5108f0U},{-685,0x1d73a775U},{-684,0x2c912643U},
 {-683,0x96afca09U},{-677,0xd1326968U},{-670,0x16f14fa5U},
 // The last two are follow-up holdouts, never tested as origins.
 {-622,0x73182ed3U},{-616,0x0bd9f8b8U}
};
static void pin(const char*name,const char*want){
 FILE*f=fopen(name,"rb");assert(f);
 assert(fseek(f,0,SEEK_END)==0);long n=ftell(f);assert(n>0&&n<1000000);
 rewind(f);unsigned char*b=(unsigned char*)malloc((size_t)n);assert(b);
 assert(fread(b,1,(size_t)n,f)==(size_t)n);fclose(f);
 unsigned char dig[32];SHA256(b,(size_t)n,dig);free(b);
 char got[65];for(int j=0;j<32;j++)sprintf(got+j*2,"%02x",dig[j]);
 got[64]=0;assert(strcmp(got,want)==0);
}
static __m256i temper(__m256i x){
 x=_mm256_xor_si256(x,_mm256_srli_epi32(x,11));
 x=_mm256_xor_si256(x,_mm256_and_si256(_mm256_slli_epi32(x,7),_mm256_set1_epi32(0x9d2c5680U)));
 x=_mm256_xor_si256(x,_mm256_and_si256(_mm256_slli_epi32(x,15),_mm256_set1_epi32(0xefc60000U)));
 return _mm256_xor_si256(x,_mm256_srli_epi32(x,18));
}
static __m256i first(__m256i s0,__m256i s1,__m256i s397){
 auto left=_mm256_and_si256(s0,_mm256_set1_epi32(0x80000000U));
 auto right=_mm256_and_si256(s1,_mm256_set1_epi32(0x7fffffffU));
 auto u=_mm256_or_si256(left,right);
 auto low=_mm256_and_si256(u,_mm256_set1_epi32(1));
 auto correction=_mm256_and_si256(_mm256_sub_epi32(_mm256_setzero_si256(),low),_mm256_set1_epi32(0x9908b0dfU));
 return temper(_mm256_xor_si256(s397,_mm256_xor_si256(_mm256_srli_epi32(u,1),correction)));
}
int main(int argc,char**argv){
 assert(argc==3);
 uint64_t begin=strtoull(argv[1],nullptr,0),end=strtoull(argv[2],nullptr,0);
 assert(begin<=end&&end<=UINT64_C(4294967296));
 pin("resources/evidence/print/spool-reconstruction.log",
     "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083");
 pin("resources/evidence/maintenance/seal-receipts.jsonl",
     "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32");
 // Scalar seeded reference against actual standard library, across boundary seeds.
 for(uint32_t seed:{0U,1U,5489U,0xdeadbeefU,0xffffffffU}){
  __m256i state[398];
  state[0]=_mm256_set1_epi32(seed);
  for(int j=1;j<398;j++){
   __m256i x=state[j-1];
   state[j]=_mm256_add_epi32(_mm256_mullo_epi32(_mm256_xor_si256(x,_mm256_srli_epi32(x,30)),_mm256_set1_epi32(1812433253U)),_mm256_set1_epi32(j));
  }
  alignas(32) uint32_t values[8];
  _mm256_store_si256((__m256i*)values,first(state[0],state[1],state[397]));
  std::mt19937 check(seed);assert(values[0]==check());
 }
 std::mt19937 check(5489U);assert(check()==3499211612U);
 puts("NATIVE_MT_SFT seeded reference controls PASS");fflush(stdout);
 uint64_t prefixes=0,second=0,third=0,checked=0;
 double started=omp_get_wtime();
 #pragma omp parallel reduction(+:prefixes,second,third,checked)
 {
  alignas(32) __m256i states[398];
  alignas(32) uint32_t lanes[8];
  #pragma omp for schedule(dynamic,8192)
  for(uint64_t base=begin;base<end;base+=8){
   int n=(int)((end-base)>=8?8:end-base);
   states[0]=_mm256_setr_epi32((int)(base+0),(int)(base+1),(int)(base+2),(int)(base+3),(int)(base+4),(int)(base+5),(int)(base+6),(int)(base+7));
   for(int j=1;j<398;j++){
    __m256i x=states[j-1];
    states[j]=_mm256_add_epi32(_mm256_mullo_epi32(_mm256_xor_si256(x,_mm256_srli_epi32(x,30)),_mm256_set1_epi32(1812433253U)),_mm256_set1_epi32(j));
   }
   auto candidate=first(states[0],states[1],states[397]);
   int mask=0;
   for(int k=0;k<15;k++){
    auto eq=_mm256_cmpeq_epi32(candidate,_mm256_set1_epi32(w[k].output));
    mask|=_mm256_movemask_ps(_mm256_castsi256_ps(eq));
   }
   if(mask){
    _mm256_store_si256((__m256i*)lanes,candidate);
    for(int lane=0;lane<n;lane++)if(mask&(1<<lane)){
     uint32_t seed=(uint32_t)(base+(uint64_t)lane);
     for(int k=0;k<15;k++)if(lanes[lane]==w[k].output){
      prefixes++;
      std::mt19937 g(seed);assert(g()==w[k].output);
      int gap1=w[k+1].index-w[k].index;
      int gap2=w[k+2].index-w[k].index;
      uint32_t y1=0,y2=0;
      for(int j=1;j<=gap2;j++){
       uint32_t out=g();
       if(j==gap1)y1=out;
       if(j==gap2)y2=out;
      }
      bool pass1=(y1==w[k+1].output);
      bool pass2=(pass1&&y2==w[k+2].output);
      second+=pass1;third+=pass2;
      #pragma omp critical
      {printf("PREFIX origin=%d seed=%u next_gap=%d next=%08X pass=%d next2_gap=%d next2=%08X pass=%d\n",
       w[k].index,seed,gap1,y1,(int)pass1,gap2,y2,(int)pass2);fflush(stdout);}
     }
    }
   }
   checked+=(uint64_t)n;
  }
 }
 printf("SHARD [%" PRIu64 ",%" PRIu64 ") checked=%" PRIu64 " origins=15 first=%" PRIu64 " second=%" PRIu64 " third=%" PRIu64 " seconds=%.2f\n",
   begin,end,checked,prefixes,second,third,omp_get_wtime()-started);
 return third?1:0;
}