/* H-17 K04: target-reaching, selected-only exhaustive uint32 native MT19937.
 * Fresh scalar-seeded std::mt19937 emits exactly four first native words per
 * Sixteen disjoint 2^28-seed CI shards span every possible uint32 seed.
 * coupon, with forward/reversed word order and little/big endian serialization.
 * The untrusted selected copied ACK2 is never used to form a coupon.
 * Source pin, real seeded controls and a planted full-component control included.
 *
 * C++17 + AVX2 + OpenMP + OpenSSL; provide start,end and original spool path.
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
static const uint8_t mask[16]={
 0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C
};
static const uint8_t target[32]={
 0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,
 0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0
};
static constexpr uint32_t PLANT=0x5A1704A2U;
static constexpr int PLANT_VIEW=3;

static void source_pin(const char*name){
 FILE*f=fopen(name,"rb");assert(f&&fseek(f,0,SEEK_END)==0);
 long n=ftell(f);assert(n>0&&n<500000);rewind(f);
 auto*b=(uint8_t*)malloc((size_t)n);assert(b);
 assert(fread(b,1,(size_t)n,f)==(size_t)n);fclose(f);
 uint8_t out[32];SHA256(b,(size_t)n,out);free(b);
 const char*expected="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
 char got[65];for(int j=0;j<32;j++)sprintf(got+2*j,"%02x",out[j]);got[64]=0;
 assert(strcmp(got,expected)==0);
}
static inline __m256i temper(__m256i x){
 x=_mm256_xor_si256(x,_mm256_srli_epi32(x,11));
 x=_mm256_xor_si256(x,_mm256_and_si256(_mm256_slli_epi32(x,7),_mm256_set1_epi32(0x9d2c5680U)));
 x=_mm256_xor_si256(x,_mm256_and_si256(_mm256_slli_epi32(x,15),_mm256_set1_epi32(0xefc60000U)));
 return _mm256_xor_si256(x,_mm256_srli_epi32(x,18));
}
static inline __m256i output(__m256i s0,__m256i s1,__m256i s397){
 auto pair=_mm256_or_si256(_mm256_and_si256(s0,_mm256_set1_epi32(0x80000000U)),
                            _mm256_and_si256(s1,_mm256_set1_epi32(0x7fffffffU)));
 auto low=_mm256_and_si256(pair,_mm256_set1_epi32(1));
 auto corr=_mm256_and_si256(_mm256_sub_epi32(_mm256_setzero_si256(),low),_mm256_set1_epi32(0x9908b0dfU));
 return temper(_mm256_xor_si256(s397,_mm256_xor_si256(_mm256_srli_epi32(pair,1),corr)));
}
static inline void complete(const uint32_t word[4],int view,uint8_t out[16]){
 for(int i=0;i<4;i++){
  uint32_t v=word[(view&2)?3-i:i];
  for(int b=0;b<4;b++)
   out[i*4+b]=(uint8_t)((v>>(((view&1)?3-b:b)*8))&255U)^mask[i*4+b];
 }
}
static void seeded_controls(){
 alignas(32) __m256i s[401];
 alignas(32) uint32_t result[8];
 for(uint32_t seed:{0U,1U,5489U,8131U,PLANT,0xffffffffU}){
  s[0]=_mm256_set1_epi32(seed);
  for(int i=1;i<=400;i++){
   auto p=s[i-1];
   s[i]=_mm256_add_epi32(_mm256_mullo_epi32(
    _mm256_xor_si256(p,_mm256_srli_epi32(p,30)),_mm256_set1_epi32(1812433253U)),
    _mm256_set1_epi32(i));
  }
  std::mt19937 actual(seed);
  for(int j=0;j<4;j++){
   _mm256_store_si256((__m256i*)result,output(s[j],s[j+1],s[j+397]));
   assert(result[0]==actual());
  }
 }
 std::mt19937 g(5489U);assert(g()==3499211612U);
 puts("SFT std::mt19937 six seeded four-native-word positive controls PASS");
 fflush(stdout);
}
static void planted_digest(uint8_t digest[32]){
 std::mt19937 g(PLANT);
 uint32_t words[4];for(auto &w:words)w=g();
 uint8_t comp[16];complete(words,PLANT_VIEW,comp);SHA256(comp,16,digest);
}
int main(int argc,char**argv){
 assert(argc==4);
 uint64_t begin=strtoull(argv[1],nullptr,0),end=strtoull(argv[2],nullptr,0);
 assert(begin<=end&&end<=UINT64_C(4294967296));
 source_pin(argv[3]);seeded_controls();
 uint8_t planted[32];planted_digest(planted);
 uint64_t checked=0,original_hits=0,plant_hits=0;
 double started=omp_get_wtime();
 #pragma omp parallel reduction(+:checked,original_hits,plant_hits)
 {
  alignas(32) __m256i s[401];
  alignas(32) uint32_t lanes[4][8];
  uint32_t four[4];uint8_t candidate[16],digest[32];
  #pragma omp for schedule(dynamic,4096)
  for(uint64_t base=begin;base<end;base+=8){
   const int n=(int)((end-base)>=8?8:end-base);
   s[0]=_mm256_setr_epi32((int)(base+0),(int)(base+1),(int)(base+2),(int)(base+3),
                           (int)(base+4),(int)(base+5),(int)(base+6),(int)(base+7));
   for(int i=1;i<=400;i++){
    auto p=s[i-1];
    s[i]=_mm256_add_epi32(_mm256_mullo_epi32(
     _mm256_xor_si256(p,_mm256_srli_epi32(p,30)),_mm256_set1_epi32(1812433253U)),
     _mm256_set1_epi32(i));
   }
   for(int j=0;j<4;j++)
    _mm256_store_si256((__m256i*)lanes[j],output(s[j],s[j+1],s[j+397]));
   for(int k=0;k<n;k++){
    for(int j=0;j<4;j++)four[j]=lanes[j][k];
    for(int view=0;view<4;view++){
     complete(four,view,candidate);
     SHA256(candidate,16,digest);
     if(memcmp(digest,target,32)==0){
      original_hits++;
      #pragma omp critical
      {
       printf("*** ORIGINAL_K04_MATCH SEED=%" PRIu64 " view=%d comp=",base+k,view);
       for(int j=0;j<16;j++)printf("%02X",candidate[j]);
       puts("");fflush(stdout);
      }
     }
     if(base+(uint64_t)k==PLANT&&memcmp(digest,planted,32)==0){
      plant_hits++;
      #pragma omp critical
      {printf("PLANTED_MATCH seed=%08X view=%d\n",PLANT,view);fflush(stdout);}
     }
    }
    checked++;
   }
  }
 }
 const uint64_t expected=(begin<=PLANT&&PLANT<end)?1:0;
 printf("SUMMARY [%" PRIu64 ",%" PRIu64 ") seeds=%" PRIu64
        " sha256_checks=%" PRIu64 " original_hits=%" PRIu64
        " planted=%" PRIu64 " expected=%" PRIu64 " seconds=%.3f\n",
        begin,end,checked,4*checked,original_hits,plant_hits,expected,omp_get_wtime()-started);
 assert(checked==end-begin&&plant_hits==expected);
 return original_hits?5:0;
}
