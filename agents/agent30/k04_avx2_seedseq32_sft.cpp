// K04 conditional original-source seed_seq single-uint32 complete seed gate.
// Fixed original ordinary-spool S[3]=873F7515, S[4]=ADD0D034 from the
// published printer-only p955 chronology, selected row129 and all late
// exceptional records excluded. The geometry/producer is hypothetical.
// Original printer SHA256:
// 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
// Native C++ std::seed_seq equivalence controls (32 seeded cases) are mandatory.
// The script reads neither selected K04 bytes, routing mask nor acceptance.
// Build with C++17 and AVX2 enabled, then run adjacent 8-aligned half-open
// integer-seed subranges; cover [0,4294967296) to exhaust the family.
// This is source-only research, not an authenticated coupon recovery.
#include <immintrin.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <chrono>
#include <random>
using V = __m256i;
static constexpr int N=624, P=306, Q=317;
static const V MUL1=_mm256_set1_epi32(1664525u);
static const V MUL2=_mm256_set1_epi32(1566083941u);
static inline V add(V a,V b){return _mm256_add_epi32(a,b);}
static inline V mul(V a,V b){return _mm256_mullo_epi32(a,b);}
static inline V xorr(V a,V b){return _mm256_xor_si256(a,b);}
static inline V diff27(V a){return xorr(a,_mm256_srli_epi32(a,27));}
static void batch(uint32_t base,std::array<uint32_t,8>&s3,
                  std::array<uint32_t,8>&s4){
  alignas(32) V a[N];
  const V constant=_mm256_set1_epi32(0x8b8b8b8b);
  for(int i=0;i<N;i++)a[i]=constant;
  const V R1=_mm256_set1_epi32(1371501266u);
  const V R2=_mm256_set1_epi32(1371501267u);
  a[P]=add(a[P],R1);a[Q]=add(a[Q],R2);a[0]=R2;
  const V seeds=_mm256_setr_epi32(
    int(base),int(base+1),int(base+2),int(base+3),
    int(base+4),int(base+5),int(base+6),int(base+7));
  for(int k=1;k<N;k++){
    const int j=k,p=(k+P)%N,q=(k+Q)%N;
    const V arg=xorr(xorr(a[j],a[p]),a[j-1]);
    const V r1=mul(MUL1,diff27(arg));
    const V r2=add(r1,add(
      (k==1?seeds:_mm256_setzero_si256()),_mm256_set1_epi32(k)));
    a[p]=add(a[p],r1);a[q]=add(a[q],r2);a[j]=r2;
  }
  // The final updates to S[3] and S[4] are at j=321,322.
  for(int j=0;j<=322;j++){
    const int p=(j+P)%N,q=(j+Q)%N;
    const V arg=add(add(a[j],a[p]),a[(j+N-1)%N]);
    const V r3=mul(MUL2,diff27(arg));
    const V r4=_mm256_sub_epi32(r3,_mm256_set1_epi32(j));
    a[p]=xorr(a[p],r3);a[q]=xorr(a[q],r4);a[j]=r4;
  }
  _mm256_storeu_si256((V*)s3.data(),a[3]);
  _mm256_storeu_si256((V*)s4.data(),a[4]);
}
static void positive(){
  for(uint32_t base:{0u,0x8130u,0x87654320u,0xfffffff8u}){
    std::array<uint32_t,8>s3{},s4{};batch(base,s3,s4);
    for(int z=0;z<8;z++){
      std::array<uint32_t,624> v{};
      std::seed_seq seq{uint32_t(base+uint32_t(z))};
      seq.generate(v.begin(),v.end());
      if(s3[z]!=v[3]||s4[z]!=v[4]){
        std::printf("AVX2_MISMATCH seed=%08X actual=%08X/%08X "
                    "native=%08X/%08X\n",
                    base+uint32_t(z),s3[z],s4[z],v[3],v[4]);
        std::exit(3);
      }
    }
  }
  puts("AVX2_NATIVE_CPP_CONTROLS_PASS seeds=32");
}
int main(int argc,char**argv){
  if(argc!=3){
    std::fputs("Expected low high-exclusive 8-aligned uint32 seed range\n",stderr);
    return 2;
  }
  const uint64_t lo=std::strtoull(argv[1],nullptr,10);
  const uint64_t hi=std::strtoull(argv[2],nullptr,10);
  if(lo>=hi||hi>4294967296ull||lo%8||hi%8)return 2;
  positive();
  uint64_t seen=0,hits3=0,hits34=0;
  const auto start=std::chrono::steady_clock::now();
  for(uint64_t v=lo;v<hi;v+=8){
    std::array<uint32_t,8>a{},b{};
    batch(uint32_t(v),a,b);
    for(int j=0;j<8;j++){
      hits3+=a[j]==0x873F7515u;
      if(a[j]==0x873F7515u&&b[j]==0xADD0D034u){
        hits34++;
        std::printf("SOURCE_MATCH seed=%llu\n",
                    (unsigned long long)(v+j));
      }
    }
    seen+=8;
  }
  const double elapsed=std::chrono::duration<double>(
    std::chrono::steady_clock::now()-start).count();
  std::printf("COMPLETE low=%llu high=%llu assignments=%llu "
              "original_S3_hits=%llu original_S3S4_hits=%llu "
              "seconds=%.3f rate=%.2f seeds/s\n",
              (unsigned long long)lo,(unsigned long long)hi,
              (unsigned long long)seen,(unsigned long long)hits3,
              (unsigned long long)hits34,elapsed,seen/elapsed);
  return 0;
}
